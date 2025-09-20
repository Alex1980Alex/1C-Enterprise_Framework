# 🔗 MCP Commands Reference - Справочник команд

## 📖 Обзор MCP интеграции

Model Context Protocol (MCP) обеспечивает интеграцию с внешними системами через стандартизированные команды серии `serena__*`.

## ⚠️ ВАЖНО: Ограничения в Claude Code

**🚨 КРИТИЧЕСКАЯ ИНФОРМАЦИЯ:**
- MCP команды `serena__*` **НЕ ДОСТУПНЫ** непосредственно в среде Claude Code
- Команды предназначены для **внешних скриптов** и **Cursor IDE интеграции** 
- Claude Code работает с правилами фреймворка через **файловую систему** и **системные механизмы**

**✅ Где работают MCP команды:**
- Внешние bash/python скрипты
- Cursor IDE плагины и расширения
- CI/CD пайплайны и автоматизация
- Интеграционные системы

**❌ Где НЕ работают MCP команды:**
- Непосредственно в Claude Code REPL
- Внутри сессий Claude Code
- В интерактивном режиме Claude

## 🎯 Категории команд

### 1️⃣ Управление проектами

#### `serena__activate_project(path)`
**Назначение**: Активация проекта 1С для работы
```python
serena__activate_project("/path/to/1c-project")
```
**Возвращает**: Статус активации и основные параметры проекта

#### `serena__get_current_config()`
**Назначение**: Получение информации о текущей активной конфигурации
```python
config = serena__get_current_config()
```
**Возвращает**: Объект с параметрами конфигурации

#### `serena__list_projects()`
**Назначение**: Получение списка всех доступных проектов
```python
projects = serena__list_projects()
```
**Возвращает**: Список проектов с базовой информацией

### 2️⃣ Система памяти проектов

#### `serena__list_memories()`
**Назначение**: Получение списка сохраненных знаний проекта
```python
memories = serena__list_memories()
```
**Возвращает**: Список доступных записей памяти

#### `serena__read_memory(name)`
**Назначение**: Чтение конкретной записи из памяти проекта
```python
content = serena__read_memory("architecture_analysis")
```
**Параметры**: 
- `name` - название записи памяти
**Возвращает**: Содержимое записи

#### `serena__write_memory(name, content)`
**Назначение**: Сохранение знаний в память проекта
```python
serena__write_memory("solution_pattern", "Описание паттерна...")
```
**Параметры**:
- `name` - название записи  
- `content` - содержимое для сохранения

#### `serena__search_memories(query)`
**Назначение**: Поиск по сохраненным знаниям
```python
results = serena__search_memories("обработка данных")
```
**Параметры**:
- `query` - поисковый запрос
**Возвращает**: Список релевантных записей

### 3️⃣ Анализ кода и структуры

#### `serena__find_symbol(name, type)`
**Назначение**: Поиск символов (процедур, функций, переменных) в коде
```python
symbols = serena__find_symbol("ОбработатьДанные", "procedure")
```
**Параметры**:
- `name` - название символа
- `type` - тип символа (procedure, function, variable, etc.)
**Возвращает**: Список найденных символов с местоположением

#### `serena__get_diagnostics(file)`
**Назначение**: Получение диагностической информации о файле
```python
diagnostics = serena__get_diagnostics("ОбщийМодуль.bsl")
```
**Параметры**:
- `file` - путь к файлу
**Возвращает**: Список ошибок, предупреждений и рекомендаций

#### `serena__analyze_structure(path)`
**Назначение**: Анализ структуры модуля или конфигурации
```python
structure = serena__analyze_structure("/path/to/module")
```
**Параметры**:
- `path` - путь для анализа
**Возвращает**: Структурированная информация об архитектуре

#### `serena__get_references(symbol)`
**Назначение**: Поиск всех ссылок на символ в коде
```python
refs = serena__get_references("МойМетод")
```
**Параметры**:
- `symbol` - символ для поиска ссылок
**Возвращает**: Список мест использования символа

### 4️⃣ Чтение и исследование кода

