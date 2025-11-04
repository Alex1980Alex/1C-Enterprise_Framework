"""
Load BSL Index to Qdrant - загрузка BSL индекса в Qdrant
Версия: 2.0 для Week 2, Day 3

Функциональность:
- Загрузка индекса из JSON в Qdrant
- Batch processing для эффективности
- Progress monitoring
- Error handling
- Создание collection с оптимальными параметрами
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QdrantIndexLoader:
    """
    Загрузчик BSL индекса в Qdrant
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "bsl_code",
        batch_size: int = 100
    ):
        """
        Инициализация загрузчика

        Args:
            qdrant_url: URL Qdrant сервера
            collection_name: Имя коллекции
            batch_size: Размер batch для загрузки
        """
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.batch_size = batch_size

        logger.info(f"QdrantIndexLoader инициализирован")
        logger.info(f"  Qdrant URL: {qdrant_url}")
        logger.info(f"  Collection: {collection_name}")
        logger.info(f"  Batch size: {batch_size}")

    def load_index_file(self, index_file: str) -> Dict[str, Any]:
        """
        Загрузка индекса из JSON файла

        Args:
            index_file: Путь к JSON файлу

        Returns:
            Данные индекса
        """
        logger.info(f"📂 Загрузка индекса: {index_file}")

        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)

            total_files = len(index_data.get('files', []))
            logger.info(f"✅ Индекс загружен: {total_files} файлов")

            return index_data

        except FileNotFoundError:
            logger.error(f"❌ Файл индекса не найден: {index_file}")
            return {}
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки индекса: {e}")
            return {}

    def create_collection(self, vector_size: int):
        """
        Создание коллекции в Qdrant

        Args:
            vector_size: Размер векторов
        """
        logger.info(f"🔧 Создание коллекции: {self.collection_name}")

        try:
            # Проверка существования коллекции
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name in collection_names:
                logger.warning(f"⚠️  Коллекция уже существует: {self.collection_name}")
                logger.info(f"🗑️  Удаление старой коллекции...")
                self.client.delete_collection(collection_name=self.collection_name)

            # Создание новой коллекции
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )

            logger.info(f"✅ Коллекция создана: {self.collection_name}")
            logger.info(f"   Размер векторов: {vector_size}")
            logger.info(f"   Метрика: COSINE")

        except Exception as e:
            logger.error(f"❌ Ошибка создания коллекции: {e}")
            raise

    def upload_to_qdrant(self, index_data: Dict[str, Any]) -> int:
        """
        Загрузка индекса в Qdrant

        Args:
            index_data: Данные индекса

        Returns:
            Количество загруженных точек
        """
        metadata = index_data.get('metadata', {})
        files = index_data.get('files', [])

        if not files:
            logger.error("❌ Нет файлов для загрузки")
            return 0

        # Создание коллекции
        vector_size = metadata.get('embedding_dimension', len(files[0]['embedding']))
        self.create_collection(vector_size)

        logger.info(f"📤 Начало загрузки в Qdrant...")
        logger.info(f"📊 Всего файлов: {len(files)}")

        # Разбиение на батчи
        batches = [
            files[i:i + self.batch_size]
            for i in range(0, len(files), self.batch_size)
        ]

        logger.info(f"📦 Создано батчей: {len(batches)}")

        total_uploaded = 0
        start_time = time.time()

        # Загрузка батчами
        for batch_idx, batch in enumerate(batches, 1):
            try:
                points = []

                for file_idx, file_data in enumerate(batch):
                    # Создание точки для Qdrant
                    point = PointStruct(
                        id=total_uploaded + file_idx,
                        vector=file_data['embedding'],
                        payload={
                            'file_path': file_data['file_path'],
                            'module_type': file_data['module_type'],
                            'functions_count': file_data['functions_count'],
                            'variables_count': file_data['variables_count'],
                            'searchable_text': file_data['searchable_text'],
                            'file_size': file_data['file_size'],
                            'indexed_at': file_data['indexed_at'],
                            'processing_time_ms': file_data.get('processing_time_ms', 0)
                        }
                    )
                    points.append(point)

                # Загрузка батча
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )

                total_uploaded += len(points)

                # Прогресс
                progress = (batch_idx / len(batches)) * 100
                elapsed = time.time() - start_time
                speed = total_uploaded / elapsed if elapsed > 0 else 0

                logger.info(
                    f"📦 Батч {batch_idx}/{len(batches)} ({progress:.1f}%): "
                    f"{len(points)} точек загружено | "
                    f"Всего: {total_uploaded} | "
                    f"Скорость: {speed:.1f} точек/сек"
                )

            except Exception as e:
                logger.error(f"❌ Ошибка загрузки батча {batch_idx}: {e}")

        # Финальная статистика
        total_time = time.time() - start_time
        logger.info(
            f"\n{'='*60}\n"
            f"✅ ЗАГРУЗКА ЗАВЕРШЕНА\n"
            f"{'='*60}\n"
            f"📊 Загружено точек:   {total_uploaded}\n"
            f"⏱️  Время загрузки:    {total_time:.1f} сек\n"
            f"⚡ Средняя скорость:  {total_uploaded/total_time:.1f} точек/сек\n"
            f"{'='*60}"
        )

        return total_uploaded

    def verify_collection(self) -> bool:
        """
        Проверка загруженной коллекции

        Returns:
            True если коллекция корректна
        """
        try:
            collection_info = self.client.get_collection(
                collection_name=self.collection_name
            )

            logger.info(
                f"\n{'='*60}\n"
                f"🔍 ИНФОРМАЦИЯ О КОЛЛЕКЦИИ\n"
                f"{'='*60}\n"
                f"📝 Название:          {collection_info.config.params.vectors.size}\n"
                f"📊 Количество точек:  {collection_info.points_count}\n"
                f"📏 Размер векторов:   {collection_info.config.params.vectors.size}\n"
                f"📐 Метрика:           {collection_info.config.params.vectors.distance}\n"
                f"💾 Статус:            OK\n"
                f"{'='*60}"
            )

            return True

        except Exception as e:
            logger.error(f"❌ Ошибка проверки коллекции: {e}")
            return False

    def test_search(self, query: str = "получить данные из базы", limit: int = 5):
        """
        Тестовый поиск в коллекции

        Args:
            query: Поисковый запрос
            limit: Количество результатов
        """
        logger.info(f"\n🔍 Тестовый поиск: '{query}'")

        try:
            # Для поиска нужен embedding, используем пустой вектор для демонстрации
            # В реальном сценарии нужно создать embedding через EmbeddingService
            logger.warning("⚠️  Для реального поиска требуется EmbeddingService")
            logger.info("💡 Используйте qdrant_search.py для семантического поиска")

        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}")


def main():
    """Главная функция"""
    import argparse

    parser = argparse.ArgumentParser(description="Load BSL Index to Qdrant")
    parser.add_argument(
        "--index-file",
        default="D:/1C-Enterprise_Framework/ai-memory-system/data/index/bsl_index_full.json",
        help="Путь к JSON файлу индекса"
    )
    parser.add_argument(
        "--qdrant-url",
        default="http://localhost:6333",
        help="URL Qdrant сервера"
    )
    parser.add_argument(
        "--collection",
        default="bsl_code",
        help="Имя коллекции в Qdrant"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Размер batch для загрузки"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Проверить коллекцию после загрузки"
    )

    args = parser.parse_args()

    # Создание загрузчика
    loader = QdrantIndexLoader(
        qdrant_url=args.qdrant_url,
        collection_name=args.collection,
        batch_size=args.batch_size
    )

    # Загрузка индекса
    index_data = loader.load_index_file(args.index_file)

    if index_data:
        # Загрузка в Qdrant
        uploaded = loader.upload_to_qdrant(index_data)

        if uploaded > 0 and args.verify:
            # Проверка коллекции
            loader.verify_collection()


if __name__ == "__main__":
    main()
