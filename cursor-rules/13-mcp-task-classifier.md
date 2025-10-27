# КЛАССИФИКАТОР ЗАДАЧ MCP: Автоматическое определение типа задачи

## 🎯 НАЗНАЧЕНИЕ

Автоматически определяет тип задачи для правильного выбора MCP инструментов на основе анализа описания задачи, контекста и ключевых слов.

---

## 🔍 АЛГОРИТМ КЛАССИФИКАЦИИ

### **Принцип работы**

```mermaid
graph LR
    Input[Описание задачи] --> Analysis[Анализ ключевых слов]
    Analysis --> Context[Анализ контекста]
    Context --> Score[Подсчет баллов]
    Score --> Classification[Классификация]
    Classification --> Confidence[Уровень уверенности]
```

### **Типы задач и критерии**

| Тип задачи | Ключевые слова | Контекстные индикаторы | Вес |
|------------|---------------|------------------------|-----|
| **Разработка ПО** | создать, внедрить, реализовать, код, функция, модуль, API, база данных | .bsl, .js, .py файлы, техническое задание | 🔴 HIGH |
| **Исследование** | анализ, исследование, изучить, понять, найти, сравнить, оценить | документация, статьи, best practices | 🟡 MEDIUM |
| **Управление проектом** | план, roadmap, задача, milestone, deadline, координация, статус | .taskmaster/, планирование, отчеты | 🔵 HIGH |
| **Автоматизация** | автоматизировать, скрипт, workflow, CI/CD, deploy, тестирование | scripts/, .github/, automation | 🟢 MEDIUM |
| **Обучение/Анализ** | обучение, tutorial, документация, анализ архитектуры, принципы | курсы, гайды, архитектурные решения | 🟣 LOW |

---

## 📊 ПРАВИЛА КЛАССИФИКАЦИИ

### **1. Анализ ключевых слов (40% веса)**

#### **Разработка ПО** - приоритет 1
```regex
# Русские термины
(создать|внедрить|реализ.*|разработ.*|код|функци.*|модуль|API|базы? данных|программ.*|алгоритм)

# Английские термины  
(create|implement|develop|code|function|module|API|database|programming|algorithm)

# Технические термины 1С
(процедур.*|обработчик|запрос|регистр|справочник|документ|форма|BSL)
```

#### **Исследование** - приоритет 2
```regex
# Русские термины
(анализ|исследован.*|изуч.*|понять|найти|сравн.*|оцен.*|рассмотр.*|проанализ.*)

# Английские термины
(analyz.*|research|study|understand|find|compare|evaluat.*|review|investigate)

# Контекстные термины
(документац.*|статьи|best practices|методы|подходы)
```

#### **Управление проектом** - приоритет 3
```regex
# Русские термины
(план|roadmap|задач.*|milestone|deadline|координац.*|статус|управл.*|проект)

# Английские термины
(plan|roadmap|task|milestone|deadline|coordination|status|manage|project)

# Специфичные термины
(sprint|scrum|kanban|backlog|планирование)
```

### **2. Контекстный анализ (35% веса)**

#### **Индикаторы файлов и папок**
```yaml
Разработка ПО:
  - extensions: [.bsl, .js, .py, .java, .cs, .cpp]
  - directories: [src/, CommonModules/, DataProcessors/]
  - files: [*.xml, Configuration.xml]

Исследование:
  - extensions: [.md, .txt, .pdf, .docx]
  - directories: [docs/, documentation/, research/]
  - files: [README.*, RESEARCH.*]

Управление проектом:
  - directories: [.taskmaster/, projects/, planning/]
  - files: [*.json, roadmap.*, plan.*]

Автоматизация:
  - extensions: [.sh, .bat, .yml, .yaml]
  - directories: [scripts/, .github/, automation/]
  - files: [Dockerfile, docker-compose.*]
```

### **3. Семантический анализ (25% веса)**

#### **Анализ намерений**
```javascript
// Псевдокод алгоритма
function classifyByIntent(description) {
    const intentions = {
        CREATE: /создать|сделать|построить|разработать/i,
        ANALYZE: /анализ|изучить|понять|исследовать/i,
        MANAGE: /управлять|координировать|планировать/i,
        AUTOMATE: /автоматизировать|настроить|деплой/i,
        LEARN: /изучить|обучение|понять принципы/i
    };
    
    // Подсчет совпадений и возврат доминирующего намерения
}
```

---

## 🎯 АЛГОРИТМ ПРИНЯТИЯ РЕШЕНИЙ

### **Правила классификации**

```yaml
# Высокий приоритет (score >= 80)
DEVELOPMENT:
  conditions:
    - keywords_score >= 7
    - has_code_files: true
    - mentions_implementation: true
  mcp_tools: ["Git Project", "Task Master"]

RESEARCH:
  conditions:
    - analysis_keywords >= 5
    - mentions_documentation: true
    - no_implementation_intent: true
  mcp_tools: ["Reasoner", "Sequential Thinking"]

PROJECT_MANAGEMENT:
  conditions:
    - planning_keywords >= 4
    - mentions_tasks: true
    - has_taskmaster_context: true
  mcp_tools: ["Task Master"]

# Средний приоритет (score 50-79)
AUTOMATION:
  conditions:
    - automation_keywords >= 3
    - has_scripts: true
    - mentions_workflow: true
  mcp_tools: ["Orchestrator"]

EDUCATION:
  conditions:
    - learning_keywords >= 3
    - mentions_principles: true
    - analysis_context: true
  mcp_tools: ["Sequential Thinking"]
```

