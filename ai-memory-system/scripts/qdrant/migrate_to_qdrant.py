"""
Миграция BSL индекса из JSON в Qdrant
Переносит все embeddings и метаданные в векторную БД
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm

# Добавление путей для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Batch

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QdrantMigrator:
    """
    Миграция BSL индекса в Qdrant
    """

    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        collection_name: str = "bsl_code"
    ):
        """
        Инициализация мигратора

        Args:
            qdrant_host: Хост Qdrant
            qdrant_port: Порт Qdrant
            collection_name: Название коллекции
        """
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.collection_name = collection_name

        logger.info(f"QdrantMigrator инициализирован: {qdrant_host}:{qdrant_port}")

    def load_json_index(self, json_path: str) -> Dict[str, Any]:
        """
        Загрузка JSON индекса

        Args:
            json_path: Путь к JSON файлу

        Returns:
            Данные индекса
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)

            logger.info(f"✅ Загружен индекс: {json_path}")
            logger.info(f"   Файлов: {len(index_data.get('files', []))}")

            return index_data

        except FileNotFoundError:
            logger.error(f"❌ Файл не найден: {json_path}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON: {e}")
            return None

    def create_collection(self, vector_size: int = 768, recreate: bool = False):
        """
        Создание коллекции в Qdrant

        Args:
            vector_size: Размерность векторов
            recreate: Пересоздать коллекцию если существует
        """
        try:
            # Проверка существования
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if exists:
                if recreate:
                    logger.info(f"♻️ Удаление существующей коллекции '{self.collection_name}'...")
                    self.client.delete_collection(self.collection_name)
                else:
                    logger.info(f"⚠️ Коллекция '{self.collection_name}' уже существует")
                    return True

            # Создание коллекции
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )

            logger.info(f"✅ Коллекция '{self.collection_name}' создана")
            logger.info(f"   Размерность: {vector_size}")
            logger.info(f"   Метрика: COSINE")

            return True

        except Exception as e:
            logger.error(f"❌ Ошибка создания коллекции: {e}")
            return False

    def migrate_batch(
        self,
        files: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> int:
        """
        Миграция данных batch-ами

        Args:
            files: Список файлов из JSON индекса
            batch_size: Размер batch для вставки

        Returns:
            Количество успешно мигрированных точек
        """
        total = len(files)
        migrated = 0

        logger.info(f"🚀 Начало миграции: {total} файлов")
        logger.info(f"   Batch size: {batch_size}")

        # Прогресс бар
        with tqdm(total=total, desc="Миграция", unit="файл") as pbar:
            for i in range(0, total, batch_size):
                batch_files = files[i:i + batch_size]

                # Подготовка точек
                points = []
                for j, file_data in enumerate(batch_files):
                    point_id = i + j + 1  # ID начинается с 1

                    # Payload с метаданными
                    payload = {
                        "file_path": file_data.get("file_path", ""),
                        "module_type": file_data.get("module_type", "Unknown"),
                        "functions_count": file_data.get("functions_count", 0),
                        "variables_count": file_data.get("variables_count", 0),
                        "searchable_text": file_data.get("searchable_text", "")[:500],  # Ограничение для payload
                        "file_size": file_data.get("file_size", 0),
                        "indexed_at": file_data.get("indexed_at", "")
                    }

                    # Вектор
                    embedding = file_data.get("embedding", [])

                    if len(embedding) != 768:
                        logger.warning(f"⚠️ Неправильная размерность эмбеддинга: {len(embedding)}")
                        continue

                    point = PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )

                    points.append(point)

                # Вставка batch
                try:
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=points,
                        wait=True
                    )

                    migrated += len(points)
                    pbar.update(len(batch_files))

                except Exception as e:
                    logger.error(f"❌ Ошибка вставки batch: {e}")

        logger.info(f"✅ Миграция завершена: {migrated}/{total} файлов")
        return migrated

    def verify_migration(self, expected_count: int):
        """
        Проверка результатов миграции

        Args:
            expected_count: Ожидаемое количество точек
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            actual_count = collection_info.points_count

            logger.info(f"\n📊 Результаты миграции:")
            logger.info(f"   Ожидалось: {expected_count}")
            logger.info(f"   Фактически: {actual_count}")
            logger.info(f"   Успех: {actual_count == expected_count}")

            if actual_count == expected_count:
                logger.info(f"✅ Миграция успешна!")
            else:
                logger.warning(f"⚠️ Несоответствие количества точек")

            return actual_count == expected_count

        except Exception as e:
            logger.error(f"❌ Ошибка проверки: {e}")
            return False

    def test_search(self, query_text: str = "процедура записи"):
        """
        Тестовый поиск для проверки работы

        Args:
            query_text: Тестовый запрос
        """
        try:
            logger.info(f"\n🔍 Тестовый поиск: '{query_text}'")

            # Для теста используем простой вектор
            # В реальности нужно создать embedding через Ollama
            test_vector = [0.1] * 768

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=test_vector,
                limit=3
            )

            logger.info(f"   Найдено: {len(results)} результатов")

            for i, result in enumerate(results, 1):
                logger.info(f"\n   {i}. {Path(result.payload['file_path']).name}")
                logger.info(f"      Score: {result.score:.4f}")
                logger.info(f"      Type: {result.payload['module_type']}")

        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}")


def main():
    """Основная функция миграции"""
    import argparse

    parser = argparse.ArgumentParser(description="Миграция BSL индекса в Qdrant")
    parser.add_argument(
        "--json",
        default="D:/1C-Enterprise_Framework/ai-memory-system/data/index/bsl_index.json",
        help="Путь к JSON индексу"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Размер batch для вставки (default: 100)"
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Пересоздать коллекцию"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("📦 Миграция BSL индекса из JSON в Qdrant")
    print("=" * 70)

    # Создание мигратора
    migrator = QdrantMigrator()

    # Загрузка JSON индекса
    print("\n1️⃣ Загрузка JSON индекса...")
    index_data = migrator.load_json_index(args.json)

    if not index_data:
        print("\n❌ Не удалось загрузить индекс")
        return

    files = index_data.get("files", [])
    metadata = index_data.get("metadata", {})

    print(f"   Файлов: {len(files)}")
    print(f"   Модель: {metadata.get('embedding_model', 'unknown')}")
    print(f"   Размерность: {metadata.get('embedding_dimension', 0)}")

    # Создание коллекции
    print("\n2️⃣ Создание коллекции в Qdrant...")
    vector_size = metadata.get("embedding_dimension", 768)

    if not migrator.create_collection(vector_size, recreate=args.recreate):
        print("\n❌ Не удалось создать коллекцию")
        return

    # Миграция данных
    print("\n3️⃣ Миграция данных...")
    migrated_count = migrator.migrate_batch(files, batch_size=args.batch_size)

    # Проверка результатов
    print("\n4️⃣ Проверка результатов...")
    success = migrator.verify_migration(len(files))

    if success:
        print("\n" + "=" * 70)
        print("✅ Миграция завершена успешно!")
        print(f"   Мигрировано: {migrated_count} файлов")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("⚠️ Миграция завершена с предупреждениями")
        print("=" * 70)


if __name__ == "__main__":
    main()
