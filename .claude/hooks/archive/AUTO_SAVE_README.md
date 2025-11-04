# Автоматическое сохранение в Memory MCP

Система автоматического сохранения важной информации в Knowledge Graph и TimescaleDB.

## Компоненты

### 1. auto-save-to-memory.py
Python скрипт для сохранения данных в Memory MCP.

**Функции:**
- Извлечение контекста из переменных окружения Claude
- Определение типа информации (code_exploration, web_research, etc.)
- Сохранение в Knowledge Graph через Memory MCP
- Сохранение в TimescaleDB через Memory-AI MCP
- Логирование в `cache/auto-save.log`

### 2. post-tool-result-auto-save.sh
Bash хук, запускающийся после выполнения инструментов.

**Триггеры:**
- Read, Grep, Glob - чтение и поиск кода
- WebFetch, WebSearch - веб-исследования
- mcp__github__ - GitHub операции
- mcp__1c - операции с 1C
- Task - выполнение задач
- mcp__serena__ - операции с кодом через Serena

### 3. auto-save-config.json
Конфигурация системы автосохранения.

**Параметры:**
```json
{
  "enabled": true,                    // Включить/выключить автосохранение
  "auto_save_tools": [...],           // Список инструментов для сохранения
  "min_content_length": 100,          // Минимальная длина результата
  "save_to_timescale": true,          // Сохранять в TimescaleDB
  "save_to_knowledge_graph": true,    // Сохранять в Knowledge Graph
  "log_file": "cache/auto-save.log",  // Файл логов
  "verbose": true                     // Подробные логи
}
```

## Установка

### Шаг 1: Проверка прав
```bash
chmod +x .claude/hooks/post-tool-result-auto-save.sh
chmod +x .claude/hooks/auto-save-to-memory.py
```

### Шаг 2: Активация хука
Переименуйте или создайте симлинк:
```bash
# Вариант 1: Переименовать старый хук (создать бэкап)
mv .claude/hooks/post-tool-result-memory-save.sh .claude/hooks/post-tool-result-memory-save.sh.backup

# Вариант 2: Заменить содержимое
cp .claude/hooks/post-tool-result-auto-save.sh .claude/hooks/post-tool-result-memory-save.sh
```

### Шаг 3: Проверка конфигурации
Убедитесь, что `auto-save-config.json` настроен правильно:
```bash
cat .claude/hooks/auto-save-config.json
```

## Использование

### Включение автосохранения
Установите `"enabled": true` в `auto-save-config.json`.

### Отключение автосохранения
Установите `"enabled": false` в `auto-save-config.json`.

### Настройка инструментов
Отредактируйте массив `auto_save_tools`:
```json
"auto_save_tools": [
  "Read",           // Чтение файлов
  "Grep",           // Поиск в коде
  "WebFetch",       // Веб-запросы
  "YourCustomTool"  // Добавьте свой инструмент
]
```

### Настройка минимальной длины
Изменяйте `min_content_length` для фильтрации коротких результатов:
```json
"min_content_length": 200  // Только результаты длиннее 200 символов
```

## Тестирование

### Тест 1: Проверка хука
```bash
CLAUDE_TOOL_NAME="Read" CLAUDE_TOOL_RESULT="Test content for auto-save" .claude/hooks/post-tool-result-auto-save.sh
```

**Ожидаемый вывод:**
```
🔄 Инструмент: Read
💾 Автосохранение в Memory MCP...
✓ Данные сохранены в Memory MCP
```

### Тест 2: Проверка Python скрипта
```bash
export CLAUDE_TOOL_NAME="Read"
export CLAUDE_TOOL_RESULT="Important code discovery: new implementation found"
export PWD="D:/1C-Enterprise_Framework"
python3 .claude/hooks/auto-save-to-memory.py
```

**Проверка логов:**
```bash
tail -f cache/auto-save.log
```

### Тест 3: Проверка в реальной работе
Выполните любой инструмент из списка `auto_save_tools`, например:
```bash
# В Claude Code выполните:
Read some_file.py
```

Проверьте, что данные сохранились:
```bash
# Проверка логов
cat cache/auto-save.log

# Проверка Knowledge Graph
mcp__memory__read_graph
```

## Работа системы

### Поток данных

```
Claude Code выполняет инструмент (Read, Grep, etc.)
    ↓
post-tool-result-auto-save.sh запускается автоматически
    ↓
Проверка: инструмент в списке auto_save_tools?
    ↓ Да
Извлечение переменных окружения (CLAUDE_TOOL_NAME, CLAUDE_TOOL_RESULT)
    ↓
auto-save-to-memory.py
    ↓
Определение типа сущности (code_exploration, web_research, etc.)
    ↓
Сохранение через Memory MCP
    ├─→ Knowledge Graph (entities + observations)
    └─→ TimescaleDB (conversations + messages)
    ↓
Логирование в cache/auto-save.log
    ↓
✓ Готово
```

### Типы сущностей

| Инструмент | Тип сущности | Описание |
|-----------|--------------|----------|
| Read, Grep | code_exploration | Исследование кода |
| WebFetch, WebSearch | web_research | Веб-исследования |
| mcp__github__ | github_interaction | GitHub операции |
| Task | task_execution | Выполнение задач |
| Другие | general_activity | Общая активность |

## Логирование

### Формат логов
```
2025-10-31T10:30:45.123456 - {"type": "knowledge_graph", "data": {...}}
```

### Просмотр логов
```bash
# Последние 20 записей
tail -20 cache/auto-save.log

# Мониторинг в реальном времени
tail -f cache/auto-save.log

# Поиск по типу
grep "code_exploration" cache/auto-save.log
```

## Troubleshooting

### Автосохранение не работает

**Проверка 1: Хук выполняется?**
```bash
ls -la .claude/hooks/post-tool-result-auto-save.sh
# Должны быть права: -rwxr-xr-x
```

**Проверка 2: Python доступен?**
```bash
python3 --version
# Должна быть версия 3.7+
```

**Проверка 3: Конфиг правильный?**
```bash
cat .claude/hooks/auto-save-config.json | grep '"enabled"'
# Должно быть: "enabled": true
```

**Проверка 4: Логи пишутся?**
```bash
ls -la cache/auto-save.log
# Файл должен существовать и обновляться
```

### Ошибка: скрипт не найден

Убедитесь, что пути правильные:
```bash
# Проверка структуры
tree .claude/hooks
```

Должно быть:
```
.claude/hooks/
├── auto-save-config.json
├── auto-save-to-memory.py
├── post-tool-result-auto-save.sh
└── ...
```

### Ошибка: Permission denied

Установите права:
```bash
chmod +x .claude/hooks/*.sh
chmod +x .claude/hooks/*.py
```

## Расширенная настройка

### Добавление кастомных правил

Отредактируйте `auto-save-to-memory.py`, функцию `save_to_knowledge_graph`:

```python
# Добавьте новый тип сущности
elif "MyCustomTool" in tool_name:
    entity_type = "my_custom_type"
    observation = f"Custom activity: {tool_result}"
```

### Интеграция с другими системами

Добавьте в `auto-save-to-memory.py`:

```python
def save_to_custom_system(context, config):
    """Сохранение в вашу систему"""
    # Ваша логика
    pass
```

## Версия и поддержка

**Версия:** 1.0.0
**Дата:** 2025-10-31
**Автор:** Claude Code
**Статус:** Production Ready ✅

---

**Quick Links:**
- [Main Hooks README](README.md)
- [Memory MCP Docs](../../ai-memory-system/README.md)
- [Auto Save Log](../../cache/auto-save.log)