### **Комбинированная классификация**

```javascript
// Алгоритм для задач с множественными типами
function getHybridClassification(scores) {
    const threshold = 60;
    const activeTypes = Object.entries(scores)
        .filter(([type, score]) => score >= threshold)
        .sort((a, b) => b[1] - a[1]);
    
    if (activeTypes.length > 1) {
        return {
            primary: activeTypes[0][0],
            secondary: activeTypes[1][0],
            hybrid: true,
            confidence: Math.min(...activeTypes.map(([,score]) => score))
        };
    }
    
    return {
        primary: activeTypes[0][0],
        hybrid: false,
        confidence: activeTypes[0][1]
    };
}
```

---

## 🔄 ИНТЕГРАЦИЯ С WORKFLOW

### **Автоматический вызов при новой задаче**

```markdown
1. **Task Master получает новую задачу**
2. **Классификатор анализирует описание задачи**
3. **Определяется тип и уровень уверенности**
4. **Селектор выбирает подходящие MCP инструменты**
5. **Workflow запускается с выбранными инструментами**
```

### **Точки интеграции**

```yaml
Trigger_Points:
  - task_creation: "Новая задача в Task Master"
  - chat_analysis: "Анализ сообщения в чате"
  - manual_request: "Ручной запрос классификации"
  
Output_Format:
  primary_type: "DEVELOPMENT"
  confidence: 0.85
  recommended_mcps: ["Git Project", "Task Master"]
  reasoning: "Обнаружены ключевые слова разработки..."
```

---

## 📋 ПРАКТИЧЕСКИЕ ПРИМЕРЫ

### **Пример 1: Задача разработки**
```
Вход: "Реализовать механизм подбора номенклатуры в модуле гкс_ВходнойКонтрольКачества"

Анализ:
- Ключевые слова: "реализовать" (+8), "механизм" (+6), "модуле" (+7)
- Контекст: упоминание .bsl модуля (+10)
- Намерение: CREATE (+8)

Результат:
- Тип: DEVELOPMENT
- Уверенность: 92%
- MCP: Git Project + Task Master
```

### **Пример 2: Исследовательская задача**
```
Вход: "Проанализировать архитектуру конфигурации и найти оптимальные паттерны"

Анализ:
- Ключевые слова: "проанализировать" (+9), "архитектуру" (+7), "паттерны" (+6)
- Контекст: архитектурный анализ (+8)
- Намерение: ANALYZE (+9)

Результат:
- Тип: RESEARCH
- Уверенность: 88%
- MCP: Reasoner + Sequential Thinking
```

### **Пример 3: Гибридная задача**
```
Вход: "Изучить и внедрить систему автоматического тестирования для 1С модулей"

Анализ:
- EDUCATION: "изучить" (+7)
- DEVELOPMENT: "внедрить" (+8), "систему" (+6)
- AUTOMATION: "автоматического" (+9), "тестирование" (+8)

Результат:
- Первичный тип: AUTOMATION
- Вторичный тип: DEVELOPMENT
- Уверенность: 78%
- MCP: Orchestrator + Git Project + Sequential Thinking
```

---

## 🛠️ НАСТРОЙКА И КОНФИГУРАЦИЯ

### **Файл конфигурации** (cursor-rules/mcp-classifier-config.json)

```json
{
  "classification_rules": {
    "keyword_weights": {
      "development": {
        "создать": 8, "реализовать": 9, "внедрить": 8,
        "код": 7, "функция": 6, "модуль": 7
      },
      "research": {
        "анализ": 9, "изучить": 7, "исследование": 8,
        "понять": 6, "сравнить": 5
      }
    },
    "context_weights": {
      "file_extensions": {
        ".bsl": 10, ".js": 8, ".py": 8,
        ".md": 6, ".txt": 4
      },
      "directories": {
        "src/": 9, "CommonModules/": 10,
        "docs/": 7, "scripts/": 8
      }
    },
    "confidence_thresholds": {
      "high": 85,
      "medium": 70,
      "low": 55
    }
  }
}
```

---

## ✅ ТЕСТИРОВАНИЕ КЛАССИФИКАТОРА

### **Тестовые сценарии**

```yaml
Test_Cases:
  development_clear:
    input: "Создать новую функцию экспорта данных в CommonModule"
    expected: {type: "DEVELOPMENT", confidence: ">90%"}
    
  research_clear:
    input: "Проанализировать документацию по регистрам сведений"
    expected: {type: "RESEARCH", confidence: ">85%"}
    
  hybrid_case:
    input: "Изучить и внедрить новый паттерн обработки ошибок"
    expected: {type: "DEVELOPMENT", secondary: "EDUCATION"}
    
  ambiguous_case:
    input: "Работа с номенклатурой"
    expected: {confidence: "<60%", requires_clarification: true}
```

---

**📅 Создано**: 2025-09-22  
**🎯 Статус**: Готов к интеграции  
**🔗 Связанные модули**: 18-mcp-selector.md, 19-mcp-selection-config.md