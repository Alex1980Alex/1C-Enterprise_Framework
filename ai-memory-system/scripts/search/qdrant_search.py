"""
Семантический поиск BSL кода через Qdrant
Использует Ollama для создания query embeddings
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

# Добавление путей для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qdrant_client import QdrantClient
from services.embedding_service import EmbeddingService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QdrantSearch:
    """
    Семантический поиск по BSL коду в Qdrant
    """

    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        collection_name: str = "bsl_code",
        ollama_host: str = "http://localhost:11434",
        embedding_model: str = "nomic-embed-text:latest"
    ):
        """
        Инициализация поискового сервиса

        Args:
            qdrant_host: Хост Qdrant
            qdrant_port: Порт Qdrant
            collection_name: Название коллекции
            ollama_host: URL Ollama сервера
            embedding_model: Модель для эмбеддингов
        """
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.collection_name = collection_name

        self.embedding_service = EmbeddingService(
            ollama_host=ollama_host,
            model=embedding_model
        )

        logger.info(f"QdrantSearch инициализирован")
        logger.info(f"   Qdrant: {qdrant_host}:{qdrant_port}")
        logger.info(f"   Коллекция: {collection_name}")
        logger.info(f"   Модель: {embedding_model}")

    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Семантический поиск по запросу

        Args:
            query: Поисковый запрос
            top_k: Количество результатов
            score_threshold: Минимальный порог релевантности

        Returns:
            Список результатов с метаданными
        """
        try:
            # Создание эмбеддинга для запроса
            logger.info(f"🔍 Поиск: '{query}'")
            query_embedding = self.embedding_service.create_embedding(query)

            if not query_embedding:
                logger.error("Не удалось создать эмбеддинг для запроса")
                return []

            # Поиск в Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold
            )

            # Форматирование результатов
            results = []
            for result in search_results:
                formatted_result = {
                    "id": result.id,
                    "score": result.score,
                    "file_path": result.payload.get("file_path", ""),
                    "module_type": result.payload.get("module_type", "Unknown"),
                    "functions_count": result.payload.get("functions_count", 0),
                    "variables_count": result.payload.get("variables_count", 0),
                    "searchable_text": result.payload.get("searchable_text", "")
                }
                results.append(formatted_result)

            logger.info(f"✅ Найдено результатов: {len(results)}")
            return results

        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}")
            return []

    def print_results(self, results: List[Dict[str, Any]]):
        """
        Красивый вывод результатов поиска

        Args:
            results: Список результатов
        """
        if not results:
            print("\n❌ Результатов не найдено")
            return

        print(f"\n📊 Найдено результатов: {len(results)}")
        print("=" * 80)

        for i, result in enumerate(results, 1):
            file_name = Path(result["file_path"]).name
            score_percent = result["score"] * 100

            print(f"\n{i}. {file_name}")
            print(f"   Релевантность: {score_percent:.1f}%")
            print(f"   Тип модуля: {result['module_type']}")
            print(f"   Функций: {result['functions_count']}")
            print(f"   Переменных: {result['variables_count']}")
            print(f"   Путь: {result['file_path']}")

            # Показываем первые 200 символов текста
            searchable_text = result['searchable_text'][:200].strip()
            if searchable_text:
                print(f"\n   Фрагмент кода:")
                for line in searchable_text.split('\n')[:5]:
                    if line.strip():
                        print(f"      {line[:70]}")

        print("\n" + "=" * 80)

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Получение статистики коллекции

        Returns:
            Словарь со статистикой
        """
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)

            stats = {
                "collection_name": self.collection_name,
                "points_count": collection_info.points_count,
                "vectors_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance
            }

            return stats

        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return {}


def main():
    """Основная функция CLI"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Семантический поиск BSL кода в Qdrant"
    )
    parser.add_argument(
        "query",
        help="Поисковый запрос"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Количество результатов (default: 5)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.0,
        help="Минимальный порог релевантности 0-1 (default: 0.0)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Показать статистику коллекции"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("🔍 Семантический поиск BSL кода через Qdrant")
    print("=" * 80)

    # Создание сервиса поиска
    search_service = QdrantSearch()

    # Статистика коллекции
    if args.stats:
        print("\n📊 Статистика коллекции:")
        stats = search_service.get_collection_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        print()

    # Поиск
    print(f"\nЗапрос: \"{args.query}\"")
    print(f"Топ: {args.top}")
    print(f"Порог: {args.threshold}")

    results = search_service.search(
        query=args.query,
        top_k=args.top,
        score_threshold=args.threshold
    )

    # Вывод результатов
    search_service.print_results(results)


if __name__ == "__main__":
    main()
