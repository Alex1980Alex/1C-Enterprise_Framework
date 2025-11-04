# Альтернативные способы настройки Neo4j для MCP сервера

## Проблема
Не можем найти правильный пароль Neo4j для MCP сервера.

## Решение 1: Использовать MCP сервер БЕЗ Neo4j (Рекомендуется для начала)

MCP сервер может работать без Neo4j! Neo4j нужен только для инструмента `analyze_graph`.

### Шаг 1: Обновите конфигурацию Claude Code

Откройте файл: `%APPDATA%\Claude\claude_desktop_config.json`

Найдите секцию `ai-memory-system` и **удалите** строку с `NEO4J_PASSWORD`:

```json
{
  "mcpServers": {
    "ai-memory-system": {
      "command": "python",
      "args": [
        "D:/1C-Enterprise_Framework/ai-memory-system/mcp_server/server_fastmcp.py"
      ],
      "cwd": "D:/1C-Enterprise_Framework/ai-memory-system",
      "env": {
        "PYTHONPATH": "D:/1C-Enterprise_Framework/ai-memory-system"
      },
      "description": "AI Memory System for BSL code analysis",
      "timeout": 30000
    }
  }
}
```

### Шаг 2: Обновите MCP сервер для работы без Neo4j

Откройте файл: `D:/1C-Enterprise_Framework/ai-memory-system/mcp_server/server_fastmcp.py`

Найдите строки 74-77:
```python
# Neo4j Service
neo4j = Neo4jService(
    uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    user=os.getenv("NEO4J_USER", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "your_password")
)
```

Замените на:
```python
# Neo4j Service (optional - disabled if password not set)
neo4j = None
if os.getenv("NEO4J_PASSWORD"):
    try:
        neo4j = Neo4jService(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD")
        )
        logger.info("✓ Neo4j Service connected")
    except Exception as e:
        logger.warning(f"Neo4j not available: {e}")
        neo4j = None
else:
    logger.info("Neo4j disabled (no password set)")
```

### Шаг 3: Перезапустите Claude Code

1. Закройте все окна Claude Code
2. Запустите заново

### Шаг 4: Проверьте работу

В Claude Code попробуйте:
```
Use search_bsl_code to search for "Справочники"
```

**Доступные инструменты БЕЗ Neo4j**:
- ✓ `search_bsl_code` - работает
- ✓ `intelligent_search` - работает
- ✓ `get_search_history` - работает
- ✓ `clear_cache` - работает
- ✗ `analyze_graph` - требует Neo4j

## Решение 2: Узнать пароль через Neo4j Desktop

### Шаг 1: Откройте Neo4j Desktop

Если Neo4j установлен через Neo4j Desktop:

1. Запустите Neo4j Desktop
2. Выберите вашу базу данных
3. Нажмите на **три точки** (⋮) справа от базы
4. Выберите **Settings** или **Manage**
5. Там должен быть пароль

### Шаг 2: Используйте найденный пароль

После того как нашли пароль:

**Вариант A - Через переменную окружения (временно)**:
```powershell
$env:NEO4J_PASSWORD="найденный_пароль"
```

**Вариант B - В конфигурации Claude Code**:
```json
"env": {
  "PYTHONPATH": "D:/1C-Enterprise_Framework/ai-memory-system",
  "NEO4J_PASSWORD": "найденный_пароль"
}
```

## Решение 3: Сброс пароля Neo4j Desktop

### Через Neo4j Desktop (самый простой):

1. Откройте Neo4j Desktop
2. **Остановите** базу данных (кнопка Stop)
3. Выберите **Settings/Manage**
4. Найдите опцию **Reset Password** или **Change Password**
5. Установите новый пароль (например, `123456`)
6. **Запустите** базу данных заново

### Через файловую систему:

Если Neo4j Desktop не помогает:

1. **Остановите Neo4j Desktop полностью**
2. Найдите файл auth:
   ```
   %LOCALAPPDATA%\Neo4j\Relate\Data\dbmss\dbms-*\data\dbms\auth
   ```
3. Удалите файл `auth`
4. Запустите Neo4j Desktop
5. Пароль сбросится на `neo4j/neo4j`
6. При первом входе установите новый пароль

## Решение 4: Установка нового Neo4j с известным паролем

Если ничего не помогло:

### Через Docker (рекомендуется):

```bash
docker run -d \
  --name neo4j-mcp \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/mcp12345 \
  neo4j:latest
```

Пароль будет: `mcp12345`

### Через Neo4j Desktop (новая база):

1. Откройте Neo4j Desktop
2. Создайте **новую** базу данных
3. При создании установите пароль: `mcp12345`
4. Запустите новую базу

## Рекомендация

**Начните с Решения 1** - запустите MCP сервер без Neo4j.

Это позволит вам:
- ✓ Сразу начать использовать поиск по коду
- ✓ Проверить, что MCP сервер работает
- ✓ Использовать 4 из 5 инструментов

Позже, когда найдете пароль или установите Neo4j с известным паролем, добавите поддержку графового анализа.

## Проверка после настройки

### Тест без Neo4j:
```bash
cd D:\1C-Enterprise_Framework\ai-memory-system
set PYTHONPATH=D:\1C-Enterprise_Framework\ai-memory-system
python mcp_server\server_fastmcp.py
```

Должны увидеть:
```
INFO:__main__:=== Starting AI Memory MCP Server (FastMCP) ===
INFO:__main__:Neo4j disabled (no password set)
INFO:__main__:✓ LLM Service
INFO:__main__:✓ Qdrant Vector Store
```

### Тест с Neo4j:
```bash
cd D:\1C-Enterprise_Framework\ai-memory-system
set NEO4J_PASSWORD=ваш_пароль
python mcp_server\server_fastmcp.py
```

Должны увидеть:
```
INFO:__main__:=== Starting AI Memory MCP Server (FastMCP) ===
INFO:__main__:✓ Neo4j Service connected
INFO:__main__:✓ LLM Service
INFO:__main__:✓ Qdrant Vector Store
```

## Помощь

Если нужна помощь:
1. Проверьте, запущен ли Neo4j: http://localhost:7474
2. Попробуйте войти через браузер с разными паролями
3. Используйте Решение 1 (без Neo4j) для начала работы
