# 📄 Работа с документацией

## 🎯 Обзор инструментов для работы с документами

Фреймворк предоставляет мощные инструменты для конвертации документов, парсинга веб-сайтов, исследования и создания технической документации.

---

## 🔧 Основные инструменты

### **1. Docling MCP v1.0 - Конвертация документов**

**Универсальная конвертация** документов любых форматов в Markdown для анализа, создания Knowledge Base и RAG систем.

#### **Поддерживаемые форматы:**
- **PDF** - включая сканированные документы с OCR
- **DOCX/DOC** - Microsoft Word документы с сохранением структуры
- **PPTX/PPT** - PowerPoint презентации с извлечением текста и изображений
- **XLSX/XLS** - Excel таблицы с конвертацией в CSV/JSON/Markdown
- **HTML** - веб-страницы и HTML отчёты
- **RTF** - Rich Text Format документы

#### **Конвертация одного документа:**
```javascript
// Основная конвертация с OCR
mcp__docling__convert_document({
  input_path: "D:/documents/ТЗ_Автоматизация.pdf",
  output_path: "cache/documents/tz-automation.md",
  extract_images: true,
  ocr_enabled: true
})

// Конвертация Word документа
mcp__docling__convert_document({
  input_path: "D:/specs/Техническая_спецификация.docx",
  output_path: "cache/specs/tech-spec.md",
  extract_images: false
})

// Конвертация презентации
mcp__docling__convert_document({
  input_path: "D:/presentations/Архитектура_системы.pptx",
  output_path: "cache/presentations/architecture.md",
  extract_images: true
})
```

#### **Пакетная обработка:**
```javascript
// Обработка всех документов в папке
mcp__docling__batch_convert({
  input_dir: "D:/project-documents/",
  output_dir: "cache/project-md/",
  file_pattern: "*.{pdf,docx,pptx,xlsx}",
  extract_images: true
})

// Обработка только PDF файлов
mcp__docling__batch_convert({
  input_dir: "D:/pdf-archive/",
  output_dir: "cache/pdf-converted/",
  file_pattern: "*.pdf",
  extract_images: false
})
```

#### **Извлечение таблиц:**
```javascript
// Извлечение таблиц в разных форматах
mcp__docling__extract_tables({
  input_path: "D:/data/Матрица_требований.xlsx",
  output_format: "markdown"  // или "csv", "json"
})

// Анализ структуры без конвертации
mcp__docling__analyze_document_structure({
  input_path: "D:/complex-document.pdf",
  include_content: false
})
```

#### **Мониторинг процесса:**
```javascript
// Проверка статуса конвертации
mcp__docling__get_conversion_status({
  job_id: "conversion_123"  // опционально - показать все, если не указан
})
```

---

### **2. Universal Web Scraper MCP v1.0 - Парсинг веб-сайтов**

**Интеллектуальный парсинг** любых веб-сайтов с автоматическим определением типа контента и применением оптимальной стратегии извлечения.

#### **Автоматический парсинг с определением типа:**
```javascript
// Парсинг документационного сайта (автоопределение)
mcp__universal-web-scraper__scrape_website({
  url: "https://docs.1c.ru/enterprise/overview/",
  include_links: true,
  include_images: true,
  save_to_memory: true
})

// Анализ структуры перед парсингом
mcp__universal-web-scraper__analyze_website_structure({
  url: "https://its.1c.ru",
  deep_analysis: true
})
```

#### **Специализированные адаптеры:**

**ITS 1C Adapter - для портала ITS:**
```javascript
mcp__universal-web-scraper__scrape_website({
  url: "https://its.1c.ru/db/metod8dev/content/5873/hdoc",
  adapter_type: "its_1c",
  include_links: true,
  include_images: true,
  max_depth: 2,
  save_to_memory: true
})
```

**Documentation Adapter - для документационных сайтов:**
```javascript
mcp__universal-web-scraper__scrape_website({
  url: "https://docs.microsoft.com/en-us/sql/",
  adapter_type: "documentation",
  max_depth: 3,
  output_format: "markdown",
  save_to_memory: true
})
```

**News Adapter - для новостных ресурсов:**
```javascript
mcp__universal-web-scraper__scrape_website({
  url: "https://habr.com/ru/articles/",
  adapter_type: "news",
  max_depth: 1,
  include_images: false
})
```

**Generic Adapter - универсальный:**
```javascript
mcp__universal-web-scraper__scrape_website({
  url: "https://любой-сайт.com",
  adapter_type: "generic",
  include_links: true,
  save_to_memory: false
})
```

#### **Пакетный парсинг:**
```javascript
// Парсинг нескольких сайтов с контролем нагрузки
mcp__universal-web-scraper__bulk_scrape_websites({
  urls: [
    "https://its.1c.ru/db/metod8dev",
    "https://its.1c.ru/db/expertguide",
    "https://v8.1c.ru/overview/"
  ],
  concurrent_limit: 2,
  delay_between_requests: 3
})
```

