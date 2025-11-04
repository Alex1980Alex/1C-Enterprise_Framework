"""
BSL Indexer - индексация BSL файлов для семантического поиска
Сканирует директории, парсит код, создает эмбеддинги
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# Добавление путей для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.embedding_service import EmbeddingService
from utils.bsl_parser import BSLParser, BSLModule

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class IndexedFile:
    """Структура для индексированного файла"""
    file_path: str
    module_type: str
    functions_count: int
    variables_count: int
    searchable_text: str
    embedding: List[float]
    indexed_at: str
    file_size: int


class BSLIndexer:
    """
    Индексатор BSL файлов
    """

    def __init__(
        self,
        output_dir: str = "D:/1C-Enterprise_Framework/ai-memory-system/data/index",
        embedding_model: str = "nomic-embed-text:latest"
    ):
        """
        Инициализация индексатора

        Args:
            output_dir: Директория для сохранения индекса
            embedding_model: Модель для создания эмбеддингов
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.embedding_service = EmbeddingService(model=embedding_model)
        self.parser = BSLParser()

        self.indexed_files: List[IndexedFile] = []

        logger.info(f"BSLIndexer инициализирован. Выход: {output_dir}")

    def index_directory(
        self,
        directory: str,
        max_files: Optional[int] = None,
        file_pattern: str = "*.bsl"
    ) -> int:
        """
        Индексация директории с BSL файлами

        Args:
            directory: Путь к директории
            max_files: Максимальное количество файлов (None = все)
            file_pattern: Паттерн для поиска файлов

        Returns:
            Количество проиндексированных файлов
        """
        logger.info(f"Начало индексации: {directory}")

        # Поиск BSL файлов
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.error(f"Директория не найдена: {directory}")
            return 0

        bsl_files = list(dir_path.rglob(file_pattern))
        total_files = len(bsl_files)

        if max_files:
            bsl_files = bsl_files[:max_files]
            logger.info(f"Ограничение: {max_files} файлов из {total_files}")
        else:
            logger.info(f"Найдено файлов: {total_files}")

        # Индексация файлов
        success_count = 0
        for i, file_path in enumerate(bsl_files, 1):
            logger.info(f"[{i}/{len(bsl_files)}] {file_path.name}")

            if self._index_file(str(file_path)):
                success_count += 1

            # Прогресс каждые 10 файлов
            if i % 10 == 0:
                logger.info(f"Прогресс: {i}/{len(bsl_files)} ({i*100//len(bsl_files)}%)")

        logger.info(f"Завершено. Успешно: {success_count}/{len(bsl_files)}")
        return success_count

    def _index_file(self, file_path: str) -> bool:
        """
        Индексация одного файла

        Args:
            file_path: Путь к файлу

        Returns:
            True если успешно
        """
        try:
            # Парсинг файла
            module = self.parser.parse_file(file_path)
            if not module:
                logger.warning(f"Не удалось распарсить: {file_path}")
                return False

            # Извлечение текста для поиска
            searchable_text = self.parser.extract_searchable_text(module)

            # Создание эмбеддинга
            embedding = self.embedding_service.create_embedding(searchable_text)
            if not embedding:
                logger.warning(f"Не удалось создать эмбеддинг: {file_path}")
                return False

            # Получение размера файла
            file_size = Path(file_path).stat().st_size

            # Создание записи индекса
            indexed_file = IndexedFile(
                file_path=file_path,
                module_type=module.module_type,
                functions_count=len(module.functions),
                variables_count=len(module.variables),
                searchable_text=searchable_text,
                embedding=embedding,
                indexed_at=datetime.now().isoformat(),
                file_size=file_size
            )

            self.indexed_files.append(indexed_file)
            return True

        except Exception as e:
            logger.error(f"Ошибка индексации {file_path}: {e}")
            return False

    def save_index(self, filename: str = "bsl_index.json"):
        """
        Сохранение индекса в файл

        Args:
            filename: Имя файла для сохранения
        """
        output_path = self.output_dir / filename

        try:
            index_data = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "total_files": len(self.indexed_files),
                    "embedding_model": self.embedding_service.model,
                    "embedding_dimension": len(self.indexed_files[0].embedding) if self.indexed_files else 0
                },
                "files": [asdict(f) for f in self.indexed_files]
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Индекс сохранен: {output_path}")
            logger.info(f"Размер файла: {output_path.stat().st_size / 1024 / 1024:.2f} MB")

        except Exception as e:
            logger.error(f"Ошибка сохранения индекса: {e}")

    def load_index(self, filename: str = "bsl_index.json") -> bool:
        """
        Загрузка индекса из файла

        Args:
            filename: Имя файла индекса

        Returns:
            True если успешно
        """
        input_path = self.output_dir / filename

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)

            self.indexed_files = [
                IndexedFile(**file_data)
                for file_data in index_data["files"]
            ]

            logger.info(f"Индекс загружен: {input_path}")
            logger.info(f"Файлов в индексе: {len(self.indexed_files)}")
            return True

        except FileNotFoundError:
            logger.warning(f"Файл индекса не найден: {input_path}")
            return False
        except Exception as e:
            logger.error(f"Ошибка загрузки индекса: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики индексации

        Returns:
            Словарь со статистикой
        """
        if not self.indexed_files:
            return {"total_files": 0}

        total_functions = sum(f.functions_count for f in self.indexed_files)
        total_variables = sum(f.variables_count for f in self.indexed_files)
        total_size = sum(f.file_size for f in self.indexed_files)

        module_types = {}
        for f in self.indexed_files:
            module_types[f.module_type] = module_types.get(f.module_type, 0) + 1

        return {
            "total_files": len(self.indexed_files),
            "total_functions": total_functions,
            "total_variables": total_variables,
            "total_size_mb": total_size / 1024 / 1024,
            "module_types": module_types,
            "embedding_model": self.embedding_service.model,
            "embedding_dimension": len(self.indexed_files[0].embedding)
        }

    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Поиск похожих файлов по запросу

        Args:
            query: Поисковый запрос
            top_k: Количество результатов

        Returns:
            Список похожих файлов с оценками релевантности
        """
        if not self.indexed_files:
            logger.warning("Индекс пуст")
            return []

        # Создание эмбеддинга для запроса
        query_embedding = self.embedding_service.create_embedding(query)
        if not query_embedding:
            logger.error("Не удалось создать эмбеддинг для запроса")
            return []

        # Вычисление косинусного сходства
        import numpy as np

        query_vec = np.array(query_embedding)
        similarities = []

        for indexed_file in self.indexed_files:
            file_vec = np.array(indexed_file.embedding)

            # Косинусное сходство
            similarity = np.dot(query_vec, file_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(file_vec)
            )

            similarities.append({
                "file_path": indexed_file.file_path,
                "module_type": indexed_file.module_type,
                "similarity": float(similarity),
                "searchable_text": indexed_file.searchable_text[:200] + "..."
            })

        # Сортировка по убыванию релевантности
        similarities.sort(key=lambda x: x["similarity"], reverse=True)

        return similarities[:top_k]


# Главная функция
def main():
    """Основная функция для командной строки"""
    import argparse

    parser = argparse.ArgumentParser(description="BSL Indexer - индексация BSL файлов")
    parser.add_argument(
        "directory",
        help="Директория с BSL файлами"
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=100,
        help="Максимальное количество файлов (default: 100)"
    )
    parser.add_argument(
        "--output",
        default="D:/1C-Enterprise_Framework/ai-memory-system/data/index",
        help="Директория для сохранения индекса"
    )
    parser.add_argument(
        "--search",
        help="Поисковый запрос для тестирования"
    )

    args = parser.parse_args()

    # Создание индексатора
    indexer = BSLIndexer(output_dir=args.output)

    # Индексация
    success_count = indexer.index_directory(
        args.directory,
        max_files=args.max_files
    )

    if success_count > 0:
        # Сохранение индекса
        indexer.save_index()

        # Статистика
        stats = indexer.get_statistics()
        print(f"\n📊 Статистика индексации:")
        print(f"   Файлов: {stats['total_files']}")
        print(f"   Функций: {stats['total_functions']}")
        print(f"   Переменных: {stats['total_variables']}")
        print(f"   Размер: {stats['total_size_mb']:.2f} MB")
        print(f"   Модель: {stats['embedding_model']}")
        print(f"   Размерность: {stats['embedding_dimension']}")

        # Тестовый поиск
        if args.search:
            print(f"\n🔍 Поиск: '{args.search}'")
            results = indexer.search_similar(args.search, top_k=3)

            for i, result in enumerate(results, 1):
                print(f"\n{i}. {Path(result['file_path']).name}")
                print(f"   Релевантность: {result['similarity']:.3f}")
                print(f"   Тип: {result['module_type']}")
                print(f"   Фрагмент: {result['searchable_text'][:100]}...")


if __name__ == "__main__":
    main()
