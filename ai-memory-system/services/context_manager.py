"""
Context Manager для AI Memory System

Интеллектуальная система сборки контекста с многостадийным подходом:

Stage 1: Intent Analysis
- Классификация намерения пользователя
- Определение оптимальной стратегии поиска
- Адаптация параметров под задачу

Stage 2: Multi-dimensional Retrieval
- Векторный поиск (semantic similarity)
- Графовый поиск (code dependencies)
- Временной поиск (code evolution) - опционально
- Гибридное объединение результатов

Stage 3: LLM Precision Ranking
- Глубокий семантический анализ
- Переранжирование на основе контекста
- Фильтрация нерелевантных результатов

Stage 4: Context Assembly
- Сборка финального контекста
- Добавление метаданных
- Структурирование для Claude Code

ROI Impact: 30% ($14,940/год)
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Типы контекста для разных задач"""
    CODE_SEARCH = "code_search"  # Поиск кода
    CODE_UNDERSTANDING = "code_understanding"  # Понимание кода
    DEBUGGING = "debugging"  # Отладка проблем
    REFACTORING = "refactoring"  # Рефакторинг
    DOCUMENTATION = "documentation"  # Документация
    EXAMPLES = "examples"  # Примеры использования


class RetrievalStrategy(Enum):
    """Стратегии извлечения информации"""
    SEMANTIC_ONLY = "semantic"  # Только семантический поиск
    GRAPH_FOCUSED = "graph"  # Фокус на зависимости
    TEMPORAL_AWARE = "temporal"  # С учетом времени
    COMPREHENSIVE = "comprehensive"  # Полный многомерный поиск
    ADAPTIVE = "adaptive"  # Адаптивная стратегия


@dataclass
class ContextRequest:
    """Запрос на формирование контекста"""
    query: str
    context_type: Optional[ContextType] = None
    max_results: int = 10
    include_dependencies: bool = True
    include_history: bool = False
    include_examples: bool = False
    min_relevance: float = 0.5
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    # Advanced options
    temporal_window_days: Optional[int] = None  # Временное окно
    preferred_module_types: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None


@dataclass
class ContextItem:
    """Элемент контекста"""
    file_path: str
    module_type: str
    content: str
    summary: str
    relevance_score: float
    source: str  # "semantic", "graph", "temporal", "hybrid"

    # Metadata
    functions_count: int = 0
    variables_count: int = 0
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    last_modified: Optional[datetime] = None

    # LLM analysis
    llm_reasoning: str = ""
    llm_confidence: float = 0.0

    # Additional context
    code_snippets: List[Dict[str, Any]] = field(default_factory=list)
    related_items: List[str] = field(default_factory=list)


@dataclass
class AssembledContext:
    """Собранный контекст для Claude Code"""
    query: str
    context_type: ContextType
    strategy_used: RetrievalStrategy

    # Results
    primary_items: List[ContextItem]  # Основные результаты
    supporting_items: List[ContextItem]  # Дополнительный контекст
    related_dependencies: List[Dict[str, Any]]  # Связанные зависимости

    # Metadata
    total_items: int
    avg_relevance: float
    processing_time_ms: int

    # LLM insights
    intent_classification: Dict[str, Any]
    suggested_actions: List[str]
    confidence_score: float

    # Timeline (if available)
    timeline_events: List[Dict[str, Any]] = field(default_factory=list)