#### **Доступные адаптеры:**
```javascript
// Получение списка всех адаптеров
mcp__universal-web-scraper__get_supported_adapters()
```

---

### **3. 1C Documentation Parser v2.0 - Специализированный парсер**

**Универсальный парсер** для любых документационных сайтов с автоматическим определением типа и сохранением иерархической структуры.

#### **Универсальный парсинг документации:**
```bash
# 1C документация (its.1c.ru)
python scripts/1c-docs-parser/universal-documentation-parser.py \
  "https://its.1c.ru/db/v8326doc" \
  --max-pages 50 \
  --format markdown

# GitHub документация
python scripts/1c-docs-parser/universal-documentation-parser.py \
  "https://docs.github.com/en/get-started" \
  --max-pages 20 \
  --format json

# MDN Web Docs
python scripts/1c-docs-parser/universal-documentation-parser.py \
  "https://developer.mozilla.org/en-US/docs/Web/JavaScript" \
  --max-pages 30

# React документация
python scripts/1c-docs-parser/universal-documentation-parser.py \
  "https://react.dev/learn" \
  --max-pages 25

# Django документация
python scripts/1c-docs-parser/universal-documentation-parser.py \
  "https://docs.djangoproject.com/en/stable/" \
  --max-pages 40

# Любой документационный сайт (автоопределение)
python scripts/1c-docs-parser/universal-documentation-parser.py \
  "https://любой-сайт-документации.com" \
  --max-pages 15
```

#### **Специализированный парсинг 1С:**
```bash
cd scripts/1c-docs-parser

# Парсинг конкретной главы
python automated-parser.py 3  # Глава 3

# Парсинг всей документации
python automated-parser.py

# Использование JavaScript функций для кастомного парсинга
node -e "
const parser = require('./universal-functions.js');
// Полный workflow парсинга с сохранением структуры
"
```

---

### **4. Brave Search - Поиск экспертной информации**

**Веб-поиск** для исследования предметных областей, поиска лучших практик и актуальных решений.

#### **Общий веб-поиск:**
```javascript
// Поиск лучших практик и решений
mcp__brave-search__brave_web_search({
  query: "1С:Предприятие лучшие практики разработки 2025",
  count: 15
})

// Поиск технических решений
mcp__brave-search__brave_web_search({
  query: "BSL Language Server интеграция VS Code настройка",
  count: 10
})

// Поиск по конкретной проблеме
mcp__brave-search__brave_web_search({
  query: "1С производительность оптимизация запросов в циклах",
  count: 12
})
```

#### **Локальный поиск:**
```javascript
// Поиск рядом расположенных услуг
mcp__brave-search__brave_local_search({
  query: "1С разработка консультации Москва",
  count: 8
})

// Поиск обучающих центров
mcp__brave-search__brave_local_search({
  query: "1С обучение курсы программирование",
  count: 5
})
```

---

## 📋 Практические сценарии

### **📄 Обработка проектной документации:**

```javascript
// 1. Конвертация технического задания
mcp__docling__convert_document({
  input_path: "D:/projects/ТЗ_Новая_Подсистема.docx",
  output_path: "cache/projects/tz-new-subsystem.md",
  extract_images: true
})

// 2. Извлечение матрицы требований из Excel
mcp__docling__extract_tables({
  input_path: "D:/projects/Матрица_требований.xlsx",
  output_format: "json"
})

// 3. Конвертация презентации архитектуры
mcp__docling__convert_document({
  input_path: "D:/projects/Архитектура_решения.pptx",
  output_path: "cache/projects/architecture.md",
  extract_images: true
})

// 4. Пакетная обработка всей проектной документации
mcp__docling__batch_convert({
  input_dir: "D:/projects/documentation/",
  output_dir: "cache/project-knowledge/",
  file_pattern: "*.{pdf,docx,pptx,xlsx}"
})
```

### **🔍 Комплексное исследование предметной области:**

```javascript
// 1. Парсинг официальной документации 1С
mcp__universal-web-scraper__scrape_website({
  url: "https://its.1c.ru/db/metod8dev/content/производство",
  adapter_type: "its_1c",
  include_links: true,
  save_to_memory: true
})

// 2. Поиск современных решений
mcp__brave-search__brave_web_search({
  query: "производственное планирование MRP JIT 1С 2025",
  count: 20
})

// 3. Парсинг экспертных статей
mcp__universal-web-scraper__scrape_website({
  url: "https://its.1c.ru/db/expertguide/content/планирование",
  adapter_type: "its_1c",
  max_depth: 2,
  save_to_memory: true
})

// 4. Поиск нормативных требований
mcp__brave-search__brave_web_search({
  query: "ГОСТ производственный учет планирование требования 2025",
  count: 15
})
```

