# 📋 Руководство по персистентному управлению задачами

## 🎯 Обзор системы

Система персистентного управления задачами позволяет сохранять и восстанавливать задачи между сеансами Claude Code в 1C-Enterprise Framework.

### ✅ Возможности:
- 💾 **Сохранение задач между сеансами** - задачи не теряются при переподключении
- 🔍 **Поиск и фильтрация** - быстрый доступ к нужным задачам
- 📊 **Отслеживание статуса** - pending, in_progress, completed
- 🔗 **Интеграция с Memory Graph** - надежное персистентное хранилище
- 🚀 **Совместимость с Task Master** - интеграция с существующими инструментами

---

## 🏗️ Архитектура системы

```
┌─────────────────────────────────────────────────┐
│             🎯 ПОЛЬЗОВАТЕЛЬ                      │
│                                                 │
│  "Поставил задачу" → "Переподключился" →         │
│  "Спросил про задачи" → "Получил список"        │
└─────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────┐
│         📋 УРОВЕНЬ TodoWrite (Сеанс)            │
│                                                 │
│  • TodoWrite() - управление задачами сеанса     │
│  • Автосохранение → Memory Graph                │
│  • Восстановление из Memory Graph               │
└─────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────┐
│       🧠 УРОВЕНЬ Memory Graph (Персистентный)   │
│                                                 │
│  • mcp__memory__create_entities()               │
│  • mcp__memory__search_nodes()                  │
│  • Тип: "user_task"                             │
│  • Хранилище: cache/memory-graph.json           │
└─────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────┐
│     🔧 УРОВЕНЬ API (scripts/persistent-tasks-api.py) │
│                                                 │
│  • create_task() - создание задач               │
│  • list_tasks() - получение списков             │
│  • update_task_status() - обновление статуса    │
│  • CLI интерфейс                                │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Быстрый старт

### 1. **Проверка готовности системы:**
```bash
# Проверка MCP Memory
mcp__memory__search_nodes("user_task")

# Проверка API
python3 scripts/persistent-tasks-api.py summary
```

### 2. **Создание первой задачи:**
```bash
# Через CLI
scripts/task-commands.sh create "Настроить персистентные задачи" "Первая тестовая задача" high

# Через Python API
python3 scripts/persistent-tasks-api.py create "Название задачи"
```

### 3. **Просмотр задач:**
```bash
# Все задачи
scripts/task-commands.sh list

# Только активные
scripts/task-commands.sh list pending
```

---

## 📖 Подробное руководство

### 🔧 **Создание задач**

#### **Метод 1: Через MCP Memory (прямой)**
```javascript
mcp__memory__create_entities([{
  name: "task_2025-10-07_abc123",
  entityType: "user_task",
  observations: [
    "Status: pending",
    "Created: 2025-10-07T22:45:00Z",
    "Title: Название задачи",
    "Description: Подробное описание",
    "Priority: high",
    "SessionId: current_session",
    "LastUpdated: 2025-10-07T22:45:00Z"
  ]
}])
```

#### **Метод 2: Через Python API**
```bash
python3 scripts/persistent-tasks-api.py create "Название" "Описание" "приоритет"
```

#### **Метод 3: Через Bash CLI**
```bash
scripts/task-commands.sh create "Название" "Описание" high
```

### 🔍 **Поиск и просмотр задач**

#### **Поиск всех задач пользователя:**
```javascript
mcp__memory__search_nodes("user_task")
```

#### **Фильтрация по статусу:**
```bash
# Pending задачи
scripts/task-commands.sh list pending

# Completed задачи
scripts/task-commands.sh list completed
```

### ✅ **Обновление статуса задач**

#### **Завершение задачи:**
```javascript
mcp__memory__add_observations([{
  entityName: "task_2025-10-07_abc123",
  contents: ["Status: completed | Notes: Задача выполнена успешно | Updated: 2025-10-07T23:00:00Z"]
}])
```

#### **Через CLI:**
```bash
scripts/task-commands.sh complete task_2025-10-07_abc123 "Выполнено успешно"
```

---

## 🎭 Интеграция с существующими системами

### **TodoWrite + Memory Graph**

Автоматическая синхронизация задач TodoWrite с персистентным хранилищем:

```bash
# Синхронизация завершенных задач
scripts/task-commands.sh sync
```

**Рекомендуемый workflow:**
1. Используй TodoWrite для текущего сеанса
2. В конце сеанса вызови синхронизацию
3. В новом сеансе восстанови задачи из Memory Graph

### **Task Master Integration**

Интеграция с существующим Task Master AI:

```bash
# Экспорт из Task Master
cd claude-task-master
task-master list --json > ../cache/taskmaster-sync.json

# Импорт в персистентную систему
python3 scripts/persistent-tasks-api.py import-taskmaster cache/taskmaster-sync.json
```

---

## 💡 Примеры использования

### **Сценарий 1: Простая задача**
```bash
# Сеанс 1: Создание задачи
scripts/task-commands.sh create "Исправить баг в модуле" "Найден баг в процедуре ОбработкаДанных" high

