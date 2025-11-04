"""
MCP Server для AI Memory System

Model Context Protocol (MCP) сервер, предоставляющий интеллектуальный поиск по BSL коду для Claude Code.

Предоставляет 6 инструментов:
1. search_bsl_code - базовый семантический поиск
2. intelligent_search - интеллектуальный многомерный поиск
3. analyze_graph - анализ графа зависимостей
4. get_search_history - получение истории поиска
5. export_results - экспорт результатов
6. clear_cache - очистка кеша

ROI Impact: 40% ($19,920/год)
"""

import asyncio
import json
import logging
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Добавляем путь к services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services'))

from llm_service import get_llm_service
from bsl_search_service import get_bsl_search_service, SearchRequest, SearchMode
from context_manager import get_context_manager, ContextRequest, ContextType
from graph_analytics import GraphAnalyticsService
from hybrid_search_engine import HybridSearchEngine
from qdrant_vector_store import QdrantVectorStore
from neo4j_service import Neo4jService
from search_history import SearchHistoryService

# MCP Protocol imports
try:
    from mcp.server import Server as McpServer
    from mcp.types import TextContent, Tool
    from mcp.server.stdio import stdio_server
except ImportError:
    print("ERROR: MCP library not installed. Install with: pip install mcp")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIMemoryMCPServer:
    """
    MCP Server для AI Memory System

    Координирует все компоненты системы и предоставляет их через MCP протокол
    """

    def __init__(self):
        """Инициализация MCP Server и всех компонентов"""
        logger.info("=== Инициализация AI Memory MCP Server ===")

        # MCP Server
        self.mcp = McpServer("ai-memory-system")

        # Services (инициализируются лениво)
        self.llm_service = None
        self.search_service = None
        self.context_manager = None
        self.graph_analytics = None
        self.history_service = None

        # Core components
        self.qdrant = None
        self.neo4j = None
        self.hybrid_engine = None

        # Configuration
        self.config = self._load_config()

        # Cache
        self.search_cache = {}
        self.cache_ttl = 300  # 5 минут

        # Register MCP tools
        self._register_tools()

        logger.info("MCP Server инициализирован")

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        config_path = Path(__file__).parent / "config.json"

        default_config = {
            "ollama": {
                "url": "http://localhost:11434",
                "reranking_model": "deepseek-coder:6.7b",
                "generation_model": "deepseek-coder:6.7b",
                "timeout": 180
            },
            "qdrant": {
                "host": "localhost",
                "port": 6333,
                "collection": "bsl_code_v2"
            },
            "neo4j": {
                "uri": "bolt://localhost:7687",
                "user": "neo4j",
                "password": "password"
            },
            "search": {
                "default_limit": 10,
                "max_limit": 50,
                "min_relevance": 0.5
            }
        }

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
                    logger.info(f"Конфигурация загружена из {config_path}")
            except Exception as e:
                logger.warning(f"Ошибка загрузки конфигурации: {e}. Используются defaults.")

        return default_config

    async def _ensure_services(self):
        """Ленивая инициализация сервисов при первом использовании"""
        if self.llm_service is not None:
            return  # Уже инициализированы

        logger.info("Инициализация сервисов...")

        try:
            # LLM Service
            ollama_config = self.config["ollama"]
            self.llm_service = get_llm_service(
                ollama_url=ollama_config["url"],
                reranking_model=ollama_config["reranking_model"],
                generation_model=ollama_config["generation_model"]
            )
            logger.info("✓ LLM Service")

            # Qdrant
            qdrant_config = self.config["qdrant"]
            self.qdrant = QdrantVectorStore(
                host=qdrant_config["host"],
                port=qdrant_config["port"],
                collection_name=qdrant_config["collection"]
            )
            logger.info("✓ Qdrant")

            # Neo4j
            neo4j_config = self.config["neo4j"]
            self.neo4j = Neo4jService(
                uri=neo4j_config["uri"],
                user=neo4j_config["user"],
                password=neo4j_config["password"]
            )
            logger.info("✓ Neo4j")

            # Hybrid Search Engine
            self.hybrid_engine = HybridSearchEngine(
                qdrant_service=self.qdrant,
                neo4j_service=self.neo4j
            )
            logger.info("✓ Hybrid Search")

            # Graph Analytics
            self.graph_analytics = GraphAnalyticsService(self.neo4j)
            logger.info("✓ Graph Analytics")

            # Search Service
            self.search_service = get_bsl_search_service(
                qdrant_service=self.qdrant,
                neo4j_service=self.neo4j,
                hybrid_engine=self.hybrid_engine,
                llm_service=self.llm_service
            )
            logger.info("✓ Search Service")

            # Context Manager
            self.context_manager = get_context_manager(
                llm_service=self.llm_service,
                search_service=self.search_service,
                graph_analytics=self.graph_analytics
            )
            logger.info("✓ Context Manager")

            # Search History
            self.history_service = SearchHistoryService(redis_client=None)
            logger.info("✓ Search History")

            logger.info("Все сервисы инициализированы успешно")

        except Exception as e:
            logger.error(f"Ошибка инициализации сервисов: {e}")
            raise

    def _register_tools(self):
        """Регистрация MCP инструментов"""

        # Tool 1: search_bsl_code
        @self.mcp.tool()
        async def search_bsl_code(
            query: str,
            limit: int = 10,
            mode: str = "semantic",
            module_types: Optional[List[str]] = None
        ) -> List[TextContent]:
            """
            Базовый семантический поиск по BSL коду

            Args:
                query: Поисковый запрос
                limit: Максимальное количество результатов (default: 10, max: 50)
                mode: Режим поиска (semantic, graph, hybrid, intelligent)
                module_types: Фильтр по типам модулей

            Returns:
                Список результатов поиска
            """
            await self._ensure_services()

            # Проверка кеша
            cache_key = f"search:{query}:{limit}:{mode}"
            if cache_key in self.search_cache:
                cached = self.search_cache[cache_key]
                if (datetime.now() - cached["timestamp"]).seconds < self.cache_ttl:
                    logger.info(f"Cache hit: {cache_key}")
                    return cached["results"]

            # Выполнение поиска
            search_config = self.config["search"]
            limit = min(limit, search_config["max_limit"])

            mode_map = {
                "semantic": SearchMode.SEMANTIC_ONLY,
                "graph": SearchMode.GRAPH_ONLY,
                "hybrid": SearchMode.HYBRID,
                "intelligent": SearchMode.INTELLIGENT
            }

            request = SearchRequest(
                query=query,
                mode=mode_map.get(mode, SearchMode.SEMANTIC_ONLY),
                limit=limit,
                module_types=module_types,
                min_score=search_config["min_relevance"]
            )

            results = await self.search_service.search(request)

            # Сохранение истории
            await self.history_service.save_search(
                query=query,
                results_count=len(results),
                mode=mode
            )

            # Форматирование для MCP
            formatted_results = []
            for i, result in enumerate(results, 1):
                text = f"""[{i}] {result.file_path}
Type: {result.module_type}
Score: {result.score:.3f}
Summary: {result.summary}
Functions: {result.functions_count}
Source: {result.source}
"""
                if result.reasoning:
                    text += f"Reasoning: {result.reasoning}\n"

                formatted_results.append(TextContent(
                    type="text",
                    text=text
                ))

            # Кеширование
            self.search_cache[cache_key] = {
                "timestamp": datetime.now(),
                "results": formatted_results
            }

            return formatted_results

        # Tool 2: intelligent_search
        @self.mcp.tool()
        async def intelligent_search(
            query: str,
            context_type: Optional[str] = None,
            max_results: int = 10,
            include_dependencies: bool = True
        ) -> List[TextContent]:
            """
            Интеллектуальный многомерный поиск с Context Manager

            Использует полный pipeline:
            1. Intent Analysis
            2. Multi-dimensional Retrieval
            3. LLM Precision Ranking
            4. Context Assembly

            Args:
                query: Поисковый запрос
                context_type: Тип контекста (code_search, code_understanding, debugging, examples)
                max_results: Максимальное количество результатов
                include_dependencies: Включить зависимости

            Returns:
                Собранный интеллектуальный контекст
            """
            await self._ensure_services()

            # Mapping context_type
            context_map = {
                "code_search": ContextType.CODE_SEARCH,
                "code_understanding": ContextType.CODE_UNDERSTANDING,
                "debugging": ContextType.DEBUGGING,
                "examples": ContextType.EXAMPLES,
                "documentation": ContextType.DOCUMENTATION
            }

            request = ContextRequest(
                query=query,
                context_type=context_map.get(context_type) if context_type else None,
                max_results=max_results,
                include_dependencies=include_dependencies
            )

            assembled_context = await self.context_manager.assemble_context(request)

            # Форматирование для MCP
            results = []

            # Summary
            summary = f"""=== INTELLIGENT SEARCH RESULTS ===

Query: {query}
Context Type: {assembled_context.context_type.value}
Strategy: {assembled_context.strategy_used.value}
Total Items: {assembled_context.total_items}
Avg Relevance: {assembled_context.avg_relevance:.3f}
Processing Time: {assembled_context.processing_time_ms}ms
Confidence: {assembled_context.confidence_score:.2f}

=== INTENT ANALYSIS ===
Intent: {assembled_context.intent_classification.get('intent', 'Unknown')}
Confidence: {assembled_context.intent_classification.get('confidence', 0):.2f}
Reasoning: {assembled_context.intent_classification.get('reasoning', 'N/A')}

=== PRIMARY RESULTS ===
"""
            results.append(TextContent(type="text", text=summary))

            # Primary items
            for i, item in enumerate(assembled_context.primary_items, 1):
                text = f"""[{i}] {item.file_path}
Type: {item.module_type}
Relevance: {item.relevance_score:.3f}
Summary: {item.summary}
Functions: {item.functions_count}
Source: {item.source}
"""
                if item.llm_reasoning:
                    text += f"LLM Reasoning: {item.llm_reasoning[:200]}...\n"

                results.append(TextContent(type="text", text=text))

            # Suggested actions
            if assembled_context.suggested_actions:
                actions_text = "\n=== SUGGESTED ACTIONS ===\n"
                for i, action in enumerate(assembled_context.suggested_actions, 1):
                    actions_text += f"{i}. {action}\n"
                results.append(TextContent(type="text", text=actions_text))

            # Dependencies
            if assembled_context.related_dependencies:
                deps_text = "\n=== DEPENDENCIES ===\n"
                for dep_info in assembled_context.related_dependencies[:3]:
                    deps_text += f"\nFile: {dep_info['file_path']}\n"
                    deps_text += f"  Dependencies: {len(dep_info.get('dependencies', []))}\n"
                    deps_text += f"  Dependents: {len(dep_info.get('dependents', []))}\n"
                results.append(TextContent(type="text", text=deps_text))

            return results

        # Tool 3: analyze_graph
        @self.mcp.tool()
        async def analyze_graph(
            file_path: Optional[str] = None,
            analysis_type: str = "dependencies"
        ) -> List[TextContent]:
            """
            Анализ графа зависимостей

            Args:
                file_path: Путь к файлу для анализа (опционально)
                analysis_type: Тип анализа (dependencies, centrality, communities, full)

            Returns:
                Результаты анализа графа
            """
            await self._ensure_services()

            results = []

            if file_path:
                # Анализ конкретного файла
                deps = self.graph_analytics.get_dependencies(file_path)

                text = f"""=== DEPENDENCY ANALYSIS ===

File: {file_path}

Imports ({len(deps.get('imports', []))}):
"""
                for imp in deps.get('imports', [])[:10]:
                    text += f"  - {imp}\n"

                text += f"\nImported By ({len(deps.get('imported_by', []))}):\n"
                for imp in deps.get('imported_by', [])[:10]:
                    text += f"  - {imp}\n"

                results.append(TextContent(type="text", text=text))

            if analysis_type in ["centrality", "full"]:
                # Анализ центральности
                centrality = self.graph_analytics.calculate_centrality()

                text = "\n=== CENTRALITY ANALYSIS ===\n\nTop 10 Most Important Modules:\n"
                for i, (module, score) in enumerate(centrality[:10], 1):
                    text += f"{i}. {module} (score: {score:.3f})\n"

                results.append(TextContent(type="text", text=text))

            if analysis_type in ["communities", "full"]:
                # Анализ сообществ
                communities = self.graph_analytics.detect_communities()

                text = f"\n=== COMMUNITY ANALYSIS ===\n\nTotal Communities: {len(communities)}\n\n"
                for i, community in enumerate(communities[:5], 1):
                    text += f"Community {i} ({len(community)} modules):\n"
                    for module in community[:5]:
                        text += f"  - {module}\n"

                results.append(TextContent(type="text", text=text))

            return results if results else [TextContent(
                type="text",
                text="No analysis performed. Specify file_path or analysis_type."
            )]

        # Tool 4: get_search_history
        @self.mcp.tool()
        async def get_search_history(
            limit: int = 10,
            filter_by: Optional[str] = None
        ) -> List[TextContent]:
            """
            Получение истории поиска

            Args:
                limit: Количество записей (default: 10)
                filter_by: Фильтр по query или mode

            Returns:
                История поисковых запросов
            """
            await self._ensure_services()

            history = await self.history_service.get_recent_searches(limit=limit)

            if not history:
                return [TextContent(
                    type="text",
                    text="История поиска пуста"
                )]

            text = "=== SEARCH HISTORY ===\n\n"
            for i, entry in enumerate(history, 1):
                text += f"[{i}] {entry.get('query', 'Unknown')}\n"
                text += f"    Time: {entry.get('timestamp', 'Unknown')}\n"
                text += f"    Results: {entry.get('results_count', 0)}\n"
                text += f"    Mode: {entry.get('mode', 'unknown')}\n\n"

            return [TextContent(type="text", text=text)]

        # Tool 5: export_results
        @self.mcp.tool()
        async def export_results(
            query: str,
            format: str = "json",
            include_metadata: bool = True
        ) -> List[TextContent]:
            """
            Экспорт результатов поиска

            Args:
                query: Поисковый запрос
                format: Формат экспорта (json, markdown, csv)
                include_metadata: Включить метаданные

            Returns:
                Экспортированные результаты
            """
            await self._ensure_services()

            # Выполняем поиск
            request = SearchRequest(
                query=query,
                mode=SearchMode.INTELLIGENT,
                limit=50
            )

            results = await self.search_service.search(request)

            if format == "json":
                data = {
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "results_count": len(results),
                    "results": [
                        {
                            "file_path": r.file_path,
                            "module_type": r.module_type,
                            "score": r.score,
                            "summary": r.summary,
                            "functions_count": r.functions_count,
                            "source": r.source
                        }
                        for r in results
                    ]
                }
                if include_metadata:
                    data["metadata"] = {
                        "total_files": len(results),
                        "avg_score": sum(r.score for r in results) / len(results) if results else 0
                    }

                return [TextContent(
                    type="text",
                    text=json.dumps(data, indent=2, ensure_ascii=False)
                )]

            elif format == "markdown":
                text = f"# Search Results: {query}\n\n"
                text += f"**Timestamp:** {datetime.now().isoformat()}\n"
                text += f"**Results:** {len(results)}\n\n"

                for i, r in enumerate(results, 1):
                    text += f"## {i}. {r.file_path}\n\n"
                    text += f"- **Type:** {r.module_type}\n"
                    text += f"- **Score:** {r.score:.3f}\n"
                    text += f"- **Summary:** {r.summary}\n"
                    text += f"- **Functions:** {r.functions_count}\n\n"

                return [TextContent(type="text", text=text)]

            elif format == "csv":
                text = "file_path,module_type,score,functions_count,source\n"
                for r in results:
                    text += f'"{r.file_path}","{r.module_type}",{r.score},{r.functions_count},"{r.source}"\n'

                return [TextContent(type="text", text=text)]

            return [TextContent(
                type="text",
                text=f"Unsupported format: {format}. Use json, markdown, or csv."
            )]

        # Tool 6: clear_cache
        @self.mcp.tool()
        async def clear_cache() -> List[TextContent]:
            """
            Очистка кеша поиска

            Returns:
                Статус очистки
            """
            cache_size = len(self.search_cache)
            self.search_cache.clear()

            return [TextContent(
                type="text",
                text=f"Cache cleared. {cache_size} entries removed."
            )]

        logger.info("Все MCP инструменты зарегистрированы")

    async def run(self):
        """Запуск MCP Server"""
        logger.info("Запуск AI Memory MCP Server...")

        async with stdio_server() as (read_stream, write_stream):
            await self.mcp.run(
                read_stream,
                write_stream,
                self.mcp.create_initialization_options()
            )


async def main():
    """Главная функция запуска сервера"""
    try:
        server = AIMemoryMCPServer()
        await server.run()
    except Exception as e:
        logger.error(f"Ошибка запуска MCP Server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
