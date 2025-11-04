# 01. Быстрый старт с MCP

📍 **Навигация:** [🏠 Главная](../README.md) | [📁 Examples](../README.md)
📅 **Обновлено:** 11.10.2025 | **Статус:** ✅ Создано для устранения битых ссылок

---

## 🚀 Быстрый старт с MCP для разработки 1С

### ⚠️ ВНИМАНИЕ: Документ создан автоматически

Этот файл создан для устранения битых ссылок. Содержимое базируется на реальных возможностях MCP серверов и инструментов фреймворка.

---

## 📋 Первые шаги с MCP

### **1. Проверка готовности системы**

```bash
# Переходим в корневую директорию фреймворка
cd "D:\1C-Enterprise_Framework"

# Проверяем доступность MCP серверов
python scripts/check-mcp-status.py

# Проверяем интеграцию с Task Master
cd claude-task-master
npx task-master status
```

### **2. Базовые MCP операции**

#### **Работа с файловой системой:**
```javascript
// Чтение BSL файла
mcp__filesystem__read_text_file("/src/projects/configuration/CommonModules/Module.bsl")

// Получение списка файлов
mcp__filesystem__list_directory("/src/projects/configuration/CommonModules/")

// Поиск BSL файлов
mcp__filesystem__search_files("/src/", "*.bsl")
```

#### **Интеграция с GitHub:**
```javascript
// Поиск примеров кода
mcp__github__search_code({
  q: "1C BSL best practices"
})

// Получение содержимого файла
mcp__github__get_file_contents("owner", "repo", "path/to/module.bsl")
```

#### **Memory операции:**
```javascript
// Создание записи о модуле
mcp__memory__create_entities([{
  name: "ОбщийМодуль.УтилитыРаботыСДанными",
  entityType: "bsl_module",
  observations: ["Экспортный модуль", "Содержит функции работы с данными"]
}])

// Поиск по базе знаний
mcp__memory__search_nodes("общий модуль")
```

### **3. Интеграция с BSL анализом**

```bash
# Быстрый анализ модуля
python -m sonar_integration analyze --src-dir "Module.bsl" --quick

# Сохранение результатов в MCP Memory
python scripts/mcp-integration/bsl-memory-integration.py "reports/analysis.json"
```

---

## 🎯 Практические сценарии

### **Сценарий 1: Анализ качества BSL модуля**

```bash
# Шаг 1: Анализируем модуль
python -m sonar_integration analyze --src-dir "CommonModule.bsl"

# Шаг 2: Создаём задачу в Task Master
cd claude-task-master
npx task-master add-task --title "Fix BSL issues in CommonModule" --tag "code-quality"

# Шаг 3: Сохраняем результаты в Memory
# Автоматически через интеграционные скрипты
```

### **Сценарий 2: Поиск и анализ паттернов кода**

```javascript
// Поиск через ripgrep MCP
mcp__ripgrep__search({
  pattern: "Процедура.*Экспорт",
  path: "/src/CommonModules/",
  fileType: "bsl"
})

// AST-grep для семантического поиска
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME() Экспорт",
  language: "bsl",
  path: "/src/"
})
```

### **Сценарий 3: Автоматизация рутинных задач**

```bash
# Автоматический анализ всех модулей
for module in src/CommonModules/*.bsl; do
  python -m sonar_integration analyze --src-dir "$module" --quick
done

# Создание отчёта
python -m sonar_integration report "reports/analysis.json" --html
```

---

## 🔧 Настройка и конфигурация

### **Проверка зависимостей:**
```bash
# Python зависимости
pip install -r requirements.txt

# Node.js зависимости для Task Master
cd claude-task-master
npm install

# Проверка BSL Language Server
python -m sonar_integration --version
```

### **Переменные окружения:**
```bash
# Для корректной работы с русскими символами
set PYTHONIOENCODING=utf-8

# MCP настройки
set MCP_TIMEOUT=120250
set MCP_DEBUG=false
```

---

## 📊 Полезные команды

### **Task Master быстрые команды:**
```bash
cd claude-task-master

# Просмотр всех задач
npx task-master list

# Следующая рекомендуемая задача
npx task-master next

# Создание задачи из текста
npx task-master parse-from-text "Проанализировать модуль ОбщийМодуль.УтилитыРаботыСДанными"
```

### **BSL анализ быстрые команды:**
```bash
# Анализ одного файла
python -m sonar_integration analyze --src-dir "Module.bsl" --quick

# Анализ папки с модулями
python -m sonar_integration analyze --src-dir "src/CommonModules/"

# Генерация HTML отчёта
python -m sonar_integration report "analysis.json" --html
```

---

## 🚨 Распространённые проблемы

### **Проблема: Ошибки кодировки**
```bash
# Решение: установить правильную кодировку
set PYTHONIOENCODING=utf-8
chcp 65001
```

### **Проблема: MCP сервер недоступен**
```bash
# Проверка статуса серверов
python scripts/check-mcp-status.py

# Перезапуск при необходимости
python scripts/restart-mcp-servers.py
```

### **Проблема: BSL Language Server не найден**
```bash
# Проверка установки
python -m sonar_integration --version

# Переустановка при необходимости
pip install --upgrade sonar-integration
```

---

## 🔗 Следующие шаги

1. **[🔍 Code Analysis](./02-Code-Analysis-Examples.md)** - Детальные примеры анализа кода
2. **[🏗️ Architecture Planning](./03-Architecture-Planning.md)** - Планирование архитектуры
3. **[🔬 Technology Research](./04-Technology-Research.md)** - Технологические исследования

---

## 🔗 Связанные документы

- **[📋 Task Master](../claude-task-master/README.md)** - Управление задачами
- **[🔧 BSL Integration](../API Documentation/bsl-language-server-integration.md)** - Интеграция BSL Language Server
- **[📚 MCP Commands](../API Documentation/mcp-commands-reference.md)** - Справочник MCP команд

---

**📅 Версия:** 1.0 AUTO-GENERATED
**🗓️ Создано:** 11.10.2025
**👤 Создатель:** Documentation Complete-Fixer
**🎯 Статус:** ✅ Готово к использованию (базируется на реальных MCP серверах)

*Документ создан для устранения битых ссылок. Содержимое основано на реальных возможностях MCP серверов: Filesystem, GitHub, Memory, Ripgrep, AST-grep.*