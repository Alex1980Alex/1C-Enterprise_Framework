# MCP Integration Details

## ✅ Working MCP Commands

### Filesystem operations
```javascript
mcp__filesystem__read_text_file("/path/to/file.bsl")
mcp__filesystem__write_file("/path/to/file.bsl", content)
mcp__filesystem__list_directory("/src/projects/configuration/CommonModules/")
```

### GitHub integration
```javascript
mcp__github__get_file_contents("owner", "repo", "path/to/file.bsl")
mcp__github__create_pull_request(...)
```

### Memory system
```javascript
mcp__memory__create_entities([{name: "ModuleAnalysis", type: "analysis", ...}])
mcp__memory__search_nodes("1C module patterns")
```

## MCP Reasoner v2.0.0

**Быстрый старт:**
```bash
python scripts/mcp-integration/full-analysis-pipeline.py \
  --input "path/to/ObjectModule.bsl" \
  --output "reports/analysis" \
  --use-reasoner \
  --save-to-memory
```

**Стратегии анализа:**
- **Beam Search**: быстрый анализ (30 сек - 2 мин)
- **MCTS**: глубокий анализ (2-10 мин)

**Конфигурация Claude Desktop:**
```json
{
  "mcpServers": {
    "mcp-reasoner": {
      "command": "node",
      "args": ["D:/1C-Enterprise_Framework/mcp-reasoner/dist/index.js"],
      "env": {
        "MAX_REASONING_DEPTH": "10",
        "SEARCH_STRATEGY": "mcts",
        "CACHE_ENABLED": "true"
      }
    }
  }
}
```

## Docling MCP v1.0

**Конвертация документов:**
```javascript
mcp__docling__convert_document({
  input_path: "D:/docs/specification.pdf",
  output_path: "cache/spec.md",
  extract_images: true,
  ocr_enabled: true
})

mcp__docling__batch_convert({
  input_dir: "D:/project-docs/",
  output_dir: "cache/markdown/",
  file_pattern: "*.{pdf,docx,pptx}"
})
```

**Поддерживаемые форматы:**
- PDF (с OCR), DOCX/DOC, PPTX/PPT
- XLSX/XLS, HTML, RTF

## Sequential Thinking MCP

```javascript
mcp__sequential-thinking__sequentialthinking({
  thought: "Анализирую структуру подсистем конфигурации",
  thoughtNumber: 1,
  totalThoughts: 10,
  nextThoughtNeeded: true
})
```

## Memory MCP - Knowledge Graph

```javascript
// Создание сущностей
mcp__memory__create_entities([{
  name: "Справочник.Номенклатура",
  entityType: "metadata_object",
  observations: ["Используется в 15 документах", "Имеет 3 табличные части"]
}])

// Создание связей
mcp__memory__create_relations([{
  from: "Документ.РеализацияТоваров",
  to: "Справочник.Номенклатура",
  relationType: "references"
}])
```

## Playwright Automation MCP

```javascript
// Навигация и тестирование
mcp__playwright-automation__playwright_navigate({
  url: "http://localhost/infobase",
  browserType: "chromium"
})

mcp__playwright-automation__playwright_click({selector: "#LoginButton"})
mcp__playwright-automation__playwright_fill({selector: "#Username", value: "Администратор"})
mcp__playwright-automation__playwright_screenshot({name: "test-result", savePng: true})

// HTTP API тестирование
mcp__playwright-automation__playwright_post({
  url: "http://localhost/infobase/hs/api/v1/documents",
  value: JSON.stringify({data: "..."}),
  token: "Bearer YOUR_TOKEN"
})
```

## Universal Web Scraper MCP

```javascript
// Парсинг документационных сайтов
mcp__universal-web-scraper__scrape_website({
  "url": "https://docs.1c.ru/article",
  "adapter_type": "documentation",
  "include_links": true,
  "save_to_memory": true
})

// Специализированный парсинг ITS 1C
mcp__universal-web-scraper__scrape_website({
  "url": "https://its.1c.ru/db/metod8dev",
  "adapter_type": "its_1c",
  "include_images": true
})
```

## Интеграция MCP с инструментами фреймворка

### BSL + Memory Integration
```bash
python -m sonar_integration analyze --src-dir . --output-dir reports/
python scripts/mcp-integration/bsl-memory-integration.py reports/analysis.json
```

### Task Master + Sequential Thinking
```bash
cd claude-task-master
npx task-master next
node ../scripts/mcp-integration/taskmaster-thinking-integration.js
```

### Docling + Memory Integration
```bash
python scripts/mcp-integration/docling-workflow.py --input "docs/" --batch
python scripts/mcp-integration/docling-memory-integration.py --source "cache/docling-output/" --save-to-graph
```