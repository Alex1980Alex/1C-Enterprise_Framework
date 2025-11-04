# Memory AI MCP Server - Обновление конфигурации Claude Desktop

## Проблема

Конфигурационный файл Claude Desktop может быть заблокирован, если приложение запущено. Для обновления timeout и добавления логирования необходимо выполнить следующие шаги:

## Решение

### Шаг 1: Закройте Claude Desktop

Полностью закройте приложение Claude Desktop, если оно запущено.

### Шаг 2: Обновите конфигурацию

Откройте файл конфигурации в текстовом редакторе:

```
C:\Users\AlexT\AppData\Roaming\Claude\claude_desktop_config.json
```

### Шаг 3: Найдите секцию memory-ai

Найдите секцию `"memory-ai"` в файле конфигурации. Она должна выглядеть примерно так:

```json
"memory-ai": {
  "command": "D:/1C-Enterprise_Framework/ai-memory-system/mcp/start-memory-ai-server.bat",
  "args": [],
  "cwd": "D:/1C-Enterprise_Framework/ai-memory-system/mcp",
  "env": {
    "PYTHONIOENCODING": "utf-8",
    "MCP_TIMEOUT": "30000",
    "MCP_MAX_RETRIES": "3"
  },
  "timeout": 30000
},
```

### Шаг 4: Замените на новую конфигурацию

Замените всю секцию `"memory-ai"` на следующую:

```json
"memory-ai": {
  "command": "D:/1C-Enterprise_Framework/ai-memory-system/mcp/start-memory-ai-server.bat",
  "args": [],
  "cwd": "D:/1C-Enterprise_Framework/ai-memory-system/mcp",
  "env": {
    "PYTHONIOENCODING": "utf-8",
    "MCP_TIMEOUT": "60000",
    "MCP_MAX_RETRIES": "3",
    "MCP_DEBUG": "true",
    "MCP_LOG_FILE": "D:/1C-Enterprise_Framework/cache/memory-ai-mcp.log"
  },
  "timeout": 60000
},
```

### Шаг 5: Сохраните и проверьте

1. Сохраните файл
2. Убедитесь, что JSON-синтаксис корректен (можно использовать онлайн-валидатор JSON)
3. Запустите Claude Desktop
4. Проверьте, что MCP сервер memory-ai загружается без ошибок

## Изменения в конфигурации

### Увеличенный timeout

- **Было:** `30000` (30 секунд)
- **Стало:** `60000` (60 секунд)

Это даёт серверу больше времени на инициализацию, особенно при первом запуске или при медленном подключении к базе данных.

### Добавлено логирование

- `MCP_DEBUG`: Включает расширенное логирование
- `MCP_LOG_FILE`: Путь к файлу логов

Логи будут сохраняться в:
```
D:\1C-Enterprise_Framework\cache\memory-ai-mcp.log
```

## Проверка работы

### Просмотр логов

Откройте файл логов, чтобы увидеть работу сервера:

```batch
type D:\1C-Enterprise_Framework\cache\memory-ai-mcp.log
```

### Тестирование инициализации

Запустите тестовый скрипт:

```batch
cd D:\1C-Enterprise_Framework\ai-memory-system\mcp
test-initialization.bat
```

Этот скрипт проверит:
- ✓ Установку Python
- ✓ Наличие необходимых модулей (psycopg2, mcp, qdrant_client)
- ✓ Импорт сервисов
- ✓ Подключение к PostgreSQL
- ✓ Подключение к Qdrant

## Требования для работы

### PostgreSQL/TimescaleDB

Сервер требует подключение к PostgreSQL:
- **Host:** localhost
- **Port:** 5432
- **Database:** ai_memory
- **User:** ai_user
- **Password:** ai_memory_secure_2025

### Qdrant

Сервер требует подключение к Qdrant:
- **Host:** localhost
- **Port:** 6333
- **Collection:** conversation_memory

## Устранение проблем

### Сервер не запускается

1. Проверьте логи в `cache/memory-ai-mcp.log`
2. Запустите `test-initialization.bat` для диагностики
3. Убедитесь, что PostgreSQL и Qdrant запущены

### Timeout ошибки

Если timeout всё ещё недостаточен, можно увеличить до 120000 (2 минуты):

```json
"timeout": 120000
```

### Проблемы с подключением к БД

Проверьте, что TimescaleDB запущен:

```batch
docker-compose ps
```

Если не запущен:

```batch
docker-compose up -d
```

## Backup конфигурации

Резервная копия конфигурации сохранена в:
```
C:\Users\AlexT\AppData\Roaming\Claude\claude_desktop_config.json.backup
```

В случае проблем можно восстановить из backup:

```batch
copy "C:\Users\AlexT\AppData\Roaming\Claude\claude_desktop_config.json.backup" "C:\Users\AlexT\AppData\Roaming\Claude\claude_desktop_config.json"
```

## Дополнительная информация

- [MCP Protocol Documentation](https://docs.mcp.com)
- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [TimescaleDB Documentation](https://docs.timescale.com)
- [Qdrant Documentation](https://qdrant.tech/documentation)