#### `serena__read_file(path)`
**Назначение**: Чтение содержимого BSL файла
```python
content = serena__read_file("src/CommonModules/Utils.bsl")
```
**Параметры**:
- `path` - путь к файлу
**Возвращает**: Содержимое файла

#### `serena__list_modules(type)`
**Назначение**: Получение списка модулей определенного типа
```python
modules = serena__list_modules("CommonModule")
```
**Параметры**:
- `type` - тип модулей (CommonModule, ObjectModule, FormModule, etc.)
**Возвращает**: Список модулей указанного типа

#### `serena__get_metadata(object)`
**Назначение**: Получение метаданных объекта конфигурации
```python
metadata = serena__get_metadata("Справочник.Номенклатура")
```
**Параметры**:
- `object` - имя объекта метаданных
**Возвращает**: Структура метаданных объекта

#### `serena__search_code(pattern)`
**Назначение**: Поиск кода по регулярному выражению
```python
results = serena__search_code(r"Функция\s+\w+Обработать\w*")
```
**Параметры**:
- `pattern` - паттерн для поиска (регулярное выражение)
**Возвращает**: Список найденных совпадений

### 5️⃣ Анализ качества кода

#### `serena__get_code_metrics(path)`
**Назначение**: Получение метрик качества кода
```python
metrics = serena__get_code_metrics("src/")
```
**Параметры**:
- `path` - путь для анализа
**Возвращает**: Объект с метриками (сложность, размер, etc.)

#### `serena__validate_standards(file)`
**Назначение**: Проверка соответствия стандартам кодирования
```python
violations = serena__validate_standards("Module.bsl")
```
**Параметры**:
- `file` - файл для проверки
**Возвращает**: Список нарушений стандартов

### 6️⃣ ДОПОЛНИТЕЛЬНЫЕ ИНСТРУМЕНТЫ (2025.09.03)

#### `serena__delete_lines(file_path, start_line, end_line)`
**Назначение**: Точное удаление диапазона строк в файле
```python
serena__delete_lines("Module.bsl", 15, 25)
```
**Параметры**:
- `file_path` - путь к файлу
- `start_line` - начальная строка (включительно)
- `end_line` - конечная строка (включительно)
**Возвращает**: Статус операции и количество удаленных строк

#### `serena__insert_at_line(file_path, line_number, content)`
**Назначение**: Вставка содержимого в указанную строку файла
```python
serena__insert_at_line("Module.bsl", 10, "// Новый комментарий")
```
**Параметры**:
- `file_path` - путь к файлу
- `line_number` - номер строки для вставки
- `content` - содержимое для вставки

#### `serena__replace_lines(file_path, start_line, end_line, new_content)`
**Назначение**: Замена диапазона строк новым содержимым
```python
serena__replace_lines("Module.bsl", 20, 22, "НоваяРеализация();")
```
**Параметры**:
- `file_path` - путь к файлу
- `start_line` - начальная строка замены
- `end_line` - конечная строка замены  
- `new_content` - новое содержимое

#### `serena__jet_brains_find_symbol(symbol_name, symbol_type)`
**Назначение**: Поиск символов через JetBrains IDE API
```python
symbols = serena__jet_brains_find_symbol("ПроцедураОбработки", "procedure")
```
**Параметры**:
- `symbol_name` - имя символа для поиска
- `symbol_type` - тип символа (function, procedure, variable)
**Возвращает**: Список символов с точным местоположением в IDE

#### `serena__jet_brains_find_referencing_symbols(target_symbol)`
**Назначение**: Поиск ссылок на символ через JetBrains IDE
```python
references = serena__jet_brains_find_referencing_symbols("МояФункция")
```
**Параметры**:
- `target_symbol` - символ для поиска ссылок
**Возвращает**: Список всех мест использования символа

#### `serena__jet_brains_get_symbols_overview(file_path)`
**Назначение**: Получение обзора символов файла через IDE
```python
overview = serena__jet_brains_get_symbols_overview("CommonModules/Utils.bsl")
```
**Параметры**:
- `file_path` - путь к файлу
**Возвращает**: Структурированный обзор всех символов файла

