# 🔍 Улучшенные правила поиска с MCP инструментами

## 🎯 Обзор возможностей

На основе внедренных MCP серверов доступны следующие инструменты поиска:

### ✅ **Активные MCP инструменты:**
- **AST-grep MCP**: Структурный поиск кода BSL/1C с BSL-специфичными типами
- **Brave Search MCP**: Поиск в интернете и GitHub через Brave Search API
- **GitHub MCP**: Прямой поиск по репозиториям GitHub
- **Filesystem MCP**: Локальный поиск по файлам проекта
- **Ripgrep MCP**: Быстрый текстовый поиск с regex поддержкой
- **Sequential Thinking MCP**: Сложное пошаговое планирование поиска
- **Memory MCP**: Knowledge Graph для сохранения найденной информации

## 🌐 Правила поиска в интернете

### **ПРИОРИТЕТ 1: Brave Search MCP (РЕКОМЕНДУЕТСЯ)**

#### **Базовый поиск 1С информации:**
```javascript
// Поиск общей информации
mcp__brave-search__brave_web_search({
  query: "1С:Предприятие BSL best practices",
  count: 10
})

// Поиск конкретных решений
mcp__brave-search__brave_web_search({
  query: "1С процедура проведения документа примеры",
  count: 15
})

// Поиск ошибок и их решений
mcp__brave-search__brave_web_search({
  query: "1С ошибка 'Нарушение типа' решение",
  count: 10
})
```

#### **Локальный поиск (для китайских ресурсов):**
```javascript
// Поиск в китайских репозиториях на Gitee
mcp__brave-search__brave_local_search({
  query: "1С конфигурация управление торговлей",
  count: 5
})
```

#### **Эффективные запросы для 1С:**
- **Документация**: `"1С:Предприятие 8" документация [конкретная тема]`
- **Примеры кода**: `BSL "процедура" "функция" [описание задачи]`
- **Решения ошибок**: `"1С ошибка" "[текст ошибки]" решение`
- **Best practices**: `"1С разработка" стандарты кодирования`
- **Типовые конфигурации**: `"УТ 11" "УПП" "БП" [функциональность]`

### **ПРИОРИТЕТ 2: WebSearch (резерв)**

```javascript
// Когда Brave Search недоступен
WebSearch({
  query: "1С:Предприятие разработка [тема]",
  allowed_domains: ["infostart.ru", "forum.infostart.ru", "1c.ru"]
})
```

## 🐙 Правила поиска на GitHub

### **ПРИОРИТЕТ 1: GitHub MCP (прямой доступ)**

#### **Поиск BSL кода:**
```javascript
// Поиск по коду
mcp__github__search_code({
  q: "Процедура ПроведениеДокумента language:bsl",
  per_page: 20
})

// Поиск в конкретной организации
mcp__github__search_code({
  q: "org:1c-syntax функция экспорт language:bsl",
  per_page: 15
})

// Поиск с фильтрами по размеру и дате
mcp__github__search_code({
  q: "ОбщийМодуль size:>1000 pushed:>2023-01-01 language:bsl",
  per_page: 10
})
```

#### **Поиск репозиториев:**
```javascript
// Поиск 1С репозиториев
mcp__github__search_repositories({
  query: "1С Enterprise BSL stars:>10",
  per_page: 20
})

// Поиск типовых конфигураций
mcp__github__search_repositories({
  query: "УТ управление торговлей 1с language:bsl",
  per_page: 15
})
```

#### **Получение файлов:**
```javascript
// Чтение конкретного BSL файла
mcp__github__get_file_contents({
  owner: "1c-syntax",
  repo: "bsl-language-server",
  path: "src/main/java/com/github/_1c_syntax/bsl/languageserver/diagnostics"
})
```

### **ПРИОРИТЕТ 2: Brave Search для GitHub**

```javascript
// Когда нужен более широкий поиск
mcp__brave-search__brave_web_search({
  query: "site:github.com BSL 1С процедура проведения",
  count: 15
})
```

## 🏗️ Структурный поиск кода (AST-grep MCP)

### **BSL-специфичный поиск:**

