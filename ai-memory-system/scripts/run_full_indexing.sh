#!/bin/bash
# Full BSL Indexing Script - Week 2, Day 3
# Полная индексация всех BSL файлов в проекте

set -e  # Exit on error

echo "=========================================="
echo "🚀 BSL Full Dataset Indexing"
echo "=========================================="
echo ""
echo "📅 Дата: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Конфигурация
PROJECT_DIR="D:/1C-Enterprise_Framework"
INDEXER_SCRIPT="${PROJECT_DIR}/ai-memory-system/scripts/indexing/bsl_indexer_async.py"
LOADER_SCRIPT="${PROJECT_DIR}/ai-memory-system/scripts/qdrant/load_index_to_qdrant.py"
OUTPUT_DIR="${PROJECT_DIR}/ai-memory-system/data/index"
BSL_DIRECTORY="${PROJECT_DIR}/src"

# Параметры индексации
MAX_FILES=""  # Пустое значение = все файлы
BATCH_SIZE=20
MAX_WORKERS=8
RETRY_ATTEMPTS=3

echo "⚙️  Конфигурация:"
echo "   Директория BSL: ${BSL_DIRECTORY}"
echo "   Выходная директория: ${OUTPUT_DIR}"
echo "   Batch size: ${BATCH_SIZE}"
echo "   Max workers: ${MAX_WORKERS}"
echo "   Retry attempts: ${RETRY_ATTEMPTS}"
echo ""

# Проверка Python
echo "🔍 Проверка Python..."
if ! command -v python &> /dev/null; then
    echo "❌ Python не найден!"
    exit 1
fi
echo "✅ Python: $(python --version)"
echo ""

# Проверка Ollama
echo "🔍 Проверка Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama не запущен!"
    echo "💡 Запустите: ollama serve"
    exit 1
fi
echo "✅ Ollama: доступен"
echo ""

# Проверка Qdrant
echo "🔍 Проверка Qdrant..."
if ! curl -s http://localhost:6333/collections > /dev/null 2>&1; then
    echo "❌ Qdrant не запущен!"
    echo "💡 Запустите: docker start 1c-qdrant"
    exit 1
fi
echo "✅ Qdrant: доступен"
echo ""

# Шаг 1: Асинхронная индексация
echo "=========================================="
echo "📊 Шаг 1/2: Асинхронная индексация BSL файлов"
echo "=========================================="
echo ""

START_TIME=$(date +%s)

python "${INDEXER_SCRIPT}" \
    "${BSL_DIRECTORY}" \
    --output "${OUTPUT_DIR}" \
    --batch-size ${BATCH_SIZE} \
    --max-workers ${MAX_WORKERS} \
    --retry-attempts ${RETRY_ATTEMPTS}

INDEXING_TIME=$(($(date +%s) - START_TIME))

echo ""
echo "✅ Индексация завершена за ${INDEXING_TIME} секунд"
echo ""

# Шаг 2: Загрузка в Qdrant
echo "=========================================="
echo "📤 Шаг 2/2: Загрузка индекса в Qdrant"
echo "=========================================="
echo ""

python "${LOADER_SCRIPT}" \
    --index-file "${OUTPUT_DIR}/bsl_index_full.json" \
    --qdrant-url "http://localhost:6333" \
    --collection "bsl_code" \
    --batch-size 100 \
    --verify

TOTAL_TIME=$(($(date +%s) - START_TIME))

echo ""
echo "=========================================="
echo "✅ ПОЛНАЯ ИНДЕКСАЦИЯ ЗАВЕРШЕНА"
echo "=========================================="
echo ""
echo "⏱️  Общее время: ${TOTAL_TIME} секунд ($(($TOTAL_TIME / 60)) минут)"
echo ""
echo "📊 Результаты:"
echo "   ✅ Индекс: ${OUTPUT_DIR}/bsl_index_full.json"
echo "   ✅ Qdrant коллекция: bsl_code"
echo ""
echo "🔍 Тестирование поиска:"
echo "   python ai-memory-system/scripts/search/qdrant_search.py 'получить данные'"
echo ""
echo "=========================================="
