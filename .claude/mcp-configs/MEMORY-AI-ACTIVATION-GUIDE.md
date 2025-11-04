# Memory-AI MCP Tools Activation Guide

## Проблема
Инструменты Memory-AI (включая `get_session_context`) были настроены, но не появлялись в Claude Code CLI.

## Корневая причина
Bat-файл запускал старую версию сервера (`memory_server.py`) вместо исправленной (`memory_server_fixed.py`).

## Исправления (выполнено 2025-10-31)

### 1. Обновлен start-memory-ai-server.bat
```batch
# Было:
"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" "%SCRIPT_DIR%\memory_server.py"

# Стало:
"C:\Users\AlexT\AppData\Local\Programs\Python\Python313\python.exe" "%SCRIPT_DIR%\memory_server_fixed.py"
```

### 2. Обновлена конфигурация Claude Desktop
Файл: `C:/Users/AlexT/AppData/Roaming/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "memory-ai": {
      "command": "C:/Users/AlexT/AppData/Local/Programs/Python/Python313/python.exe",
      "args": [
        "D:/1C-Enterprise_Framework/ai-memory-system/mcp/memory_server_fixed.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "D:/1C-Enterprise_Framework/ai-memory-system/services"
      },
      "timeout": 60000
    }
  }
}
```

## Доступные инструменты (6 штук)

После перезапуска Claude приложений будут доступны:

1. **mcp__memory-ai__save_conversation_fact** - Сохранение важного факта в долгосрочную память
2. **mcp__memory-ai__search_memory** - Семантический поиск по памяти
3. **mcp__memory-ai__get_session_context** - Получение контекста сессии (ваш запрошенный инструмент!)
4. **mcp__memory-ai__start_memory_session** - Начало новой сессии памяти
5. **mcp__memory-ai__get_project_summary** - Сводка по проекту
6. **mcp__memory-ai__get_important_messages** - Получение важных сообщений

## Инструкции по активации

### Для Claude Desktop
1. Закройте Claude Desktop полностью (проверьте в Task Manager)
2. Перезапустите Claude Desktop
3. Инструменты появятся автоматически с префиксом `mcp__memory-ai__*`

### Для Claude Code CLI
1. Завершите текущую сессию Claude Code (`exit` или Ctrl+C)
2. Запустите новую сессию
3. Проверьте доступность: `claude mcp list` должен показать memory-ai
4. Попробуйте вызвать инструмент (команда будет доступна автоматически)

## Проверка работоспособности

### Тест 1: Проверка подключения
```bash
claude mcp list
```
Должен показать `memory-ai: ✓ Connected`

### Тест 2: Вызов инструмента
В Claude Code попробуйте:
```
Используй инструмент mcp__memory-ai__get_project_summary
```

### Тест 3: Проверка логов
```bash
type D:\1C-Enterprise_Framework\cache\memory-ai-mcp.log
```

## Различия между Claude Desktop и Claude Code

### Claude Desktop
- ✅ Все 6 инструментов memory-ai доступны
- ✅ Базовый Memory MCP (@modelcontextprotocol/server-memory) доступен
- Использует: `claude_desktop_config.json`

### Claude Code CLI
- ❓ Memory-AI инструменты (требуется проверка после перезапуска)
- ✅ Базовый Memory MCP доступен (`mcp__memory__*`)
- Использует: Собственную систему конфигурации MCP

## Архитектура Memory-AI

```
┌─────────────────────────────────────────┐
│     Claude Desktop / Claude Code        │
└──────────────┬──────────────────────────┘
               │
               ├─── MCP Protocol (stdio)
               │
┌──────────────▼──────────────────────────┐
│     memory_server_fixed.py              │
│  (MCP Server with lazy initialization)  │
└──────────────┬──────────────────────────┘
               │
               ├─── ConversationStorage
               ├─── MessageVectorization
               └─── ContextRestoration
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   TimescaleDB   Qdrant    Ollama
   (PostgreSQL) (Vectors) (Embeddings)
```

## Troubleshooting

### Проблема: Инструменты не появляются
**Решение:**
1. Проверьте логи: `D:\1C-Enterprise_Framework\cache\memory-ai-mcp.log`
2. Убедитесь, что Docker контейнеры запущены: `docker ps`
3. Проверьте подключение к БД: `python ai-memory-system/mcp/test_memory_ai_simple.py`

### Проблема: Ошибка при запуске сервера
**Решение:**
1. Проверьте Python версию: должна быть 3.13
2. Проверьте зависимости: все сервисы должны импортироваться
3. Проверьте PYTHONPATH: должен включать `ai-memory-system/services`

### Проблема: Сервер подключается, но инструменты не работают
**Решение:**
1. Проверьте, что используется `memory_server_fixed.py`, а не `memory_server.py`
2. Проверьте логи на наличие ошибок инициализации
3. Проверьте доступность БД компонентов (TimescaleDB, Qdrant, Ollama)

## Полезные команды

```bash
# Проверка статуса MCP серверов
claude mcp list

# Проверка Docker контейнеров
docker ps

# Проверка логов Memory-AI
type D:\1C-Enterprise_Framework\cache\memory-ai-mcp.log

# Тест базовых компонентов
python D:\1C-Enterprise_Framework\ai-memory-system\mcp\test_memory_ai_simple.py

# Проверка Memory Knowledge Graph
# (использует стандартный Memory MCP, который точно работает)
```

## Статус
- ✅ Конфигурация обновлена
- ✅ Bat-файл исправлен
- ⏳ Требуется перезапуск для применения изменений
- ⏳ Требуется тестирование после перезапуска

---
*Обновлено: 2025-10-31*
*Версия: 1.0*
