# 📊 Анализ и контроль качества кода

## 🎯 Обзор инструментов анализа

Фреймворк предоставляет комплексные инструменты для анализа качества BSL кода, семантического поиска и глубокого анализа архитектуры.

---

## 🔧 Основные инструменты

### **1. BSL Language Server - Анализ качества кода**

**793 правила анализа** для контроля качества BSL кода с автоматической категоризацией по критичности.

#### **Быстрый старт:**
```bash
# Анализ текущего файла
python -m sonar_integration analyze --src-dir "Module.bsl" --quick

# Полный анализ проекта
python -m sonar_integration analyze --src-dir "src/" --output-dir "reports/"

# Генерация отчётов (HTML + Excel + CSV)
python -m sonar_integration report "reports/analysis.json" --html --excel --csv
```

#### **Фильтрация по критичности:**
```bash
# Только критичные ошибки
python -m sonar_integration analyze --severity CRITICAL,BLOCKER --src-dir .

# Анализ конкретной папки
python -m sonar_integration analyze --src-dir "src/CommonModules/"

# Быстрая проверка изменений
git diff --name-only | grep "\.bsl$" | xargs python -m sonar_integration analyze --src-dir
```

#### **Уровни критичности:**
- **🔴 BLOCKER** - Критические ошибки (блокируют PR)
- **🟠 CRITICAL** - Серьёзные проблемы безопасности и производительности
- **🟡 MAJOR** - Важные замечания по качеству кода
- **🔵 MINOR** - Мелкие улучшения стиля
- **⚪ INFO** - Информационные сообщения

---

### **2. AST-grep для BSL - Семантический поиск**

**Структурный анализ** BSL кода через AST дерево с поддержкой сложных паттернов.

#### **Поиск функций и процедур:**
```javascript
// Все экспортные функции
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($$$ARGS) Экспорт",
  path: "src/CommonModules/",
  bsl_type: "functions",
  export_only: true
})

// Процедуры с конкретным паттерном
mcp__ast-grep-mcp__ast_grep({
  pattern: "Процедура $NAME($PARAM) Если $PARAM = Неопределено Тогда Возврат КонецЕсли",
  path: "src/",
  context: 2
})

// Поиск блоков обработки исключений
mcp__ast-grep-mcp__ast_grep({
  pattern: "Попытка $BODY Исключение $HANDLER КонецПопытки",
  path: "src/",
  multiline: true
})
```

#### **Поиск потенциальных проблем:**
```javascript
// Пустые обработчики исключений
mcp__ast-grep-mcp__ast_grep({
  pattern: "Попытка $BODY Исключение КонецПопытки",
  path: "src/",
  mode: "count"
})

// Функции без возврата значения
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($$$ARGS) $BODY КонецФункции",
  path: "src/",
  mode: "search"
})

// Использование устаревших методов
mcp__ast-grep-mcp__ast_grep({
  pattern: "$OBJ.УстаревшийМетод($$$ARGS)",
  path: "src/"
})
```

#### **Массовый рефакторинг:**
```javascript
// Добавление документации к функциям
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($$$ARGS) Экспорт",
  replacement: "// TODO: Добавить описание функции\\nФункция $NAME($$$ARGS) Экспорт",
  mode: "replace",
  dry_run: true  // Предварительный просмотр
})

// Замена устаревших конструкций
mcp__ast-grep-mcp__ast_grep({
  pattern: "СтрДлина($STR)",
  replacement: "СтрДлина($STR)",
  mode: "replace"
})
```

---

### **3. MCP Reasoner v2.0.0 - Глубокий анализ**

**MCTS и Beam Search** для анализа сложных архитектурных проблем и поиска неочевидных зависимостей.

#### **Подготовка задач для анализа:**
```bash
# Подготовка задачи для глубокого анализа
python scripts/mcp-integration/bsl-reasoner-integration.py "src/CommonModules/ComplexModule.bsl"

# Полный pipeline с сохранением в Knowledge Graph
python scripts/mcp-integration/full-analysis-pipeline.py \
  --input "src/Documents/ImportantDocument/" \
  --output "reports/deep-analysis" \
  --use-reasoner \
  --save-to-memory
```

