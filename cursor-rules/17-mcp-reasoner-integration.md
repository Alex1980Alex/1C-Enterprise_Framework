# 21. MCP Reasoner Integration - Интеграция глубокого анализа

> **Интеграция MCP Reasoner для сложного пошагового анализа и решения архитектурных задач 1С**

## 🎯 НАЗНАЧЕНИЕ

Определяет правила работы с MCP Reasoner v2.0.0 для глубокого анализа конфигураций 1С, архитектурных решений и сложных технических задач.

---

## 🧠 MCP REASONER ВОЗМОЖНОСТИ

### **ПРАВИЛО**: Автоматическое использование Reasoner для сложных задач

#### **Типы задач для MCP Reasoner**
1. **Архитектурный анализ** - структура конфигурации, зависимости
2. **Анализ качества кода** - глубокий анализ BSL проблем
3. **Оптимизация производительности** - узкие места, рефакторинг
4. **Поиск дублирования** - анализ повторяющихся паттернов
5. **Планирование решений** - декомпозиция сложных задач

#### **Стратегии анализа**
```python
strategies = {
    "beam_search": {
        "use_for": ["простые задачи", "быстрый анализ"],
        "time": "< 5 минут",
        "depth": 5,
        "suitable_for": "BSL ошибки, простые рефакторинги"
    },
    "mcts": {
        "use_for": ["сложные архитектурные решения", "критичные проблемы"],
        "time": "10-15 минут",
        "depth": 10,
        "suitable_for": "архитектура конфигурации, производительность"
    }
}
```

### **Автоматический выбор стратегии**
```python
def select_reasoner_strategy(task_context):
    """Автоматический выбор стратегии на основе контекста задачи"""

    # Анализ сложности
    complexity_indicators = [
        "архитектура" in task_context.description.lower(),
        "производительность" in task_context.description.lower(),
        "рефакторинг" in task_context.description.lower(),
        task_context.priority == "high",
        len(task_context.dependencies) > 3,
        "критичн" in task_context.description.lower()
    ]

    complexity_score = sum(complexity_indicators)

    if complexity_score >= 3:
        return "mcts"  # Глубокий анализ
    else:
        return "beam_search"  # Быстрый анализ
```

---

## 🔄 ИНТЕГРАЦИЯ С WORKFLOW

### **ОБНОВЛЕННЫЙ Task Master → Sequential Thinking → MCP Reasoner → Serena**

#### **Автоматическое включение Reasoner в workflow**
```python
def enhanced_workflow_with_reasoner(task_id):
    """Расширенный workflow с автоматическим использованием MCP Reasoner"""

    # 1. Task Master: получение структурированных данных
    task_data = get_task_json(task_id)

    # 2. Анализ необходимости Reasoner
    needs_reasoner = analyze_task_complexity(task_data)

    if needs_reasoner:
        # 3a. MCP Reasoner для сложных задач
        reasoner_result = prepare_and_run_reasoner(task_data)

        # 4a. Sequential Thinking с результатами Reasoner
        thinking_result = mcp__sequential_thinking__sequentialthinking({
            "thought": f"Анализирую результаты MCP Reasoner для задачи {task_id}",
            "reasoner_context": reasoner_result,
            "task_data": task_data
        })
    else:
        # 3b. Прямо Sequential Thinking для простых задач
        thinking_result = mcp__sequential_thinking__sequentialthinking({
            "thought": f"Анализирую задачу {task_id}",
            "task_data": task_data
        })

    # 5. Serena: сохранение всех результатов
    mcp__serena__write_memory(f"task_{task_id}_complete_analysis", {
        "task_data": task_data,
        "reasoner_used": needs_reasoner,
        "reasoner_result": reasoner_result if needs_reasoner else None,
        "thinking_result": thinking_result,
        "timestamp": datetime.now().isoformat()
    })

    return thinking_result

def analyze_task_complexity(task_data):
    """Определение необходимости MCP Reasoner"""
    complexity_triggers = [
        "архитектур" in task_data["description"].lower(),
        "производительност" in task_data["description"].lower(),
        "анализ зависимост" in task_data["description"].lower(),
        "рефакторинг" in task_data["description"].lower(),
        "оптимизаци" in task_data["description"].lower(),
        task_data["priority"] == "high",
        len(task_data["dependencies"]) > 2
    ]

    return sum(complexity_triggers) >= 2
```

#### **Автоматические триггеры Reasoner**
```bash
# При обнаружении ключевых слов в запросе пользователя
reasoner_triggers="архитектура|производительность|оптимизация|рефакторинг|анализ зависимостей|граф зависимостей|дублирование кода"

if [[ $user_request =~ $reasoner_triggers ]]; then
    echo "🧠 Обнаружена сложная задача - запуск MCP Reasoner"
    python scripts/mcp-integration/auto-reasoner-analysis.py --request="$user_request"
fi
```

