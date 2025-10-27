# MCP Commands Reference - Справочник команд MCP

📍 **Навигация:** [🏠 Главная](../README.md) | [📚 API Documentation](./README.md)
📅 **Обновлено:** 11.10.2025 | **Статус:** ✅ Создано для устранения битых ссылок

---

## 🔧 Полный справочник команд MCP серверов

### ⚠️ ВНИМАНИЕ: Документ создан автоматически

Этот файл создан для устранения битых ссылок. Содержимое базируется на реальных MCP серверах, интегрированных в фреймворк.

---

## 📋 Категории MCP команд

### **1. Filesystem MCP - Работа с файловой системой**

#### **Чтение файлов:**
```javascript
// Чтение текстового файла
mcp__filesystem__read_text_file({
  path: "/path/to/file.bsl"
})

// Чтение множественных файлов
mcp__filesystem__read_multiple_files({
  paths: ["/file1.bsl", "/file2.bsl", "/file3.bsl"]
})

// Чтение медиа файла (изображения, видео)
mcp__filesystem__read_media_file({
  path: "/path/to/image.png"
})
```

#### **Запись и редактирование файлов:**
```javascript
// Создание нового файла
mcp__filesystem__write_file({
  path: "/path/to/new-file.bsl",
  content: "// Новый BSL модуль\nПроцедура НоваяПроцедура() Экспорт\nКонецПроцедуры"
})

// Редактирование существующего файла
mcp__filesystem__edit_file({
  path: "/path/to/existing.bsl",
  edits: [{
    oldText: "Процедура СтараяПроцедура()",
    newText: "Процедура НоваяПроцедура()"
  }]
})
```

#### **Операции с директориями:**
```javascript
// Создание директории
mcp__filesystem__create_directory({
  path: "/new/directory/path"
})

// Просмотр содержимого директории
mcp__filesystem__list_directory({
  path: "/src/CommonModules"
})

// Дерево директорий (рекурсивно)
mcp__filesystem__directory_tree({
  path: "/src/projects/configuration"
})

// Поиск файлов
mcp__filesystem__search_files({
  path: "/src",
  pattern: "*.bsl"
})
```

### **2. GitHub MCP - Интеграция с GitHub**

#### **Поиск и исследование:**
```javascript
// Поиск репозиториев
mcp__github__search_repositories({
  query: "1C Enterprise framework",
  perPage: 20
})

// Поиск кода
mcp__github__search_code({
  q: "1C BSL best practices"
})

// Поиск issues и PR
mcp__github__search_issues({
  q: "1C configuration performance"
})

// Поиск пользователей
mcp__github__search_users({
  q: "1C developer"
})
```

#### **Работа с репозиториями:**
```javascript
// Получение содержимого файла
mcp__github__get_file_contents({
  owner: "username",
  repo: "repository",
  path: "CommonModule.bsl"
})

// Создание файла в репозитории
mcp__github__create_or_update_file({
  owner: "username", 
  repo: "repository",
  path: "NewModule.bsl",
  content: "// Новый модуль",
  message: "Add new BSL module",
  branch: "main"
})

// Пакетная загрузка файлов
mcp__github__push_files({
  owner: "username",
  repo: "repository", 
  branch: "feature-branch",
  files: [
    {path: "Module1.bsl", content: "..."},
    {path: "Module2.bsl", content: "..."}
  ],
  message: "Add multiple BSL modules"
})
```

#### **Issues и Pull Requests:**
```javascript
// Создание issue
mcp__github__create_issue({
  owner: "username",
  repo: "repository",
  title: "BSL code quality improvement",
  body: "Detailed description..."
})

// Создание Pull Request
mcp__github__create_pull_request({
  owner: "username",
  repo: "repository",
  title: "Feature: New BSL utilities",
  head: "feature-branch",
  base: "main",
  body: "PR description..."
})

// Создание ревью на PR
mcp__github__create_pull_request_review({
  owner: "username",
  repo: "repository", 
  pull_number: 123,
  body: "Review comments",
  event: "APPROVE"
})
```

### **3. Memory MCP - Knowledge Graph**