#### **Готовые сценарии анализа:**
- **Анализ проведения документа** - `scripts/mcp-integration/scenarios/01-document-posting-analysis.md`
- **Поиск дублирующегося кода** - `scripts/mcp-integration/scenarios/02-duplicate-code-analysis.md`
- **Граф зависимостей конфигурации** - `scripts/mcp-integration/scenarios/03-dependency-graph-analysis.md`

#### **Возможности анализа:**
- **Архитектурный анализ** - циклы, зависимости, "божественные объекты"
- **Анализ производительности** - запросы в циклах, сложность O(n)
- **Поиск дублирующегося кода** - семантическое сравнение
- **Оценка соответствия best practices** - автоматическая проверка

#### **Стратегии анализа:**
- **Beam Search** - быстрый анализ простых проблем (30 сек - 2 мин)
- **MCTS** - глубокий анализ сложных задач (2-10 мин)

---

### **4. Serena Framework - Продвинутый анализ**

**Контекстный анализ** с пониманием архитектуры 1С и возможностями рефакторинга.

#### **Анализ структуры:**
```javascript
// Обзор символов в файле
mcp__serena__get_symbols_overview({
  relative_path: "CommonModules/UtilsModule.bsl"
})

// Поиск конкретного символа
mcp__serena__find_symbol({
  name_path: "ОбработатьДанные",
  relative_path: "ObjectModule.bsl",
  include_body: true,
  depth: 1
})

// Анализ зависимостей
mcp__serena__find_referencing_symbols({
  name_path: "УстаревшаяФункция",
  relative_path: "Module.bsl"
})
```

#### **Поиск паттернов:**
```javascript
// Поиск по тексту с контекстом
mcp__serena__search_for_pattern({
  substring_pattern: "Попытка.*Исключение.*КонецПопытки",
  relative_path: "src/",
  context_lines_before: 2,
  context_lines_after: 2
})

// Поиск в конкретном типе файлов
mcp__serena__search_for_pattern({
  substring_pattern: "ВЫБРАТЬ.*ИЗ.*ГДЕ",
  paths_include_glob: "*.bsl",
  restrict_search_to_code_files: true
})
```

#### **Рефакторинг кода:**
```javascript
// Замена тела функции
mcp__serena__replace_symbol_body({
  name_path: "УстаревшаяФункция",
  relative_path: "Module.bsl",
  body: "// Новая улучшенная реализация\nВозврат НовыйАлгоритм();"
})

// Добавление новой функции
mcp__serena__insert_after_symbol({
  name_path: "СуществующаяФункция",
  relative_path: "Module.bsl",
  body: "\n\nПроцедура НоваяПроцедура() Экспорт\n\t// Реализация\nКонецПроцедуры"
})
```

---

### **5. BSL Semantic Diff - Семантическое сравнение**

**Интеллектуальное сравнение** BSL файлов с пониманием структуры и семантики.

#### **Анализ отдельного модуля:**
```bash
# Структурный анализ модуля
python scripts/bsl-semantic-diff/semantic_diff_poc.py "CommonModule.bsl" --analyze-only

# Анализ метаданных
python scripts/bsl-semantic-diff/metadata_analyzer.py "src/Documents/" --export-json

# Архитектурный обзор конфигурации
python scripts/bsl-semantic-diff/compare-configs.py "src/" --analyze-architecture
```

#### **Сравнение версий:**
```bash
# Сравнение двух версий файла
python scripts/bsl-semantic-diff/semantic_diff_poc.py \
  "old_version/Module.bsl" \
  "new_version/Module.bsl"

# Сравнение конфигураций с метаданными
python scripts/bsl-semantic-diff/compare-configs.py \
  "config_v1/" \
  "config_v2/" \
  "comparison_report.txt" \
  --metadata
```

