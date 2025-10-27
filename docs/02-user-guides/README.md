# 📚 Руководства пользователей 1C-Enterprise Framework

## 🎯 Обзор возможностей

1C-Enterprise Framework предоставляет комплексные инструменты для работы с 1С без привязки к конкретным ролям - все функции доступны всем пользователям.

---

## 🔧 Основные направления работы

### **📊 [Анализ и контроль качества кода](./code-analysis/)**
- **BSL Language Server** - анализ качества кода (793 правила)
- **AST-grep для BSL** - семантический поиск по структуре кода
- **MCP Reasoner v2.0.0** - глубокий анализ с MCTS и Beam Search
- **Serena Framework** - продвинутый анализ и рефакторинг

### **🤖 [Автоматизация и тестирование](./automation/)**
- **Task Master v0.26.0** - управление задачами (93 задачи + 535 подзадач)
- **Playwright Automation** - автотестирование веб-интерфейса
- **Git hooks** - автоматическая проверка при коммитах
- **CI/CD Pipeline** - GitHub Actions с автоматическими отчётами

### **📄 [Работа с документацией](./documentation/)**
- **Docling MCP v1.0** - конвертация PDF/DOCX в Markdown для RAG
- **Universal Web Scraper MCP** - парсинг любых веб-сайтов (5 адаптеров)
- **1C Documentation Parser v2.0** - специализированный парсер документации 1С
- **Brave Search** - поиск экспертной информации

### **🧠 [Управление знаниями](./knowledge-management/)**
- **Memory MCP** - Knowledge Graph для сохранения знаний
- **Sequential Thinking MCP** - пошаговое решение сложных задач
- **BSL Semantic Diff** - семантическое сравнение BSL кода
- **Dynamic Context Engine** - автоматический выбор инструментов

---

## 🚀 Быстрый старт

### **⚡ Анализ качества кода - начните здесь:**

```bash
# Быстрый анализ качества
python -m sonar_integration analyze --src-dir . --quick

# Семантический поиск функций в BSL
```
```javascript
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($$$ARGS)",
  path: "src/CommonModules/",
  bsl_type: "functions"
})
```

### **🔍 Поиск и исследование:**

```javascript
// Поиск в документации фреймворка
mcp__1c-framework-docs__search_docs({
  query: "семантический анализ BSL кода",
  search_type: "hybrid"
})

// Парсинг экспертных материалов
mcp__universal-web-scraper__scrape_website({
  url: "https://its.1c.ru/db/metod8dev",
  adapter_type: "its_1c",
  save_to_memory: true
})
```

### **📋 Управление задачами:**

```bash
cd claude-task-master
npx task-master list          # Просмотр всех задач
npx task-master next          # Следующая рекомендуемая задача
```

### **🧪 Автотестирование:**

```javascript
// Автоматическое тестирование веб-интерфейса
mcp__playwright-automation__playwright_navigate({
  url: "http://localhost/infobase",
  browserType: "chromium"
})
```

---

## 📋 Типовые сценарии использования

### **🔄 Полный цикл анализа проекта:**

```bash
# 1. Анализ качества кода
python -m sonar_integration analyze --src-dir src/ --output-dir reports/

# 2. Семантический анализ структуры
```
```javascript
mcp__ast-grep-mcp__ast_grep({
  pattern: "Процедура $NAME($$$ARGS) Экспорт",
  path: "src/",
  export_only: true
})
```
```bash
# 3. Глубокий анализ проблемных областей
python scripts/mcp-integration/full-analysis-pipeline.py \
  --input "src/CommonModules/" \
  --use-reasoner \
  --save-to-memory

# 4. Сохранение результатов в Knowledge Graph
```
```javascript
mcp__memory__create_entities([{
  name: "Анализ.Проект_" + new Date().toISOString().slice(0,10),
  entityType: "code_analysis",
  observations: ["Выявлено 25 замечаний", "Рекомендован рефакторинг 3 модулей"]
}])
```

### **📚 Исследование и документирование:**

