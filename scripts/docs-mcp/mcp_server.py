#!/usr/bin/env python3
"""
MCP сервер для гибридного поиска по документации фреймворка 1C
Интеграция с Claude Code через Model Context Protocol
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Добавляем текущую директорию в путь для импорта
sys.path.append(str(Path(__file__).parent))

try:
    from mcp.server import Server
    from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
    from hybrid_search_engine import HybridSearchEngine, SearchResult
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("[ERROR] MCP не установлен. Установите: pip install mcp")

class FrameworkDocsMCPServer:
    """MCP сервер для документации фреймворка"""
    
    def __init__(self):
        """Инициализация сервера"""
        self.search_engine = HybridSearchEngine()
        self.server = Server("1c-framework-docs") if MCP_AVAILABLE else None
        
        # Получаем путь к документации из переменной окружения или используем абсолютный путь
        docs_root = os.getenv('DOCS_ROOT')
        if docs_root:
            self.docs_path = Path(docs_root)
        else:
            # Абсолютный путь к документации
            self.docs_path = Path("D:/1C-Enterprise_Framework/Документация по фреймворку")
        
        if MCP_AVAILABLE:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков MCP"""
        if not self.server:
            return
        
        # Список доступных инструментов
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """Список доступных инструментов поиска"""
            return [
                Tool(
                    name="search_docs",
                    description="Поиск по документации фреймворка 1C. Поддерживает полнотекстовый, семантический и гибридный поиск.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Поисковый запрос на русском или английском языке"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Максимальное количество результатов (по умолчанию: 5)",
                                "default": 5,
                                "minimum": 1,
                                "maximum": 20
                            },
                            "search_type": {
                                "type": "string",
                                "description": "Тип поиска: fulltext, semantic, hybrid",
                                "enum": ["fulltext", "semantic", "hybrid"],
                                "default": "hybrid"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_document",
                    description="Получить полное содержимое документа по ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_id": {
                                "type": "string",
                                "description": "ID документа для получения"
                            }
                        },
                        "required": ["document_id"]
                    }
                ),
                Tool(
                    name="reindex_docs",
                    description="Переиндексация всей документации фреймворка",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "force": {
                                "type": "boolean",
                                "description": "Принудительная переиндексация всех документов",
                                "default": False
                            }
                        }
                    }
                ),
                Tool(
                    name="get_stats",
                    description="Получить статистику поискового индекса",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        # Обработчик поиска документов
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Обработка вызовов инструментов"""
            
            if name == "search_docs":
                return await self._handle_search(arguments)
            elif name == "get_document":
                return await self._handle_get_document(arguments)
            elif name == "reindex_docs":
                return await self._handle_reindex(arguments)
            elif name == "get_stats":
                return await self._handle_get_stats(arguments)
            else:
                return [TextContent(
                    type="text",
                    text=f"[ERROR] Неизвестный инструмент: {name}"
                )]
    
    async def _handle_search(self, args: Dict[str, Any]) -> List[TextContent]:
        """Обработка поиска по документации"""
        query = args.get("query", "")
        limit = args.get("limit", 5)
        search_type = args.get("search_type", "hybrid")
        
        if not query.strip():
            return [TextContent(
                type="text",
                text="[ERROR] Пустой поисковый запрос"
            )]
        
        try:
            # Выполняем поиск
            results = self.search_engine.search(query, limit=limit, search_type=search_type)
            
            if not results:
                return [TextContent(
                    type="text",
                    text=f"[SEARCH] По запросу '{query}' ничего не найдено."
                )]
            
            # Форматируем результаты
            response_text = f"[SEARCH] **Результаты поиска по запросу:** '{query}'\n"
            response_text += f"[STATS] **Тип поиска:** {search_type}\n"
            response_text += f"[LIST] **Найдено:** {len(results)} результат(ов)\n\n"
            
            for i, result in enumerate(results, 1):
                doc = result.document
                score = result.score
                match_type = result.match_type
                snippet = result.snippet
                
                response_text += f"## {i}. {doc.title}\n"
                response_text += f"**[FOLDER] Файл:** `{Path(doc.path).name}`\n"
                response_text += f"**[TARGET] Релевантность:** {score:.3f} ({match_type})\n"
                response_text += f"**📏 Размер:** {doc.size} символов\n"
                response_text += f"**🏷️ Теги:** {', '.join(doc.tags) if doc.tags else 'нет'}\n"
                response_text += f"**[NOTE] Фрагмент:**\n```\n{snippet}\n```\n"
                response_text += f"**🆔 ID:** `{doc.id}`\n\n"
                response_text += "---\n\n"
            
            response_text += f"[INFO] **Совет:** Используйте `get_document` с ID для получения полного содержимого.\n"
            
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"[ERROR] Ошибка поиска: {str(e)}"
            )]
    
    async def _handle_get_document(self, args: Dict[str, Any]) -> List[TextContent]:
        """Получение полного содержимого документа"""
        document_id = args.get("document_id", "")
        
        if not document_id:
            return [TextContent(
                type="text",
                text="[ERROR] Не указан ID документа"
            )]
        
        try:
            # Поиск документа по ID
            import sqlite3
            conn = sqlite3.connect(self.search_engine.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT title, path, content, size, modified, tags, doc_type
                FROM documents 
                WHERE id = ?
            """, (document_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return [TextContent(
                    type="text",
                    text=f"[ERROR] Документ с ID '{document_id}' не найден"
                )]
            
            title, path, content, size, modified, tags, doc_type = result
            tags_list = json.loads(tags) if tags else []
            
            response_text = f"# [FILE] {title}\n\n"
            response_text += f"**[FOLDER] Путь:** `{path}`\n"
            response_text += f"**📏 Размер:** {size} символов\n"
            response_text += f"**📅 Изменен:** {modified}\n"
            response_text += f"**🏷️ Теги:** {', '.join(tags_list) if tags_list else 'нет'}\n"
            response_text += f"**[LIST] Тип:** {doc_type}\n\n"
            response_text += "---\n\n"
            response_text += "## 📖 Содержимое\n\n"
            response_text += content
            
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"[ERROR] Ошибка получения документа: {str(e)}"
            )]
    
    async def _handle_reindex(self, args: Dict[str, Any]) -> List[TextContent]:
        """Переиндексация документации"""
        force = args.get("force", False)
        
        try:
            if not self.docs_path.exists():
                return [TextContent(
                    type="text",
                    text=f"[ERROR] Папка документации не найдена: {self.docs_path}"
                )]
            
            response_text = "[SYNC] **Переиндексация документации фреймворка**\n\n"
            
            indexed_count = 0
            skipped_count = 0
            error_count = 0
            
            # Индексируем все markdown файлы
            for md_file in self.docs_path.rglob("*.md"):
                try:
                    if self.search_engine.index_document(str(md_file)):
                        indexed_count += 1
                        response_text += f"[OK] {md_file.name}\n"
                    else:
                        skipped_count += 1
                        response_text += f"⏭️ {md_file.name} (актуален)\n"
                except Exception as e:
                    error_count += 1
                    response_text += f"[ERROR] {md_file.name}: {e}\n"
            
            # Статистика
            response_text += f"\n[STATS] **Результаты индексации:**\n"
            response_text += f"- [OK] Проиндексировано: {indexed_count}\n"
            response_text += f"- ⏭️ Пропущено: {skipped_count}\n"
            response_text += f"- [ERROR] Ошибок: {error_count}\n"
            
            # Общая статистика индекса
            stats = self.search_engine.get_statistics()
            response_text += f"\n📈 **Статистика индекса:**\n"
            response_text += f"- [DOCS] Всего документов: {stats['total_documents']}\n"
            response_text += f"- 🧠 С эмбеддингами: {stats['documents_with_embeddings']}\n"
            response_text += f"- [SAVE] Размер: {stats['total_size_mb']} MB\n"
            
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"[ERROR] Ошибка переиндексации: {str(e)}"
            )]
    
    async def _handle_get_stats(self, args: Dict[str, Any]) -> List[TextContent]:
        """Получение статистики индекса"""
        try:
            stats = self.search_engine.get_statistics()
            
            response_text = "[STATS] **Статистика поискового индекса**\n\n"
            response_text += f"[DOCS] **Документы:**\n"
            response_text += f"- Всего: {stats['total_documents']}\n"
            response_text += f"- С эмбеддингами: {stats['documents_with_embeddings']}\n"
            response_text += f"- Уникальных тегов: {stats['unique_tags']}\n\n"
            
            response_text += f"[SAVE] **Размер:**\n"
            response_text += f"- Общий: {stats['total_size_mb']} MB\n"
            response_text += f"- Байт: {stats['total_size_bytes']:,}\n\n"
            
            response_text += f"[LIST] **Типы документов:**\n"
            for doc_type, count in stats['document_types'].items():
                response_text += f"- {doc_type}: {count}\n"
            
            response_text += f"\n🧠 **Эмбеддинги:**\n"
            response_text += f"- Включены: {'[OK]' if stats['embeddings_enabled'] else '[ERROR]'}\n"
            if stats['model_name']:
                response_text += f"- Модель: {stats['model_name']}\n"
            
            response_text += f"\n[CONFIG] **Возможности:**\n"
            response_text += f"- Полнотекстовый поиск: [OK] (SQLite FTS5)\n"
            response_text += f"- Семантический поиск: {'[OK]' if stats['embeddings_enabled'] else '[ERROR]'}\n"
            response_text += f"- Гибридный поиск: {'[OK]' if stats['embeddings_enabled'] else '[WARNING] (только FTS5)'}\n"
            
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"[ERROR] Ошибка получения статистики: {str(e)}"
            )]
    
    async def run(self):
        """Запуск MCP сервера"""
        if not MCP_AVAILABLE:
            print("[ERROR] MCP не доступен. Установите зависимости.")
            return
        
        print("[START] Запуск MCP сервера документации фреймворка 1C")
        print("[DOCS] Доступные инструменты:")
        print("  - search_docs: Поиск по документации")
        print("  - get_document: Получение полного документа")
        print("  - reindex_docs: Переиндексация")
        print("  - get_stats: Статистика индекса")
        print("\n[OK] Сервер готов к работе")
        
        # Автоматическая индексация при старте
        if self.docs_path.exists():
            print("[SYNC] Проверка индекса документации...")
            stats = self.search_engine.get_statistics()
            if stats['total_documents'] == 0:
                print("[DOCS] Первичная индексация документации...")
                for md_file in self.docs_path.rglob("*.md"):
                    self.search_engine.index_document(str(md_file))
                print("[OK] Индексация завершена")
        
        # Запуск сервера
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, 
                                 self.server.create_initialization_options())


async def main():
    """Главная функция"""
    server = FrameworkDocsMCPServer()
    await server.run()


if __name__ == "__main__":
    if not MCP_AVAILABLE:
        print("[ERROR] Для работы требуется установка MCP:")
        print("pip install mcp sentence-transformers")
        sys.exit(1)
    
    asyncio.run(main())