# [ПЕРЕПОДКЛЮЧЕНИЕ]

# Сеанс 2: Проверка задач
scripts/task-commands.sh list pending
# Вывод: task_2025-10-07_abc123 - Исправить баг в модуле (pending)

# Работа над задачей...

# Завершение задачи
scripts/task-commands.sh complete task_2025-10-07_abc123 "Баг исправлен, тестирование пройдено"
```

### **Сценарий 2: Комплексный проект**
```bash
# Создание нескольких связанных задач
scripts/task-commands.sh create "Анализ требований проекта X" "Изучить ТЗ и создать план" high
scripts/task-commands.sh create "Проектирование архитектуры" "Создать схему модулей" medium
scripts/task-commands.sh create "Реализация модуля авторизации" "Написать код авторизации" medium

# Просмотр всех задач проекта
scripts/task-commands.sh list
```

### **Сценарий 3: Интеграция с TodoWrite**
```bash
# В процессе работы используй TodoWrite как обычно
TodoWrite([
  {content: "Проанализировать код модуля", status: "in_progress"},
  {content: "Написать тесты", status: "pending"},
  {content: "Обновить документацию", status: "completed"}
])

# В конце сеанса - синхронизация
scripts/task-commands.sh sync
```

---

## 🔧 Настройка и конфигурация

### **Структура файлов:**
```
D:\1C-Enterprise_Framework\
├── scripts/
│   ├── persistent-tasks-api.py    # Python API
│   └── task-commands.sh           # Bash CLI
├── cache/
│   └── memory-graph.json          # Хранилище Memory Graph
└── docs/
    └── Persistent-Task-Management-Guide.md  # Эта документация
```

### **Зависимости:**
- ✅ **Memory MCP** - основное хранилище
- ✅ **Python 3** - для API скриптов
- ✅ **Bash** - для CLI команд
- ✅ **Claude Code** - среда выполнения

### **Конфигурация Memory Graph:**
```json
{
  "entities": [
    {
      "name": "task_YYYY-MM-DD_identifier",
      "entityType": "user_task",
      "observations": [
        "Status: pending|in_progress|completed",
        "Created: ISO_timestamp",
        "Title: string",
        "Description: string",
        "Priority: low|medium|high",
        "SessionId: string",
        "LastUpdated: ISO_timestamp"
      ]
    }
  ]
}
```

---

## 🚨 Устранение неполадок

### **Проблема: Задачи не сохраняются**
```bash
# Проверка Memory Graph
mcp__memory__read_graph()

# Проверка прав доступа к файлам
ls -la cache/memory-graph.json

# Тест создания задачи
python3 scripts/persistent-tasks-api.py create "Test Task"
```

### **Проблема: API не работает**
```bash
# Проверка Python
python3 --version

# Проверка зависимостей
pip3 install uuid datetime json

# Тест API
python3 scripts/persistent-tasks-api.py summary
```

### **Проблема: CLI команды недоступны**
```bash
# Проверка прав выполнения
chmod +x scripts/task-commands.sh

# Тест команды
./scripts/task-commands.sh summary
```

---

## 📊 Мониторинг и отчетность

### **Просмотр статистики:**
```bash
# Сводка текущего сеанса
scripts/task-commands.sh summary

# Все задачи с фильтрацией
mcp__memory__search_nodes("user_task Status:pending")
mcp__memory__search_nodes("user_task Status:completed")
```

### **Экспорт данных:**
```bash
# Экспорт всех задач в JSON
mcp__memory__read_graph() > tasks_backup.json

# Восстановление из бэкапа
# (требует ручной загрузки через MCP Memory API)
```

---

## 🔮 Планы развития

### **Фаза 2: Расширенные возможности**
- 🏷️ **Теги и категории** - группировка задач по проектам
- ⏰ **Временные метки** - дедлайны и напоминания
- 📎 **Вложения** - связь с файлами и документами
- 🔗 **Зависимости** - связи между задачами

### **Фаза 3: Интеграция с внешними системами**
- 📧 **Email уведомления** - отправка отчетов
- 📱 **Web интерфейс** - управление через браузер
- 🔄 **GitHub Issues** - синхронизация с GitHub
- 📋 **Jira интеграция** - экспорт в корпоративные системы

---

## ✅ Заключение

Система персистентного управления задачами готова к использованию и предоставляет:

1. ✅ **Надежное сохранение** между сеансами
2. ✅ **Простой API** для управления
3. ✅ **Интеграцию** с существующими инструментами
4. ✅ **Гибкость** в использовании

**Начни использовать уже сегодня:**
```bash
scripts/task-commands.sh create "Моя первая персистентная задача" "Тестирование новой системы" high
```

---

*Документация обновлена: 2025-10-07*
*Версия системы: 1.0.0*
*Статус: Готово к продуктивному использованию*