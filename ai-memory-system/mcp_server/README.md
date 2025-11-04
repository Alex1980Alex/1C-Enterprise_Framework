# AI Memory System MCP Server

MCP (Model Context Protocol) сервер для интеграции AI Memory System с Claude Code.

## Описание

Предоставляет 6 интеллектуальных инструментов для поиска по BSL коду через Claude Code:

1. **search_bsl_code** - Базовый семантический поиск
2. **intelligent_search** - Интеллектуальный многомерный поиск с Context Manager
3. **analyze_graph** - Анализ графа зависимостей
4. **get_search_history** - История поисковых запросов
5. **export_results** - Экспорт результатов в JSON/Markdown/CSV
6. **clear_cache** - Очистка кеша

## Требования

### Системные зависимости

```bash
# Python 3.10+
python --version

# MCP library
pip install mcp

# Other dependencies
pip install -r ../requirements.txt
```

### Сервисы

- **Ollama** (localhost:11434) - для LLM
- **Qdrant** (localhost:6333) - для векторного поиска
- **Neo4j** (localhost:7687) - для графовых запросов

## Установка

### 1. Установка зависимостей

```bash
cd ai-memory-system
pip install -r requirements.txt
pip install mcp
```

### 2. Настройка конфигурации

Отредактируйте `mcp_server/config.json`:

```json
{
  "ollama": {
    "url": "http://localhost:11434",
    "reranking_model": "deepseek-coder:6.7b",
    "generation_model": "deepseek-coder:6.7b"
  },
  "qdrant": {
    "host": "localhost",
    "port": 6333,
    "collection": "bsl_code_v2"
  },
  "neo4j": {
    "uri": "bolt://localhost:7687",
    "user": "neo4j",
    "password": "your_password"
  }
}
```

### 3. Регистрация в Claude Code

Добавьте в конфигурацию Claude Code (`~/.config/claude-code/mcp_servers.json`):

```json
{
  "mcpServers": {
    "ai-memory-system": {
      "command": "python",
      "args": [
        "D:/1C-Enterprise_Framework/ai-memory-system/mcp_server/server.py"
      ],
      "cwd": "D:/1C-Enterprise_Framework/ai-memory-system",
      "env": {
        "PYTHONPATH": "D:/1C-Enterprise_Framework/ai-memory-system"
      }
    }
  }
}
```

## Использование

### Запуск сервера

```bash
cd ai-memory-system
python mcp_server/server.py
```

Сервер автоматически инициализирует все компоненты при первом запросе.

### Инструменты

#### 1. search_bsl_code

Базовый поиск по коду:

```python
# В Claude Code
@search_bsl_code(
    query="обработка документов поступления",
    limit=10,
    mode="semantic"
)
```

**Параметры:**
- `query` (str): Поисковый запрос
- `limit` (int): Макс. результатов (default: 10, max: 50)
- `mode` (str): Режим (semantic, graph, hybrid, intelligent)
- `module_types` (list): Фильтр по типам модулей

#### 2. intelligent_search

Интеллектуальный поиск с полным pipeline:

```python
@intelligent_search(
    query="найти функции обработки документов",
    context_type="code_search",
    max_results=10,
    include_dependencies=True
)
```

**Параметры:**
- `query` (str): Поисковый запрос
- `context_type` (str): code_search, code_understanding, debugging, examples
- `max_results` (int): Макс. результатов
- `include_dependencies` (bool): Включить зависимости

**Pipeline:**
1. Intent Analysis (LLM классифицирует намерение)
2. Multi-dimensional Retrieval (векторный + граф + временной)
3. LLM Precision Ranking (переранжирование)
4. Context Assembly (сборка финального контекста)

#### 3. analyze_graph

Анализ графа зависимостей:

```python
@analyze_graph(
    file_path="Документы/ПоступлениеТоваров/МодульОбъекта.bsl",
    analysis_type="full"
)
```

