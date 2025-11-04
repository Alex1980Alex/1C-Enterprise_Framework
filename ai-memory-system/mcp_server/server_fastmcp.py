"""
AI Memory MCP Server - Using FastMCP (MCP 1.16.0)

Использует FastMCP для упрощенной регистрации инструментов
"""

import asyncio
import logging
import sys
import os
from typing import List, Dict, Any

# Добавляем директорию services в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services'))

# Импорты MCP (FastMCP - рекомендуемый способ для 1.16.0)
from mcp.server.fastmcp import FastMCP

# Импорты сервисов
from llm_service import LLMService
from bsl_search_service import BSLSearchService, SearchRequest, SearchMode
from context_manager import get_context_manager, ContextRequest, ContextType
from graph_analytics import GraphAnalyticsService
from qdrant_vector_store import QdrantVectorStore
from neo4j_service import Neo4jService
from search_history import SearchHistoryService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем FastMCP server
mcp = FastMCP("AI Memory System")

# Глобальные сервисы (ленивая инициализация)
_services_initialized = False
llm_service = None
search_service = None
context_manager = None
graph_analytics = None
history_service = None
qdrant = None
neo4j = None


async def ensure_services():
    """Ленивая инициализация всех сервисов"""
    global _services_initialized, llm_service, search_service, context_manager
    global graph_analytics, history_service, qdrant, neo4j

    if _services_initialized:
        return

    logger.info("=== Инициализация сервисов ===")

    # LLM Service
    llm_service = LLMService(
        ollama_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        reranking_model="deepseek-coder:6.7b",
        generation_model="deepseek-coder:6.7b",
        timeout=180
    )
    logger.info("✓ LLM Service")

    # Qdrant Vector Store
    qdrant = QdrantVectorStore(
        host=os.getenv("QDRANT_HOST", "localhost"),
        port=int(os.getenv("QDRANT_PORT", "6333")),
        collection_name=os.getenv("QDRANT_COLLECTION", "bsl_code")
    )
    logger.info("✓ Qdrant Vector Store")

    # Neo4j Service
    neo4j = Neo4jService(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "your_password")
    )
    logger.info("✓ Neo4j Service")

    # Graph Analytics
    graph_analytics = GraphAnalyticsService(neo4j)
    logger.info("✓ Graph Analytics Service")

    # BSL Search Service
    search_service = BSLSearchService(
        qdrant_service=qdrant,
        neo4j_service=neo4j,
        hybrid_engine=None,  # Опционально
        llm_service=llm_service
    )
    logger.info("✓ BSL Search Service")

    # Context Manager
    context_manager = get_context_manager(
        llm_service=llm_service,
        search_service=search_service,
        graph_analytics=graph_analytics
    )
    logger.info("✓ Context Manager")

    # Search History
    history_service = SearchHistoryService(redis_client=None)
    logger.info("✓ Search History Service")

    _services_initialized = True
    logger.info("=== Все сервисы инициализированы ===")


# ================================================================
# Tool 1: search_bsl_code - Базовый семантический поиск
# ================================================================
@mcp.tool()
async def search_bsl_code(
    query: str,
    limit: int = 10,
    mode: str = "semantic"
) -> str:
    """
    Базовый семантический поиск по BSL коду

    Args:
        query: Поисковый запрос
        limit: Максимальное количество результатов (по умолчанию 10)
        mode: Режим поиска (semantic, fulltext, hybrid)

    Returns:
        Список найденных фрагментов кода с метаданными
    """
    await ensure_services()

    logger.info(f"search_bsl_code: query='{query}', limit={limit}, mode={mode}")

    try:
        # Создаем запрос
        request = SearchRequest(
            query=query,
            mode=SearchMode(mode),
            limit=min(limit, 50)
        )

        # Выполняем поиск
        results = await search_service.search(request)

        # Добавляем в историю
        if history_service:
            history_service.add_search(
                query=query,
                mode=mode,
                results_count=len(results)
            )

        # Форматируем результаты
        if not results:
            return f"No results found for query: '{query}'"

        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"""### Result {i} (score: {result.score:.3f})

**File**: {result.file_path}
**Type**: {result.module_type}

**Code**:
```bsl
{result.code_snippet}
```
""")

        return "\n\n".join(formatted)

    except Exception as e:
        logger.error(f"Error in search_bsl_code: {e}", exc_info=True)
        return f"Error during search: {str(e)}"