---

## 📋 АНАЛИТИЧЕСКИЕ СЦЕНАРИИ

### **ПРАВИЛО**: Использование готовых сценариев для типовых задач

#### **Сценарий 1: Анализ проведения документа**
```bash
# scripts/mcp-integration/scenarios/01-document-posting-analysis.md
python scripts/mcp-integration/full-analysis-pipeline.py \
  --input "src/Documents/ДокументПроведения/Ext/ObjectModule.bsl" \
  --scenario "document-posting" \
  --use-reasoner \
  --strategy "mcts" \
  --output "reports/document-posting-analysis"
```

#### **Сценарий 2: Поиск дублирующегося кода**
```bash
# scripts/mcp-integration/scenarios/02-duplicate-code-analysis.md
python scripts/mcp-integration/full-analysis-pipeline.py \
  --input "src/" \
  --scenario "duplicate-analysis" \
  --use-reasoner \
  --strategy "beam_search" \
  --output "reports/duplicate-code-analysis"
```

#### **Сценарий 3: Граф зависимостей конфигурации**
```bash
# scripts/mcp-integration/scenarios/03-dependency-graph-analysis.md
python scripts/mcp-integration/full-analysis-pipeline.py \
  --input "src/" \
  --scenario "dependency-graph" \
  --use-reasoner \
  --strategy "mcts" \
  --output "reports/dependency-analysis"
```

### **Автоматический выбор сценария**
```python
def auto_select_scenario(task_description, file_patterns):
    """Автоматический выбор сценария анализа"""

    scenarios = {
        "document-posting": {
            "keywords": ["проведение", "документ", "транзакция"],
            "file_patterns": ["**/Documents/**/ObjectModule.bsl"]
        },
        "duplicate-analysis": {
            "keywords": ["дублирование", "повтор", "общий модуль"],
            "file_patterns": ["**/CommonModules/**/*.bsl"]
        },
        "dependency-graph": {
            "keywords": ["зависимости", "граф", "архитектура"],
            "file_patterns": ["src/**/*.bsl"]
        }
    }

    for scenario_name, config in scenarios.items():
        if any(keyword in task_description.lower() for keyword in config["keywords"]):
            return scenario_name

    return "general-analysis"  # По умолчанию
```

---

## 🤖 АВТОМАТИЗАЦИЯ REASONER

### **Полный автоматический pipeline**

#### **scripts/mcp-integration/auto-reasoner-workflow.py**
```python
#!/usr/bin/env python3
"""
Автоматический workflow с MCP Reasoner
Использование: python auto-reasoner-workflow.py --task-id=67
"""

import json
import subprocess
import sys
from datetime import datetime

def main():
    task_id = sys.argv[2] if len(sys.argv) > 2 else None

    if not task_id:
        print("❌ Не указан task-id")
        return

    print(f"🚀 Запуск автоматического анализа задачи #{task_id}")

    # 1. Получение данных Task Master
    task_json = get_task_data(task_id)
    print(f"📋 Задача: {task_json['title']}")

    # 2. Анализ сложности
    complexity = analyze_complexity(task_json)
    strategy = "mcts" if complexity > 3 else "beam_search"
    print(f"🧠 Стратегия: {strategy} (сложность: {complexity})")

    # 3. Подготовка для Reasoner
    reasoner_task = prepare_reasoner_task(task_json, strategy)

    # 4. Запуск полного pipeline
    result = run_full_pipeline(task_id, reasoner_task)

    # 5. Сохранение результатов
    save_results(task_id, result)

    print(f"✅ Анализ завершен: reports/task-{task_id}-reasoner-analysis/")

def get_task_data(task_id):
    """Получение данных задачи из Task Master"""
    result = subprocess.run([
        "npx", "task-master", "show", task_id, "--json"
    ], capture_output=True, text=True, cwd="claude-task-master")

    return json.loads(result.stdout)

def analyze_complexity(task_data):
    """Анализ сложности задачи"""
    complexity_indicators = [
        "архитектур" in task_data["description"].lower(),
        "производительност" in task_data["description"].lower(),
        "рефакторинг" in task_data["description"].lower(),
        "оптимизаци" in task_data["description"].lower(),
        task_data["priority"] == "high",
        len(task_data["dependencies"]) > 2,
        "критичн" in task_data["description"].lower()
    ]

    return sum(complexity_indicators)

def prepare_reasoner_task(task_data, strategy):
    """Подготовка задачи для MCP Reasoner"""
    return {
        "problem": task_data["title"],
        "context": {
            "description": task_data["description"],
            "priority": task_data["priority"],
            "dependencies": task_data["dependencies"]
        },
        "strategy": strategy,
        "max_depth": 10 if strategy == "mcts" else 5
    }

if __name__ == "__main__":
    main()
```