#### **Поиск процедур и функций:**
```javascript
// Все экспортные процедуры
mcp__ast-grep-mcp__ast_grep({
  pattern: "Процедура $NAME($PARAMS) Экспорт",
  language: "bsl",
  bsl_type: "procedures",
  export_only: true,
  path: "src/CommonModules/"
})

// Функции с возвращаемым значением
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($PARAMS)",
  language: "bsl",
  bsl_type: "functions",
  context: 3
})
```

#### **Поиск конструкций 1С:**
```javascript
// Поиск блоков Try-Catch
mcp__ast-grep-mcp__ast_grep({
  pattern: "Попытка",
  language: "bsl",
  context: 5,
  head_limit: 20
})

// Поиск запросов
mcp__ast-grep-mcp__ast_grep({
  pattern: "Запрос = Новый Запрос",
  language: "bsl",
  bsl_type: "text"
})

// Поиск обработчиков событий
mcp__ast-grep-mcp__ast_grep({
  pattern: "Процедура.*При.*",
  language: "bsl",
  bsl_type: "procedures"
})
```

#### **Рефакторинг с заменой:**
```javascript
// Замена устаревших конструкций
mcp__ast-grep-mcp__ast_grep({
  pattern: "Сообщить($MSG)",
  replacement: "ОбщегоНазначения.СообщитьПользователю($MSG)",
  language: "bsl",
  mode: "replace",
  dry_run: true
})
```

## 📁 Локальный поиск файлов

### **Filesystem MCP:**

```javascript
// Поиск BSL файлов
mcp__filesystem__search_files({
  path: "src/projects/configuration",
  pattern: "*.bsl"
})

// Чтение множественных файлов
mcp__filesystem__read_multiple_files({
  paths: [
    "src/CommonModules/ОбщегоНазначения.bsl",
    "src/CommonModules/РаботаСФайлами.bsl"
  ]
})
```

### **Ripgrep MCP (быстрый текстовый поиск):**

```javascript
// Поиск с regex
mcp__ripgrep__search({
  pattern: "Процедура\\s+\\w+.*Экспорт",
  path: "src/",
  filePattern: "*.bsl"
})

// Подсчет совпадений
mcp__ripgrep__count-matches({
  pattern: "ОбщегоНазначения\\.",
  path: "src/",
  filePattern: "*.bsl"
})

// Поиск только в определенных типах файлов
mcp__ripgrep__advanced-search({
  pattern: "УстановитьПривилегированныйРежим",
  path: "src/",
  fileType: "bsl",
  showLineNumbers: true,
  context: 2
})
```

## 🧠 Сложное планирование поиска

### **Sequential Thinking для комплексного поиска:**

```javascript
mcp__sequential-thinking__sequentialthinking({
  thought: "Нужно найти все способы работы с файлами в 1С конфигурации: встроенные функции, общие модули, типовые решения",
  thoughtNumber: 1,
  totalThoughts: 8,
  nextThoughtNeeded: true
})

// Последующие шаги:
// 1. Поиск встроенных функций через AST-grep
// 2. Поиск в общих модулях через Filesystem
// 3. Поиск в интернете через Brave Search
// 4. Поиск примеров на GitHub
// 5. Анализ найденной информации
// 6. Сохранение в Memory MCP
```

## 💾 Сохранение результатов поиска

### **Memory MCP для Knowledge Graph:**

```javascript
// Создание сущности с результатами поиска
mcp__memory__create_entities([{
  name: "Работа_с_файлами_1С",
  entityType: "search_results",
  observations: [
    "Найдено 15 общих модулей для работы с файлами",
    "Типовое решение: РаботаСФайлами из БСП",
    "GitHub: 23 репозитория с примерами"
  ]
}])

// Связывание с источниками
mcp__memory__create_relations([{
  from: "Работа_с_файлами_1С",
  to: "BSL_Language_Server",
  relationType: "found_in_repository"
}])

// Поиск сохраненной информации
mcp__memory__search_nodes("файлы 1С")
```

## 📊 Эффективные стратегии поиска

### **1. Поэтапный поиск (рекомендуется):**

```javascript
// Этап 1: Локальный поиск
mcp__ast-grep-mcp__ast_grep({
  pattern: "целевая_функция",
  language: "bsl",
  path: "src/"
})

// Этап 2: GitHub поиск при отсутствии локальных результатов
if (local_results.length === 0) {
  mcp__github__search_code({
    q: "целевая_функция language:bsl",
    per_page: 20
  })
}

// Этап 3: Интернет поиск для контекста
mcp__brave-search__brave_web_search({
  query: "1С целевая_функция примеры использования",
  count: 10
})

// Этап 4: Сохранение комплексных результатов
mcp__memory__create_entities([{
  name: "Поиск_целевая_функция",
  entityType: "comprehensive_search",
  observations: ["Локально: X результатов", "GitHub: Y результатов", "Интернет: Z ссылок"]
}])
```