#### **Создание и управление сущностями:**
```javascript
// Создание сущностей
mcp__memory__create_entities([{
  name: "ОбщийМодуль.УтилитыРаботыСДанными",
  entityType: "bsl_module",
  observations: [
    "Содержит функции для работы с данными",
    "Экспортный модуль",
    "Используется в 15 конфигурациях"
  ]
}])

// Добавление наблюдений к существующим сущностям
mcp__memory__add_observations([{
  entityName: "ОбщийМодуль.УтилитыРаботыСДанными",
  contents: [
    "Добавлена функция ОбработатьМассивДанных()",
    "Исправлена ошибка в функции ВалидироватьДанные()"
  ]
}])

// Удаление сущностей
mcp__memory__delete_entities({
  entityNames: ["Устаревший.Модуль", "Неиспользуемый.Компонент"]
})
```

#### **Создание связей:**
```javascript
// Создание связей между сущностями
mcp__memory__create_relations([{
  from: "Документ.ЗаказПокупателя",
  to: "ОбщийМодуль.УтилитыРаботыСДанными",
  relationType: "uses"
}, {
  from: "Справочник.Номенклатура", 
  to: "Документ.ЗаказПокупателя",
  relationType: "referenced_by"
}])

// Удаление связей
mcp__memory__delete_relations({
  relations: [{
    from: "СтарыйМодуль",
    to: "УстаревшийКомпонент", 
    relationType: "depends_on"
  }]
})
```

#### **Поиск и чтение:**
```javascript
// Поиск узлов
mcp__memory__search_nodes({
  query: "общий модуль данные"
})

// Чтение конкретных узлов
mcp__memory__open_nodes({
  names: ["ОбщийМодуль.УтилитыРаботыСДанными", "Документ.ЗаказПокупателя"]
})

// Чтение всего графа
mcp__memory__read_graph()
```

### **4. Ripgrep MCP - Поиск по коду**

#### **Базовый поиск:**
```javascript
// Простой поиск
mcp__ripgrep__search({
  pattern: "Процедура.*Экспорт",
  path: "/src/CommonModules"
})

// Поиск с контекстом
mcp__ripgrep__search({
  pattern: "Попытка.*Исключение", 
  path: "/src",
  context: 3,
  filePattern: "*.bsl"
})
```

#### **Продвинутый поиск:**
```javascript
// Расширенный поиск
mcp__ripgrep__advanced-search({
  pattern: "Функция\\s+\\w+\\(.*\\)\\s+Экспорт",
  path: "/src",
  fileType: "bsl",
  caseSensitive: false,
  showLineNumbers: true,
  maxResults: 50
})

// Подсчёт совпадений
mcp__ripgrep__count-matches({
  pattern: "TODO|FIXME|HACK",
  path: "/src",
  filePattern: "*.bsl"
})
```

### **5. AST-grep MCP - Семантический поиск**

#### **Поиск по AST паттернам:**
```javascript
// Поиск экспортных процедур
mcp__ast-grep-mcp__ast_grep({
  pattern: "Процедура $NAME() Экспорт",
  language: "bsl",
  path: "/src/CommonModules"
})

// Поиск функций с параметрами
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($PARAMS) Экспорт",
  language: "bsl",
  mode: "search"
})

// Поиск блоков обработки исключений
mcp__ast-grep-mcp__ast_grep({
  pattern: "Попытка $BODY Исключение $HANDLER КонецПопытки",
  language: "bsl",
  context: 2
})
```

#### **Замена кода:**
```javascript
// Рефакторинг с заменой
mcp__ast-grep-mcp__ast_grep({
  pattern: "Процедура $NAME() Экспорт",
  replacement: "Процедура $NAME() Экспорт\n\t// TODO: Добавить документацию",
  language: "bsl",
  mode: "replace",
  dry_run: true  // Предварительный просмотр
})
```

### **6. Sequential Thinking MCP - Сложное мышление**

#### **Пошаговое планирование:**
```javascript
// Начало сессии размышления
mcp__sequential-thinking__sequentialthinking({
  thought: "Анализирую архитектуру подсистемы управления складом",
  thoughtNumber: 1, 
  totalThoughts: 10,
  nextThoughtNeeded: true
})

// Продолжение размышления
mcp__sequential-thinking__sequentialthinking({
  thought: "Определяю ключевые компоненты: документы, справочники, отчёты",
  thoughtNumber: 2,
  totalThoughts: 10, 
  nextThoughtNeeded: true
})

// Ревизия предыдущего размышления
mcp__sequential-thinking__sequentialthinking({
  thought: "Пересматриваю решение о структуре документов",
  thoughtNumber: 3,
  totalThoughts: 12,  // Увеличили общее количество
  nextThoughtNeeded: true,
  isRevision: true,
  revisesThought: 2
})
```

### **7. Playwright Automation MCP - Автоматизация веб-интерфейса**

