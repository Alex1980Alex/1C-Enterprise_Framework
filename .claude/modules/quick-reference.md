# Quick Reference Commands

## BSL Language Server

```bash
# Быстрая проверка одного модуля
python -m sonar_integration analyze --src-dir "ОбщийМодуль.bsl" --quick

# Полный анализ проекта
python -m sonar_integration analyze --src-dir src/ --output-dir reports/

# Анализ конкретной папки
python -m sonar_integration analyze --src-dir "src/projects/configuration/CommonModules/" --output-dir reports/

# Генерация отчётов (все форматы)
python -m sonar_integration report reports/analysis.json --html --excel --csv

# Анализ с фильтрацией по критичности
python -m sonar_integration analyze --src-dir . --severity CRITICAL,BLOCKER

# Создание HTML отчёта и автоматическое открытие
python -m sonar_integration report analysis.json --html && start reports/report.html
```

## Task Master

```bash
cd claude-task-master

# Управление задачами
npx task-master list                    # Все задачи (93 доступно)
npx task-master next                    # Следующая рекомендуемая задача
npx task-master view <id>               # Детали задачи
npx task-master show 1                  # Показать задачу #1

# Анализ и фильтрация
npx task-master tags                    # Управление тегами
npx task-master list --tag master       # Фильтр по тегу
npx task-master models                  # Конфигурация AI моделей
npx task-master status                  # Обзор статуса проекта

# Работа с тегами
npx task-master tags --show-metadata    # Показать все теги с метаданными
npx task-master list --tag cc-kiro-hooks # Задачи для конкретного workflow

# Завершение задач
npx task-master mark-complete <id>      # Отметить как выполненную

# Интеграция с разработкой 1С
npx task-master add-task --title "Analyze BSL module" --description "Review CommonModule for quality issues"
npx task-master parse-from-text "Create 1C report form with data composition schema"
```

## Семантическое сравнение BSL

```bash
# АНАЛИЗ: Структура одного BSL модуля
python scripts/bsl-semantic-diff/semantic_diff_poc.py module.bsl --analyze-only

# АНАЛИЗ: Метаданные конфигурации
python scripts/bsl-semantic-diff/metadata_analyzer.py config_dir --export-json

# АНАЛИЗ: Полный архитектурный обзор
python scripts/bsl-semantic-diff/compare-configs.py config --analyze-architecture

# СРАВНЕНИЕ: Два BSL файла
python scripts/bsl-semantic-diff/semantic_diff_poc.py file1.bsl file2.bsl

# СРАВНЕНИЕ: Конфигурации + метаданные
python scripts/bsl-semantic-diff/compare-configs.py config1 config2 report.txt --metadata
```

## Docling MCP

```bash
# Конвертация PDF/DOCX в Markdown
python scripts/mcp-integration/docling-workflow.py --input "document.pdf" --output "cache/docling-output/"

# Пакетная обработка документов
python scripts/mcp-integration/docling-workflow.py --batch --input-dir "docs/" --output-dir "cache/markdown/"

# Интеграция с Memory MCP
python scripts/mcp-integration/docling-memory-integration.py --source "reports/" --save-to-graph
```

## Universal Web Scraper

```bash
# Использование в Claude Desktop с MCP команды
# Специализированный парсинг ITS 1C
mcp__universal-web-scraper__scrape_website({
  "url": "https://its.1c.ru/db/metod8dev",
  "adapter_type": "its_1c",
  "include_images": true
})

# Пакетный парсинг нескольких сайтов
mcp__universal-web-scraper__bulk_scrape_websites({
  "urls": ["site1.com", "site2.com", "site3.com"],
  "concurrent_limit": 3,
  "delay_between_requests": 2
})
```

## Universal Documentation Parser

```bash
# УНИВЕРСАЛЬНЫЙ ПАРСЕР - работает с ЛЮБЫМИ документационными сайтами
# 1C документация (its.1c.ru)
python scripts/1c-docs-parser/universal-documentation-parser.py \
  "https://its.1c.ru/db/v8326doc" \
  --max-pages 50 --format markdown

# Парсинг документации 1С
cd scripts/1c-docs-parser
python automated-parser.py 3  # Глава 3
python automated-parser.py    # Парсинг всей документации
```

## Валидация проекта

```bash
bash scripts/validate-project.sh    # Полная проверка проекта
bash scripts/setup-environment.sh   # Проверка окружения
```

## Полный цикл анализа

```bash
# Автоматический полный анализ (РЕКОМЕНДУЕТСЯ)
python scripts/mcp-integration/full-analysis-pipeline.py \
  --input "path/to/module.bsl" \
  --output "reports/analysis" \
  --use-reasoner \
  --save-to-memory

# MCP Reasoner для сложного анализа
python scripts/mcp-integration/bsl-reasoner-integration.py "path/to/module.bsl"
```