### **2. Тематический поиск:**

#### **Производительность:**
- **AST-grep**: поиск циклов, запросов, алгоритмов
- **GitHub**: репозитории с тегами "performance", "optimization"
- **Brave Search**: статьи про оптимизацию 1С

#### **Безопасность:**
- **AST-grep**: поиск привилегированного режима, RLS
- **GitHub**: примеры реализации безопасности
- **Brave Search**: рекомендации по безопасности 1С

#### **Интеграции:**
- **AST-grep**: поиск HTTP запросов, web-сервисов
- **GitHub**: интеграционные решения
- **Brave Search**: документация по API

### **3. Отладка и решение проблем:**

```javascript
// Поиск конкретной ошибки
const error_text = "Нарушение доступа при записи объекта";

// 1. Локальный поиск кода с похожими проблемами
mcp__ripgrep__search({
  pattern: "Нарушение доступа",
  path: "src/",
  context: 5
})

// 2. Поиск решений в интернете
mcp__brave-search__brave_web_search({
  query: `"${error_text}" 1С решение`,
  count: 15
})

// 3. Поиск в GitHub issues
mcp__github__search_code({
  q: `"${error_text}" type:issue language:bsl`,
  per_page: 10
})
```

## 🎯 Комбинированные workflow

### **Workflow 1: Исследование новой функциональности**

```bash
# 1. Sequential Thinking для планирования
# 2. AST-grep для поиска существующих реализаций
# 3. GitHub для поиска примеров
# 4. Brave Search для документации
# 5. Memory для сохранения архитектурного решения
```

### **Workflow 2: Отладка проблемы**

```bash
# 1. Ripgrep для поиска ошибки в логах
# 2. AST-grep для поиска проблемного кода
# 3. Brave Search для поиска решений
# 4. GitHub для поиска похожих issues
# 5. Memory для сохранения решения
```

### **Workflow 3: Изучение best practices**

```bash
# 1. GitHub поиск популярных репозиториев
# 2. AST-grep анализ паттернов кода
# 3. Brave Search поиск статей и рекомендаций
# 4. Sequential Thinking для анализа
# 5. Memory для создания knowledge base
```

## ⚠️ Ограничения и рекомендации

### **Лимиты использования:**
- **Brave Search**: до 100 запросов/день
- **GitHub API**: до 5000 запросов/час
- **AST-grep**: ограничения на размер файлов (50MB)
- **Sequential Thinking**: сложные задачи требуют больше времени

### **Рекомендации по оптимизации:**
1. **Кэширование**: сохраняйте результаты в Memory MCP
2. **Батчинг**: группируйте похожие запросы
3. **Фильтрация**: используйте конкретные домены и фильтры
4. **Приоритизация**: начинайте с локального поиска

### **Обработка ошибок:**
```javascript
// Fallback стратегия
try {
  // Попытка AST-grep поиска
  result = await mcp__ast-grep-mcp__ast_grep(params);
} catch (error) {
  // Fallback на Ripgrep
  result = await mcp__ripgrep__search(fallback_params);
}
```

## 📈 Метрики эффективности

### **Отслеживание результативности:**
- Время поиска по источникам
- Количество релевантных результатов
- Успешность решения задач
- Использование кэшированных данных

### **Еженедельный анализ:**
```markdown
## Отчет по поиску (неделя)

**MCP инструменты:**
- AST-grep: X запросов, Y% успешных
- GitHub: X запросов, Y релевантных результатов
- Brave Search: X запросов, Y полезных ссылок
- Memory: X сохраненных результатов, Y повторных использований

**Эффективность:**
- Среднее время решения задач: X минут
- Процент задач, решенных без интернет поиска: Y%
- Повторное использование сохраненных знаний: Z%
```

---

**Версия**: 1.0
**Дата обновления**: 27.09.2025
**Базируется на**: Актуальных MCP серверах (AST-grep, Brave Search, GitHub, Memory, Sequential Thinking)