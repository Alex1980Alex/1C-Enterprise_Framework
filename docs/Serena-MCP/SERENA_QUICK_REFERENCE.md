# Serena - Краткая справка (Quick Reference)

## 🚀 Быстрый старт

### Инициализация нового проекта

```bash
# 1. Перейти в корень проекта
cd /path/to/project

# 2. Создать структуру .serena
mkdir -p .serena/memories .serena/cache

# 3. Создать минимальный project.yml
cat > .serena/project.yml << 'EOF'
language: python
ignore_all_files_in_gitignore: true
ignored_paths: []
read_only: false
excluded_tools: []
initial_prompt: ""
project_name: "my-project"
EOF

# 4. Запустить Serena
serena-mcp-server
```

---

## 📂 Структура файлов

```
project-root/
└── .serena/
    ├── project.yml          # Конфигурация
    ├── memories/            # Память (MD файлы)
    └── cache/               # Кэш (автоматически)
```

---

## 🔧 Основные инструменты

### Memory Tools

```python
# Создать/обновить память
write_memory(
    memory_name="my_analysis",
    content="# Content..."
)

# Прочитать память
read_memory("my_analysis")

# Список всех воспоминаний
list_memories()

# Удалить память
delete_memory("outdated_memory")
```

### File Tools

```python
# Прочитать файл
read_file("path/to/file.py")

# Список файлов
list_dir(".", recursive=True)

# Поиск по паттерну
search_for_pattern(
    substring_pattern="Функция\\s+(\\w+)",
    path="src/"
)

# Создать файл
create_text_file(
    relative_path="docs/new.md",
    content="# New document"
)
```

### Symbol Tools (требуют LSP)

```python
# Найти символ
find_symbol(
    name_path="MyClass/my_method",
    include_body=True
)

# Обзор символов файла
get_symbols_overview("src/module.py")

# Найти ссылки на символ
find_referencing_symbols(
    name_path="MyClass",
    relative_path="src/module.py"
)
```

### Workflow Tools

```python
# Проверка онбординга
check_onboarding_performed()

# Запуск онбординга
onboarding()

# Получить текущую конфигурацию
get_current_config()
```

---

## 📝 Работа с памятью

### Соглашения об именовании

| Тип памяти | Шаблон имени | Пример |
|------------|--------------|--------|
| Обзор проекта | `project_overview` | `project_overview.md` |
| Обзор подпроекта | `project_<ID>_overview` | `project_251029_overview.md` |
| Детальный анализ | `detailed_analysis_<Name>` | `detailed_analysis_ARM_Composite.md` |
| Активный контекст | `active_project_context` | `active_project_context.md` |
| Конвенции | `<domain>_conventions` | `1c_code_conventions.md` |
| Руководства | `<topic>_guide` | `deployment_guide.md` |

### Структура MD-файла памяти

```markdown
# Заголовок памяти

## 1. Основная информация
- Что это
- Зачем нужно
- Когда создано

## 2. Детали
### 2.1 Подраздел 1
### 2.2 Подраздел 2

## 3. Связи
- Связь с X
- Связь с Y

## 4. Примеры
\`\`\`language
code example
\`\`\`

## 5. Заметки
- Важное 1
- Важное 2
```

---

## 🎯 Типичные сценарии

### Сценарий 1: Анализ кода

```python
# 1. Прочитать обзор (если есть)
overview = read_memory("project_overview")

# 2. Найти нужный файл
files = list_dir("src/", recursive=True)

# 3. Получить обзор символов
symbols = get_symbols_overview("src/module.py")

# 4. Прочитать детали
details = find_symbol("MyClass", include_body=True)

# 5. Сохранить анализ
write_memory(
    "detailed_analysis_MyClass",
    "# Analysis of MyClass\n..."
)
```

### Сценарий 2: Работа с подпроектами

