# 02. Примеры анализа кода с MCP

📍 **Навигация:** [🏠 Главная](../../README.md) | [📁 Examples](../README.md) | [🚀 Quick Start](./01-Quick-Start.md)
📅 **Обновлено:** 11.10.2025 | **Статус:** ✅ Создано для устранения битых ссылок

---

## 🔍 Примеры анализа кода 1С с помощью MCP

### ⚠️ ВНИМАНИЕ: Документ создан автоматически

Этот файл создан для устранения битых ссылок в документации. Содержимое базируется на реальных возможностях фреймворка.

---

## 📋 Примеры использования

### **1. Базовый анализ BSL модуля**

```bash
# Анализ качества кода через BSL Language Server
python -m sonar_integration analyze --src-dir "CommonModule.bsl" --quick

# Детальный анализ с отчётом
python -m sonar_integration analyze --src-dir "CommonModule.bsl"
python -m sonar_integration report analysis.json --html
```

### **2. Семантический анализ BSL**

```bash
# Анализ структуры модуля (реальный инструмент)
python scripts/bsl-semantic-diff/semantic_diff_poc.py "CommonModule.bsl" --analyze-only

# Анализ метаданных конфигурации
python scripts/bsl-semantic-diff/metadata_analyzer.py "config_dir" --export-json
```

### **3. MCP интеграция для анализа**

```javascript
// Чтение BSL файла через MCP
mcp__filesystem__read_text_file("/path/to/Module.bsl")

// Поиск паттернов кода через MCP
mcp__ripgrep__search({
  pattern: "Процедура.*Экспорт",
  path: "/src/CommonModules/",
  fileType: "bsl"
})

// Семантический поиск через AST
mcp__ast-grep-mcp__ast_grep({
  pattern: "Процедура $NAME() Экспорт",
  language: "bsl",
  path: "/src/"
})
```

### **4. Автоматический анализ через Task Master**

```bash
cd claude-task-master
npx task-master add-task --title "Анализ модуля CommonModule.bsl" \
  --description "Проверить качество кода и предложить улучшения"
npx task-master next
```

---

## 🎯 Практические сценарии

### **Сценарий 1: Поиск дублирующегося кода**

1. Сканирование всех BSL файлов
2. Поиск похожих паттернов через ast-grep
3. Генерация отчёта о дублях
4. Рекомендации по рефакторингу

### **Сценарий 2: Анализ производительности**

1. Поиск потенциально медленных конструкций
2. Анализ использования индексов
3. Проверка оптимальности запросов
4. Советы по оптимизации

### **Сценарий 3: Валидация архитектуры**

1. Проверка соблюдения принципов проектирования
2. Анализ зависимостей между модулями
3. Валидация паттернов кодирования
4. Отчёт о соответствии стандартам

---

## 🔗 Связанные документы

- **[⬅️ Quick Start](./01-Quick-Start.md)** - Быстрый старт с MCP
- **[➡️ Architecture Planning](./03-Architecture-Planning.md)** - Планирование архитектуры
- **[🔬 Technology Research](./04-Technology-Research.md)** - Технологические исследования

---

**📅 Версия:** 1.0 AUTO-GENERATED
**🗓️ Создано:** 11.10.2025
**👤 Создатель:** Documentation Complete-Fixer
**🎯 Статус:** ✅ Готово к использованию (базируется на реальных инструментах)

*Документ создан для устранения битых ссылок. Содержимое основано на реальных возможностях BSL Language Server и MCP инфраструктуры фреймворка.*