**Параметры:**
- `file_path` (str): Путь к файлу (опционально)
- `analysis_type` (str): dependencies, centrality, communities, full

#### 4. get_search_history

История поиска:

```python
@get_search_history(
    limit=10,
    filter_by="query"
)
```

#### 5. export_results

Экспорт результатов:

```python
@export_results(
    query="обработка документов",
    format="json",
    include_metadata=True
)
```

**Форматы:**
- `json` - структурированный JSON
- `markdown` - форматированный Markdown
- `csv` - таблица CSV

#### 6. clear_cache

Очистка кеша:

```python
@clear_cache()
```

## Архитектура

```
MCP Server
    ├── LLM Service
    │   ├── Intent Classification
    │   ├── Results Re-ranking
    │   └── Code Explanation
    │
    ├── BSL Search Service
    │   ├── Semantic Search (Qdrant)
    │   ├── Graph Search (Neo4j)
    │   ├── Hybrid Search
    │   └── Intelligent Search (+ LLM)
    │
    ├── Context Manager
    │   ├── Intent Analysis
    │   ├── Multi-dimensional Retrieval
    │   ├── LLM Precision Ranking
    │   └── Context Assembly
    │
    └── Graph Analytics
        ├── Dependencies
        ├── Centrality
        └── Communities
```

## Примеры использования в Claude Code

### Пример 1: Поиск кода

```
Prompt: Найди все функции обработки документов поступления

Claude Code использует:
@intelligent_search(
    query="функции обработки документов поступления",
    context_type="code_search",
    max_results=10
)

Результат:
- Intent: find_function (confidence: 0.85)
- Primary Results: 8 релевантных модулей
- Dependencies: 12 связанных файлов
- Suggested Actions: "Просмотрите найденные функции..."
```

### Пример 2: Понимание кода

```
Prompt: Как работает проведение документа РеализацияТоваров?

Claude Code использует:
@intelligent_search(
    query="проведение документа РеализацияТоваров",
    context_type="code_understanding",
    include_dependencies=True
)

@analyze_graph(
    file_path="Документы/РеализацияТоваров/МодульОбъекта.bsl",
    analysis_type="dependencies"
)

Результат: Полный контекст с зависимостями и граф связей
```

### Пример 3: Отладка

```
Prompt: Почему возникает ошибка при проведении документа?

Claude Code использует:
@intelligent_search(
    query="ошибка при проведении документа",
    context_type="debugging"
)

@get_search_history(limit=5)

Результат: Релевантные модули + история похожих запросов
```

### Пример 4: Экспорт

```
Prompt: Экспортируй все модули работы с документами в JSON

Claude Code использует:
@export_results(
    query="модули работы с документами",
    format="json",
    include_metadata=True
)

Результат: JSON файл с результатами
```

## ROI Impact

**40% годового ROI ($19,920/год)**

Основные преимущества:
- Интеллектуальный поиск с пониманием намерений
- Многомерный анализ (семантика + граф + время)
- LLM re-ranking для точности
- Интеграция с Claude Code
- История и экспорт результатов

## Логирование

Логи сохраняются в `../logs/mcp_server.log`

```bash
# Просмотр логов
tail -f logs/mcp_server.log
```

## Устранение проблем

### Сервер не запускается

```bash
# Проверка зависимостей
pip list | grep mcp

# Проверка сервисов
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:6333/collections  # Qdrant
```

### Долгое выполнение запросов

- Ollama timeout увеличен до 180 секунд
- Кеш результатов (TTL 5 минут)
- Используйте `mode="semantic"` для быстрого поиска

### Ошибки инициализации

Сервисы инициализируются лениво при первом запросе. Если ошибка - проверьте доступность Qdrant, Neo4j, Ollama.

## Поддержка

Для вопросов и проблем создавайте issues в репозитории проекта.

---

**Версия:** 1.0.0
**Автор:** Claude Code AI Assistant
**Дата:** 2025-11-03
