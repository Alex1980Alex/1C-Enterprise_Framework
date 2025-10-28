# MCP Priority Rules - Правила приоритизации инструментов

> **Цель:** Автоматически использовать специализированные MCP инструменты вместо базовых инструментов для повышения эффективности работы.

## 🎯 Основной принцип

**Семантические операции → MCP серверы**
**Текстовые операции → Стандартные инструменты**

## 🔴 ОБЯЗАТЕЛЬНОЕ ПРАВИЛО для BSL файлов

**ВСЕГДА используй `mcp__ast-grep-mcp__ast_grep` для анализа структуры BSL файлов**

**Почему:**
- ✅ BSL Language Server часто НЕ видит функции из-за сложного синтаксиса
- ✅ AST-grep работает ВСЕГДА, независимо от регистрации проекта в Serena
- ✅ Проверено и надежно работает на всех проектах

---

## 📋 Матрица решений по типу задачи

### 1️⃣ **Анализ структуры BSL кода** ⭐

#### ✅ ПРИОРИТЕТ 1: `mcp__ast-grep-mcp__ast_grep` (ОБЯЗАТЕЛЬНО)
```javascript
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($$$ARGS)",
  path: "src/DataProcessors/Module/Ext/ObjectModule.bsl",
  bsl_type: "functions"
})
```

#### ⚠️ Альтернатива: `mcp__serena__get_symbols_overview`
```javascript
// Использовать ТОЛЬКО если проект зарегистрирован и Language Server работает
mcp__serena__get_symbols_overview({
  relative_path: "src/.../Module.bsl"
})
```

**Когда использовать AST-grep:**
- ✅ **ВСЕГДА** для BSL файлов (основной метод)
- Нужен обзор всех процедур/функций в модуле
- Анализ структуры незнакомого файла
- Поиск только экспортных процедур (`export_only: true`)
- Проект не зарегистрирован в Serena

**Вместо:** `Read` + ручной анализ

**Преимущества AST-grep:**
- Работает без Language Server
- Не требует регистрации проекта
- Находит ВСЕ функции/процедуры
- Поддержка паттернов с переменными ($NAME, $ARGS)

---

### 2️⃣ **Поиск конкретной процедуры/функции** ⭐

#### ✅ ПРИОРИТЕТ 1: `mcp__ast-grep-mcp__ast_grep` (ОБЯЗАТЕЛЬНО)
```javascript
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция ПроверитьСовпадениеДанныхСПервойСтрокой($$$ARGS)",
  path: "Forms/Форма/Ext/Form/Module.bsl",
  bsl_type: "functions"
})
```

#### ⚠️ Альтернатива: `mcp__serena__find_symbol`
```javascript
// Использовать ТОЛЬКО если проект зарегистрирован
mcp__serena__find_symbol({
  name_path: "ПроверитьСовпадениеДанныхСПервойСтрокой",
  relative_path: "Forms/Форма/Ext/Form/Module.bsl",
  include_body: true,
  depth: 0
})
```

**Когда использовать AST-grep:**
- ✅ **ВСЕГДА** для BSL файлов (основной метод)
- Нужно найти определение функции/процедуры
- Анализ конкретного символа с телом
- Поиск методов класса

**Вместо:** `Grep` или `Read` + поиск вручную

**Параметры:**
- `include_body: true` - получить тело функции
- `depth: 1` - получить вложенные символы (для классов)
- `substring_matching: true` - нечеткий поиск по имени

---

### 3️⃣ **Поиск где используется функция/переменная**

#### ✅ ИСПОЛЬЗОВАТЬ: `mcp__serena__find_referencing_symbols`
```javascript
mcp__serena__find_referencing_symbols({
  name_path: "ЗаполнитьСписокПроизвольныйКомпозит",
  relative_path: "Ext/ObjectModule.bsl"
})
```

**Когда:**
- Анализ зависимостей перед рефакторингом
- Поиск всех мест вызова функции
- Понимание архитектуры кода

**Вместо:** `Grep` с именем функции

**Преимущества:**
- Семантический анализ (не просто текстовый поиск)
- Контекст каждого использования
- Отфильтрованы комментарии и строки

---

### 4️⃣ **Замена тела процедуры/функции**

#### ✅ ИСПОЛЬЗОВАТЬ: `mcp__serena__replace_symbol_body`
```javascript
mcp__serena__replace_symbol_body({
  name_path: "КомандаСформироватьПробыПроизвольныйКомпозит",
  relative_path: "Forms/Форма/Ext/Form/Module.bsl",
  body: "// Новое тело функции\n..."
})
```

**Когда:**
- Замена логики целой функции/процедуры
- Рефакторинг метода
- Полная переработка процедуры

**Вместо:** `Edit` с регулярными выражениями

**Преимущества:**
- Автоматическое сохранение отступов
- Корректная замена с учетом синтаксиса
- Не нужно искать границы функции

