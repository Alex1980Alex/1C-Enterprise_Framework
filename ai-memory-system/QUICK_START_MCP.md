# Быстрый старт: Memory MCP Server для Claude Code

## Что это?

Memory MCP Server — это расширение для Claude Code, которое дает Claude AI долгосрочную память между сессиями. Claude сможет:
- Запоминать важную информацию из разговоров
- Находить релевантную информацию из прошлых сессий
- Восстанавливать контекст при продолжении работы
- Вести несколько проектов с раздельной памятью

---

## Шаг 1: Запустить необходимые сервисы

### Проверить Docker контейнеры

```bash
# Проверить что контейнеры запущены
docker ps | grep -E "timescale|qdrant"

# Если не запущены, запустить:
docker start 1c-timescaledb
docker start 1c-qdrant
```

### Проверить Ollama

```bash
# Проверить что Ollama запущен
curl http://localhost:11434/api/version

# Проверить что модель установлена
ollama list | grep nomic-embed-text

# Если модель не установлена:
ollama pull nomic-embed-text
```

---

## Шаг 2: Установить Python зависимости

```bash
cd D:/1C-Enterprise_Framework/ai-memory-system
pip install -r requirements.txt
```

---

## Шаг 3: Проверить что MCP сервер работает

```bash
cd D:/1C-Enterprise_Framework/ai-memory-system/mcp
python test_server_import.py
```

**Ожидаемый результат**:
```
Testing imports...
✅ MCP imports OK
✅ Service imports OK

Testing database connection...
✅ TimescaleDB connection OK

Testing Qdrant connection...
✅ Qdrant connection OK

Testing MCP Server initialization...
✅ MCP Server initialization OK

==================================================
All validation tests passed!
MCP server is ready to use.
==================================================
```

Если все тесты прошли успешно — переходите к Шагу 4.

**Если есть ошибки**, смотрите раздел Troubleshooting ниже.

---

## Шаг 4: Конфигурация уже добавлена ✅

Конфигурация Memory MCP Server **уже добавлена** в проект:

### Файл конфигурации
`.claude/mcp-configs/memory-config.json`:
```json
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": ["D:/1C-Enterprise_Framework/ai-memory-system/mcp/memory_server.py"],
      "env": {"PYTHONIOENCODING": "utf-8"}
    }
  }
}
```

### Разрешения
`.claude/settings.local.json` — уже содержит разрешения для всех 6 инструментов памяти:
- ✅ `mcp__memory__save_conversation_fact`
- ✅ `mcp__memory__search_memory`
- ✅ `mcp__memory__get_session_context`
- ✅ `mcp__memory__start_memory_session`
- ✅ `mcp__memory__get_project_summary`
- ✅ `mcp__memory__get_important_messages`

---

## Шаг 5: Перезапустить Claude Code (если он был запущен)

Если Claude Code уже был запущен, перезапустите его для применения новой конфигурации MCP.

---

## Шаг 6: Проверить что инструменты доступны

В Claude Code выполните команду:
```
/tools
```

Вы должны увидеть в списке инструменты памяти:
- `save_conversation_fact`
- `search_memory`
- `get_session_context`
- `start_memory_session`
- `get_project_summary`
- `get_important_messages`

---

## Шаг 7: Начать использовать!

### Пример 1: Начать новую сессию памяти

```
Пользователь: Claude, начни новую сессию памяти для проекта 1C-Enterprise_Framework

Claude: [Использует start_memory_session]
✅ Сессия памяти запущена
Session ID: session_20251031_123456
Project: 1C-Enterprise_Framework
```

### Пример 2: Сохранить важную информацию

```
Пользователь: Запомни, что BSL индексация использует Qdrant для векторного поиска

Claude: [Использует save_conversation_fact с importance=0.9]
✅ Сохранено в долгосрочную память
Importance: 0.9
```

### Пример 3: Найти информацию из прошлых разговоров

```
Пользователь: Как работала векторизация, которую мы обсуждали?

Claude: [Использует search_memory query="векторизация"]
🔍 Найдено 3 результата:

1. [0.840] Векторизация использует Ollama для создания embeddings...
2. [0.720] Qdrant хранит 768-dim vectors с COSINE distance...
3. [0.680] MessageVectorization сервис интегрирует Ollama и Qdrant...

На основе найденной информации: Векторизация работала следующим образом...
```

### Пример 4: Восстановить контекст при продолжении работы

```
Пользователь: Продолжим работу над системой памяти

Claude: [Использует get_session_context query="система памяти"]
📋 Контекст восстановлен:
- 15 messages из предыдущих сессий
- Semantic matches: векторизация, TimescaleDB, MCP integration
- Important: создание schema, тестирование сервисов, MCP server

Хорошо, давайте продолжим. В прошлый раз мы...
```