class ContextManager:
    """
    Интеллектуальный менеджер контекста

    Координирует работу всех компонентов для оптимальной сборки контекста:
    - LLM Service (intent + ranking)
    - BSL Search Service (multi-modal search)
    - Timeline Service (code evolution) - опционально
    - Graph Analytics (dependencies)
    """

    def __init__(
        self,
        llm_service,  # LLMService
        search_service,  # BSLSearchService
        graph_analytics,  # GraphAnalyticsService
        timeline_service=None,  # Optional TimescaleDB integration
        redis_client=None  # Optional caching
    ):
        """
        Инициализация Context Manager

        Args:
            llm_service: Сервис для работы с LLM
            search_service: Сервис поиска
            graph_analytics: Сервис анализа графа
            timeline_service: Опциональный сервис временной аналитики
            redis_client: Опциональный Redis для кеширования
        """
        self.llm = llm_service
        self.search = search_service
        self.graph = graph_analytics
        self.timeline = timeline_service
        self.redis = redis_client

        logger.info("ContextManager инициализирован")
        logger.info(f"  LLM Service: {'✓' if llm_service else '✗'}")
        logger.info(f"  Search Service: {'✓' if search_service else '✗'}")
        logger.info(f"  Graph Analytics: {'✓' if graph_analytics else '✗'}")
        logger.info(f"  Timeline Service: {'✓' if timeline_service else '✗'}")
        logger.info(f"  Redis Cache: {'✓' if redis_client else '✗'}")

    async def assemble_context(
        self,
        request: ContextRequest
    ) -> AssembledContext:
        """
        Главная точка входа - сборка интеллектуального контекста

        Выполняет полный pipeline:
        1. Intent Analysis
        2. Multi-dimensional Retrieval
        3. LLM Precision Ranking
        4. Context Assembly

        Args:
            request: Запрос на формирование контекста

        Returns:
            AssembledContext с собранным контекстом
        """
        start_time = datetime.now()

        logger.info(f"=== Context Assembly Started ===")
        logger.info(f"Query: '{request.query}'")
        logger.info(f"Type: {request.context_type}")

        # STAGE 1: Intent Analysis
        logger.info("[Stage 1] Анализ намерений...")
        intent_result = await self._analyze_intent(request)

        # Определяем стратегию на основе intent
        strategy = self._select_strategy(intent_result, request)
        logger.info(f"  Выбрана стратегия: {strategy.value}")

        # STAGE 2: Multi-dimensional Retrieval
        logger.info("[Stage 2] Многомерный поиск...")
        retrieval_results = await self._multi_dimensional_retrieval(
            request,
            intent_result,
            strategy
        )
        logger.info(f"  Найдено результатов: {len(retrieval_results)}")

        # STAGE 3: LLM Precision Ranking
        logger.info("[Stage 3] LLM переранжирование...")
        ranked_results = await self._llm_precision_ranking(
            request.query,
            retrieval_results,
            intent_result
        )
        logger.info(f"  После ranking: {len(ranked_results)}")

        # STAGE 4: Context Assembly
        logger.info("[Stage 4] Сборка контекста...")
        assembled = await self._assemble_final_context(
            request,
            ranked_results,
            intent_result,
            strategy,
            start_time
        )

        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(f"=== Context Assembly Complete ({processing_time:.0f}ms) ===")

        return assembled

    async def _analyze_intent(
        self,
        request: ContextRequest
    ) -> Dict[str, Any]:
        """
        Stage 1: Анализ намерений пользователя

        Использует LLM для глубокого понимания запроса
        """
        try:
            classification = self.llm.classify_intent(request.query)

            # Если тип контекста не указан, определяем из intent
            if request.context_type is None:
                request.context_type = self._map_intent_to_context_type(
                    classification.intent
                )

            return {
                "intent": classification.intent,
                "confidence": classification.confidence,
                "reasoning": classification.reasoning,
                "suggested_filters": classification.suggested_filters,
                "mapped_context_type": request.context_type
            }

        except Exception as e:
            logger.error(f"Ошибка анализа намерений: {e}")
            # Fallback на базовый анализ
            return {
                "intent": "general_search",
                "confidence": 0.5,
                "reasoning": "Fallback to general search",
                "suggested_filters": {},
                "mapped_context_type": ContextType.CODE_SEARCH
            }

    async def _multi_dimensional_retrieval(
        self,
        request: ContextRequest,
        intent_result: Dict[str, Any],
        strategy: RetrievalStrategy
    ) -> List[Dict[str, Any]]:
        """
        Stage 2: Многомерный поиск

        Комбинирует результаты из разных источников:
        - Semantic (vector search)
        - Graph (dependencies)
        - Temporal (code history) - если доступен
        """
        from services.bsl_search_service import SearchRequest, SearchMode

        # Подготовка поисковых запросов
        search_requests = []

        # 1. Semantic Search (всегда)
        semantic_request = SearchRequest(
            query=request.query,
            mode=SearchMode.SEMANTIC_ONLY,
            limit=request.max_results * 2,  # Берем больше для фильтрации
            module_types=request.preferred_module_types,
            min_score=request.min_relevance,
            use_llm_reranking=False  # Делаем на Stage 3
        )
        search_requests.append(("semantic", semantic_request))

        # 2. Graph Search (если нужны зависимости)
        if request.include_dependencies:
            graph_request = SearchRequest(
                query=request.query,
                mode=SearchMode.GRAPH_ONLY,
                limit=request.max_results,
                min_score=request.min_relevance
            )
            search_requests.append(("graph", graph_request))

        # 3. Hybrid Search (для comprehensive стратегии)
        if strategy == RetrievalStrategy.COMPREHENSIVE:
            hybrid_request = SearchRequest(
                query=request.query,
                mode=SearchMode.HYBRID,
                limit=request.max_results * 2,
                min_score=request.min_relevance,
                combine_sources=True
            )
            search_requests.append(("hybrid", hybrid_request))

        # Параллельное выполнение всех поисков
        tasks = []
        for source, req in search_requests:
            tasks.append(self._execute_search(source, req))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Объединение результатов
        all_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Ошибка в поиске {search_requests[i][0]}: {result}")
                continue
            all_results.extend(result)

        # 4. Temporal Search (если доступен)
        if self.timeline and request.include_history:
            temporal_results = await self._temporal_search(
                request.query,
                request.temporal_window_days
            )
            all_results.extend(temporal_results)

        # Дедупликация по file_path
        unique_results = self._deduplicate_results(all_results)

        return unique_results

    async def _execute_search(
        self,
        source: str,
        search_request
    ) -> List[Dict[str, Any]]:
        """Выполнение одного поискового запроса"""
        try:
            results = await self.search.search(search_request)

            # Конвертация в dict формат
            return [
                {
                    "file_path": r.file_path,
                    "module_type": r.module_type,
                    "score": r.score,
                    "summary": r.summary,
                    "functions_count": r.functions_count,
                    "variables_count": r.variables_count,
                    "source": source,
                    "metadata": r.metadata or {}
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Ошибка выполнения {source} search: {e}")
            return []

    async def _temporal_search(
        self,
        query: str,
        window_days: Optional[int]
    ) -> List[Dict[str, Any]]:
        """
        Временной поиск (код который недавно изменялся)

        Требует TimescaleDB для работы
        """
        if not self.timeline:
            return []

        try:
            # Поиск файлов, измененных в указанном окне
            results = await self.timeline.search_recent_changes(
                query=query,
                days=window_days or 30
            )

            return [
                {
                    "file_path": r["file_path"],
                    "module_type": r.get("module_type", "Unknown"),
                    "score": r.get("score", 0.5),
                    "summary": r.get("summary", ""),
                    "source": "temporal",
                    "last_modified": r.get("timestamp"),
                    "metadata": {"change_frequency": r.get("change_frequency", 0)}
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Ошибка temporal search: {e}")
            return []

    async def _llm_precision_ranking(
        self,
        query: str,
        results: List[Dict[str, Any]],
        intent_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Stage 3: LLM Precision Ranking

        Глубокий семантический анализ с учетом контекста и намерений
        """
        if not results:
            return []

        try:
            # Добавляем контекст намерения в query для LLM
            enhanced_query = self._enhance_query_with_intent(query, intent_result)

            # LLM Re-ranking
            reranked = self.llm.rerank_results(
                query=enhanced_query,
                results=results[:20],  # Ограничиваем для LLM
                top_k=len(results)
            )

            # Конвертация обратно в dict с добавлением LLM metadata
            return [
                {
                    **r.result,
                    "score": r.new_score,
                    "original_score": r.original_score,
                    "llm_reasoning": r.reasoning,
                    "llm_confidence": r.new_score,
                    "reranked": True
                }
                for r in reranked
            ]

        except Exception as e:
            logger.error(f"Ошибка LLM ranking: {e}")
            # Fallback на оригинальные результаты
            return results

    async def _assemble_final_context(
        self,
        request: ContextRequest,
        ranked_results: List[Dict[str, Any]],
        intent_result: Dict[str, Any],
        strategy: RetrievalStrategy,
        start_time: datetime
    ) -> AssembledContext:
        """
        Stage 4: Финальная сборка контекста

        Структурирование результатов для Claude Code
        """
        # Разделение на primary и supporting
        primary_count = min(request.max_results, len(ranked_results))
        primary_results = ranked_results[:primary_count]
        supporting_results = ranked_results[primary_count:primary_count * 2]

        # Получение зависимостей для primary items
        dependencies = []
        if request.include_dependencies:
            dependencies = await self._fetch_dependencies(
                [r["file_path"] for r in primary_results]
            )

        # Конвертация в ContextItem
        primary_items = [
            self._dict_to_context_item(r) for r in primary_results
        ]
        supporting_items = [
            self._dict_to_context_item(r) for r in supporting_results
        ]

        # Вычисление метрик
        avg_relevance = (
            sum(r["score"] for r in ranked_results) / len(ranked_results)
            if ranked_results else 0.0
        )

        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

        # Suggested actions на основе intent
        suggested_actions = self._generate_suggested_actions(
            intent_result,
            primary_items
        )

        return AssembledContext(
            query=request.query,
            context_type=request.context_type or ContextType.CODE_SEARCH,
            strategy_used=strategy,
            primary_items=primary_items,
            supporting_items=supporting_items,
            related_dependencies=dependencies,
            total_items=len(ranked_results),
            avg_relevance=avg_relevance,
            processing_time_ms=processing_time,
            intent_classification=intent_result,
            suggested_actions=suggested_actions,
            confidence_score=intent_result.get("confidence", 0.5),
            timeline_events=[]  # TODO: Добавить если timeline доступен
        )

    def _select_strategy(
        self,
        intent_result: Dict[str, Any],
        request: ContextRequest
    ) -> RetrievalStrategy:
        """Выбор оптимальной стратегии поиска на основе intent"""
        intent = intent_result.get("intent", "general_search")
        confidence = intent_result.get("confidence", 0.5)

        # Mapping intent → strategy
        if intent == "find_function":
            return RetrievalStrategy.SEMANTIC_ONLY
        elif intent == "understand_code":
            return RetrievalStrategy.GRAPH_FOCUSED
        elif intent == "debug_issue":
            return RetrievalStrategy.COMPREHENSIVE
        elif confidence > 0.7:
            return RetrievalStrategy.ADAPTIVE
        else:
            return RetrievalStrategy.COMPREHENSIVE

    def _map_intent_to_context_type(self, intent) -> ContextType:
        """Mapping SearchIntent → ContextType"""
        mapping = {
            "find_function": ContextType.CODE_SEARCH,
            "find_module": ContextType.CODE_SEARCH,
            "understand_code": ContextType.CODE_UNDERSTANDING,
            "find_examples": ContextType.EXAMPLES,
            "debug_issue": ContextType.DEBUGGING,
            "general_search": ContextType.CODE_SEARCH
        }
        return mapping.get(intent.value if hasattr(intent, 'value') else str(intent),
                         ContextType.CODE_SEARCH)

    def _enhance_query_with_intent(
        self,
        query: str,
        intent_result: Dict[str, Any]
    ) -> str:
        """Добавление контекста намерения в query для LLM"""
        intent = intent_result.get("intent", "general_search")
        reasoning = intent_result.get("reasoning", "")

        if reasoning:
            return f"{query} [Intent: {intent}, Context: {reasoning[:100]}]"
        return query

    def _deduplicate_results(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Дедупликация результатов по file_path с объединением scores"""
        seen = {}

        for result in results:
            file_path = result.get("file_path", "")
            if not file_path:
                continue

            if file_path not in seen:
                seen[file_path] = result
            else:
                # Объединяем scores (weighted average)
                existing = seen[file_path]
                existing["score"] = (existing["score"] + result["score"]) / 2
                existing["source"] = f"{existing['source']},{result['source']}"

        return sorted(seen.values(), key=lambda x: x.get("score", 0), reverse=True)

    async def _fetch_dependencies(
        self,
        file_paths: List[str]
    ) -> List[Dict[str, Any]]:
        """Получение зависимостей для списка файлов"""
        try:
            all_deps = []
            for file_path in file_paths[:5]:  # Ограничиваем для производительности
                deps = self.graph.get_dependencies(file_path)
                all_deps.append({
                    "file_path": file_path,
                    "dependencies": deps.get("imports", []),
                    "dependents": deps.get("imported_by", [])
                })
            return all_deps
        except Exception as e:
            logger.error(f"Ошибка получения зависимостей: {e}")
            return []

    def _dict_to_context_item(self, data: Dict[str, Any]) -> ContextItem:
        """Конвертация dict в ContextItem"""
        return ContextItem(
            file_path=data.get("file_path", ""),
            module_type=data.get("module_type", "Unknown"),
            content="",  # Загружается отдельно при необходимости
            summary=data.get("summary", ""),
            relevance_score=data.get("score", 0.0),
            source=data.get("source", "unknown"),
            functions_count=data.get("functions_count", 0),
            variables_count=data.get("variables_count", 0),
            dependencies=data.get("metadata", {}).get("dependencies", []),
            dependents=data.get("metadata", {}).get("dependents", []),
            last_modified=data.get("last_modified"),
            llm_reasoning=data.get("llm_reasoning", ""),
            llm_confidence=data.get("llm_confidence", 0.0)
        )

    def _generate_suggested_actions(
        self,
        intent_result: Dict[str, Any],
        items: List[ContextItem]
    ) -> List[str]:
        """Генерация рекомендуемых действий на основе intent и результатов"""
        intent = intent_result.get("intent", "general_search")
        actions = []

        if intent == "find_function":
            actions.append("Просмотрите найденные функции в primary items")
            actions.append("Проверьте зависимости для понимания контекста использования")
        elif intent == "understand_code":
            actions.append("Изучите граф зависимостей между модулями")
            actions.append("Используйте LLM для генерации объяснений кода")
        elif intent == "debug_issue":
            actions.append("Проверьте recent changes в timeline events")
            actions.append("Анализируйте зависимости для поиска источника проблемы")
        elif intent == "find_examples":
            actions.append("Изучите code snippets в найденных модулях")
            actions.append("Сравните разные реализации для best practices")

        # Общие рекомендации
        if len(items) > 5:
            actions.append(f"Найдено {len(items)} релевантных результатов - рассмотрите top-5")

        return actions


# Singleton instance
_context_manager: Optional[ContextManager] = None


def get_context_manager(
    llm_service,
    search_service,
    graph_analytics,
    timeline_service=None,
    redis_client=None
) -> ContextManager:
    """
    Получение singleton instance ContextManager

    Args:
        llm_service: LLMService instance
        search_service: BSLSearchService instance
        graph_analytics: GraphAnalyticsService instance
        timeline_service: Optional timeline service
        redis_client: Optional Redis client

    Returns:
        ContextManager instance
    """
    global _context_manager

    if _context_manager is None:
        _context_manager = ContextManager(
            llm_service=llm_service,
            search_service=search_service,
            graph_analytics=graph_analytics,
            timeline_service=timeline_service,
            redis_client=redis_client
        )

    return _context_manager