---

### 5️⃣ **Добавление новой процедуры/функции**

#### ✅ ИСПОЛЬЗОВАТЬ: `mcp__serena__insert_after_symbol` или `insert_before_symbol`
```javascript
mcp__serena__insert_after_symbol({
  name_path: "ПоследняяФункцияВМодуле",
  relative_path: "Module.bsl",
  body: "\nПроцедура НоваяПроцедура()\n\t// Код\nКонецПроцедуры"
})
```

**Когда:**
- Добавление новой функции в конец модуля
- Вставка процедуры после определенного символа
- Добавление обработчика события

**Вместо:** `Edit` или `Write`

**Преимущества:**
- Корректная вставка с сохранением структуры
- Автоматические отступы
- Вставка в семантически правильное место

---

### 6️⃣ **Поиск паттернов в коде**

#### ✅ ИСПОЛЬЗОВАТЬ: `mcp__serena__search_for_pattern`
```javascript
mcp__serena__search_for_pattern({
  substring_pattern: "НСтр\\(\"ru = ",
  relative_path: "src/projects/configuration/",
  restrict_search_to_code_files: true,
  context_lines_before: 2,
  context_lines_after: 2
})
```

**Когда:**
- Поиск использования конкретной функции БСП
- Анализ паттернов локализации
- Поиск по регулярному выражению в коде

**Вместо:** `Grep`

**Параметры:**
- `paths_include_glob: "*.bsl"` - только BSL файлы
- `paths_exclude_glob: "*test*"` - исключить тесты
- `context_lines_before/after` - контекст вокруг совпадения

---

### 7️⃣ **Работа с документацией 1С**

#### ✅ ИСПОЛЬЗОВАТЬ: `mcp__1c-framework-docs__search_docs`
```javascript
mcp__1c-framework-docs__search_docs({
  query: "регистр сведений композитные пробы",
  search_type: "hybrid",
  limit: 5
})
```

**Когда:**
- Поиск информации по фреймворку
- Непонятный механизм конфигурации
- Нужны примеры из документации

**Типы поиска:**
- `"hybrid"` - комбинированный (рекомендуется)
- `"semantic"` - семантический (по смыслу)
- `"fulltext"` - полнотекстовый (точное совпадение)

---

### 8️⃣ **Парсинг внешних сайтов**

#### ✅ ИСПОЛЬЗОВАТЬ: `mcp__universal-web-scraper__scrape_website`
```javascript
mcp__universal-web-scraper__scrape_website({
  url: "https://its.1c.ru/db/metod8dev",
  adapter_type: "its_1c",
  include_links: true,
  save_to_memory: true
})
```

**Когда:**
- Нужна информация с портала ITS 1C
- Парсинг технических статей
- Извлечение документации с внешних сайтов

**Адаптеры:**
- `"its_1c"` - специализированный для ITS
- `"documentation"` - документационные сайты
- `"news"` - новостные сайты
- `"generic"` - универсальный парсер

---

### 9️⃣ **Конвертация документов (PDF, DOCX)**

#### ✅ ИСПОЛЬЗОВАТЬ: `mcp__docling__convert_document`
```javascript
mcp__docling__convert_document({
  input_path: "D:/documents/техническое_задание.pdf",
  output_path: "cache/tz.md",
  extract_images: true,
  ocr_enabled: true
})
```

**Когда:**
- Конвертация PDF в Markdown для RAG
- Обработка технических заданий
- Извлечение данных из Word документов

**Форматы:** PDF, DOCX, PPTX, XLSX, HTML, RTF

---

### 🔟 **Сохранение знаний о проекте**

#### ✅ ИСПОЛЬЗОВАТЬ: `mcp__memory__create_entities` + `create_relations`
```javascript
// Создание сущностей
mcp__memory__create_entities([{
  name: "Обработка.гкс_АРМПромежуточныйКомпозит",
  entityType: "1c_dataprocessor",
  observations: [
    "Формирует композитные пробы из регистраций",
    "Использует фильтры: Номенклатура, Контрагент, Договор"
  ]
}])

// Создание связей
mcp__memory__create_relations([{
  from: "Обработка.гкс_АРМПромежуточныйКомпозит",
  to: "РегистрСведений.гкс_КомпозитныеПробы",
  relationType: "uses"
}])
```

**Когда:**
- Документирование архитектуры проекта
- Сохранение важных паттернов
- Создание Knowledge Graph конфигурации

**Альтернатива:** `mcp__serena__write_memory` (для простых заметок)

---

### 1️⃣1️⃣ **Сложный многоступенчатый анализ**

#### ✅ ИСПОЛЬЗОВАТЬ: `mcp__sequential-thinking__sequentialthinking`
```javascript
mcp__sequential-thinking__sequentialthinking({
  thought: "Анализирую зависимости между модулями для рефакторинга",
  thoughtNumber: 1,
  totalThoughts: 5,
  nextThoughtNeeded: true
})
```

