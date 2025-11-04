"""
Hybrid Search Engine
Объединяет Semantic Search (Qdrant) и Graph Search (Neo4j)
для комплексного поиска по BSL коду
"""

import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

# Добавление путей
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.search.semantic_search_enhanced import SemanticSearchEngine
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class HybridSearchResult:
    """Результат гибридного поиска"""
    # Основная информация
    file_path: str
    module_name: str
    module_type: str

    # Semantic search scores
    semantic_score: float
    relevance_label: str

    # Graph metrics
    functions_count: int
    procedures_count: int
    incoming_calls: int  # Сколько раз функции этого модуля вызываются
    outgoing_calls: int  # Сколько вызовов делают функции этого модуля

    # Graph relationships
    called_by: List[str]  # Функции, вызывающие функции этого модуля
    calls_to: List[str]   # Функции, которые вызывают функции этого модуля
    related_modules: List[str]  # Связанные модули

    # Combined score
    hybrid_score: float

    # Preview
    preview: str
    indexed_at: str


class HybridSearchEngine:
    """
    Гибридный поисковый движок

    Использует:
    - Semantic Search (Qdrant) для поиска по смыслу
    - Graph Search (Neo4j) для анализа зависимостей
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        qdrant_collection: str = "bsl_code",
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password123"
    ):
        """
        Инициализация гибридного поиска

        Args:
            qdrant_url: URL Qdrant сервера
            qdrant_collection: Имя коллекции в Qdrant
            neo4j_uri: URI Neo4j
            neo4j_user: Пользователь Neo4j
            neo4j_password: Пароль Neo4j
        """
        # Semantic search engine
        self.semantic_engine = SemanticSearchEngine(
            qdrant_url=qdrant_url,
            collection_name=qdrant_collection
        )

        # Neo4j graph connection
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )

        logger.info("✅ HybridSearchEngine инициализирован")
        logger.info(f"   Qdrant: {qdrant_url}")
        logger.info(f"   Neo4j: {neo4j_uri}")

    def close(self):
        """Закрытие подключений"""
        if self.neo4j_driver:
            self.neo4j_driver.close()
            logger.info("🔌 Neo4j подключение закрыто")

    def _get_graph_metrics(self, file_path: str) -> Dict:
        """
        Получение метрик из графа для файла

        Args:
            file_path: Путь к файлу

        Returns:
            Словарь с метриками
        """
        with self.neo4j_driver.session() as session:
            # Нормализация пути (удаление начального слэша если есть)
            normalized_path = file_path.lstrip('/')

            # Поиск модуля по пути
            result = session.run("""
                MATCH (m:Module)
                WHERE m.file_path CONTAINS $file_path_part
                OPTIONAL MATCH (m)-[:CONTAINS]->(f)
                WHERE f:Function OR f:Procedure
                OPTIONAL MATCH (f)<-[incoming:CALLS]-()
                OPTIONAL MATCH (f)-[outgoing:CALLS]->()
                RETURN
                    m.name as module_name,
                    m.module_type as module_type,
                    count(DISTINCT f) as total_functions,
                    count(DISTINCT incoming) as incoming_calls,
                    count(DISTINCT outgoing) as outgoing_calls
            """, file_path_part=normalized_path.replace('\\', '/'))

            record = result.single()

            if not record:
                # Модуль не найден в графе
                return {
                    'module_name': Path(file_path).stem,
                    'module_type': 'Unknown',
                    'functions_count': 0,
                    'incoming_calls': 0,
                    'outgoing_calls': 0,
                    'called_by': [],
                    'calls_to': [],
                    'related_modules': []
                }

            # Получение функций, вызывающих этот модуль
            called_by = session.run("""
                MATCH (m:Module)
                WHERE m.file_path CONTAINS $file_path_part
                MATCH (m)-[:CONTAINS]->(target)
                WHERE target:Function OR target:Procedure
                MATCH (source)-[c:CALLS]->(target)
                WHERE source:Function OR source:Procedure
                RETURN DISTINCT source.name as caller_name
                LIMIT 10
            """, file_path_part=normalized_path.replace('\\', '/')).values()

            # Получение функций, которые вызывает этот модуль
            calls_to = session.run("""
                MATCH (m:Module)
                WHERE m.file_path CONTAINS $file_path_part
                MATCH (m)-[:CONTAINS]->(source)
                WHERE source:Function OR source:Procedure
                MATCH (source)-[c:CALLS]->(target)
                WHERE target:Function OR target:Procedure
                RETURN DISTINCT target.name as target_name
                LIMIT 10
            """, file_path_part=normalized_path.replace('\\', '/')).values()

            # Связанные модули (через вызовы)
            related_modules = session.run("""
                MATCH (m1:Module)
                WHERE m1.file_path CONTAINS $file_path_part
                MATCH (m1)-[:CONTAINS]->(f1)
                WHERE f1:Function OR f1:Procedure
                MATCH (f1)-[:CALLS]-(f2)
                WHERE f2:Function OR f2:Procedure
                MATCH (m2:Module)-[:CONTAINS]->(f2)
                WHERE m2 <> m1
                RETURN DISTINCT m2.name as related_module
                LIMIT 5
            """, file_path_part=normalized_path.replace('\\', '/')).values()

            return {
                'module_name': record['module_name'] or Path(file_path).stem,
                'module_type': record['module_type'] or 'Unknown',
                'functions_count': record['total_functions'] or 0,
                'incoming_calls': record['incoming_calls'] or 0,
                'outgoing_calls': record['outgoing_calls'] or 0,
                'called_by': [r[0] for r in called_by if r[0]],
                'calls_to': [r[0] for r in calls_to if r[0]],
                'related_modules': [r[0] for r in related_modules if r[0]]
            }

    def _calculate_hybrid_score(
        self,
        semantic_score: float,
        graph_metrics: Dict,
        weights: Dict = None
    ) -> float:
        """
        Вычисление комбинированного score

        Args:
            semantic_score: Score из semantic search (0-1)
            graph_metrics: Метрики из графа
            weights: Веса для различных факторов

        Returns:
            Гибридный score (0-1)
        """
        if weights is None:
            weights = {
                'semantic': 0.6,      # Базовая релевантность
                'incoming_calls': 0.2,  # Популярность (вызовы)
                'outgoing_calls': 0.1,  # Активность (делает вызовы)
                'connections': 0.1      # Связность (связанные модули)
            }

        # Нормализация graph метрик (0-1)
        incoming_norm = min(graph_metrics['incoming_calls'] / 10.0, 1.0)
        outgoing_norm = min(graph_metrics['outgoing_calls'] / 10.0, 1.0)
        connections_norm = min(len(graph_metrics['related_modules']) / 5.0, 1.0)

        # Взвешенная сумма
        hybrid_score = (
            weights['semantic'] * semantic_score +
            weights['incoming_calls'] * incoming_norm +
            weights['outgoing_calls'] * outgoing_norm +
            weights['connections'] * connections_norm
        )

        return hybrid_score

    def search(
        self,
        query: str,
        limit: int = 10,
        min_semantic_score: float = 0.3,
        include_graph_context: bool = True,
        score_weights: Dict = None
    ) -> List[HybridSearchResult]:
        """
        Гибридный поиск

        Args:
            query: Поисковый запрос
            limit: Количество результатов
            min_semantic_score: Минимальный semantic score
            include_graph_context: Включить graph контекст
            score_weights: Веса для гибридного score

        Returns:
            Список результатов поиска
        """
        logger.info(f"🔍 Гибридный поиск: '{query}'")

        # 1. Semantic search через Qdrant
        semantic_results = self.semantic_engine.search(
            query=query,
            limit=limit * 2,  # Берем больше для фильтрации
            min_score=min_semantic_score
        )

        logger.info(f"   📊 Semantic results: {len(semantic_results)}")

        # 2. Обогащение результатов graph метриками
        hybrid_results = []

        for sem_result in semantic_results:
            # Получение graph метрик
            if include_graph_context:
                graph_metrics = self._get_graph_metrics(sem_result.file_path)
            else:
                graph_metrics = {
                    'module_name': Path(sem_result.file_path).stem,
                    'module_type': sem_result.module_type,
                    'functions_count': sem_result.functions_count,
                    'incoming_calls': 0,
                    'outgoing_calls': 0,
                    'called_by': [],
                    'calls_to': [],
                    'related_modules': []
                }

            # Вычисление гибридного score
            hybrid_score = self._calculate_hybrid_score(
                semantic_score=sem_result.score,
                graph_metrics=graph_metrics,
                weights=score_weights
            )

            # Создание результата
            hybrid_result = HybridSearchResult(
                file_path=sem_result.file_path,
                module_name=graph_metrics['module_name'],
                module_type=graph_metrics['module_type'],
                semantic_score=sem_result.score,
                relevance_label=sem_result.relevance_label,
                functions_count=graph_metrics['functions_count'],
                procedures_count=0,  # TODO: добавить из graph_metrics
                incoming_calls=graph_metrics['incoming_calls'],
                outgoing_calls=graph_metrics['outgoing_calls'],
                called_by=graph_metrics['called_by'],
                calls_to=graph_metrics['calls_to'],
                related_modules=graph_metrics['related_modules'],
                hybrid_score=hybrid_score,
                preview=sem_result.preview,
                indexed_at=sem_result.indexed_at
            )

            hybrid_results.append(hybrid_result)

        # 3. Сортировка по гибридному score
        hybrid_results.sort(key=lambda x: x.hybrid_score, reverse=True)

        # 4. Ограничение результатов
        final_results = hybrid_results[:limit]

        logger.info(f"   ✅ Hybrid results: {len(final_results)}")

        return final_results

    def find_related_by_graph(
        self,
        file_path: str,
        depth: int = 2,
        limit: int = 10
    ) -> List[str]:
        """
        Поиск связанных модулей через граф

        Args:
            file_path: Путь к файлу
            depth: Глубина поиска в графе
            limit: Максимальное количество результатов

        Returns:
            Список путей к связанным файлам
        """
        with self.neo4j_driver.session() as session:
            normalized_path = file_path.lstrip('/').replace('\\', '/')

            result = session.run("""
                MATCH (m1:Module)
                WHERE m1.file_path CONTAINS $file_path_part
                MATCH (m1)-[:CONTAINS]->(f1)
                WHERE f1:Function OR f1:Procedure
                MATCH path = (f1)-[:CALLS*1..$depth]-(f2)
                WHERE f2:Function OR f2:Procedure
                MATCH (m2:Module)-[:CONTAINS]->(f2)
                WHERE m2 <> m1
                RETURN DISTINCT m2.file_path as related_path
                LIMIT $limit
            """,
                file_path_part=normalized_path,
                depth=depth,
                limit=limit
            )

            return [record['related_path'] for record in result]

    def get_statistics(self) -> Dict:
        """
        Получение статистики гибридной системы

        Returns:
            Словарь со статистикой
        """
        # Статистика Qdrant
        qdrant_stats = self.semantic_engine.get_statistics()

        # Статистика Neo4j
        with self.neo4j_driver.session() as session:
            neo4j_stats = {}

            # Количество узлов
            result = session.run("MATCH (m:Module) RETURN count(m) as count")
            neo4j_stats['modules'] = result.single()['count']

            result = session.run("MATCH (f:Function) RETURN count(f) as count")
            neo4j_stats['functions'] = result.single()['count']

            result = session.run("MATCH (p:Procedure) RETURN count(p) as count")
            neo4j_stats['procedures'] = result.single()['count']

            # Количество связей
            result = session.run("MATCH ()-[r:CALLS]->() RETURN count(r) as count")
            neo4j_stats['function_calls'] = result.single()['count']

        return {
            'qdrant': qdrant_stats,
            'neo4j': neo4j_stats,
            'hybrid': {
                'total_modules': max(
                    qdrant_stats.get('total_points', 0),
                    neo4j_stats.get('modules', 0)
                ),
                'graph_coverage': neo4j_stats.get('modules', 0) / max(qdrant_stats.get('total_points', 1), 1)
            }
        }


# Пример использования
if __name__ == "__main__":
    logger.info("🚀 Testing Hybrid Search Engine...")

    # Создание движка
    engine = HybridSearchEngine()

    try:
        # Тест 1: Гибридный поиск
        logger.info("\n📌 Test 1: Hybrid Search")
        results = engine.search(
            query="получить данные из базы",
            limit=5,
            include_graph_context=True
        )

        logger.info(f"\nРезультаты поиска ({len(results)}):")
        for i, result in enumerate(results, 1):
            logger.info(f"\n{i}. {result.module_name}")
            logger.info(f"   Path: {result.file_path}")
            logger.info(f"   Semantic Score: {result.semantic_score:.3f}")
            logger.info(f"   Hybrid Score: {result.hybrid_score:.3f}")
            logger.info(f"   Incoming Calls: {result.incoming_calls}")
            logger.info(f"   Outgoing Calls: {result.outgoing_calls}")
            if result.related_modules:
                logger.info(f"   Related: {', '.join(result.related_modules[:3])}")

        # Тест 2: Статистика
        logger.info("\n📌 Test 2: Statistics")
        stats = engine.get_statistics()
        logger.info(f"\nQdrant: {stats['qdrant'].get('total_points', 0)} documents")
        logger.info(f"Neo4j: {stats['neo4j']['modules']} modules, {stats['neo4j']['functions']} functions")
        logger.info(f"Graph Coverage: {stats['hybrid']['graph_coverage']*100:.1f}%")

        logger.info("\n✅ Tests completed!")

    finally:
        engine.close()
