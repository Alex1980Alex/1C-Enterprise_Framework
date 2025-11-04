"""
Enhanced Semantic Search для BSL кода
Версия: 2.0 с расширенными возможностями

Возможности:
- Semantic search через Qdrant
- Гибридный поиск (vector + metadata filters)
- Ranking и scoring
- Highlighted результаты
- Export в различные форматы
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

# Добавление путей для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.embedding_service import EmbeddingService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Результат поиска"""
    file_path: str
    module_type: str
    score: float
    functions_count: int
    variables_count: int
    preview: str
    file_size: int
    indexed_at: str

    @property
    def relevance_label(self) -> str:
        """Метка релевантности"""
        if self.score >= 0.8:
            return "Отлично"
        elif self.score >= 0.6:
            return "Хорошо"
        elif self.score >= 0.4:
            return "Средне"
        else:
            return "Слабо"


class SemanticSearchEngine:
    """
    Расширенный поисковый движок для BSL кода
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "bsl_code",
        embedding_model: str = "nomic-embed-text:latest"
    ):
        """
        Инициализация поискового движка

        Args:
            qdrant_url: URL Qdrant сервера
            collection_name: Имя коллекции
            embedding_model: Модель для embeddings
        """
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.embedding_service = EmbeddingService(model=embedding_model)

        logger.info(f"SemanticSearchEngine инициализирован")
        logger.info(f"  Qdrant: {qdrant_url}")
        logger.info(f"  Collection: {collection_name}")
        logger.info(f"  Model: {embedding_model}")

    def search(
        self,
        query: str,
        limit: int = 10,
        min_score: float = 0.3,
        module_type: Optional[str] = None,
        min_functions: Optional[int] = None
    ) -> List[SearchResult]:
        """
        Семантический поиск с фильтрами

        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов
            min_score: Минимальный score релевантности
            module_type: Фильтр по типу модуля
            min_functions: Минимальное количество функций

        Returns:
            Список результатов поиска
        """
        logger.info(f"🔍 Поиск: '{query}'")

        # Создание embedding для запроса
        query_vector = self.embedding_service.create_embedding(query)
        if not query_vector:
            logger.error("❌ Не удалось создать embedding для запроса")
            return []

        # Построение фильтров
        search_filter = None
        filter_conditions = []

        if module_type:
            filter_conditions.append(
                FieldCondition(
                    key="module_type",
                    match=MatchValue(value=module_type)
                )
            )

        if min_functions is not None:
            filter_conditions.append(
                FieldCondition(
                    key="functions_count",
                    range={
                        "gte": min_functions
                    }
                )
            )

        if filter_conditions:
            search_filter = Filter(must=filter_conditions)

        # Выполнение поиска
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit * 2,  # Берем больше для фильтрации по score
                query_filter=search_filter
            )

            # Фильтрация по минимальному score
            filtered_results = [
                r for r in results
                if r.score >= min_score
            ][:limit]

            # Конвертация в SearchResult
            search_results = []
            for result in filtered_results:
                payload = result.payload

                search_result = SearchResult(
                    file_path=payload['file_path'],
                    module_type=payload['module_type'],
                    score=result.score,
                    functions_count=payload['functions_count'],
                    variables_count=payload['variables_count'],
                    preview=payload['searchable_text'][:300],
                    file_size=payload['file_size'],
                    indexed_at=payload['indexed_at']
                )
                search_results.append(search_result)

            logger.info(f"✅ Найдено результатов: {len(search_results)}")
            return search_results

        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}")
            return []

    def search_similar_code(
        self,
        code_snippet: str,
        limit: int = 5
    ) -> List[SearchResult]:
        """
        Поиск похожего кода

        Args:
            code_snippet: Фрагмент кода для поиска
            limit: Количество результатов

        Returns:
            Список похожих файлов
        """
        logger.info(f"🔍 Поиск похожего кода (длина: {len(code_snippet)} символов)")

        return self.search(
            query=code_snippet,
            limit=limit,
            min_score=0.5  # Более высокий порог для code similarity
        )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики коллекции

        Returns:
            Словарь со статистикой
        """
        try:
            collection_info = self.client.get_collection(
                collection_name=self.collection_name
            )

            stats = {
                "collection_name": self.collection_name,
                "total_points": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": str(collection_info.config.params.vectors.distance),
                "status": "OK"
            }

            return stats

        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            return {}

    def export_results(
        self,
        results: List[SearchResult],
        format: str = "json",
        output_file: Optional[str] = None
    ) -> str:
        """
        Экспорт результатов поиска

        Args:
            results: Результаты поиска
            format: Формат экспорта (json, csv, markdown)
            output_file: Путь для сохранения файла

        Returns:
            Экспортированные данные в виде строки
        """
        if format == "json":
            data = json.dumps(
                [asdict(r) for r in results],
                ensure_ascii=False,
                indent=2
            )

        elif format == "csv":
            import csv
            from io import StringIO

            output = StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=['file_path', 'module_type', 'score', 'relevance_label', 'functions_count']
            )
            writer.writeheader()

            for r in results:
                writer.writerow({
                    'file_path': r.file_path,
                    'module_type': r.module_type,
                    'score': f"{r.score:.3f}",
                    'relevance_label': r.relevance_label,
                    'functions_count': r.functions_count
                })

            data = output.getvalue()

        elif format == "markdown":
            lines = ["# Результаты поиска\n"]

            for i, r in enumerate(results, 1):
                lines.append(f"## {i}. {Path(r.file_path).name}")
                lines.append(f"**Релевантность**: {r.score:.3f} ({r.relevance_label})")
                lines.append(f"**Тип**: {r.module_type}")
                lines.append(f"**Функций**: {r.functions_count}")
                lines.append(f"**Путь**: `{r.file_path}`")
                lines.append(f"\n**Превью**:\n```bsl\n{r.preview}\n```\n")

            data = "\n".join(lines)

        else:
            raise ValueError(f"Неподдерживаемый формат: {format}")

        # Сохранение в файл
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(data)
            logger.info(f"💾 Результаты экспортированы: {output_file}")

        return data

    def print_results(self, results: List[SearchResult], detailed: bool = False):
        """
        Красивый вывод результатов в консоль

        Args:
            results: Результаты поиска
            detailed: Показать детальную информацию
        """
        if not results:
            print("\n❌ Результатов не найдено")
            return

        print(f"\n{'='*80}")
        print(f"🔍 РЕЗУЛЬТАТЫ ПОИСКА ({len(results)} найдено)")
        print(f"{'='*80}\n")

        for i, result in enumerate(results, 1):
            score_bar = self._create_score_bar(result.score)

            print(f"{i}. {Path(result.file_path).name}")
            print(f"   📊 Релевантность: {score_bar} {result.score:.3f} ({result.relevance_label})")
            print(f"   📁 Тип: {result.module_type}")
            print(f"   🔧 Функций: {result.functions_count} | Переменных: {result.variables_count}")

            if detailed:
                print(f"   📂 Путь: {result.file_path}")
                print(f"   💾 Размер: {result.file_size} bytes")
                print(f"   📅 Индексировано: {result.indexed_at}")
                print(f"\n   📝 Превью:\n   {result.preview[:200]}...\n")
            else:
                print(f"   📝 {result.preview[:100]}...\n")

        print(f"{'='*80}\n")

    @staticmethod
    def _create_score_bar(score: float, length: int = 20) -> str:
        """Создание визуальной шкалы score"""
        filled = int(length * score)
        bar = '█' * filled + '░' * (length - filled)
        return f"[{bar}]"