```python
# 1. Обновить активный контекст
write_memory(
    "active_project_context",
    """
# Active Context
Current subproject: 251029_GKSTCPLK-1831
Working on: ARM development
"""
)

# 2. Прочитать обзор подпроекта
subproject = read_memory("project_251029_overview")

# 3. Провести работу...

# 4. Сохранить результаты
write_memory(
    "detailed_analysis_ARM",
    "# Results..."
)
```

### Сценарий 3: Переключение контекста

```python
# Старый контекст
current = read_memory("active_project_context")

# Обновить на новый
write_memory(
    "active_project_context",
    """
# Active Context
Previous: 251029_GKSTCPLK-1831
Current: 251027_GKSTCPLK-1788
Task: Bug fixing
"""
)

# Загрузить новый контекст
new_context = read_memory("project_251027_overview")
```

---

## ⚙️ Конфигурация project.yml

### Минимальная

```yaml
language: python
project_name: "my-project"
```

### Полная

```yaml
# Язык для LSP
language: python

# Игнорирование
ignore_all_files_in_gitignore: true
ignored_paths:
  - "**/*.log"
  - "temp/**"
  - "cache/**"

# Режим
read_only: false

# Исключенные инструменты
excluded_tools:
  - delete_lines
  - execute_shell_command

# Начальный промпт
initial_prompt: |
  This is a specialized project.
  Follow these conventions:
  - Use proper naming
  - Write tests
  - Document changes

# Имя проекта
project_name: "my-project"
```

---

## 🔍 Поиск и навигация

### Поиск файлов

```python
# По имени
list_dir(".", recursive=True)

# По шаблону (regex)
search_for_pattern(
    substring_pattern="*.bsl",
    path="src/"
)
```

### Поиск кода

```python
# Простой поиск
search_for_pattern(
    substring_pattern="Процедура\\s+(\\w+)",
    path="src/",
    output_mode="files_with_matches"
)

# С контекстом
search_for_pattern(
    substring_pattern="ФормированиеНомераПробы",
    context_lines_before=3,
    context_lines_after=3,
    output_mode="content"
)
```

### Поиск символов (требует LSP)

```python
# Все функции в файле
find_symbol(
    name_path="*",
    relative_path="module.py",
    include_kinds=[12]  # 12 = Function
)

# Конкретный класс с методами
find_symbol(
    name_path="MyClass",
    depth=1,  # включить методы
    include_body=False
)
```

---

## 📊 Онбординг

### Процесс

```
1. check_onboarding_performed()
   ↓
2. Если НЕТ памяти:
   onboarding()
   ↓
3. Изучение проекта:
   - list_dir
   - read_file
   - find_symbol
   ↓
4. Создание памяти:
   - project_overview
   - suggested_commands
   - task_completion_checklist
   ↓
5. Готово!
```

### Что создается

| Файл | Описание |
|------|----------|
| `project_overview.md` | Обзор проекта |
| `suggested_commands.md` | Команды для работы |
| `task_completion_checklist.md` | Чеклист задач |

---

## 🛠️ Contexts и Modes

### Contexts

| Context | Описание | Инструменты |
|---------|----------|-------------|
| `desktop-app` | Claude Desktop | Все + UI |
| `agent` | Автономный агент | Все + планирование |
| `ide-assistant` | IDE интеграция | Ограниченные |

### Modes

| Mode | Описание | Поведение |
|------|----------|-----------|
| `interactive` | Интерактивный | Задает вопросы |
| `editing` | Редактирование | Активно меняет код |
| `planning` | Планирование | Только планы |
| `one-shot` | Одна задача | Без контекста |

### Переключение

```python
switch_modes(["interactive", "editing"])
```

---

## 📋 Чеклист онбординга

### Для нового проекта

- [ ] Создать `.serena/project.yml`
- [ ] Создать папки `memories/` и `cache/`
- [ ] Запустить `serena-mcp-server`
- [ ] Проверить `check_onboarding_performed()`
- [ ] Если нужно: `onboarding()`
- [ ] Проверить создание `project_overview.md`
- [ ] Проверить `suggested_commands.md`
- [ ] Проверить `task_completion_checklist.md`