**Когда:**
- Сложная архитектурная задача
- Многоступенчатое планирование
- Анализ с неясным решением
- Несколько альтернативных подходов

---

### 1️⃣2️⃣ **AST-анализ BSL кода**

#### ✅ ИСПОЛЬЗОВАТЬ: `mcp__ast-grep-mcp__ast_grep`
```javascript
mcp__ast-grep-mcp__ast_grep({
  pattern: "Процедура $NAME($ARGS)",
  path: "src/projects/configuration/",
  bsl_type: "procedures",
  export_only: true
})
```

**Когда:**
- Структурный поиск процедур/функций
- Анализ синтаксических конструкций
- Поиск экспортных процедур
- Рефакторинг с заменой AST паттернов

---

## 🚫 Когда НЕ использовать MCP

### ❌ Использовать стандартные инструменты:

1. **Read** - для однократного быстрого чтения небольшого фрагмента
2. **Edit** - для замены 1-2 строк через регулярное выражение
3. **Write** - для создания новых небольших файлов
4. **Grep** - для простого поиска текста без семантики
5. **Bash** - для системных команд (git, npm, mkdir, etc.)

---

## 📊 Таблица быстрого выбора

| Задача | MCP инструмент | Стандартный инструмент |
|--------|----------------|------------------------|
| Обзор структуры BSL файла | `serena__get_symbols_overview` | ❌ |
| Поиск функции в BSL | `serena__find_symbol` | ❌ |
| Где используется функция | `serena__find_referencing_symbols` | `Grep` (fallback) |
| Замена тела функции | `serena__replace_symbol_body` | `Edit` (для простых) |
| Добавить новую функцию | `serena__insert_after_symbol` | `Edit` (для простых) |
| Поиск паттерна в коде | `serena__search_for_pattern` | `Grep` (для простого) |
| Поиск в документации | `1c-framework-docs__search_docs` | ❌ |
| Парсинг ITS/веб-сайтов | `universal-web-scraper__scrape_website` | ❌ |
| Конвертация PDF/DOCX | `docling__convert_document` | ❌ |
| Сохранение знаний | `memory__create_entities` | `Write` (markdown) |
| Сложный анализ | `sequential-thinking__sequentialthinking` | ❌ |
| AST поиск в BSL | `ast-grep-mcp__ast_grep` | ❌ |
| Чтение 10-20 строк | ❌ | `Read` |
| Замена 1-2 строк | ❌ | `Edit` |
| Git команды | ❌ | `Bash` |

---

## 🔄 Workflow примеры

### Пример 1: Рефакторинг процедуры
```
1. serena__find_symbol → найти процедуру
2. serena__find_referencing_symbols → где используется
3. sequential-thinking → спланировать изменения
4. serena__replace_symbol_body → заменить тело
5. memory__create_entities → задокументировать изменение
```

### Пример 2: Анализ новой конфигурации
```
1. serena__get_symbols_overview → обзор основных модулей
2. serena__search_for_pattern → найти ключевые паттерны
3. 1c-framework-docs__search_docs → изучить документацию
4. memory__create_entities + create_relations → создать Knowledge Graph
5. serena__write_memory → сохранить выводы
```

### Пример 3: Исследование механизма из документации ITS
```
1. universal-web-scraper__scrape_website → парсинг статьи с ITS
2. docling__convert_document → конвертация PDF если есть
3. memory__create_entities → сохранение в Knowledge Graph
4. serena__search_for_pattern → поиск использования в коде
```

---

## ✅ Чек-лист перед выбором инструмента

- [ ] Это BSL файл? → Рассмотри Serena MCP
- [ ] Нужен семантический анализ? → Используй Serena/AST-grep
- [ ] Нужна информация из документации? → Используй 1C Docs MCP
- [ ] Нужно распарсить веб-сайт? → Используй Universal Web Scraper
- [ ] Нужно конвертировать документ? → Используй Docling MCP
- [ ] Сложная многоступенчатая задача? → Используй Sequential Thinking
- [ ] Нужно сохранить знания? → Используй Memory MCP
- [ ] Простая текстовая операция? → Используй стандартные инструменты

---

## 📝 Как интегрировать эти правила

### Вариант 1: Добавить в CLAUDE.md
Скопируй содержимое этого файла в секцию "Tool usage policy" в CLAUDE.md

### Вариант 2: Ссылка из CLAUDE.md
Добавь в CLAUDE.md:
```markdown
## MCP Priority Rules
Следуй правилам приоритизации инструментов из `.claude/mcp-priority-rules.md`
```

### Вариант 3: Использовать как справочник
Обращайся к этому файлу при выборе инструмента для задачи

---

**Версия:** 1.0
**Дата создания:** 2025-10-23
**Последнее обновление:** 2025-10-23
