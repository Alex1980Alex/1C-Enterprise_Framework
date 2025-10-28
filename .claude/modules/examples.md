# Practical Examples

## Example 1: Analyzing existing 1C module

```bash
# Step 1: Analyze code quality
python -m sonar_integration analyze --src-dir "src/projects/configuration/CommonModules/UtilsModule.bsl"

# Step 2: Create task for improvements
cd claude-task-master
npx task-master add-task --title "Refactor UtilsModule" --description "Fix BSL issues found in analysis"

# Step 3: Apply development automation
# Claude automatically provides intelligent analysis and guidance
```

## Example 2: Starting new 1C project

```bash
# Step 1: Set up project validation
bash scripts/validate-project.sh

# Step 2: Initialize Task Master for project
cd claude-task-master
npx task-master parse-prd "requirements.md"

# Step 3: Get first development task
npx task-master next
# Claude provides intelligent guidance for development workflow
```

## Example 3: Code review workflow

```bash
# Step 1: Pre-commit analysis (automatic via Git hooks)
git add CommonModule.bsl
git commit -m "feat: new utility functions"
# Git hook automatically runs BSL analysis

# Step 2: Manual quality check if needed
python -m sonar_integration analyze --src-dir . --severity BLOCKER,CRITICAL

# Step 3: Document findings in Task Master
npx task-master add-task --title "Fix critical BSL issues" --tag quality-control
```

## Example 4: Universal Web Scraper для изучения документации

```bash
# Парсинг документации 1С с портала ITS
mcp__universal-web-scraper__scrape_website({
  "url": "https://its.1c.ru/db/metod8dev/content/5873/hdoc",
  "adapter_type": "its_1c",
  "include_links": true,
  "save_to_memory": true
})

# Анализ структуры сайта перед парсингом
mcp__universal-web-scraper__analyze_website_structure({
  "url": "https://docs.1c.ru",
  "deep_analysis": true
})

# Пакетный парсинг технических статей
mcp__universal-web-scraper__bulk_scrape_websites({
  "urls": [
    "https://its.1c.ru/db/metod8dev",
    "https://its.1c.ru/db/expertguide",
    "https://its.1c.ru/db/pubmethodique"
  ],
  "concurrent_limit": 2,
  "delay_between_requests": 3
})
```

## Example 5: 1C Documentation Parser для полного извлечения

```bash
# Парсинг конкретной главы документации
cd scripts/1c-docs-parser
python automated-parser.py 4  # Глава 4: Встроенный язык

# Использование универсальных функций для кастомного парсинга
node -e "
const {extractHierarchicalStructure, saveStructureToJSON} = require('./universal-functions.js');
// Извлечение структуры и сохранение в JSON
"

# Интеграция с Memory MCP для создания Knowledge Graph
python scripts/mcp-integration/docs-memory-integration.py \
  --source "Проекты/1C-Platform-Doc-Parser" \
  --entity-type "1c_documentation" \
  --save-to-graph
```

## Example 6: Playwright автотестирование

```bash
# Использование MCP команд для тестирования веб-интерфейса 1С
# См. примеры: tests/playwright/examples/01-example-login.md
# См. примеры: tests/playwright/examples/02-example-document-form.md
# См. примеры: tests/playwright/examples/03-example-rest-api-test.md

# Генерация тестового кода
mcp__playwright-automation__start_codegen_session({
  options: {outputPath: "tests/playwright/generated/", testNamePrefix: "1C_Test"}
})
```

## Workflow примеры

### Рефакторинг процедуры
1. `serena__find_symbol` → найти процедуру
2. `serena__find_referencing_symbols` → где используется
3. `sequential-thinking` → спланировать изменения
4. `serena__replace_symbol_body` → заменить тело
5. `memory__create_entities` → задокументировать

### Анализ новой конфигурации
1. `serena__get_symbols_overview` → обзор модулей
2. `1c-framework-docs__search_docs` → изучить документацию
3. `memory__create_entities` → создать Knowledge Graph

### Полный workflow разработки
```bash
# 1. Анализ кода → 2. Сохранение в граф → 3. Планирование → 4. Тестирование → 5. Документация
python -m sonar_integration analyze --src-dir src/
python scripts/mcp-integration/bsl-memory-integration.py reports/analysis.json
python scripts/mcp-integration/docling-workflow.py --input "reports/" --batch
cd claude-task-master && npx task-master next
# См. примеры тестов в tests/playwright/examples/
```