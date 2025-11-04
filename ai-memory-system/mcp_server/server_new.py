"""
AI Memory MCP Server - New API (MCP 1.16.0)

Полностью переписанный MCP сервер для работы с MCP SDK 1.16.0
Использует новый API с Server и stdio_server
"""

import asyncio
import logging
import sys
import os
from typing import Optional, List, Dict, Any

# Добавляем директорию services в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services'))

# Импорты нового MCP API
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Импорты сервисов
from llm_service import LLMService
from bsl_search_service import get_bsl_search_service, SearchRequest, SearchMode
from context_manager import get_context_manager
from graph_analytics import GraphAnalyticsService
from qdrant_vector_store import QdrantVectorStore
from neo4j_service import Neo4jService
from search_history import SearchHistoryService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIMemoryMCPServer:
    """MCP Server для AI Memory System на базе нового API"""

    def __init__(self):
        """Инициализация MCP сервера"""
        logger.info("=== Инициализация AI Memory MCP Server (New API) ===")

        # Создаем MCP Server
        self.server = Server("ai-memory-system")

        # Сервисы (ленивая инициализация)
        self.llm_service: Optional[LLMService] = None
        self.search_service = None
        self.context_manager = None
        self.graph_analytics: Optional[GraphAnalyticsService] = None
        self.history_service: Optional[SearchHistoryService] = None
        self.qdrant = None
        self.neo4j = None

        # Регистрируем инструменты
        self._register_tools()

        logger.info("✓ MCP Server инициализирован")

    def _register_tools(self):
        """Регистрация всех инструментов MCP"""

        # ============================================================
        # Tool 1: search_bsl_code - Базовый семантический поиск
        # ============================================================
        @self.server.call_tool()
        async def search_bsl_code(arguments: dict) -> List[TextContent]:
            """
            Базовый семантический поиск по BSL коду

            Args:
                query: Поисковый запрос
                limit: Максимальное количество результатов (по умолчанию 10)
                mode: Режим поиска (semantic, fulltext, hybrid)

            Returns:
                Список найденных фрагментов кода с метаданными
            """
            await self._ensure_services()

            query = arguments.get("query")
            limit = arguments.get("limit", 10)
            mode = arguments.get("mode", "semantic")

            if not query:
                return [TextContent(
                    type="text",
                    text="Error: 'query' parameter is required"
                )]

            logger.info(f"search_bsl_code: query='{query}', limit={limit}, mode={mode}")

            try:
                # Создаем запрос
                request = SearchRequest(
                    query=query,
                    mode=SearchMode(mode),
                    limit=min(limit, 50)
                )

                # Выполняем поиск
                results = await self.search_service.search(request)

                # Добавляем в историю
                if self.history_service:
                    self.history_service.add_search(
                        query=query,
                        mode=mode,
                        results_count=len(results)
                    )

                # Форматируем результаты
                if not results:
                    return [TextContent(
                        type="text",
                        text=f"No results found for query: '{query}'"
                    )]

                formatted = []
                for i, result in enumerate(results, 1):
                    formatted.append(TextContent(
                        type="text",
                        text=f"""### Result {i} (score: {result.score:.3f})

**File**: {result.file_path}
**Type**: {result.module_type}

**Code**:
```bsl
{result.code_snippet}
```
"""
                    ))

                return formatted

            except Exception as e:
                logger.error(f"Error in search_bsl_code: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error during search: {str(e)}"
                )]

        # ============================================================
        # Tool 2: intelligent_search - Интеллектуальный поиск
        # ============================================================
        @self.server.call_tool()
        async def intelligent_search(arguments: dict) -> List[TextContent]:
            """
            Интеллектуальный многомерный поиск с анализом контекста

            Args:
                query: Поисковый запрос
                context_type: Тип контекста (code_search, documentation, examples)
                max_results: Максимальное количество результатов

            Returns:
                Интеллектуально подобранные результаты с анализом
            """
            await self._ensure_services()

            query = arguments.get("query")
            context_type = arguments.get("context_type", "code_search")
            max_results = arguments.get("max_results", 10)

            if not query:
                return [TextContent(
                    type="text",
                    text="Error: 'query' parameter is required"
                )]

            logger.info(f"intelligent_search: query='{query}', context_type={context_type}")

            try:
                # Используем Context Manager для интеллектуального поиска
                context = await self.context_manager.get_context(
                    query=query,
                    context_type=context_type,
                    max_results=max_results
                )

                # Форматируем результаты
                intent = context.get('intent', 'unknown')
                results = context.get('results', [])
                summary = context.get('summary', 'No summary available')

                return [TextContent(
                    type="text",
                    text=f"""## Intelligent Search Results

**Query**: {query}
**Detected Intent**: {intent}
**Results Found**: {len(results)}

### Summary
{summary}

### Results Details
{self._format_results_list(results)}
"""
                )]

            except Exception as e:
                logger.error(f"Error in intelligent_search: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error during intelligent search: {str(e)}"
                )]

        # ============================================================
        # Tool 3: analyze_graph - Анализ графа зависимостей
        # ============================================================
        @self.server.call_tool()
        async def analyze_graph(arguments: dict) -> List[TextContent]:
            """
            Анализ графа зависимостей BSL кода

            Args:
                file_path: Путь к файлу для анализа (опционально)
                analysis_type: Тип анализа (dependencies, centrality, communities, full)

            Returns:
                Результаты анализа графа зависимостей
            """
            await self._ensure_services()

            file_path = arguments.get("file_path")
            analysis_type = arguments.get("analysis_type", "dependencies")

            logger.info(f"analyze_graph: file_path='{file_path}', type={analysis_type}")

            # Проверяем доступность графа
            if not self.graph_analytics or not self.graph_analytics.driver:
                return [TextContent(
                    type="text",
                    text="⚠️ Graph analytics not available (Neo4j not connected)"
                )]

            try:
                results = []

                # Анализ конкретного файла
                if file_path and analysis_type in ["dependencies", "full"]:
                    deps = self.graph_analytics.get_dependencies(file_path)

                    imports_list = '\n'.join(f'- {imp}' for imp in deps['imports']) if deps['imports'] else '- None'
                    imported_by_list = '\n'.join(f'- {imp}' for imp in deps['imported_by']) if deps['imported_by'] else '- None'

                    results.append(TextContent(
                        type="text",
                        text=f"""## Dependencies for {file_path}

**Imports**: {len(deps['imports'])} modules
**Imported by**: {len(deps['imported_by'])} modules

### This module imports:
{imports_list}

### This module is imported by:
{imported_by_list}
"""
                    ))

                # Анализ центральности
                if analysis_type in ["centrality", "full"]:
                    centrality = self.graph_analytics.calculate_centrality(top_n=10)

                    if centrality:
                        centrality_list = '\n'.join(
                            f'{i}. {mod} (score: {score:.1f})'
                            for i, (mod, score) in enumerate(centrality, 1)
                        )

                        results.append(TextContent(
                            type="text",
                            text=f"""## Top 10 Central Modules

These modules are most important in the codebase based on their connections:

{centrality_list}
"""
                        ))

                # Анализ сообществ
                if analysis_type in ["communities", "full"]:
                    communities = self.graph_analytics.detect_communities(max_communities=5)

                    if communities:
                        communities_text = '\n\n'.join(
                            f'**Community {i}** ({len(comm)} modules):\n' +
                            '\n'.join(f'  - {mod}' for mod in comm[:5]) +
                            (f'\n  ... and {len(comm) - 5} more' if len(comm) > 5 else '')
                            for i, comm in enumerate(communities, 1)
                        )

                        results.append(TextContent(
                            type="text",
                            text=f"""## Detected Communities

Found {len(communities)} communities of related modules:

{communities_text}
"""
                        ))

                return results if results else [TextContent(
                    type="text",
                    text="No analysis results available"
                )]

            except Exception as e:
                logger.error(f"Error in analyze_graph: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error during graph analysis: {str(e)}"
                )]

        # ============================================================
        # Tool 4: get_search_history - История поисковых запросов
        # ============================================================
        @self.server.call_tool()
        async def get_search_history(arguments: dict) -> List[TextContent]:
            """
            Получить историю поисковых запросов

            Args:
                limit: Количество последних запросов (по умолчанию 10)

            Returns:
                История поисковых запросов с метаданными
            """
            await self._ensure_services()

            limit = arguments.get("limit", 10)

            logger.info(f"get_search_history: limit={limit}")

            try:
                if not self.history_service:
                    return [TextContent(
                        type="text",
                        text="Search history service not available"
                    )]

                history = self.history_service.get_recent_searches(limit=limit)

                if not history:
                    return [TextContent(
                        type="text",
                        text="No search history available"
                    )]

                # Форматируем историю
                formatted_entries = []
                for i, entry in enumerate(history, 1):
                    formatted_entries.append(
                        f"{i}. **{entry['query']}**\n"
                        f"   - Mode: {entry['mode']}\n"
                        f"   - Results: {entry['results_count']}\n"
                        f"   - Time: {entry['timestamp']}"
                    )

                return [TextContent(
                    type="text",
                    text=f"""## Search History

Last {len(history)} searches:

{chr(10).join(formatted_entries)}
"""
                )]

            except Exception as e:
                logger.error(f"Error in get_search_history: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error retrieving search history: {str(e)}"
                )]

        # ============================================================
        # Tool 5: export_results - Экспорт результатов
        # ============================================================
        @self.server.call_tool()
        async def export_results(arguments: dict) -> List[TextContent]:
            """
            Экспортировать результаты последнего поиска

            Args:
                format: Формат экспорта (json, markdown, text)
                filename: Имя файла для экспорта

            Returns:
                Подтверждение экспорта или данные
            """
            await self._ensure_services()

            export_format = arguments.get("format", "json")
            filename = arguments.get("filename", "export")

            logger.info(f"export_results: format={export_format}, filename={filename}")

            return [TextContent(
                type="text",
                text=f"""## Export Results

**Format**: {export_format}
**Filename**: {filename}

⚠️ Export functionality is not yet implemented in this version.
This is a placeholder for future implementation.
"""
            )]

        # ============================================================
        # Tool 6: clear_cache - Очистка кеша
        # ============================================================
        @self.server.call_tool()
        async def clear_cache(arguments: dict) -> List[TextContent]:
            """
            Очистить кеш и историю поиска

            Args:
                cache_type: Тип кеша (search_history, all)

            Returns:
                Подтверждение очистки
            """
            await self._ensure_services()

            cache_type = arguments.get("cache_type", "search_history")

            logger.info(f"clear_cache: type={cache_type}")

            try:
                if cache_type in ["search_history", "all"]:
                    if self.history_service:
                        self.history_service.clear_history()
                        return [TextContent(
                            type="text",
                            text="✓ Search history cleared successfully"
                        )]

                return [TextContent(
                    type="text",
                    text=f"Cache type '{cache_type}' not recognized"
                )]

            except Exception as e:
                logger.error(f"Error in clear_cache: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error clearing cache: {str(e)}"
                )]

        logger.info("✓ Зарегистрировано 6 инструментов")

    async def _ensure_services(self):
        """Ленивая инициализация всех сервисов"""
        if self.llm_service is None:
            logger.info("=== Инициализация сервисов ===")

            # LLM Service
            self.llm_service = LLMService(
                base_url="http://localhost:11434",
                model="deepseek-coder:6.7b"
            )
            logger.info("✓ LLM Service")

            # Qdrant Vector Store
            self.qdrant = QdrantVectorStore(
                host="localhost",
                port=6333,
                collection_name="bsl_code"
            )
            logger.info("✓ Qdrant Vector Store")

            # Neo4j Service
            self.neo4j = Neo4jService(
                uri="bolt://localhost:7687",
                user="neo4j",
                password="your_password"  # ⚠️ ИЗМЕНИТЬ!
            )
            logger.info("✓ Neo4j Service")

            # Graph Analytics
            self.graph_analytics = GraphAnalyticsService(self.neo4j)
            logger.info("✓ Graph Analytics Service")

            # BSL Search Service
            self.search_service = get_bsl_search_service(
                qdrant_client=self.qdrant.get_client(),
                collection_name="bsl_code",
                llm_service=self.llm_service
            )
            logger.info("✓ BSL Search Service")

            # Context Manager
            self.context_manager = get_context_manager(
                llm_service=self.llm_service,
                search_service=self.search_service,
                graph_analytics=self.graph_analytics
            )
            logger.info("✓ Context Manager")

            # Search History
            self.history_service = SearchHistoryService(redis_client=None)
            logger.info("✓ Search History Service")

            logger.info("=== Все сервисы инициализированы ===")

    def _format_results_list(self, results: List[Any]) -> str:
        """Форматировать список результатов для вывода"""
        if not results:
            return "No results"

        formatted = []
        for i, result in enumerate(results[:5], 1):  # Показываем первые 5
            if hasattr(result, 'file_path'):
                formatted.append(f"{i}. {result.file_path} (score: {result.score:.3f})")
            else:
                formatted.append(f"{i}. {str(result)[:100]}...")

        if len(results) > 5:
            formatted.append(f"... and {len(results) - 5} more results")

        return '\n'.join(formatted)

    async def run(self):
        """Запуск MCP сервера через stdio"""
        logger.info("=== Запуск MCP Server через stdio ===")

        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Error running MCP server: {e}", exc_info=True)
            raise


async def main():
    """Главная функция"""
    try:
        server = AIMemoryMCPServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
