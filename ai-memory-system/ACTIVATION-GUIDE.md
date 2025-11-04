# Активация Memory-AI MCP Server в Claude Desktop

## Статус компонентов ✅

Все компоненты проверены и работают:
- ✅ **TimescaleDB (PostgreSQL)** - База данных для хранения разговоров
  - Контейнер: `1c-timescaledb` (healthy)
  - Порт: 5432
  - База: `ai_memory`
  - Таблицы: conversations, messages, message_entities

- ✅ **Qdrant** - Векторная база данных для semantic search
  - Контейнер: `1c-qdrant` (running)
  - Порты: 6333, 6334
  - Коллекция: `conversation_memory`

- ✅ **Python зависимости** - Все установлены
  - mcp >= 0.9.0
  - psycopg2-binary >= 2.9.9
  - qdrant-client >= 1.7.0
  - asyncpg, ollama, httpx

- ✅ **MCP Server конфигурация** - Добавлена в Claude Desktop config

## Шаги активации

### 1. Проверить Docker контейнеры

Убедитесь что контейнеры запущены:

```bash
docker ps | grep -E "timescale|qdrant"
```

Если контейнеры не запущены, запустите их:

```bash
cd D:/1C-Enterprise_Framework/ai-memory-system/docker
docker-compose up -d
```

### 2. Закрыть Claude Desktop полностью

**ВАЖНО:** Нужно полностью закрыть приложение:
- Закройте все окна Claude Desktop
- Проверьте в Task Manager что процесс `Claude.exe` завершен
- Или выполните: `taskkill /F /IM Claude.exe`

### 3. Перезапустить Claude Desktop

Запустите Claude Desktop заново. При старте загрузятся все MCP серверы, включая memory-ai.

### 4. Проверить активацию

После запуска Claude Desktop выполните в чате:

```
Проверь доступность memory-ai MCP сервера.
Используй команду start_memory_session для инициализации новой сессии памяти.
```

Или проверьте наличие следующих tools:
- `mcp__memory-ai__start_memory_session`
- `mcp__memory-ai__save_conversation_fact`
- `mcp__memory-ai__search_memory`
- `mcp__memory-ai__get_session_context`
- `mcp__memory-ai__get_project_summary`
- `mcp__memory-ai__get_important_messages`

## Проверка логов

### Лог файл MCP сервера

```bash
cat D:/1C-Enterprise_Framework/cache/memory-ai-mcp.log
```

Успешный запуск должен содержать:
```
Starting Memory AI MCP Server
Database: ai_memory@localhost
Qdrant: localhost:6333
```

### Docker логи

```bash
# TimescaleDB
docker logs 1c-timescaledb --tail 20

# Qdrant
docker logs 1c-qdrant --tail 20
```

## Использование Memory-AI

### Инициализация сессии

```
start_memory_session с проектом "1C-Enterprise_Framework"
```

### Сохранение важной информации

```
save_conversation_fact: "Важная информация о проекте..."
importance: 0.8
```

### Поиск в памяти

```
search_memory: "поиск по ключевым словам"
limit: 10
```

### Получение контекста сессии

```
get_session_context для текущей сессии
```

## Troubleshooting

### Memory-AI не отвечает

1. Проверьте Docker контейнеры:
```bash
docker ps -a | grep -E "timescale|qdrant"
docker logs 1c-timescaledb
docker logs 1c-qdrant
```

2. Проверьте лог MCP сервера:
```bash
tail -50 D:/1C-Enterprise_Framework/cache/memory-ai-mcp.log
```

3. Перезапустите контейнеры:
```bash
cd D:/1C-Enterprise_Framework/ai-memory-system/docker
docker-compose restart
```

4. Полностью перезапустите Claude Desktop

### База данных не отвечает

Проверьте подключение:
```bash
docker exec 1c-timescaledb psql -U ai_user -d ai_memory -c "SELECT COUNT(*) FROM conversations;"
```

Если ошибка - пересоздайте контейнер:
```bash
docker-compose down
docker-compose up -d
```

### Qdrant не отвечает

Проверьте:
```bash
curl http://localhost:6333/healthz
curl http://localhost:6333/collections
```

## Автоматический запуск Docker при старте Windows

Создайте задачу в Task Scheduler:
1. Откройте Task Scheduler
2. Создайте новую задачу
3. Триггер: At startup
4. Действие: Start program
   - Program: `docker-compose`
   - Arguments: `up -d`
   - Start in: `D:\1C-Enterprise_Framework\ai-memory-system\docker`

## Полезные команды

```bash
# Проверка статуса всех компонентов
cd D:/1C-Enterprise_Framework/ai-memory-system/mcp
python test-memory-ai-simple.py

# Просмотр структуры БД
docker exec 1c-timescaledb psql -U ai_user -d ai_memory -c "\dt"

# Количество сохраненных разговоров
docker exec 1c-timescaledb psql -U ai_user -d ai_memory -c "SELECT COUNT(*) FROM conversations;"

# Количество сообщений
docker exec 1c-timescaledb psql -U ai_user -d ai_memory -c "SELECT COUNT(*) FROM messages;"

# Проверка Qdrant коллекций
curl http://localhost:6333/collections
```

## Дополнительная информация

- Конфигурация Claude Desktop: `C:/Users/AlexT/AppData/Roaming/Claude/claude_desktop_config.json`
- MCP Server код: `D:/1C-Enterprise_Framework/ai-memory-system/mcp/memory_server.py`
- Docker конфигурация: `D:/1C-Enterprise_Framework/ai-memory-system/docker/docker-compose.yml`
- Сервисы Python: `D:/1C-Enterprise_Framework/ai-memory-system/services/`

## Контакты и поддержка

- GitHub Issues: [1C-Enterprise_Framework Issues](https://github.com/yourusername/1C-Enterprise_Framework/issues)
- Документация MCP: https://modelcontextprotocol.io
- Документация Qdrant: https://qdrant.tech/documentation/
- Документация TimescaleDB: https://docs.timescale.com/
