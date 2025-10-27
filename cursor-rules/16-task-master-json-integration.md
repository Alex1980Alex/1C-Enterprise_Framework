# 20. Task Master JSON Integration - Интеграция JSON вывода и Cursor keybindings

> **Интеграция Task Master с современными инструментами разработки через JSON API и горячие клавиши**

## 🎯 НАЗНАЧЕНИЕ

Определяет правила работы с новой JSON функциональностью Task Master и интеграцией с Cursor Editor для повышения продуктивности разработки.

---

## 🔧 JSON OUTPUT ФУНКЦИОНАЛЬНОСТЬ

### **ПРАВИЛО**: Использование JSON для автоматизации

#### **Новые команды Task Master (v0.26.0+)**
```bash
# Основные команды с JSON выводом
npx task-master list --json                    # Все задачи в JSON
npx task-master list --status=pending --json   # Фильтрация + JSON
npx task-master list --tag=feature --json      # По тегам + JSON
npx task-master show <id> --json               # Детали задачи в JSON
```

#### **Структура JSON ответа**
```json
{
  "tasks": [
    {
      "id": 67,
      "title": "Add CLI JSON output and Cursor keybindings integration",
      "description": "Implementation details...",
      "status": "completed",
      "dependencies": [],
      "priority": "high",
      "testStrategy": "Test JSON output and keybindings functionality"
    }
  ],
  "filter": "pending",
  "stats": {
    "total": 96,
    "completed": 59,
    "pending": 34,
    "inProgress": 2,
    "completionPercentage": 61.46
  }
}
```

### **Автоматическое использование JSON API**

#### **В скриптах интеграции**
```bash
# Экспорт задач для обработки
npx task-master list --json > current-tasks.json

# Интеграция с внешними инструментами
npx task-master list --status=pending --json | jq '.stats.pending'

# Автоматическое обновление дашбордов
npx task-master list --json | python scripts/update-dashboard.py
```

#### **В MCP интеграции**
```python
# scripts/mcp-integration/taskmaster-json-integration.py
def get_task_context_json(task_id):
    """Получение структурированных данных задачи для MCP"""
    result = subprocess.run([
        "npx", "task-master", "show", str(task_id), "--json"
    ], capture_output=True, text=True, cwd="claude-task-master")

    return json.loads(result.stdout)

def export_for_reasoner(task_id):
    """Экспорт задачи для MCP Reasoner анализа"""
    task_data = get_task_context_json(task_id)
    reasoner_task = {
        "task": task_data["title"],
        "description": task_data["description"],
        "priority": task_data["priority"],
        "context": task_data["testStrategy"]
    }
    return reasoner_task
```

---

## ⌨️ CURSOR EDITOR ИНТЕГРАЦИЯ

### **ПРАВИЛО**: Использование горячих клавиш для повышения продуктивности

#### **Основные сочетания клавиш (Ctrl+Shift+T + клавиша)**
```json
{
  "Ctrl+Shift+T L": "npx task-master list",
  "Ctrl+Shift+T J": "npx task-master list --json",
  "Ctrl+Shift+T N": "npx task-master next",
  "Ctrl+Shift+T P": "npx task-master list --status=pending",
  "Ctrl+Shift+T D": "npx task-master list --status=done",
  "Ctrl+Shift+T S": "npx task-master show ",
  "Ctrl+Shift+T A": "npx task-master add-task --prompt=\"",
  "Ctrl+Shift+T U": "npx task-master set-status --id=",
  "Ctrl+Shift+T C": "npx task-master list --compact",
  "Ctrl+Shift+T T": "npx task-master tags",
  "Ctrl+Shift+T H": "npx task-master --help",
  "Ctrl+Shift+T R": "npx task-master research \""
}
```

#### **Автоматическое использование в workflow**
```bash
# Быстрый доступ к задачам
Ctrl+Shift+T N        # Получить следующую задачу
Ctrl+Shift+T S 67     # Показать детали задачи #67
Ctrl+Shift+T J        # Экспорт в JSON для обработки
```

### **Интеграция с Claude Code**

#### **JSON вывод в чате Claude Code**
```bash
# Команды работают напрямую в терминале Claude Code
npx task-master list --json | head -20
npx task-master show 67 --json | jq '.priority'
```

#### **MCP команды + JSON**
```javascript
// Альтернативные способы получения данных
mcp__task_master_ai__get_tasks();    // = npx task-master list --json
mcp__task_master_ai__next_task();    // = npx task-master next

// Интеграция с Sequential Thinking
const taskData = await mcp__task_master_ai__get_task(67);
await mcp__sequential_thinking__sequentialthinking({
  thought: `Анализирую задачу: ${taskData.title}`,
  taskContext: taskData
});
```

---

## 🔄 WORKFLOW ИНТЕГРАЦИЯ

### **ОБНОВЛЕННЫЙ workflow с JSON**

#### **Task Master → Sequential Thinking → Serena (С JSON)**
```python
# Расширенный workflow с JSON API
def enhanced_task_processing(task_id):
    # 1. Получение структурированных данных
    task_json = get_task_json(task_id)

    # 2. Подготовка для Sequential Thinking
    thinking_prompt = f"""
    Задача: {task_json['title']}
    Описание: {task_json['description']}
    Приоритет: {task_json['priority']}
    Статус: {task_json['status']}
    Зависимости: {task_json['dependencies']}
    """

    # 3. Sequential Thinking с контекстом
    result = mcp__sequential_thinking__sequentialthinking({
        "thought": thinking_prompt,
        "totalThoughts": calculate_complexity(task_json),
        "taskContext": task_json
    })

    # 4. Serena сохранение с метаданными
    mcp__serena__write_memory(f"task_{task_id}_json_analysis", {
        "task_data": task_json,
        "thinking_result": result,
        "timestamp": datetime.now().isoformat()
    })

    return result
```