---

## Troubleshooting

### Ошибка: TimescaleDB connection failed

**Симптом**:
```
❌ TimescaleDB connection failed: could not connect to server
```

**Решение**:
```bash
# Запустить контейнер
docker start 1c-timescaledb

# Проверить доступность
docker exec 1c-timescaledb psql -U ai_user -d ai_memory -c "SELECT 1;"

# Если база данных не существует, создать:
cd ai-memory-system/database
python init_memory_schema.py
```

---

### Ошибка: Qdrant connection failed

**Симптом**:
```
❌ Qdrant connection failed: Connection refused
```

**Решение**:
```bash
# Запустить контейнер
docker start 1c-qdrant

# Проверить доступность
curl http://localhost:6333

# Проверить что collection создана
curl http://localhost:6333/collections/conversation_memory
```

---

### Ошибка: ModuleNotFoundError

**Симптом**:
```
❌ Service import failed: No module named 'psycopg2'
```

**Решение**:
```bash
cd ai-memory-system
pip install -r requirements.txt
```

**requirements.txt содержит**:
```
psycopg2-binary>=2.9.9
qdrant-client>=1.7.0
requests>=2.31.0
mcp>=0.1.0
```

---

### Ошибка: Ollama not responding

**Симптом**:
```
❌ Failed to create embedding: Connection refused to localhost:11434
```

**Решение**:
```bash
# Запустить Ollama (если не запущен)
ollama serve &

# Проверить что модель установлена
ollama list

# Если модель отсутствует:
ollama pull nomic-embed-text

# Проверить что Ollama отвечает
curl http://localhost:11434/api/version
```

---

### Ошибка: MCP tools not showing in Claude Code

**Симптом**: После перезапуска Claude Code инструменты памяти не появляются в `/tools`

**Решение**:
1. Проверить что конфигурация на месте:
   ```bash
   cat .claude/mcp-configs/memory-config.json
   ```

2. Проверить логи Claude Code на ошибки запуска MCP сервера

3. Попробовать запустить сервер вручную:
   ```bash
   cd ai-memory-system/mcp
   python memory_server.py
   ```
   Если сервер не запускается — смотрите ошибки в консоли

4. Убедиться что разрешения добавлены в `.claude/settings.local.json`

---

## Полезные команды

### Проверить статус всех сервисов

```bash
# Docker контейнеры
docker ps | grep -E "timescale|qdrant"

# Ollama
curl http://localhost:11434/api/version

# TimescaleDB
docker exec 1c-timescaledb psql -U ai_user -d ai_memory -c "\dt"

# Qdrant
curl http://localhost:6333/collections
```

### Просмотреть данные в памяти

```bash
# TimescaleDB: просмотр разговоров
docker exec 1c-timescaledb psql -U ai_user -d ai_memory -c "SELECT * FROM conversations ORDER BY started_at DESC LIMIT 5;"

# TimescaleDB: просмотр сообщений
docker exec 1c-timescaledb psql -U ai_user -d ai_memory -c "SELECT id, role, importance_score, content_preview FROM messages ORDER BY timestamp DESC LIMIT 10;"

# Qdrant: количество векторов
curl http://localhost:6333/collections/conversation_memory | jq .result.points_count
```

### Очистить память (для тестирования)

**ВНИМАНИЕ**: Это удалит все данные!

```bash
# Очистить TimescaleDB
docker exec 1c-timescaledb psql -U ai_user -d ai_memory -c "TRUNCATE TABLE messages CASCADE; TRUNCATE TABLE conversations CASCADE;"

# Очистить Qdrant collection
curl -X DELETE http://localhost:6333/collections/conversation_memory
curl -X PUT http://localhost:6333/collections/conversation_memory \
  -H "Content-Type: application/json" \
  -d '{"vectors": {"size": 768, "distance": "Cosine"}}'
```

---

## Дополнительная документация

- **Полная документация MCP Server**: `ai-memory-system/mcp/README.md`
- **Архитектура системы памяти**: `ai-memory-system/ARCHITECTURE_MEMORY.md`
- **Отчет о завершении**: `ai-memory-system/COMPLETION_WEEK2_DAY4_MCP.md`
- **Конфигурации MCP**: `.claude/mcp-configs/README.md`

---

## Поддержка

При возникновении проблем:
1. Проверьте раздел Troubleshooting выше
2. Запустите `python test_server_import.py` для диагностики
3. Проверьте логи Docker контейнеров: `docker logs 1c-timescaledb` и `docker logs 1c-qdrant`
4. Проверьте что все сервисы запущены: TimescaleDB, Qdrant, Ollama

---

**Версия**: 1.0.0
**Дата**: 2025-10-31
**Статус**: ✅ Production Ready