### Для существующего проекта

- [ ] Проверить наличие `.serena/`
- [ ] Проверить `project.yml`
- [ ] Запустить `serena-mcp-server`
- [ ] Выполнить `list_memories()`
- [ ] Прочитать `active_project_context`
- [ ] Загрузить нужные воспоминания

---

## 🐛 Troubleshooting

### Проблема: Папка .serena в подпапке пустая

**Решение**: Это нормально! Serena использует только корневую `.serena/`

### Проблема: Онбординг не выполняется

```python
# 1. Проверить наличие memories
list_memories()

# 2. Если пусто - запустить онбординг
onboarding()

# 3. Следовать инструкциям
```

### Проблема: Language Server не работает

**Решение**:
- Для BSL: используйте file_tools вместо symbol_tools
- Для других языков: проверьте установку LSP

### Проблема: Память не сохраняется

```python
# Проверить путь к проекту
get_current_config()

# Проверить наличие .serena/memories/
list_dir(".serena/memories/")

# Попробовать явно
write_memory("test", "# Test")
list_memories()
```

### Проблема: Кэш устарел

```bash
# Удалить кэш
rm -rf .serena/cache/*

# Перезапустить Serena
serena-mcp-server
```

---

## 📚 Полезные ссылки

- **Документация**: `docs/SERENA_PROJECT_MANAGEMENT.md`
- **Диаграммы**: `docs/SERENA_ARCHITECTURE_DIAGRAM.md`
- **Serena README**: `serena/README.md`
- **Serena CLAUDE.md**: `serena/CLAUDE.md`

---

## 💡 Советы и трюки

### 1. Используйте префиксы

```
✅ project_251029_overview
✅ detailed_analysis_ARM
✅ active_project_context

❌ overview
❌ analysis
❌ context
```

### 2. Структурируйте память

```markdown
# Хорошо
## 1. Overview
## 2. Details
## 3. Examples

# Плохо
Все в одном абзаце без структуры
```

### 3. Обновляйте active_project_context

```python
# При каждом переключении задачи
write_memory("active_project_context", "...")
```

### 4. Используйте list_memories() в начале

```python
# Первое действие в сессии
memories = list_memories()
# Посмотреть что доступно
```

### 5. Не дублируйте код в памяти

```markdown
# Хорошо
Файл: src/module.py
Функция: process_data() (строки 45-67)
Описание: обрабатывает данные из источника

# Плохо
Файл: src/module.py
Код:
\`\`\`python
def process_data():
    # 200 строк кода
\`\`\`
```

---

## ⚡ Команды на каждый день

### Утром (начало работы)

```python
# 1. Проверить список памяти
list_memories()

# 2. Прочитать активный контекст
read_memory("active_project_context")

# 3. Загрузить нужную память
read_memory("project_current_overview")
```

### В процессе работы

```python
# Анализ
get_symbols_overview("file.py")
find_symbol("MyClass", include_body=True)

# Сохранение
write_memory("analysis_result", "...")
```

### Вечером (завершение работы)

```python
# Обновить контекст
write_memory(
    "active_project_context",
    """
    Completed: анализ модуля X
    Next: разработка функции Y
    """
)
```

---

## 🎓 Глоссарий

| Термин | Описание |
|--------|----------|
| **Memory** | MD-файл в `.serena/memories/` |
| **Onboarding** | Первичная инициализация проекта |
| **Active context** | Текущее состояние работы |
| **Context** | Набор доступных инструментов |
| **Mode** | Режим работы агента |
| **LSP** | Language Server Protocol |
| **Symbol** | Элемент кода (класс, функция и т.д.) |

---

**Дата создания**: 2025-10-29
**Версия**: 1.0

Этот quick reference создан для быстрого доступа к основным функциям Serena.
Для подробной информации см. `SERENA_PROJECT_MANAGEMENT.md`