### **📚 Создание базы знаний проекта:**

```bash
# 1. Конвертация всей документации
```
```javascript
mcp__docling__batch_convert({
  input_dir: "D:/knowledge-base/sources/",
  output_dir: "cache/knowledge-base/converted/",
  file_pattern: "*.{pdf,docx,pptx,xlsx,rtf}"
})
```

```bash
# 2. Парсинг релевантных веб-ресурсов
```
```javascript
mcp__universal-web-scraper__bulk_scrape_websites({
  urls: [
    "https://its.1c.ru/db/metod8dev",
    "https://its.1c.ru/db/expertguide",
    "https://v8.1c.ru/overview/"
  ],
  save_to_memory: true
})
```

```bash
# 3. Исследование дополнительных источников
```
```javascript
mcp__brave-search__brave_web_search({
  query: "предметная_область лучшие практики автоматизация",
  count: 25
})
```

### **📖 Создание технической документации:**

```bash
# 1. Универсальный парсинг документации технологий
python scripts/1c-docs-parser/universal-documentation-parser.py \
  "https://docs.технология.com" \
  --max-pages 100 \
  --format markdown
```

```javascript
// 2. Конвертация внутренней документации
mcp__docling__convert_document({
  input_path: "D:/internal-docs/Регламент_разработки.pdf",
  output_path: "cache/internal/development-regulations.md",
  ocr_enabled: true
})

// 3. Анализ структуры существующих документов
mcp__docling__analyze_document_structure({
  input_path: "D:/templates/Шаблон_документации.docx",
  include_content: false
})
```

---

## 🔗 Интеграция с другими инструментами

### **Memory MCP интеграция:**
```bash
# Workflow: Docling → Memory MCP → Knowledge Graph
python scripts/mcp-integration/docling-workflow.py --input "docs/" --batch
python scripts/mcp-integration/docling-memory-integration.py \
  --source "cache/docling-output/" \
  --entity-type "documentation" \
  --save-to-graph
```

### **BSL Analysis интеграция:**
```bash
# Workflow: BSL Analysis → Docling → Reports
python -m sonar_integration analyze --src-dir src/ --output-format json
python scripts/mcp-integration/docling-workflow.py \
  --input "reports/analysis.json" \
  --output "cache/analysis-docs/" \
  --convert-json-to-markdown
```

### **Task Master интеграция:**
```bash
# Создание задач из результатов анализа документации
cd claude-task-master
npx task-master parse-from-text "Изучить техническую документацию по новой подсистеме"
```

---

## 📁 Структура выходных файлов

### **Docling выходные файлы:**
```
cache/docling-output/
├── document_name.md          # Основной Markdown файл
├── images/                   # Извлечённые изображения
│   ├── image_001.png
│   └── image_002.jpg
├── tables/                   # Извлечённые таблицы
│   ├── table_001.csv
│   └── table_002.json
└── metadata.json            # Метаданные документа
```

### **Universal Web Scraper выходные файлы:**
```
cache/web-scraper-output/
├── site_content.md          # Основной контент
├── links.json               # Извлечённые ссылки
├── images/                  # Скачанные изображения
└── metadata.json           # Метаданные сайта
```

### **1C Documentation Parser выходные файлы:**
```
Проекты/1C-Platform-Doc-Parser/
├── parsed_content/
│   ├── chapter_01.md
│   ├── chapter_02.md
│   └── ...
├── structure.json          # Иерархическая структура
└── metadata.json          # Метаданные парсинга
```

---

## ⚙️ Производительность и оптимизация

### **Docling производительность:**
- **Обычные PDF**: 1-5 страниц/секунда
- **С OCR**: 0.5-2 страницы/секунда
- **DOCX/PPTX**: 10-50 страниц/секунда
- **Пакетная обработка**: до 100 документов параллельно

### **Web Scraper производительность:**
- **Простые страницы**: 2-5 страниц/секунда
- **Сложные сайты**: 0.5-2 страницы/секунда
- **Параллельный парсинг**: до 10 сайтов одновременно
- **Контроль нагрузки**: настраиваемые задержки

### **Рекомендации по оптимизации:**
- Используйте пакетную обработку для множественных файлов
- Отключайте извлечение изображений если не требуется
- Настраивайте задержки при парсинге сайтов
- Используйте фильтры по типам файлов

---

*Руководство обновлено: 26.10.2025*  
*Поддерживаемые форматы: PDF, DOCX, PPTX, XLSX, HTML, RTF*  
*Поддерживаемые сайты: ITS 1С, GitHub Docs, MDN, React, Django и любые документационные порталы*