#### **Навигация и взаимодействие:**
```javascript
// Открытие браузера и навигация
mcp__playwright-automation__playwright_navigate({
  url: "http://localhost/infobase",
  browserType: "chromium",
  headless: false
})

// Заполнение форм
mcp__playwright-automation__playwright_fill({
  selector: "#username",
  value: "Администратор"
})

mcp__playwright-automation__playwright_fill({
  selector: "#password", 
  value: "password123"
})

// Клики и навигация
mcp__playwright-automation__playwright_click({
  selector: "#login-button"
})

// Создание скриншотов
mcp__playwright-automation__playwright_screenshot({
  name: "login-page",
  fullPage: true,
  savePng: true
})
```

#### **HTTP API тестирование:**
```javascript
// POST запросы к REST API 1С
mcp__playwright-automation__playwright_post({
  url: "http://localhost/infobase/hs/api/v1/documents",
  value: JSON.stringify({
    DocumentType: "ЗаказПокупателя",
    Data: {
      Покупатель: "Клиент001",
      Товары: [...]
    }
  }),
  headers: {
    "Content-Type": "application/json"
  },
  token: "Bearer YOUR_API_TOKEN"
})

// GET запросы
mcp__playwright-automation__playwright_get({
  url: "http://localhost/infobase/hs/api/v1/catalogs/Номенклатура"
})
```

### **8. Brave Search MCP - Веб-поиск**

#### **Поиск информации:**
```javascript
// Общий веб-поиск
mcp__brave-search__brave_web_search({
  query: "1С:Предприятие лучшие практики разработки 2025",
  count: 10
})

// Локальный поиск (для поиска рядом расположенных услуг)
mcp__brave-search__brave_local_search({
  query: "1С разработка консультации",
  count: 5
})
```

---

## 🔗 Практические примеры использования

### **Комплексный анализ BSL модуля:**
```javascript
// 1. Чтение файла
const content = await mcp__filesystem__read_text_file({
  path: "/src/CommonModules/УтилитыРаботыСДанными.bsl"
})

// 2. Семантический анализ
const exports = await mcp__ast-grep-mcp__ast_grep({
  pattern: "Процедура $NAME() Экспорт",
  language: "bsl",
  path: "/src/CommonModules/УтилитыРаботыСДанными.bsl"
})

// 3. Поиск использований
const usages = await mcp__ripgrep__search({
  pattern: "УтилитыРаботыСДанными\\.",
  path: "/src"
})

// 4. Сохранение анализа в Memory
await mcp__memory__create_entities([{
  name: "Анализ.УтилитыРаботыСДанными",
  entityType: "module_analysis",
  observations: [
    `Экспортных процедур: ${exports.length}`,
    `Использований: ${usages.length}`,
    `Размер файла: ${content.length} символов`
  ]
}])
```

### **Автоматизированное тестирование 1С веб-клиента:**
```javascript
// 1. Авторизация
await mcp__playwright-automation__playwright_navigate({
  url: "http://localhost/infobase"
})

await mcp__playwright-automation__playwright_fill({
  selector: "#username",
  value: "Тестировщик"
})

await mcp__playwright-automation__playwright_click({
  selector: "#login"
})

// 2. Создание документа
await mcp__playwright-automation__playwright_click({
  selector: "[data-document='ЗаказПокупателя']"
})

// 3. Скриншот результата
await mcp__playwright-automation__playwright_screenshot({
  name: "document-created",
  savePng: true
})

// 4. Сохранение результата теста
await mcp__memory__create_entities([{
  name: "Тест.СозданиеЗаказа",
  entityType: "test_result",
  observations: ["Тест пройден успешно", "Документ создан корректно"]
}])
```

---

## 🔗 Связанные документы

- **[⬅️ API Documentation](./README.md)** - Главная страница API документации
- **[🔧 BSL Integration](./bsl-language-server-integration.md)** - Интеграция BSL Language Server
- **[📖 Hooks System](./hooks-system-overview-CORRECTED.md)** - Система хуков

---

**📅 Версия:** 1.0 AUTO-GENERATED
**🗓️ Создано:** 11.10.2025
**👤 Создатель:** Documentation Complete-Fixer
**🎯 Статус:** ✅ Готово к использованию (базируется на реальных MCP серверах)

*Документ создан для устранения битых ссылок. Все команды основаны на реальных MCP серверах, интегрированных в фреймворк: Filesystem, GitHub, Memory, Ripgrep, AST-grep, Sequential Thinking, Playwright, Brave Search.*