#### `serena__get_current_config()`
**Назначение**: Получение текущей конфигурации Serena Framework
```python
config = serena__get_current_config()
```
**Возвращает**: Полная конфигурация с активными проектами, инструментами, режимами

#### `serena__initial_instructions(project_path)`
**Назначение**: Получение начальных инструкций для проекта
```python
instructions = serena__initial_instructions("/path/to/project")
```
**Параметры**:
- `project_path` - путь к проекту
**Возвращает**: Начальные инструкции и правила для работы с проектом

#### `serena__restart_language_server(server_type)`
**Назначение**: Перезапуск языкового сервера
```python
serena__restart_language_server("bsl")
```
**Параметры**:
- `server_type` - тип сервера (bsl, onescript, typescript)
**Возвращает**: Статус перезапуска и новое состояние сервера

#### `serena__summarize_changes(changes_context, summary_type)`
**Назначение**: Автоматическое создание резюме изменений
```python
summary = serena__summarize_changes(git_diff_output, "commit")
```
**Параметры**:
- `changes_context` - контекст изменений (diff, файлы, описание)
- `summary_type` - тип резюме (commit, release, daily)
**Возвращает**: Структурированное резюме изменений

#### `serena__switch_modes(mode_name, context)`
**Назначение**: Переключение режимов работы Serena
```python
serena__switch_modes("development", {"strict_validation": True})
```
**Параметры**:
- `mode_name` - имя режима (development, analysis, debugging, consulting)
- `context` - дополнительный контекст для режима
**Возвращает**: Статус переключения и активированные возможности

#### `serena__remove_project(project_path)`
**Назначение**: Удаление проекта из конфигурации Serena
```python
serena__remove_project("/path/to/old/project")
```
**Параметры**:
- `project_path` - путь к проекту для удаления
**Возвращает**: Подтверждение удаления и очистка ресурсов

### 7️⃣ КОМАНДЫ АВТОМАТИЗАЦИИ (2025.09.02)

#### `serena__auto_save_response_to_journal(response_text, user_question, task_type, compliance_status)`
**Назначение**: Автоматическое сохранение ответа AI в журнал фреймворка
```python
serena__auto_save_response_to_journal(
    response_text="Подробный ответ...",
    user_question="Как создать модуль?", 
    task_type="Консультация",
    compliance_status="✅"
)
```
**Параметры**:
- `response_text` - текст ответа для сохранения
- `user_question` - исходный вопрос пользователя
- `task_type` - тип задачи (Консультация, Программирование, Архитектура)
- `compliance_status` - статус соблюдения правил (✅/❌)
**Возвращает**: Подтверждение записи в журнал с timestamp

#### `serena__auto_git_commit_with_template(changes_description, commit_type)`
**Назначение**: Автоматический Git коммит с шаблоном фреймворка
```python
serena__auto_git_commit_with_template(
    changes_description="Добавлен новый общий модуль",
    commit_type="feat"
)
```
**Параметры**:
- `changes_description` - описание изменений
- `commit_type` - тип коммита (feat, fix, docs, refactor)
**Возвращает**: Hash коммита и статус выполнения

#### `serena__predict_compliance_risk(task_description, context)`
**Назначение**: Предсказание рисков нарушения правил фреймворка
```python
risk = serena__predict_compliance_risk(
    task_description="Создать сложный алгоритм обработки",
    context="Пользователь спешит"
)
```
**Параметры**:
- `task_description` - описание предстоящей задачи
- `context` - контекстная информация
**Возвращает**: Оценка риска (LOW/MEDIUM/HIGH) с рекомендациями

#### `serena__track_rule_violations(violation_type, severity, description)`
**Назначение**: Отслеживание нарушений правил фреймворка
```python
serena__track_rule_violations(
    violation_type="structure_missing",
    severity="HIGH", 
    description="Отсутствует чек-лист в ответе"
)
```
**Параметры**:
- `violation_type` - тип нарушения
- `severity` - серьезность (LOW/MEDIUM/HIGH/CRITICAL)
- `description` - описание нарушения
**Возвращает**: ID записи нарушения для отслеживания