# ================================================================
# Tool 2: intelligent_search - Интеллектуальный поиск
# ================================================================
@mcp.tool()
async def intelligent_search(
    query: str,
    context_type: str = "code_search",
    max_results: int = 10
) -> str:
    """
    Интеллектуальный многомерный поиск с анализом контекста

    Args:
        query: Поисковый запрос
        context_type: Тип контекста (code_search, code_understanding, debugging, documentation, examples, refactoring)
        max_results: Максимальное количество результатов

    Returns:
        Интеллектуально подобранные результаты с анализом
    """
    await ensure_services()

    logger.info(f"intelligent_search: query='{query}', context_type={context_type}")

    try:
        # Маппинг строки в ContextType enum
        context_type_map = {
            "code_search": ContextType.CODE_SEARCH,
            "code_understanding": ContextType.CODE_UNDERSTANDING,
            "debugging": ContextType.DEBUGGING,
            "documentation": ContextType.DOCUMENTATION,
            "examples": ContextType.EXAMPLES,
            "refactoring": ContextType.REFACTORING
        }

        # Создаём запрос
        request = ContextRequest(
            query=query,
            context_type=context_type_map.get(context_type, ContextType.CODE_SEARCH),
            max_results=max_results,
            include_dependencies=True,
            include_examples=(context_type == "examples"),
            min_relevance=0.5
        )

        # Собираем контекст через Context Manager
        assembled = await context_manager.assemble_context(request)

        # Форматируем результаты
        formatted_results = []
        for i, item in enumerate(assembled.primary_items[:5], 1):
            formatted_results.append(f"""### Result {i} (relevance: {item.relevance_score:.3f})

**File**: {item.file_path}
**Type**: {item.module_type}
**Source**: {item.source}

**Summary**: {item.summary}

**LLM Analysis**:
{item.llm_reasoning if item.llm_reasoning else 'N/A'}

**Functions**: {item.functions_count}
**Dependencies**: {', '.join(item.dependencies[:3]) if item.dependencies else 'None'}
""")

        if len(assembled.primary_items) > 5:
            formatted_results.append(f"... and {len(assembled.primary_items) - 5} more results")

        return f"""## Intelligent Search Results

**Query**: {query}
**Context Type**: {assembled.context_type.value}
**Strategy Used**: {assembled.strategy_used.value}
**Total Items**: {assembled.total_items}
**Avg Relevance**: {assembled.avg_relevance:.3f}
**Processing Time**: {assembled.processing_time_ms}ms
**Confidence**: {assembled.confidence_score:.2f}

### Intent Classification
**Intent**: {assembled.intent_classification.get('intent', 'unknown')}
**Confidence**: {assembled.intent_classification.get('confidence', 0):.2f}

### Suggested Actions
{chr(10).join(f'- {action}' for action in assembled.suggested_actions)}

### Primary Results
{chr(10).join(formatted_results)}

### Supporting Context
Found {len(assembled.supporting_items)} additional supporting items
Related dependencies: {len(assembled.related_dependencies)}
"""

    except Exception as e:
        logger.error(f"Error in intelligent_search: {e}", exc_info=True)
        return f"Error during intelligent search: {str(e)}"