---

## 📋 Практические сценарии

### **🔍 Комплексный анализ проекта:**

```bash
# 1. Базовый анализ качества
python -m sonar_integration analyze --src-dir "src/" --output-dir "reports/"

# 2. Семантический анализ структуры
```
```javascript
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($$$ARGS)",
  path: "src/",
  bsl_type: "functions",
  mode: "count"
})
```
```bash
# 3. Глубокий анализ проблемных областей
python scripts/mcp-integration/full-analysis-pipeline.py \
  --input "src/CommonModules/" \
  --use-reasoner \
  --save-to-memory

# 4. Генерация итогового отчёта
python -m sonar_integration report "reports/analysis.json" --html
start "reports/report.html"
```

### **🔧 Поиск и устранение технического долга:**

```javascript
// 1. Поиск пустых обработчиков исключений
mcp__ast-grep-mcp__ast_grep({
  pattern: "Попытка $BODY Исключение КонецПопытки",
  path: "src/",
  context: 1
})

// 2. Поиск дублирующегося кода
mcp__serena__search_for_pattern({
  substring_pattern: "Если.*Неопределено.*Тогда.*Возврат",
  relative_path: "src/",
  context_lines_before: 2,
  context_lines_after: 2
})

// 3. Анализ сложных функций
mcp__serena__find_symbol({
  name_path: "СложнаяФункция",
  include_body: true,
  relative_path: "Module.bsl"
})
```

### **📊 Анализ архитектуры и зависимостей:**

```bash
# 1. Анализ структуры конфигурации
python scripts/bsl-semantic-diff/compare-configs.py "src/" --analyze-architecture

# 2. Подготовка задачи для глубокого анализа зависимостей
python scripts/mcp-integration/bsl-reasoner-integration.py "src/"

# 3. Использование MCP Reasoner для анализа (в Claude Desktop)
# Загрузить задачу из cache/reasoner-task.json и применить MCTS стратегию
```

### **🎯 Целевой рефакторинг:**

```javascript
// 1. Поиск целевых функций для рефакторинга
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($$$ARGS) $$$BODY КонецФункции",
  path: "src/CommonModules/TargetModule.bsl"
})

// 2. Анализ использования функции
mcp__serena__find_referencing_symbols({
  name_path: "ЦелеваяФункция",
  relative_path: "CommonModules/TargetModule.bsl"
})

// 3. Рефакторинг с сохранением совместимости
mcp__serena__replace_symbol_body({
  name_path: "ЦелеваяФункция",
  relative_path: "CommonModules/TargetModule.bsl",
  body: "// Улучшенная реализация\nВозврат НовыйОптимизированныйАлгоритм();"
})
```

---

## 🔗 Интеграция и автоматизация

### **Git hooks интеграция:**
- Автоматическая проверка качества при коммитах
- Блокировка коммитов с BLOCKER ошибками
- Генерация отчётов для changed файлов

### **VS Code/Cursor интеграция:**
- **Ctrl+Shift+B** - анализ текущего файла
- **Ctrl+Alt+B** - полный анализ проекта
- **Ctrl+Shift+Alt+B** - генерация HTML отчёта

### **CI/CD Pipeline:**
- GitHub Actions с автоматическими проверками
- Автоматические комментарии в PR с результатами
- Блокировка PR при критичных ошибках

---

## 📈 Метрики и отчётность

### **Доступные метрики:**
- Количество нарушений по категориям
- Сложность кода (цикломатическая, когнитивная)
- Покрытие анализом (% проанализированного кода)
- Динамика изменений качества

### **Форматы отчётов:**
- **HTML** - интерактивные отчёты с навигацией
- **Excel** - табличные данные для анализа
- **CSV** - данные для импорта в другие системы
- **JSON** - программный доступ к результатам

---

*Руководство обновлено: 26.10.2025*  
*Поддерживаемые версии: 1C:Enterprise 8.3.26+, BSL Language Server, MCP Reasoner v2.0.0*