#### `serena__auto_load_framework_rules(force_reload)`
**Назначение**: Автоматическая загрузка всех правил фреймворка в память
```python
result = serena__auto_load_framework_rules(force_reload=True)
```
**Параметры**:
- `force_reload` - принудительная перезагрузка правил (по умолчанию False)
**Возвращает**: Отчет о загруженных правилах и статистику

#### `serena__auto_load_context(user_question, context_type)`
**Назначение**: Автоматическая загрузка релевантного контекста на основе вопроса
```python
context = serena__auto_load_context(
    user_question="Как создать общий модуль?",
    context_type="auto"  # auto, full, minimal
)
```
**Параметры**:
- `user_question` - вопрос пользователя для анализа
- `context_type` - тип загружаемого контекста
**Возвращает**: Структурированный контекст с релевантными правилами

#### `serena__auto_compliance_controller(response_draft, validation_level)`
**Назначение**: Автоматический контроллер соблюдения правил
```python
report = serena__auto_compliance_controller(
    response_draft="Черновик ответа...",
    validation_level="strict"  # strict, normal, lenient
)
```
**Параметры**:
- `response_draft` - черновик ответа для проверки
- `validation_level` - уровень строгости проверки
**Возвращает**: Детальный отчет о соответствии с рекомендациями

### 🤖 АВТОМАТИЗАЦИЯ WORKFLOW

**Полный автоматизированный цикл работы с фреймворком:**

1. **Перед началом работы:**
```python
# Загружаем все правила фреймворка
serena__auto_load_framework_rules(force_reload=True)
```

2. **При получении вопроса пользователя:**
```python  
# Автоматически загружаем релевантный контекст
context = serena__auto_load_context(user_question)
# Предсказываем риски нарушения правил
risk = serena__predict_compliance_risk(user_question, "standard_task")
```

3. **После формирования ответа:**
```python
# Проверяем соответствие правилам
compliance = serena__auto_compliance_controller(response_draft)
# Автоматически сохраняем в журнал
serena__auto_save_response_to_journal(response_text, user_question)
```

4. **При изменениях в коде:**
```python
# Автоматический коммит с правильным шаблоном
serena__auto_git_commit_with_template(changes_description, "feat")

## 🔄 Рекомендуемый workflow использования

### 1. Начало работы с проектом:
```python
# Активировать проект
serena__activate_project("/path/to/project")

# Прочитать накопленные знания
memories = serena__list_memories()
for memory in memories:
    content = serena__read_memory(memory['name'])
```

### 2. Анализ кода:
```python
# Получить структуру
structure = serena__analyze_structure("/src/CommonModules/")

# Проанализировать качество
diagnostics = serena__get_diagnostics("Module.bsl")
metrics = serena__get_code_metrics("Module.bsl")
```

### 3. Сохранение результатов:
```python
# Сохранить анализ в память
serena__write_memory("code_analysis_2025", analysis_results)
```

## ⚠️ Важные ограничения

### Безопасность:
- Все команды работают в режиме **только чтения**
- Изменение кода через MCP **запрещено**
- Доступ ограничен активным проектом

### Производительность:
- Команды анализа могут выполняться долго для больших проектов
- Рекомендуется кэшировать результаты в памяти проекта
- Используйте фильтрацию для оптимизации поиска

## 🔧 Интеграция с cursor-rules

Все MCP команды должны использоваться в соответствии с правилами из `cursor-rules/08-mcp-memory.md`:

1. **Обязательная активация** проекта перед любыми операциями
2. **Сохранение ключевых результатов** в память проекта
3. **Структурированное логирование** всех операций
4. **Соблюдение принципов** безопасности и производительности

---

**📅 Версия документа:** 1.0  
**🗓️ Последнее обновление:** 03.09.2025  
**👤 Ответственный:** Команда 1C-Enterprise Cursor Framework  
**🔗 Связанные документы:** `ultimate-hooks-system.md`, `claude-code-hooks-api.md`

*Для получения актуального списка команд используйте `serena__list_commands()` в активном проекте*