# ================================================================
# Tool 3: analyze_graph - Анализ графа зависимостей
# ================================================================
@mcp.tool()
async def analyze_graph(
    file_path: str = None,
    analysis_type: str = "dependencies"
) -> str:
    """
    Анализ графа зависимостей BSL кода

    Args:
        file_path: Путь к файлу для анализа (опционально)
        analysis_type: Тип анализа (dependencies, centrality, communities, full)

    Returns:
        Результаты анализа графа зависимостей
    """
    await ensure_services()

    logger.info(f"analyze_graph: file_path='{file_path}', type={analysis_type}")

    # Проверяем доступность графа
    if not graph_analytics or not graph_analytics.driver:
        return "⚠️ Graph analytics not available (Neo4j not connected)"

    try:
        results = []

        # Анализ конкретного файла
        if file_path and analysis_type in ["dependencies", "full"]:
            deps = graph_analytics.get_dependencies(file_path)

            imports_list = '\n'.join(f'- {imp}' for imp in deps['imports']) if deps['imports'] else '- None'
            imported_by_list = '\n'.join(f'- {imp}' for imp in deps['imported_by']) if deps['imported_by'] else '- None'

            results.append(f"""## Dependencies for {file_path}

**Imports**: {len(deps['imports'])} modules
**Imported by**: {len(deps['imported_by'])} modules

### This module imports:
{imports_list}

### This module is imported by:
{imported_by_list}
""")

        # Анализ центральности
        if analysis_type in ["centrality", "full"]:
            centrality = graph_analytics.calculate_centrality(top_n=10)

            if centrality:
                centrality_list = '\n'.join(
                    f'{i}. {mod} (score: {score:.1f})'
                    for i, (mod, score) in enumerate(centrality, 1)
                )

                results.append(f"""## Top 10 Central Modules

These modules are most important in the codebase based on their connections:

{centrality_list}
""")

        # Анализ сообществ
        if analysis_type in ["communities", "full"]:
            communities = graph_analytics.detect_communities(max_communities=5)

            if communities:
                communities_text = '\n\n'.join(
                    f'**Community {i}** ({len(comm)} modules):\n' +
                    '\n'.join(f'  - {mod}' for mod in comm[:5]) +
                    (f'\n  ... and {len(comm) - 5} more' if len(comm) > 5 else '')
                    for i, comm in enumerate(communities, 1)
                )

                results.append(f"""## Detected Communities

Found {len(communities)} communities of related modules:

{communities_text}
""")

        return "\n\n".join(results) if results else "No analysis results available"

    except Exception as e:
        logger.error(f"Error in analyze_graph: {e}", exc_info=True)
        return f"Error during graph analysis: {str(e)}"


# ================================================================
# Tool 4: get_search_history - История поисковых запросов
# ================================================================
@mcp.tool()
async def get_search_history(limit: int = 10) -> str:
    """
    Получить историю поисковых запросов

    Args:
        limit: Количество последних запросов (по умолчанию 10)

    Returns:
        История поисковых запросов с метаданными
    """
    await ensure_services()

    logger.info(f"get_search_history: limit={limit}")

    try:
        if not history_service:
            return "Search history service not available"

        history = history_service.get_recent_searches(limit=limit)

        if not history:
            return "No search history available"

        # Форматируем историю
        formatted_entries = []
        for i, entry in enumerate(history, 1):
            formatted_entries.append(
                f"{i}. **{entry['query']}**\n"
                f"   - Mode: {entry['mode']}\n"
                f"   - Results: {entry['results_count']}\n"
                f"   - Time: {entry['timestamp']}"
            )

        return f"""## Search History

Last {len(history)} searches:

{chr(10).join(formatted_entries)}
"""

    except Exception as e:
        logger.error(f"Error in get_search_history: {e}", exc_info=True)
        return f"Error retrieving search history: {str(e)}"


# ================================================================
# Tool 5: clear_cache - Очистка кеша
# ================================================================
@mcp.tool()
async def clear_cache(cache_type: str = "search_history") -> str:
    """
    Очистить кеш и историю поиска

    Args:
        cache_type: Тип кеша (search_history, all)

    Returns:
        Подтверждение очистки
    """
    await ensure_services()

    logger.info(f"clear_cache: type={cache_type}")

    try:
        if cache_type in ["search_history", "all"]:
            if history_service:
                history_service.clear_history()
                return "✓ Search history cleared successfully"

        return f"Cache type '{cache_type}' not recognized"

    except Exception as e:
        logger.error(f"Error in clear_cache: {e}", exc_info=True)
        return f"Error clearing cache: {str(e)}"


if __name__ == "__main__":
    logger.info("=== Starting AI Memory MCP Server (FastMCP) ===")
    mcp.run()