```bash
# 1. Конвертация технической документации
```
```javascript
mcp__docling__batch_convert({
  input_dir: "D:/project-docs/",
  output_dir: "cache/project-md/",
  file_pattern: "*.{pdf,docx,pptx}"
})
```
```bash
# 2. Исследование предметной области
```
```javascript
mcp__brave-search__brave_web_search({
  query: "1С лучшие практики 2025 производство автоматизация",
  count: 15
})
```
```bash
# 3. Создание базы знаний
```
```javascript
mcp__memory__create_entities([{
  name: "Исследование.ЛучшиеПрактики",
  entityType: "research_result",
  observations: ["Найдено 10 ключевых принципов", "Выделены 5 anti-patterns"]
}])
```

### **🧪 Автоматизация тестирования:**

```javascript
// 1. Функциональное тестирование
mcp__playwright-automation__playwright_navigate({
  url: "http://localhost/infobase"
})

mcp__playwright-automation__playwright_fill({
  selector: "#username",
  value: "Тестировщик"
})

mcp__playwright-automation__playwright_click({
  selector: "#login-button"
})

// 2. API тестирование
mcp__playwright-automation__playwright_post({
  url: "http://localhost/infobase/hs/api/v1/test",
  value: JSON.stringify({test: "data"}),
  headers: {"Content-Type": "application/json"}
})

// 3. Создание отчёта
mcp__playwright-automation__playwright_screenshot({
  name: "test-results",
  savePng: true
})
```

---

## 🔗 Интеграция инструментов

### **🔄 Workflow разработки:**
1. **Анализ** → BSL Language Server + AST-grep
2. **Планирование** → Task Master + Sequential Thinking
3. **Реализация** → Serena Framework + Git hooks
4. **Тестирование** → Playwright Automation
5. **Документирование** → Memory MCP + Docling

### **📊 Аналитический workflow:**
1. **Исследование** → Universal Web Scraper + Brave Search
2. **Обработка документов** → Docling MCP
3. **Структурирование** → Memory MCP
4. **Анализ** → Sequential Thinking + MCP Reasoner

### **🔧 Workflow оптимизации:**
1. **Диагностика** → BSL Language Server + MCP Reasoner
2. **Планирование улучшений** → Sequential Thinking
3. **Рефакторинг** → Serena Framework
4. **Валидация** → Автотесты + повторный анализ

---

## 💡 Готовые команды и алиасы

### **Анализ качества:**
```bash
# Быстрый анализ
python -m sonar_integration analyze --quick

# Полный анализ с отчётом
python -m sonar_integration analyze && python -m sonar_integration report analysis.json --html

# Семантическое сравнение
python scripts/bsl-semantic-diff/semantic_diff_poc.py module1.bsl module2.bsl
```

### **Управление задачами:**
```bash
# Task Master
cd claude-task-master && npx task-master next

# Генерация тестов
npx task-master generate-test --id=1 --output-dir=tests/ --research
```

### **VS Code/Cursor интеграция:**
- **Ctrl+Shift+B** - анализ текущего файла
- **Ctrl+Alt+B** - полный анализ проекта
- **Ctrl+Shift+Alt+B** - генерация HTML отчёта

---

## 📊 Статус инструментов

### **✅ Полностью готовы:**
- BSL Language Server (80% интеграция)
- Task Master AI (85% готовность)
- MCP Reasoner v2.0.0 (100% готовность)
- Docling MCP v1.0 (100% готовность)
- Universal Web Scraper MCP (100% готовность)
- Playwright Automation (95% готовность)
- Git Automation (90% готовность)

### **⚙️ В разработке:**
- Расширенная интеграция с IDE
- Дополнительные MCP серверы
- Улучшение производительности

---

## 🔗 Дополнительные ресурсы

- **[🚀 Быстрый старт](../01-getting-started/quick-start.md)** - Установка и первые шаги
- **[🔧 Техническая справка](../05-reference/)** - API и команды
- **[💡 Примеры](../04-examples/)** - Практические кейсы
- **[📖 Полная документация](../README.md)** - Обзор всего фреймворка

---

*Документация обновлена: 26.10.2025*  
*Версия фреймворка: 2025.10.26 PRODUCTION*  
*Функциональный подход без ролевых ограничений*