#### **Автоматические триггеры**
```bash
# При обнаружении упоминания задачи в чате
if [[ $user_message =~ "задача #([0-9]+)" ]]; then
    task_id=${BASH_REMATCH[1]}
    # Автоматически получить JSON данные
    task_json=$(npx task-master show $task_id --json)
    # Запустить enhanced workflow
    process_task_with_json $task_id
fi
```

---

## 🤖 MCP REASONER ИНТЕГРАЦИЯ

### **ПРАВИЛО**: Автоматическое использование JSON для Reasoner

#### **Экспорт задач для глубокого анализа**
```python
# scripts/mcp-integration/taskmaster-reasoner-integration.py
def export_task_for_reasoner(task_id):
    """Экспорт задачи Task Master для MCP Reasoner"""

    # 1. Получение JSON данных
    task_data = json.loads(subprocess.run([
        "npx", "task-master", "show", str(task_id), "--json"
    ], capture_output=True, text=True).stdout)

    # 2. Подготовка для Reasoner
    reasoner_task = {
        "problem": task_data["title"],
        "context": {
            "description": task_data["description"],
            "priority": task_data["priority"],
            "dependencies": task_data["dependencies"],
            "testStrategy": task_data.get("testStrategy", "")
        },
        "strategy": "mcts" if task_data["priority"] == "high" else "beam_search",
        "max_depth": 10 if "complex" in task_data["description"].lower() else 5
    }

    # 3. Сохранение для Reasoner
    with open(f"cache/reasoner-task-{task_id}.json", "w", encoding="utf-8") as f:
        json.dump(reasoner_task, f, ensure_ascii=False, indent=2)

    return reasoner_task
```

#### **Полный цикл с Task Master + Reasoner**
```bash
# Полная интеграция Task Master + MCP Reasoner
python scripts/mcp-integration/full-task-analysis.py \
  --task-id=67 \
  --use-json \
  --use-reasoner \
  --save-to-memory
```

---

## 📊 ПРАКТИЧЕСКИЕ ПРИМЕРЫ

### **Пример 1: Задача #67 (выполненная)**
```bash
# 1. Получение данных задачи
npx task-master show 67 --json
# Output: {"id": 67, "title": "Add CLI JSON output and Cursor keybindings", ...}

# 2. Использование Cursor keybindings
Ctrl+Shift+T S 67     # Быстрый просмотр
Ctrl+Shift+T J        # JSON экспорт для анализа

# 3. Интеграция с MCP
python scripts/mcp-integration/taskmaster-reasoner-integration.py --task-id=67
```

### **Пример 2: Автоматический анализ pending задач**
```bash
# 1. Экспорт всех pending задач
npx task-master list --status=pending --json > pending-tasks.json

# 2. Массовая обработка через MCP Reasoner
python scripts/mcp-integration/batch-task-analysis.py --input=pending-tasks.json

# 3. Обновление статусов через JSON API
python scripts/update-task-status.py --completed-tasks=analysis-results.json
```

### **Пример 3: Dashboard интеграция**
```bash
# Создание real-time dashboard
npx task-master list --json | \
python scripts/mcp-integration/generate-dashboard.py \
  --output="reports/task-dashboard.html" \
  --auto-refresh=30
```

---

## ✅ КОНТРОЛЬНЫЙ ЧЕКЛИСТ

### **При работе с Task Master**
- [ ] Используются JSON команды для экспорта данных
- [ ] Cursor keybindings настроены и используются
- [ ] JSON данные интегрируются с MCP инструментами
- [ ] Автоматические скрипты обновлены для JSON API

### **При интеграции с MCP**
- [ ] Task Master данные экспортируются в JSON формате
- [ ] JSON структура совместима с MCP Reasoner
- [ ] Результаты анализа сохраняются в Serena с метаданными
- [ ] Статусы задач обновляются автоматически

### **При разработке**
- [ ] Горячие клавиши используются для быстрого доступа
- [ ] JSON API интегрирован в workflow скрипты
- [ ] Dashboard обновляется автоматически
- [ ] Cursor integration работает в Claude Code

---

## 🚫 ЗАПРЕЩЕНО

1. ❌ Использовать старые текстовые команды вместо JSON API
2. ❌ Игнорировать Cursor keybindings в пользу ручного ввода
3. ❌ Экспортировать данные в не-JSON форматах для MCP
4. ❌ Пропускать сохранение JSON контекста в Serena
5. ❌ Использовать Task Master без интеграции с MCP инструментами

---

## 🔗 ИНТЕГРАЦИЯ С ДРУГИМИ ПРАВИЛАМИ

Данный модуль расширяет и интегрируется с:
- `16-workflow-integration.md` - интеграция workflow
- `08-mcp-memory.md` - работа с памятью Serena
- `21-mcp-reasoner-integration.md` - интеграция с MCP Reasoner
- `07-automation-rules.md` - правила автоматизации

---

**📅 Создано**: 2025-09-27 (по итогам Task Master #67)
**🎯 Статус**: ОБЯЗАТЕЛЬНОЕ правило для работы с Task Master
**✅ Применение**: Немедленное для всех проектов с Task Master v0.26.0+
**🔧 Реализация**: Готова и протестирована