#### **Интеграция с Task Master workflow**
```bash
# Автоматический запуск при создании задачи
#!/bin/bash
# hook: post-task-creation

TASK_ID=$1
TASK_JSON=$(npx task-master show $TASK_ID --json)

# Проверка необходимости Reasoner
if echo "$TASK_JSON" | jq -r '.description' | grep -qE "архитектур|производительност|рефакторинг"; then
    echo "🧠 Запуск MCP Reasoner анализа для задачи #$TASK_ID"
    python scripts/mcp-integration/auto-reasoner-workflow.py --task-id=$TASK_ID
else
    echo "📝 Простая задача #$TASK_ID - Reasoner не требуется"
fi
```

---

## 📊 ПРАКТИЧЕСКИЕ ПРИМЕРЫ

### **Пример 1: Архитектурный анализ конфигурации**
```bash
# Пользователь: "Проанализируй архитектуру конфигурации на предмет оптимизации"

# 1. Автоматическое создание задачи
npx task-master add-task --prompt="Архитектурный анализ конфигурации для оптимизации"
# Output: Created task #108

# 2. Автоматический запуск Reasoner (triggered by keywords)
python scripts/mcp-integration/auto-reasoner-workflow.py --task-id=108
# Output: 🧠 Стратегия: mcts (сложность: 5)

# 3. Результат: reports/task-108-reasoner-analysis/
#    - dependency-graph.json
#    - architecture-recommendations.md
#    - optimization-plan.md
```

### **Пример 2: Анализ производительности BSL кода**
```bash
# Обнаружение проблем производительности
python -m sonar_integration analyze --severity=MAJOR | \
grep -i "производительность" | \
python scripts/mcp-integration/create-reasoner-task.py --type="performance"

# Автоматический глубокий анализ через MCP Reasoner
# Результат: конкретные рекомендации по оптимизации
```

### **Пример 3: Планирование рефакторинга**
```bash
# Task Master + MCP Reasoner для планирования
npx task-master add-task --prompt="Рефакторинг модуля ОбщегоНазначения с выделением подмодулей"
# → Автоматически запускается MCTS анализ
# → Генерируется пошаговый план рефакторинга
# → Сохраняется в Serena для повторного использования
```

---

## ✅ КОНТРОЛЬНЫЙ ЧЕКЛИСТ

### **При работе со сложными задачами**
- [ ] Проверена необходимость MCP Reasoner (сложность >= 2)
- [ ] Выбрана подходящая стратегия (beam_search/mcts)
- [ ] Подготовлены структурированные данные для анализа
- [ ] Запущен полный pipeline с сохранением результатов

### **При архитектурном анализе**
- [ ] Использован сценарий dependency-graph-analysis
- [ ] Стратегия MCTS с глубиной 10
- [ ] Результаты сохранены в Serena с метаданными
- [ ] Созданы диаграммы и рекомендации

### **При анализе производительности**
- [ ] Интегрирован с BSL Language Server
- [ ] Использована стратегия MCTS для критичных проблем
- [ ] Сгенерированы конкретные рекомендации по оптимизации
- [ ] Результаты связаны с исходным кодом

---

## 🚫 ЗАПРЕЩЕНО

1. ❌ Использовать MCP Reasoner для простых задач (сложность < 2)
2. ❌ Запускать Reasoner без структурированной подготовки данных
3. ❌ Игнорировать автоматический выбор стратегии
4. ❌ Пропускать сохранение результатов в Serena
5. ❌ Использовать Reasoner без интеграции с Task Master

---

## 🔗 ИНТЕГРАЦИЯ С ДРУГИМИ ПРАВИЛАМИ

Данный модуль расширяет и интегрируется с:
- `20-task-master-json-integration.md` - JSON API Task Master
- `16-workflow-integration.md` - основной workflow
- `08-mcp-memory.md` - сохранение в Serena
- `06-development-scenarios.md` - сценарии разработки

---

**📅 Создано**: 2025-09-27 (по итогам внедрения MCP Reasoner)
**🎯 Статус**: ОБЯЗАТЕЛЬНОЕ правило для сложных задач
**✅ Применение**: Автоматическое при сложности >= 2
**🔧 Реализация**: Готова и протестирована (v2.0.0)