def main():
    """Главная функция для CLI"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced Semantic Search для BSL кода",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Простой поиск
  python semantic_search_enhanced.py "получить данные из базы"

  # Поиск с фильтрами
  python semantic_search_enhanced.py "обработка документа" --module-type ObjectModule --limit 5

  # Поиск с минимальным количеством функций
  python semantic_search_enhanced.py "работа с запросами" --min-functions 3

  # Экспорт результатов
  python semantic_search_enhanced.py "вычисление" --export json --output results.json

  # Статистика коллекции
  python semantic_search_enhanced.py --stats
        """
    )

    parser.add_argument(
        "query",
        nargs='?',
        help="Поисковый запрос"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Количество результатов (default: 10)"
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.3,
        help="Минимальный score (0.0-1.0, default: 0.3)"
    )
    parser.add_argument(
        "--module-type",
        help="Фильтр по типу модуля"
    )
    parser.add_argument(
        "--min-functions",
        type=int,
        help="Минимальное количество функций"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Показать детальную информацию"
    )
    parser.add_argument(
        "--export",
        choices=['json', 'csv', 'markdown'],
        help="Формат экспорта результатов"
    )
    parser.add_argument(
        "--output",
        help="Файл для сохранения результатов"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Показать статистику коллекции"
    )
    parser.add_argument(
        "--qdrant-url",
        default="http://localhost:6333",
        help="URL Qdrant сервера"
    )
    parser.add_argument(
        "--collection",
        default="bsl_code",
        help="Имя коллекции"
    )

    args = parser.parse_args()

    # Создание поискового движка
    engine = SemanticSearchEngine(
        qdrant_url=args.qdrant_url,
        collection_name=args.collection
    )

    # Статистика коллекции
    if args.stats:
        stats = engine.get_statistics()
        print(f"\n{'='*60}")
        print(f"📊 СТАТИСТИКА КОЛЛЕКЦИИ")
        print(f"{'='*60}")
        print(f"Название:      {stats.get('collection_name', 'N/A')}")
        print(f"Точек:         {stats.get('total_points', 0):,}")
        print(f"Размер векторов: {stats.get('vector_size', 0)}")
        print(f"Метрика:       {stats.get('distance_metric', 'N/A')}")
        print(f"Статус:        {stats.get('status', 'N/A')}")
        print(f"{'='*60}\n")
        return

    # Проверка наличия запроса
    if not args.query:
        parser.print_help()
        return

    # Выполнение поиска
    results = engine.search(
        query=args.query,
        limit=args.limit,
        min_score=args.min_score,
        module_type=args.module_type,
        min_functions=args.min_functions
    )

    # Вывод результатов
    engine.print_results(results, detailed=args.detailed)

    # Экспорт результатов
    if args.export and results:
        output_file = args.output or f"search_results.{args.export}"
        engine.export_results(results, format=args.export, output_file=output_file)


if __name__ == "__main__":
    main()
