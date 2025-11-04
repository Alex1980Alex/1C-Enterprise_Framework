# AI Memory System для 1C Framework

Система семантического поиска BSL кода с векторным индексом и REST API.

## Быстрый старт

### 1. Проверка сервисов

Убедитесь, что запущены необходимые сервисы:

```bash
# Qdrant (векторная БД)
docker ps | grep qdrant

# Ollama (embeddings)
curl http://localhost:11434/api/tags
```

### 2. Семантический поиск

Поиск BSL кода по смыслу запроса:

```bash
cd ai-memory-system

# Пример: найти код работы с базой данных
python scripts/search/semantic_search_enhanced.py "получить данные из базы" --limit 5

# Поиск с фильтрами
python scripts/search/semantic_search_enhanced.py "обработка документа" \
    --module-type ObjectModule \
    --min-functions 3 \
    --limit 10
```

### 3. REST API (опционально)

Запуск веб-интерфейса и API:

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Открыть в браузере
http://localhost:8000/
```

## Возможности

### Semantic Search

- Поиск по смыслу, не по ключевым словам
- Находит похожие примеры кода
- Фильтрация по типу модуля и количеству функций
- Ranking по релевантности

### Векторный индекс

- 100 BSL файлов в индексе
- 768-размерные embeddings (nomic-embed-text)
- COSINE метрика для similarity search
- Qdrant для быстрого поиска

## Примеры поиска

```bash
# Найти код работы с запросами
python scripts/search/semantic_search_enhanced.py "выполнить запрос к базе данных"

# Найти код обработки документов
python scripts/search/semantic_search_enhanced.py "проведение документа поступление"

# Найти код формирования отчетов
python scripts/search/semantic_search_enhanced.py "создать табличный документ"
```

## Статус

**Week 2 Complete** (2025-11-02)

✅ Компоненты:
- REST API (9 endpoints)
- Web UI
- Async Indexer
- Qdrant Integration
- Semantic Search Engine

✅ Данные:
- 100 BSL файлов проиндексировано
- Векторы загружены в Qdrant
- Поиск работает корректно

## Производительность

- **Индексация**: 100 файлов за ~5 минут
- **Поиск**: <2 секунды на запрос
- **Qdrant upload**: 19.1 точек/сек
- **Vector size**: 768-dimensional embeddings

