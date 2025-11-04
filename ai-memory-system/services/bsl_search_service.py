"""
BSL Search Service - Единый интерфейс поиска

Объединяет все поисковые движки системы:
1. Semantic Search (Qdrant) - векторный поиск по эмбеддингам
2. Graph Search (Neo4j) - поиск по графу зависимостей
3. Hybrid Search - комбинированный подход
4. LLM Re-ranking - финальное ранжирование через LLM

Архитектура:
- Параллельное выполнение нескольких типов поиска
- Умное объединение результатов
- LLM-based precision ranking для финального результата
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SearchMode(Enum):
    """Режимы поиска"""
    SEMANTIC_ONLY = "semantic"  # Только векторный поиск
    GRAPH_ONLY = "graph"  # Только поиск по графу
    HYBRID = "hybrid"  # Гибридный подход
    INTELLIGENT = "intelligent"  # Умный поиск с LLM re-ranking
    MULTI_STAGE = "multi_stage"  # Многостадийный поиск


@dataclass
class SearchResult:
    """Результат поиска"""
    file_path: str
    module_type: str
    score: float
    original_score: float
    summary: str
    functions_count: int
    variables_count: int = 0
    source: str = "unknown"  # Источник результата (semantic, graph, hybrid)
    reranked: bool = False  # Был ли применен LLM re-ranking
    reasoning: str = ""  # Объяснение от LLM (если reranked=True)
    metadata: Dict[str, Any] = None


@dataclass
class SearchRequest:
    """Запрос на поиск"""
    query: str
    mode: SearchMode = SearchMode.INTELLIGENT
    limit: int = 10

    # Фильтры
    module_types: Optional[List[str]] = None
    file_path_pattern: Optional[str] = None
    min_score: float = 0.0

    # Опции
    include_functions: bool = False
    use_llm_reranking: bool = True
    combine_sources: bool = True  # Объединять результаты из разных источников


class BSLSearchService:
    """
    Единый сервис поиска для BSL кода

    Объединяет все поисковые движки и предоставляет
    унифицированный интерфейс для поиска по кодовой базе.
    """

    def __init__(
        self,
        qdrant_service,  # QdrantVectorStore
        neo4j_service,   # Neo4jService или GraphAnalyzer
        hybrid_engine,    # HybridSearchEngine
        llm_service      # LLMService
    ):
        """
        Инициализация BSL Search Service

        Args:
            qdrant_service: Сервис векторного поиска
            neo4j_service: Сервис графового поиска
            hybrid_engine: Гибридный поисковый движок
            llm_service: Сервис для LLM re-ranking
        """
        self.qdrant = qdrant_service
        self.neo4j = neo4j_service
        self.hybrid = hybrid_engine
        self.llm = llm_service

        logger.info("BSLSearchService инициализирован")
        logger.info(f"  Qdrant: {'✓' if qdrant_service else '✗'}")
        logger.info(f"  Neo4j: {'✓' if neo4j_service else '✗'}")
        logger.info(f"  Hybrid: {'✓' if hybrid_engine else '✗'}")
        logger.info(f"  LLM: {'✓' if llm_service else '✗'}")

    async def search(self, request: SearchRequest) -> List[SearchResult]:
        """
        Выполнить поиск согласно запросу

        Args:
            request: Параметры поискового запроса

        Returns:
            Список результатов поиска, отсортированных по релевантности
        """
        logger.info(f"Начат поиск: query='{request.query}', mode={request.mode.value}")

        # Выбор стратегии поиска
        if request.mode == SearchMode.SEMANTIC_ONLY:
            results = await self._semantic_search(request)

        elif request.mode == SearchMode.GRAPH_ONLY:
            results = await self._graph_search(request)

        elif request.mode == SearchMode.HYBRID:
            results = await self._hybrid_search(request)

        elif request.mode == SearchMode.INTELLIGENT:
            results = await self._intelligent_search(request)

        elif request.mode == SearchMode.MULTI_STAGE:
            results = await self._multi_stage_search(request)

        else:
            logger.warning(f"Неизвестный режим поиска: {request.mode}")
            results = await self._semantic_search(request)

        logger.info(f"Поиск завершен: найдено {len(results)} результатов")
        return results[:request.limit]

    async def _semantic_search(self, request: SearchRequest) -> List[SearchResult]:
        """Векторный поиск через Qdrant"""
        logger.debug("Выполняется semantic search")

        if not self.qdrant:
            logger.warning("Qdrant недоступен")
            return []

        try:
            # Вызов Qdrant search
            raw_results = await self._call_qdrant_search(
                query=request.query,
                limit=request.limit * 2,  # Берем больше для фильтрации
                filters=self._build_qdrant_filters(request)
            )

            # Конвертация в SearchResult
            results = []
            for r in raw_results:
                results.append(SearchResult(
                    file_path=r.get("file_path", ""),
                    module_type=r.get("module_type", "Unknown"),
                    score=r.get("score", 0.0),
                    original_score=r.get("score", 0.0),
                    summary=r.get("summary", ""),
                    functions_count=r.get("functions_count", 0),
                    variables_count=r.get("variables_count", 0),
                    source="semantic",
                    metadata=r
                ))

            return results

        except Exception as e:
            logger.error(f"Ошибка semantic search: {e}")
            return []

    async def _graph_search(self, request: SearchRequest) -> List[SearchResult]:
        """Поиск по графу зависимостей через Neo4j"""
        logger.debug("Выполняется graph search")

        if not self.neo4j:
            logger.warning("Neo4j недоступен")
            return []

        try:
            # Поиск в Neo4j по тексту запроса
            # (Предполагается что есть полнотекстовый индекс)
            raw_results = await self._call_neo4j_search(
                query=request.query,
                limit=request.limit * 2
            )

            results = []
            for r in raw_results:
                results.append(SearchResult(
                    file_path=r.get("file_path", ""),
                    module_type=r.get("type", "Unknown"),
                    score=r.get("relevance", 0.5),
                    original_score=r.get("relevance", 0.5),
                    summary=r.get("description", ""),
                    functions_count=r.get("functions_count", 0),
                    source="graph",
                    metadata=r
                ))

            return results

        except Exception as e:
            logger.error(f"Ошибка graph search: {e}")
            return []

    async def _hybrid_search(self, request: SearchRequest) -> List[SearchResult]:
        """Гибридный поиск через HybridSearchEngine"""
        logger.debug("Выполняется hybrid search")

        if not self.hybrid:
            logger.warning("Hybrid engine недоступен")
            # Fallback: semantic + graph вручную
            return await self._manual_hybrid_search(request)

        try:
            raw_results = await self._call_hybrid_search(
                query=request.query,
                limit=request.limit * 2
            )

            results = []
            for r in raw_results:
                results.append(SearchResult(
                    file_path=r.get("file_path", ""),
                    module_type=r.get("module_type", "Unknown"),
                    score=r.get("combined_score", 0.0),
                    original_score=r.get("combined_score", 0.0),
                    summary=r.get("summary", ""),
                    functions_count=r.get("functions_count", 0),
                    source="hybrid",
                    metadata=r
                ))

            return results

        except Exception as e:
            logger.error(f"Ошибка hybrid search: {e}")
            return []

    async def _intelligent_search(self, request: SearchRequest) -> List[SearchResult]:
        """
        Умный поиск с LLM re-ranking

        Шаги:
        1. Классификация намерения запроса (LLM)
        2. Выбор оптимальной стратегии поиска
        3. Выполнение поиска
        4. LLM re-ranking результатов
        """
        logger.debug("Выполняется intelligent search с LLM")

        # Шаг 1: Классификация намерения
        intent = None
        if self.llm and request.use_llm_reranking:
            try:
                intent_result = self.llm.classify_intent(request.query)
                intent = intent_result.intent
                logger.info(f"Intent: {intent.value}, confidence: {intent_result.confidence:.2f}")
            except Exception as e:
                logger.warning(f"Ошибка классификации намерения: {e}")

        # Шаг 2: Выбор стратегии на основе intent
        # (Можно адаптировать параметры поиска)

        # Шаг 3: Hybrid search как базовая стратегия
        results = await self._hybrid_search(request)

        if not results:
            logger.warning("Hybrid search не вернул результатов, пробуем semantic")
            results = await self._semantic_search(request)

        # Шаг 4: LLM Re-ranking
        if self.llm and request.use_llm_reranking and results:
            try:
                logger.debug(f"Применяется LLM re-ranking к {len(results)} результатам")

                # Подготовка данных для re-ranking
                results_for_llm = [
                    {
                        "file_path": r.file_path,
                        "module_type": r.module_type,
                        "summary": r.summary,
                        "functions_count": r.functions_count,
                        "score": r.score
                    }
                    for r in results
                ]

                # LLM re-ranking
                reranked = self.llm.rerank_results(
                    query=request.query,
                    results=results_for_llm,
                    top_k=request.limit
                )

                # Применение новых scores
                reranked_results = []
                for rr in reranked:
                    original_result = results[rr.original_index]
                    original_result.score = rr.new_score
                    original_result.reranked = True
                    original_result.reasoning = rr.reasoning
                    reranked_results.append(original_result)

                logger.info(f"LLM re-ranking выполнен: {len(reranked_results)} результатов")
                return reranked_results

            except Exception as e:
                logger.error(f"Ошибка LLM re-ranking: {e}")
                # Возвращаем оригинальные результаты

        return results

    async def _multi_stage_search(self, request: SearchRequest) -> List[SearchResult]:
        """
        Многостадийный поиск

        Стадия 1: Быстрый широкий поиск (semantic)
        Стадия 2: Уточнение через граф (graph enrichment)
        Стадия 3: Финальный hybrid search на топ результатах
        Стадия 4: LLM re-ranking
        """
        logger.debug("Выполняется multi-stage search")

        # Стадия 1: Широкий semantic search
        semantic_results = await self._semantic_search(
            SearchRequest(
                query=request.query,
                limit=request.limit * 5  # Широкая выборка
            )
        )

        if not semantic_results:
            return []

        # Стадия 2: Enrichment через граф
        # (Добавление информации о зависимостях из Neo4j)
        enriched_results = await self._enrich_with_graph(semantic_results)

        # Стадия 3: Hybrid scoring на обогащенных результатах
        # (Пересчет scores с учетом графовых метрик)
        hybrid_scored = await self._apply_hybrid_scoring(enriched_results)

        # Стадия 4: LLM re-ranking финального набора
        if self.llm and request.use_llm_reranking:
            top_candidates = hybrid_scored[:request.limit * 2]

            try:
                results_for_llm = [
                    {
                        "file_path": r.file_path,
                        "module_type": r.module_type,
                        "summary": r.summary,
                        "functions_count": r.functions_count,
                        "score": r.score
                    }
                    for r in top_candidates
                ]

                reranked = self.llm.rerank_results(
                    query=request.query,
                    results=results_for_llm,
                    top_k=request.limit
                )

                final_results = []
                for rr in reranked:
                    original_result = top_candidates[rr.original_index]
                    original_result.score = rr.new_score
                    original_result.reranked = True
                    original_result.reasoning = rr.reasoning
                    final_results.append(original_result)

                return final_results

            except Exception as e:
                logger.error(f"Ошибка LLM re-ranking в multi-stage: {e}")
                return hybrid_scored[:request.limit]

        return hybrid_scored[:request.limit]

    async def _manual_hybrid_search(self, request: SearchRequest) -> List[SearchResult]:
        """Ручное объединение semantic + graph поиска"""
        logger.debug("Выполняется ручной hybrid search")

        # Параллельный запуск
        semantic_task = self._semantic_search(request)
        graph_task = self._graph_search(request)

        semantic_results, graph_results = await asyncio.gather(
            semantic_task,
            graph_task,
            return_exceptions=True
        )

        # Обработка исключений
        if isinstance(semantic_results, Exception):
            logger.error(f"Semantic search failed: {semantic_results}")
            semantic_results = []

        if isinstance(graph_results, Exception):
            logger.error(f"Graph search failed: {graph_results}")
            graph_results = []

        # Объединение и дедупликация
        combined = self._merge_results(
            semantic_results,
            graph_results,
            weights={"semantic": 0.6, "graph": 0.4}
        )

        return combined

    def _merge_results(
        self,
        *result_sets,
        weights: Dict[str, float] = None
    ) -> List[SearchResult]:
        """
        Объединение результатов из разных источников

        Args:
            result_sets: Наборы результатов для объединения
            weights: Веса для каждого источника

        Returns:
            Объединенный и отсортированный список
        """
        if not weights:
            weights = {"semantic": 0.5, "graph": 0.5}

        # Дедупликация по file_path
        unique_results = {}

        for results in result_sets:
            if not results:
                continue

            for result in results:
                path = result.file_path

                if path in unique_results:
                    # Комбинируем scores с учетом весов
                    existing = unique_results[path]
                    weight_key = result.source
                    weight = weights.get(weight_key, 0.5)

                    # Weighted average
                    existing.score = (
                        existing.score * (1 - weight) +
                        result.score * weight
                    )

                    # Объединяем источники
                    if result.source not in existing.source:
                        existing.source = f"{existing.source}+{result.source}"
                else:
                    unique_results[path] = result

        # Сортировка по score
        sorted_results = sorted(
            unique_results.values(),
            key=lambda x: x.score,
            reverse=True
        )

        return sorted_results

    async def _enrich_with_graph(self, results: List[SearchResult]) -> List[SearchResult]:
        """Обогащение результатов данными из графа"""
        # TODO: Реализация
        # Добавить метрики из Neo4j (fan-in, fan-out, centrality)
        return results

    async def _apply_hybrid_scoring(self, results: List[SearchResult]) -> List[SearchResult]:
        """Применение гибридного scoring к результатам"""
        # TODO: Реализация
        # Пересчет scores с учетом графовых метрик
        return results

    # Вспомогательные методы для вызова реальных сервисов

    async def _call_qdrant_search(
        self,
        query: str,
        limit: int,
        filters: Any
    ) -> List[Dict]:
        """
        Вызов Qdrant search с генерацией embedding через Ollama

        Args:
            query: Поисковый запрос
            limit: Количество результатов
            filters: Фильтры Qdrant (Filter object)

        Returns:
            Список результатов поиска
        """
        if not self.qdrant:
            logger.warning("Qdrant service недоступен")
            return []

        try:
            # Импорт зависимостей
            from services.embedding_service import EmbeddingService
            from qdrant_client import QdrantClient

            # Инициализация сервисов (если нужно)
            if not hasattr(self, '_embedding_service'):
                self._embedding_service = EmbeddingService(
                    ollama_host="http://localhost:11434",
                    model="nomic-embed-text"
                )

            if not hasattr(self, '_qdrant_client'):
                self._qdrant_client = QdrantClient(
                    host="localhost",
                    port=6333
                )

            # Генерация embedding для запроса
            logger.debug(f"Генерация embedding для запроса: '{query[:50]}...'")
            query_embedding = self._embedding_service.create_embedding(query)

            if not query_embedding:
                logger.error("Не удалось создать embedding для запроса")
                return []

            logger.debug(f"Embedding создан: {len(query_embedding)} размерность")

            # Поиск в Qdrant
            search_params = {
                "collection_name": "bsl_code",
                "query_vector": query_embedding,
                "limit": limit
            }

            if filters:
                search_params["query_filter"] = filters

            logger.debug(f"Поиск в Qdrant: collection=bsl_code, limit={limit}")
            search_results = self._qdrant_client.search(**search_params)

            # Преобразование результатов
            results = []
            for hit in search_results:
                payload = hit.payload or {}
                results.append({
                    "file_path": payload.get("file_path", ""),
                    "module_type": payload.get("module_type", "Unknown"),
                    "score": hit.score,
                    "summary": payload.get("searchable_text", "")[:500],
                    "functions_count": payload.get("functions_count", 0),
                    "variables_count": payload.get("variables_count", 0),
                    "functions": payload.get("functions", []),
                    "procedures": payload.get("procedures", []),
                    "file_size": payload.get("file_size", 0),
                    "indexed_at": payload.get("indexed_at", "")
                })

            logger.info(f"Qdrant search завершен: найдено {len(results)} результатов")
            return results

        except ImportError as e:
            logger.error(f"Ошибка импорта зависимостей: {e}")
            return []
        except Exception as e:
            logger.error(f"Ошибка Qdrant search: {e}", exc_info=True)
            return []

    async def _call_neo4j_search(
        self,
        query: str,
        limit: int
    ) -> List[Dict]:
        """
        Вызов Neo4j search через Cypher запрос

        Args:
            query: Поисковый запрос
            limit: Количество результатов

        Returns:
            Список результатов поиска
        """
        if not self.neo4j:
            logger.warning("Neo4j service недоступен")
            return []

        try:
            # Извлечение ключевых слов из запроса
            keywords = self._extract_keywords_from_query(query)

            if not keywords:
                logger.warning("Не удалось извлечь ключевые слова из запроса")
                return []

            logger.debug(f"Ключевые слова для Neo4j поиска: {keywords}")

            # Cypher запрос для поиска модулей по ключевым словам
            cypher_query = """
            MATCH (m:Module)
            WHERE ANY(keyword IN $keywords WHERE
                toLower(m.name) CONTAINS toLower(keyword) OR
                toLower(m.file_path) CONTAINS toLower(keyword)
            )

            // Получение функций модуля
            OPTIONAL MATCH (m)-[:CONTAINS]->(f)
            WHERE f:Function OR f:Procedure

            // Получение зависимостей
            OPTIONAL MATCH (m)-[:DEPENDS_ON]->(dep:Module)

            WITH m,
                 collect(DISTINCT f.name)[0..10] as functions,
                 count(DISTINCT f) as functions_count,
                 collect(DISTINCT dep.name)[0..5] as dependencies

            RETURN
                m.name as module_name,
                m.file_path as file_path,
                m.type as module_type,
                functions,
                functions_count,
                dependencies
            LIMIT $limit
            """

            # Выполнение запроса
            results = self.neo4j.execute_query(
                cypher_query,
                {"keywords": keywords, "limit": limit}
            )

            # Преобразование результатов
            formatted_results = []
            for r in results:
                # Расчет релевантности на основе совпадений ключевых слов
                relevance = self._calculate_relevance(
                    query=query,
                    module_name=r.get("module_name", ""),
                    file_path=r.get("file_path", "")
                )

                formatted_results.append({
                    "file_path": r.get("file_path", ""),
                    "type": r.get("module_type", "Unknown"),
                    "module_type": r.get("module_type", "Unknown"),
                    "relevance": relevance,
                    "description": f"Модуль {r.get('module_name', 'Unknown')} с {r.get('functions_count', 0)} функциями",
                    "functions_count": r.get("functions_count", 0),
                    "functions": r.get("functions", []),
                    "dependencies": r.get("dependencies", []),
                    "summary": f"Зависимости: {', '.join(r.get('dependencies', [])[:3])}" if r.get('dependencies') else "Нет зависимостей"
                })

            logger.info(f"Neo4j search завершен: найдено {len(formatted_results)} результатов")
            return formatted_results

        except Exception as e:
            logger.error(f"Ошибка Neo4j search: {e}", exc_info=True)
            return []

    async def _call_hybrid_search(
        self,
        query: str,
        limit: int
    ) -> List[Dict]:
        """
        Вызов HybridSearchEngine или ручное объединение semantic + graph

        Args:
            query: Поисковый запрос
            limit: Количество результатов

        Returns:
            Список результатов гибридного поиска
        """
        if self.hybrid:
            # Использование HybridSearchEngine если доступен
            try:
                logger.debug("Использование HybridSearchEngine")

                # Вызов метода intelligent_search гибридного движка
                if hasattr(self.hybrid, 'intelligent_search'):
                    results = await self.hybrid.intelligent_search(
                        query=query,
                        limit=limit
                    )
                    return results
                else:
                    logger.warning("HybridSearchEngine не имеет метода intelligent_search")

            except Exception as e:
                logger.error(f"Ошибка HybridSearchEngine: {e}")

        # Fallback: ручное объединение semantic + graph
        logger.debug("Fallback: ручное объединение semantic + graph")

        try:
            # Параллельный запуск semantic и graph search
            semantic_results_task = self._call_qdrant_search(
                query=query,
                limit=limit * 2,  # Берем больше для лучшего объединения
                filters=None
            )

            graph_results_task = self._call_neo4j_search(
                query=query,
                limit=limit
            )

            # Ожидание завершения обоих поисков
            semantic_results, graph_results = await asyncio.gather(
                semantic_results_task,
                graph_results_task,
                return_exceptions=True
            )

            # Обработка ошибок
            if isinstance(semantic_results, Exception):
                logger.error(f"Semantic search failed: {semantic_results}")
                semantic_results = []

            if isinstance(graph_results, Exception):
                logger.error(f"Graph search failed: {graph_results}")
                graph_results = []

            # Объединение результатов
            combined_results = self._combine_search_results(
                semantic_results=semantic_results,
                graph_results=graph_results,
                semantic_weight=0.6,
                graph_weight=0.4
            )

            logger.info(f"Hybrid search завершен: {len(combined_results)} результатов")
            return combined_results[:limit]

        except Exception as e:
            logger.error(f"Ошибка hybrid search: {e}", exc_info=True)
            return []

    def _build_qdrant_filters(self, request: SearchRequest) -> Any:
        """
        Построение фильтров для Qdrant из параметров SearchRequest

        Args:
            request: Запрос на поиск

        Returns:
            Filter object для Qdrant или None
        """
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny

            conditions = []

            # Фильтр по типам модулей
            if request.module_types and len(request.module_types) > 0:
                if len(request.module_types) == 1:
                    # Одно значение - используем MatchValue
                    conditions.append(
                        FieldCondition(
                            key="module_type",
                            match=MatchValue(value=request.module_types[0])
                        )
                    )
                else:
                    # Несколько значений - используем MatchAny
                    conditions.append(
                        FieldCondition(
                            key="module_type",
                            match=MatchAny(any=request.module_types)
                        )
                    )

            # Фильтр по паттерну пути к файлу (упрощенный - через contains)
            if request.file_path_pattern:
                # Примечание: Qdrant не поддерживает regex напрямую
                # Используем text match для базовой фильтрации
                # Для полноценного regex нужна пост-обработка
                conditions.append(
                    FieldCondition(
                        key="file_path",
                        match=MatchValue(value=request.file_path_pattern)
                    )
                )

            # Если есть условия, создаем Filter
            if conditions:
                filter_obj = Filter(must=conditions)
                logger.debug(f"Построен Qdrant фильтр: {len(conditions)} условий")
                return filter_obj
            else:
                logger.debug("Фильтры не заданы, используется поиск без фильтров")
                return None

        except ImportError as e:
            logger.error(f"Ошибка импорта qdrant_client.models: {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка построения фильтров: {e}")
            return None

    # Дополнительные вспомогательные методы

    def _extract_keywords_from_query(self, query: str) -> List[str]:
        """
        Извлечение ключевых слов из поискового запроса

        Args:
            query: Поисковый запрос

        Returns:
            Список ключевых слов
        """
        # Стоп-слова для русского и английского
        stopwords = {
            # Русские
            "как", "что", "где", "когда", "почему", "кто", "чем", "это", "все",
            "для", "из", "при", "с", "по", "на", "в", "о", "от", "до", "к",
            "и", "или", "не", "но", "а", "также", "еще", "уже", "только",
            "можно", "нужно", "надо", "должен", "может", "есть", "был", "будет",
            # Английские
            "the", "is", "at", "which", "on", "in", "a", "an", "and", "or",
            "but", "for", "with", "from", "to", "of", "by", "as", "this", "that",
            "are", "was", "were", "be", "been", "has", "have", "had", "do", "does"
        }

        # Разбиение на слова и очистка
        words = query.lower().split()

        # Фильтрация стоп-слов и коротких слов
        keywords = [
            w.strip('.,!?;:()[]{}"\'-')
            for w in words
            if len(w) > 2 and w.lower() not in stopwords
        ]

        # Удаление дубликатов с сохранением порядка
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords[:10]  # Максимум 10 ключевых слов

    def _calculate_relevance(
        self,
        query: str,
        module_name: str,
        file_path: str
    ) -> float:
        """
        Расчет релевантности результата Neo4j поиска

        Args:
            query: Исходный запрос
            module_name: Имя модуля
            file_path: Путь к файлу

        Returns:
            Оценка релевантности (0.0-1.0)
        """
        query_lower = query.lower()
        module_lower = module_name.lower()
        path_lower = file_path.lower()

        # Базовая релевантность
        relevance = 0.5

        # Точное совпадение с именем модуля - высокая релевантность
        if query_lower in module_lower:
            relevance = 0.9

        # Частичное совпадение с именем модуля
        keywords = self._extract_keywords_from_query(query)
        matches = sum(1 for kw in keywords if kw in module_lower)
        if matches > 0:
            relevance = min(0.5 + (matches * 0.1), 1.0)

        # Совпадение с путем к файлу
        path_matches = sum(1 for kw in keywords if kw in path_lower)
        if path_matches > 0:
            relevance = min(relevance + (path_matches * 0.05), 1.0)

        return round(relevance, 2)

    def _combine_search_results(
        self,
        semantic_results: List[Dict],
        graph_results: List[Dict],
        semantic_weight: float = 0.6,
        graph_weight: float = 0.4
    ) -> List[Dict]:
        """
        Объединение результатов semantic и graph поиска

        Args:
            semantic_results: Результаты векторного поиска
            graph_results: Результаты графового поиска
            semantic_weight: Вес semantic результатов
            graph_weight: Вес graph результатов

        Returns:
            Объединенный список результатов
        """
        # Индексация результатов по file_path
        combined = {}

        # Добавление semantic результатов
        for result in semantic_results:
            file_path = result.get("file_path", "")
            if not file_path:
                continue

            combined[file_path] = {
                "file_path": file_path,
                "module_type": result.get("module_type", "Unknown"),
                "combined_score": result.get("score", 0.5) * semantic_weight,
                "semantic_score": result.get("score", 0.5),
                "graph_score": 0.0,
                "summary": result.get("summary", ""),
                "functions_count": result.get("functions_count", 0),
                "variables_count": result.get("variables_count", 0),
                "functions": result.get("functions", []),
                "source": "semantic"
            }

        # Добавление graph результатов
        for result in graph_results:
            file_path = result.get("file_path", "")
            if not file_path:
                continue

            graph_score = result.get("relevance", 0.5)

            if file_path in combined:
                # Файл уже есть - обновляем combined_score
                combined[file_path]["combined_score"] += graph_score * graph_weight
                combined[file_path]["graph_score"] = graph_score
                combined[file_path]["source"] = "semantic+graph"

                # Дополняем информацию из графа
                if "dependencies" in result:
                    combined[file_path]["dependencies"] = result["dependencies"]
            else:
                # Новый файл из graph поиска
                combined[file_path] = {
                    "file_path": file_path,
                    "module_type": result.get("module_type", "Unknown"),
                    "combined_score": graph_score * graph_weight,
                    "semantic_score": 0.0,
                    "graph_score": graph_score,
                    "summary": result.get("summary", ""),
                    "functions_count": result.get("functions_count", 0),
                    "functions": result.get("functions", []),
                    "dependencies": result.get("dependencies", []),
                    "source": "graph"
                }

        # Сортировка по combined_score
        sorted_results = sorted(
            combined.values(),
            key=lambda x: x["combined_score"],
            reverse=True
        )

        logger.debug(f"Объединено {len(sorted_results)} уникальных результатов")
        return sorted_results


# Singleton instance
_bsl_search_service: Optional[BSLSearchService] = None


def get_bsl_search_service(
    qdrant_service=None,
    neo4j_service=None,
    hybrid_engine=None,
    llm_service=None
) -> BSLSearchService:
    """
    Получение singleton instance BSLSearchService

    Args:
        qdrant_service: Qdrant vector store
        neo4j_service: Neo4j service
        hybrid_engine: Hybrid search engine
        llm_service: LLM service

    Returns:
        BSLSearchService instance
    """
    global _bsl_search_service

    if _bsl_search_service is None:
        _bsl_search_service = BSLSearchService(
            qdrant_service=qdrant_service,
            neo4j_service=neo4j_service,
            hybrid_engine=hybrid_engine,
            llm_service=llm_service
        )

    return _bsl_search_service
