# Memory AI MCP Server - Lazy Initialization Fix

## Проблема

Оригинальный `memory_server.py` инициализировал базы данных (PostgreSQL + Qdrant) на глобальном уровне при импорте модуля:

```python
# memory_server.py - ПРОБЛЕМНАЯ версия
storage = ConversationStorage(DB_CONFIG)  # 20-30 секунд
vectorizer = MessageVectorization(...)     # 5-10 секунд
```

**Результат**:
- Запуск MCP сервера занимал 30+ секунд
- Claude Code получал timeout при подключении
- Статус: `✗ Failed to connect`

## Решение

В `memory_server_fixed.py` реализована **lazy initialization** (ленивая инициализация):

```python
# memory_server_fixed.py - ИСПРАВЛЕННАЯ версия
_services = None

def get_services():
    """
    Lazy initialization of database services.
    This allows MCP server to start quickly (< 1 second)
    and only connect to DB when first tool is called.
    """
    global _services
    if _services is None:
        logger.info("Initializing database services (lazy load)...")
        storage = ConversationStorage(DB_CONFIG)
        vectorizer = MessageVectorization(
            qdrant_host="localhost",
            qdrant_port=6333,
            collection_name="conversation_memory"
        )
        restoration = ContextRestoration(storage, vectorizer)
        _services = {
            'storage': storage,
            'vectorizer': vectorizer,
            'restoration': restoration
        }
        logger.info("Database services initialized successfully")
    return _services
```

**Использование в tool handlers**:

```python
@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    # Initialize services lazily on first tool call
    services = get_services()
    storage = services['storage']
    vectorizer = services['vectorizer']
    restoration = services['restoration']
    # ... handle tool call
```

**Результат**:
- ✅ Запуск сервера < 1 секунды
- ✅ Подключение к Claude Code успешно: `✓ Connected`
- ✅ БД инициализируется только при первом вызове tool
- ✅ Все tools работают корректно

## Конфигурация Claude Code

```bash
claude mcp add --transport stdio memory-ai \
  -e PYTHONIOENCODING=utf-8 \
  -e "PYTHONPATH=D:/1C-Enterprise_Framework/ai-memory-system/services" \
  -- "C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" \
  D:/1C-Enterprise_Framework/ai-memory-system/mcp/memory_server_fixed.py
```

## Доступные Tools

- `mcp__memory-ai__save_conversation_fact` - Сохранить факт из разговора
- `mcp__memory-ai__search_memory` - Поиск в долгосрочной памяти
- `mcp__memory-ai__get_session_context` - Получить контекст сессии
- `mcp__memory-ai__start_memory_session` - Начать новую сессию
- `mcp__memory-ai__get_project_summary` - Получить сводку проекта
- `mcp__memory-ai__get_important_messages` - Получить важные сообщения

## Зависимости

- PostgreSQL/TimescaleDB на порту 5432
- Qdrant на порту 6333
- Python 3.13+
- Зависимости из ai-memory-system/services:
  - conversation_storage.py
  - message_vectorization.py
  - context_restoration.py

## Проверка статуса

```bash
# Проверить подключение
claude mcp list | grep memory-ai

# Ожидаемый результат:
# memory-ai: ... - ✓ Connected
```

---

**Дата создания**: 2025-10-31
**Автор**: Claude Code
**Версия**: 1.0
