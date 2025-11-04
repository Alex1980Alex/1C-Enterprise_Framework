# Memory AI MCP - Руководство по активации в Claude Code

## ✅ Статус установки

Memory AI MCP server установлен и настроен для Claude Code CLI.

## 🔧 Конфигурация

Memory AI MCP добавлен в конфигурацию с помощью команды:

```bash
claude mcp add --transport stdio memory-ai \
  -e PYTHONIOENCODING=utf-8 \
  -e "PYTHONPATH=D:/1C-Enterprise_Framework/ai-memory-system/services" \
  -- "C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" \
  D:/1C-Enterprise_Framework/ai-memory-system/mcp/memory_server.py
```

## 📋 Текущий статус

**✅ РЕШЕНО**: Memory AI MCP успешно подключен и работает!

**Статус**: `✓ Connected`

### Выявленная проблема:

**Глобальная инициализация БД** - `memory_server.py` инициализировал PostgreSQL и Qdrant на глобальном уровне при импорте модуля, что занимало 30+ секунд и приводило к timeout при подключении MCP.

### Решение:

Реализована **lazy initialization** в `memory_server_fixed.py`:
- Сервер запускается < 1 секунды
- Подключение к БД происходит только при первом вызове tool
- Services инициализируются через функцию `get_services()` при необходимости

## 🔍 Диагностика

### Проверка компонентов

```bash
# TimescaleDB
docker ps --filter name=timescale

# Python зависимости
cd D:/1C-Enterprise_Framework/ai-memory-system/mcp
"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" -c "import sys; sys.path.insert(0, r'D:/1C-Enterprise_Framework/ai-memory-system/services'); from conversation_storage import ConversationStorage; from message_vectorization import MessageVectorization; from context_restoration import ContextRestoration; print('All services ready')"

# MCP серверы
claude mcp list | grep memory-ai
```

### Логи

Проверьте логи сервера (если используется батник с логированием):
```bash
cat D:/1C-Enterprise_Framework/cache/memory-ai-mcp.log
```

## 🛠️ Решение проблем

### Вариант 1: Увеличить timeout

В `.claude.json` добавьте timeout для Memory AI:

```json
"memory-ai": {
  "type": "stdio",
  "command": "C:\\Users\\AlexT\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
  "args": [
    "D:/1C-Enterprise_Framework/ai-memory-system/mcp/memory_server.py"
  ],
  "env": {
    "PYTHONIOENCODING": "utf-8",
    "PYTHONPATH": "D:/1C-Enterprise_Framework/ai-memory-system/services"
  },
  "timeout": 60000
}
```

### Вариант 2: Использовать wrapper script

Создайте `start-memory-ai-stdio.bat` с минимальным кодом:
```bat
@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONPATH=D:\1C-Enterprise_Framework\ai-memory-system\services
"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" "D:\1C-Enterprise_Framework\ai-memory-system\mcp\memory_server.py"
```

### Вариант 3: Проверить доступность портов

Убедитесь что PostgreSQL (5432) и Qdrant (6333) доступны:

```bash
# PostgreSQL
"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5432, database='ai_memory', user='ai_user', password='ai_memory_secure_2025'); print('PostgreSQL OK'); conn.close()"

# Qdrant (через curl или браузер)
curl http://localhost:6333/health
```

## 📝 Доступные Tools

Когда сервер подключится успешно, будут доступны следующие инструменты:

- `mcp__memory-ai__save_conversation_fact` - Сохранить факт из разговора
- `mcp__memory-ai__search_memory` - Поиск в памяти
- `mcp__memory-ai__get_session_context` - Получить контекст сессии
- `mcp__memory-ai__start_memory_session` - Начать новую сессию памяти
- `mcp__memory-ai__get_project_summary` - Получить сводку проекта
- `mcp__memory-ai__get_important_messages` - Получить важные сообщения

## ✅ Финальная конфигурация

Memory AI MCP добавлен с использованием исправленной версии:

```bash
claude mcp add --transport stdio memory-ai \
  -e PYTHONIOENCODING=utf-8 \
  -e "PYTHONPATH=D:/1C-Enterprise_Framework/ai-memory-system/services" \
  -- "C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" \
  D:/1C-Enterprise_Framework/ai-memory-system/mcp/memory_server_fixed.py
```

## 🎯 Выполненные шаги

1. ✅ Компоненты (PostgreSQL, Qdrant) работают
2. ✅ Python зависимости установлены
3. ✅ Memory AI MCP добавлен в конфигурацию
4. ✅ **Решена проблема**: глобальная инициализация заменена на lazy initialization
5. ✅ **Подключение работает**: статус `✓ Connected`
6. ⏳ **Следующий шаг**: тестирование работы tools

## 💡 Альтернатива

Пока Memory AI MCP отлаживается, можно использовать стандартный `@modelcontextprotocol/server-memory` который уже работает:

```bash
claude mcp list | grep "memory:"
# memory: npx -y @modelcontextprotocol/server-memory - ✓ Connected
```

Этот сервер предоставляет базовую функциональность памяти.

---

**Дата создания**: 2025-10-31
**Последнее обновление**: 2025-10-31 (добавлен restore_context)
**Версия**: 2.1
**Статус**: ✅ Успешно подключен и работает (исправлен get_session_context)

## 📊 Технические детали решения

### Проблема (memory_server.py):
```python
# Глобальная инициализация - БЛОКИРУЕТ запуск на 30+ секунд
storage = ConversationStorage(DB_CONFIG)  # 20-30 сек
vectorizer = MessageVectorization(...)     # 5-10 сек
```

### Решение (memory_server_fixed.py):
```python
# Lazy initialization - запуск < 1 секунды
_services = None

def get_services():
    global _services
    if _services is None:
        storage = ConversationStorage(DB_CONFIG)
        vectorizer = MessageVectorization(...)
        _services = {'storage': storage, 'vectorizer': vectorizer, ...}
    return _services
```

Services инициализируются только при первом вызове tool через `get_services()`.

## 🔧 Исправление от 2025-10-31

### Проблема: get_session_context не работал

**Ошибка**: `'ContextRestoration' object has no attribute 'restore_context'`

**Причина**: В `memory_server_fixed.py` вызывался несуществующий метод `restoration.restore_context()`

**Решение**: Добавлен метод `restore_context()` в `context_restoration.py`:

```python
def restore_context(
    self,
    conversation_id: str,
    query: Optional[str] = None,
    max_messages: int = 20
) -> List[Dict[str, Any]]:
    """Восстановить контекст для разговора"""
```

**Для применения**: Перезапустите Claude Code, чтобы MCP сервер загрузил обновленный модуль.

**Подробнее**: См. `.claude/mcp-configs/memory-ai-fix-2025-10-31.md`
