# КОНФИГУРАЦИЯ СИСТЕМЫ ВЫБОРА MCP: Настройки и правила

## 🎯 НАЗНАЧЕНИЕ

Централизованная система конфигурации для управления правилами выбора MCP инструментов, настройками классификации и пользовательскими предпочтениями.

---

## 📁 СТРУКТУРА КОНФИГУРАЦИИ

### **Файловая организация**

```
.mcp-selection/
├── config/
│   ├── main.json              # Основная конфигурация
│   ├── classification.json    # Правила классификации
│   ├── selection.json         # Правила выбора MCP
│   └── overrides.json         # Переопределения проекта
├── profiles/
│   ├── 1c-enterprise.json     # Профиль для 1С разработки
│   ├── research.json          # Профиль для исследований
│   └── automation.json        # Профиль для автоматизации
└── schemas/
    ├── config.schema.json     # JSON схема конфигурации
    └── validation.js          # Скрипты валидации
```

---

## ⚙️ ОСНОВНАЯ КОНФИГУРАЦИЯ

### **main.json - Главные настройки**

```json
{
  "version": "1.0.0",
  "system": {
    "name": "MCP Selection System",
    "description": "Автоматический выбор MCP инструментов для задач",
    "default_mode": "semi_automatic",
    "fallback_mode": "interactive",
    "max_concurrent_mcps": 4,
    "response_timeout": 30
  },
  
  "confidence_thresholds": {
    "automatic": {
      "min": 0.85,
      "description": "Автоматический выбор без подтверждения"
    },
    "semi_automatic": {
      "min": 0.65,
      "max": 0.84,
      "description": "Предложение с запросом подтверждения"
    },
    "interactive": {
      "min": 0.45,
      "max": 0.64,
      "description": "Интерактивный выбор с пользователем"
    },
    "manual": {
      "max": 0.44,
      "description": "Ручной выбор пользователем"
    }
  },
  
  "available_mcps": {
    "task-master": {
      "enabled": true,
      "priority": 1,
      "description": "Управление задачами и планирование",
      "requirements": ["node", "npm"]
    },
    "sequential-thinking": {
      "enabled": true,
      "priority": 1,
      "description": "Глубокий анализ и последовательное мышление",
      "requirements": ["mcp-client"]
    },
    "serena": {
      "enabled": true,
      "priority": 2,
      "description": "Управление памятью и контекстом",
      "requirements": ["mcp-client"]
    },
    "git-project": {
      "enabled": false,
      "priority": 3,
      "description": "Управление Git репозиториями",
      "requirements": ["git", "mcp-client"]
    },
    "orchestrator": {
      "enabled": false,
      "priority": 3,
      "description": "Автоматизация и оркестрация процессов",
      "requirements": ["docker", "mcp-client"]
    },
    "reasoner": {
      "enabled": false,
      "priority": 4,
      "description": "Логическое рассуждение и анализ",
      "requirements": ["mcp-client", "knowledge-base"]
    }
  },
  
  "logging": {
    "enabled": true,
    "level": "info",
    "file": ".mcp-selection/logs/selection.log",
    "rotation": "daily"
  }
}
```

---

## 🔍 КОНФИГУРАЦИЯ КЛАССИФИКАЦИИ

### **classification.json - Правила классификации**

```json
{
  "classification_rules": {
    "language_support": ["ru", "en"],
    "default_language": "ru",
    
    "keyword_weights": {
      "development": {
        "ru": {
          "создать": 9, "реализовать": 9, "внедрить": 8, "разработать": 8,
          "код": 7, "функция": 7, "модуль": 8, "процедура": 7,
          "API": 6, "интерфейс": 6, "алгоритм": 7, "структура": 6,
          "база данных": 8, "запрос": 6, "регистр": 8, "справочник": 8
        },
        "en": {
          "create": 9, "implement": 9, "develop": 8, "build": 7,
          "code": 7, "function": 7, "module": 8, "procedure": 7,
          "API": 6, "interface": 6, "algorithm": 7, "structure": 6
        }
      },
      
      "research": {
        "ru": {
          "анализ": 9, "исследование": 9, "изучить": 8, "понять": 7,
          "сравнить": 7, "оценить": 7, "рассмотреть": 6, "проанализировать": 9,
          "документация": 6, "архитектура": 8, "паттерн": 7, "подход": 6
        },
        "en": {
          "analyze": 9, "research": 9, "study": 8, "understand": 7,
          "compare": 7, "evaluate": 7, "review": 6, "investigate": 8,
          "documentation": 6, "architecture": 8, "pattern": 7, "approach": 6
        }
      },
      
      "project_management": {
        "ru": {
          "план": 8, "планирование": 9, "управление": 9, "координация": 8,
          "задача": 7, "проект": 8, "статус": 6, "milestone": 7,
          "deadline": 7, "roadmap": 8, "sprint": 7, "backlog": 7
        },
        "en": {
          "plan": 8, "planning": 9, "management": 9, "coordination": 8,
          "task": 7, "project": 8, "status": 6, "milestone": 7,
          "deadline": 7, "roadmap": 8, "sprint": 7, "backlog": 7
        }
      },
      
      "automation": {
        "ru": {
          "автоматизация": 9, "автоматизировать": 9, "скрипт": 8, "workflow": 8,
          "деплой": 7, "развертывание": 7, "CI/CD": 8, "тестирование": 6,
          "интеграция": 6, "оркестрация": 8, "мониторинг": 6
        },
        "en": {
          "automation": 9, "automate": 9, "script": 8, "workflow": 8,
          "deploy": 7, "deployment": 7, "CI/CD": 8, "testing": 6,
          "integration": 6, "orchestration": 8, "monitoring": 6
        }
      },
      
      "education": {
        "ru": {
          "обучение": 9, "изучение": 8, "tutorial": 8, "руководство": 7,
          "принципы": 7, "основы": 7, "курс": 8, "документация": 6,
          "объяснение": 7, "понимание": 7, "освоение": 8
        },
        "en": {
          "learning": 9, "education": 8, "tutorial": 8, "guide": 7,
          "principles": 7, "basics": 7, "course": 8, "documentation": 6,
          "explanation": 7, "understanding": 7, "mastering": 8
        }
      }
    },
    
    "context_weights": {
      "file_extensions": {
        ".bsl": 10, ".os": 9, ".xml": 8,
        ".js": 8, ".ts": 8, ".py": 7,
        ".md": 6, ".txt": 4, ".docx": 5,
        ".json": 5, ".yaml": 6, ".yml": 6,
        ".sh": 8, ".bat": 8, ".ps1": 7
      },
      
      "directories": {
        "CommonModules/": 10, "DataProcessors/": 9, "Reports/": 8,
        "Documents/": 8, "Catalogs/": 8, "InformationRegisters/": 9,
        "src/": 9, "scripts/": 8, "docs/": 7,
        ".taskmaster/": 8, ".github/": 7, "automation/": 8
      },
      
      "frameworks": {
        "1C:Enterprise": 10, "1С:Предприятие": 10,
        "React": 7, "Vue": 7, "Angular": 7,
        "Node.js": 8, "Python": 7, "Docker": 6
      }
    },
    
    "negative_indicators": {
      "development": ["только анализ", "без изменений", "теоретически"],
      "research": ["внедрить немедленно", "срочная разработка"],
      "automation": ["ручной процесс", "одноразовая задача"]
    },
    
    "boost_conditions": {
      "1c_context": {
        "condition": "mentions 1C OR BSL OR конфигурация",
        "boost_factor": 1.2,
        "applicable_types": ["development", "research"]
      },
      "urgent_task": {
        "condition": "mentions срочно OR urgent OR ASAP",
        "boost_factor": 1.1,
        "applicable_types": ["development", "automation"]
      },
      "complex_task": {
        "condition": "word_count > 50 OR mentions архитектура",
        "boost_factor": 1.15,
        "applicable_types": ["research", "development"]
      }
    }
  },
  
  "confidence_calculation": {
    "keyword_weight": 0.4,
    "context_weight": 0.35,
    "semantic_weight": 0.25,
    
    "penalties": {
      "ambiguous_keywords": -0.1,
      "conflicting_indicators": -0.15,
      "insufficient_context": -0.2
    },
    
    "bonuses": {
      "clear_intent": 0.1,
      "rich_context": 0.15,
      "domain_expertise": 0.05
    }
  }
}
```

---

## 🎯 КОНФИГУРАЦИЯ ВЫБОРА MCP

### **selection.json - Правила выбора инструментов**

```json
{
  "selection_rules": {
    "base_mappings": {
      "DEVELOPMENT": {
        "primary": ["task-master"],
        "secondary": ["serena", "git-project"],
        "optional": ["sequential-thinking"],
        "score_multiplier": 1.0
      },
      
      "RESEARCH": {
        "primary": ["sequential-thinking"],
        "secondary": ["serena", "reasoner"],
        "optional": ["memory", "web-search"],
        "score_multiplier": 1.0
      },
      
      "PROJECT_MANAGEMENT": {
        "primary": ["task-master"],
        "secondary": ["sequential-thinking"],
        "optional": ["serena"],
        "score_multiplier": 1.1
      },
      
      "AUTOMATION": {
        "primary": ["orchestrator"],
        "secondary": ["task-master", "git-project"],
        "optional": ["sequential-thinking"],
        "score_multiplier": 0.9
      },
      
      "EDUCATION": {
        "primary": ["sequential-thinking"],
        "secondary": ["memory", "serena"],
        "optional": ["web-search", "reasoner"],
        "score_multiplier": 0.8
      }
    },
    
    "hybrid_combinations": {
      "DEVELOPMENT_RESEARCH": {
        "strategy": "merge_weighted",
        "primary_weight": 0.7,
        "secondary_weight": 0.3,
        "max_tools": 4
      },
      
      "RESEARCH_EDUCATION": {
        "strategy": "sequential_priority",
        "phase_1": ["sequential-thinking", "reasoner"],
        "phase_2": ["memory", "serena"]
      },
      
      "PROJECT_DEVELOPMENT": {
        "strategy": "parallel_execution",
        "management_tools": ["task-master"],
        "development_tools": ["git-project", "serena"]
      }
    },
    
    "context_modifiers": {
      "1c_enterprise": {
        "boost_tools": ["serena", "task-master"],
        "boost_factor": 1.3,
        "reason": "1С разработка требует управления задачами и контекста"
      },
      
      "high_complexity": {
        "force_include": ["sequential-thinking"],
        "boost_tools": ["reasoner"],
        "boost_factor": 1.2
      },
      
      "time_critical": {
        "prioritize": ["task-master", "orchestrator"],
        "exclude": ["reasoner"],
        "reason": "Срочные задачи требуют быстрого выполнения"
      },
      
      "team_collaboration": {
        "force_include": ["git-project"],
        "boost_tools": ["task-master"],
        "boost_factor": 1.1
      }
    },
    
    "exclusion_rules": {
      "resource_constraints": {
        "condition": "available_memory < 4GB",
        "exclude": ["reasoner", "orchestrator"],
        "reason": "Недостаточно ресурсов для тяжелых MCP"
      },
      
      "security_requirements": {
        "condition": "security_level = high",
        "exclude": ["web-search"],
        "reason": "Безопасность не позволяет внешние запросы"
      },
      
      "offline_mode": {
        "condition": "network_access = false",
        "exclude": ["web-search", "reasoner"],
        "include_only": ["task-master", "serena", "sequential-thinking"]
      }
    }
  },
  
  "scoring_algorithm": {
    "base_scores": {
      "task-master": {
        "DEVELOPMENT": 90, "PROJECT_MANAGEMENT": 95,
        "AUTOMATION": 60, "RESEARCH": 40, "EDUCATION": 30
      },
      "sequential-thinking": {
        "RESEARCH": 95, "EDUCATION": 90, "DEVELOPMENT": 70,
        "PROJECT_MANAGEMENT": 50, "AUTOMATION": 40
      },
      "serena": {
        "DEVELOPMENT": 80, "RESEARCH": 75, "PROJECT_MANAGEMENT": 60,
        "AUTOMATION": 50, "EDUCATION": 70
      },
      "git-project": {
        "DEVELOPMENT": 85, "AUTOMATION": 70, "PROJECT_MANAGEMENT": 60,
        "RESEARCH": 30, "EDUCATION": 20
      },
      "orchestrator": {
        "AUTOMATION": 95, "DEVELOPMENT": 50, "PROJECT_MANAGEMENT": 40,
        "RESEARCH": 20, "EDUCATION": 15
      },
      "reasoner": {
        "RESEARCH": 90, "EDUCATION": 85, "DEVELOPMENT": 45,
        "PROJECT_MANAGEMENT": 30, "AUTOMATION": 25
      }
    },
    
    "context_bonuses": {
      "file_context": 10,
      "directory_context": 8,
      "framework_context": 12,
      "complexity_context": 6
    },
    
    "confidence_penalties": {
      "0.9-1.0": 0,
      "0.8-0.89": -5,
      "0.7-0.79": -10,
      "0.6-0.69": -15,
      "0.5-0.59": -25,
      "0.0-0.49": -40
    }
  }
}
```

---

## 👤 ПОЛЬЗОВАТЕЛЬСКИЕ ПРОФИЛИ

### **Профиль для 1С разработки** (profiles/1c-enterprise.json)

```json
{
  "profile_name": "1C Enterprise Development",
  "description": "Оптимизированный профиль для разработки на платформе 1С:Предприятие",
  "version": "1.0.0",
  
  "classification_overrides": {
    "keyword_weights": {
      "development": {
        "BSL": 10, "конфигурация": 9, "общий модуль": 9,
        "обработка данных": 8, "регистр сведений": 9,
        "справочник": 8, "документ": 8, "форма": 7,
        "запрос": 8, "процедура": 8, "функция": 8
      },
      "research": {
        "архитектура": 9, "производительность": 8,
        "оптимизация": 8, "анализ конфигурации": 9,
        "паттерны 1С": 9, "best practices": 8
      }
    },
    
    "context_boost": {
      "CommonModules/": 15,
      "DataProcessors/": 12,
      "InformationRegisters/": 12,
      "Catalogs/": 10,
      "Documents/": 10,
      ".bsl": 15,
      ".xml": 10
    }
  },
  
  "selection_overrides": {
    "force_include": {
      "condition": "ANY",
      "tools": ["serena"],
      "reason": "1С разработка всегда требует сохранения контекста"
    },
    
    "boost_scores": {
      "task-master": 1.4,
      "serena": 1.3,
      "sequential-thinking": 1.2
    },
    
    "specialized_combinations": {
      "bsl_development": {
        "trigger": "mentions .bsl OR BSL",
        "tools": ["task-master", "serena", "sequential-thinking"],
        "priority": "high"
      },
      
      "configuration_analysis": {
        "trigger": "mentions конфигурация OR архитектура",
        "tools": ["sequential-thinking", "serena"],
        "priority": "high"
      },
      
      "performance_optimization": {
        "trigger": "mentions производительность OR оптимизация",
        "tools": ["sequential-thinking", "serena", "reasoner"],
        "priority": "medium"
      }
    }
  },
  
  "user_preferences": {
    "default_mode": "semi_automatic",
    "max_concurrent_mcps": 3,
    "always_include_serena": true,
    "prefer_task_master": true,
    "enable_1c_specific_hints": true
  }
}
```

### **Профиль для исследований** (profiles/research.json)

```json
{
  "profile_name": "Research and Analysis",
  "description": "Профиль для исследовательских задач и глубокого анализа",
  "version": "1.0.0",
  
  "classification_overrides": {
    "boost_research_keywords": 1.3,
    "enable_semantic_analysis": true,
    "prefer_detailed_classification": true
  },
  
  "selection_overrides": {
    "primary_preference": ["sequential-thinking", "reasoner"],
    "always_include": ["memory", "serena"],
    "boost_scores": {
      "sequential-thinking": 1.5,
      "reasoner": 1.4,
      "memory": 1.3
    }
  },
  
  "workflow_settings": {
    "enable_multi_phase": true,
    "phase_1": "information_gathering",
    "phase_2": "analysis",
    "phase_3": "synthesis"
  }
}
```

---

## 🎛️ ПЕРЕОПРЕДЕЛЕНИЯ ПРОЕКТА

### **overrides.json - Настройки конкретного проекта**

```json
{
  "project_overrides": {
    "project_name": "1C-Enterprise_Framework",
    "project_type": "1c_enterprise",
    "active_profile": "1c-enterprise",
    
    "custom_rules": {
      "task_master_integration": {
        "enabled": true,
        "auto_create_tasks": true,
        "sync_with_workflow": true
      },
      
      "serena_memory": {
        "auto_save": true,
        "save_patterns": [
          "task_{id}_analysis",
          "task_{id}_context",
          "task_{id}_decisions"
        ]
      },
      
      "sequential_thinking": {
        "default_complexity": 5,
        "auto_trigger_threshold": 0.7,
        "save_reasoning": true
      }
    },
    
    "disabled_mcps": ["git-project", "orchestrator", "reasoner"],
    "required_mcps": ["task-master", "serena", "sequential-thinking"],
    
    "workflow_overrides": {
      "enable_workflow_integration": true,
      "workflow_steps": [
        "task_master_input",
        "mcp_selection",
        "sequential_thinking_analysis",
        "serena_save",
        "task_master_update"
      ]
    },
    
    "logging_overrides": {
      "log_all_selections": true,
      "log_user_choices": true,
      "performance_monitoring": true
    }
  }
}
```

---

## 📋 СХЕМЫ ВАЛИДАЦИИ

### **config.schema.json - JSON Schema для валидации**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MCP Selection Configuration",
  "type": "object",
  
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    
    "system": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "default_mode": {
          "type": "string",
          "enum": ["automatic", "semi_automatic", "interactive", "manual"]
        },
        "max_concurrent_mcps": {
          "type": "integer",
          "minimum": 1,
          "maximum": 10
        }
      },
      "required": ["name", "default_mode"]
    },
    
    "confidence_thresholds": {
      "type": "object",
      "properties": {
        "automatic": {"$ref": "#/definitions/threshold"},
        "semi_automatic": {"$ref": "#/definitions/threshold"},
        "interactive": {"$ref": "#/definitions/threshold"}
      }
    },
    
    "available_mcps": {
      "type": "object",
      "patternProperties": {
        "^[a-z-]+$": {"$ref": "#/definitions/mcp_definition"}
      }
    }
  },
  
  "definitions": {
    "threshold": {
      "type": "object",
      "properties": {
        "min": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "max": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "description": {"type": "string"}
      }
    },
    
    "mcp_definition": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean"},
        "priority": {
          "type": "integer",
          "minimum": 1,
          "maximum": 5
        },
        "description": {"type": "string"},
        "requirements": {
          "type": "array",
          "items": {"type": "string"}
        }
      },
      "required": ["enabled", "priority", "description"]
    }
  },
  
  "required": ["version", "system", "confidence_thresholds", "available_mcps"]
}
```

---

## 🔧 API КОНФИГУРАЦИИ

### **Программный интерфейс**

```javascript
// Класс управления конфигурацией
class MCPSelectionConfig {
    constructor(configPath = '.mcp-selection/config/') {
        this.configPath = configPath;
        this.config = null;
        this.profiles = new Map();
        this.overrides = null;
    }
    
    async load() {
        this.config = await this.loadMainConfig();
        await this.loadProfiles();
        this.overrides = await this.loadOverrides();
        await this.validate();
    }
    
    getClassificationRules() {
        return {
            ...this.config.classification,
            ...this.getActiveProfile()?.classification_overrides,
            ...this.overrides?.classification_overrides
        };
    }
    
    getSelectionRules() {
        return {
            ...this.config.selection,
            ...this.getActiveProfile()?.selection_overrides,
            ...this.overrides?.selection_overrides
        };
    }
    
    getAvailableMCPs() {
        const baseMCPs = this.config.available_mcps;
        const disabled = this.overrides?.disabled_mcps || [];
        
        return Object.entries(baseMCPs)
            .filter(([name, config]) => 
                config.enabled && !disabled.includes(name)
            )
            .reduce((acc, [name, config]) => {
                acc[name] = config;
                return acc;
            }, {});
    }
    
    async updateUserPreferences(preferences) {
        if (!this.overrides) {
            this.overrides = {};
        }
        this.overrides.user_preferences = {
            ...this.overrides.user_preferences,
            ...preferences
        };
        await this.saveOverrides();
    }
}

// Использование
const config = new MCPSelectionConfig();
await config.load();

const classificationRules = config.getClassificationRules();
const selectionRules = config.getSelectionRules();
const availableMCPs = config.getAvailableMCPs();
```

---

## 🧪 ТЕСТОВЫЕ КОНФИГУРАЦИИ

### **test-config.json - Конфигурация для тестирования**

```json
{
  "version": "1.0.0-test",
  "system": {
    "name": "MCP Selection Test",
    "default_mode": "interactive",
    "max_concurrent_mcps": 2,
    "response_timeout": 5
  },
  
  "confidence_thresholds": {
    "automatic": {"min": 0.95},
    "semi_automatic": {"min": 0.8, "max": 0.94},
    "interactive": {"min": 0.6, "max": 0.79}
  },
  
  "available_mcps": {
    "mock-task-master": {
      "enabled": true,
      "priority": 1,
      "description": "Mock Task Master for testing"
    },
    "mock-sequential-thinking": {
      "enabled": true,
      "priority": 1,
      "description": "Mock Sequential Thinking for testing"
    }
  },
  
  "test_scenarios": [
    {
      "name": "simple_development",
      "input": "Создать новую функцию",
      "expected_classification": "DEVELOPMENT",
      "expected_mcps": ["mock-task-master"]
    }
  ]
}
```

---

## 📊 МОНИТОРИНГ И АНАЛИТИКА

### **Конфигурация метрик**

```json
{
  "monitoring": {
    "enabled": true,
    "metrics": {
      "selection_accuracy": {
        "target": 0.85,
        "warning_threshold": 0.75,
        "critical_threshold": 0.65
      },
      
      "response_time": {
        "target_ms": 2000,
        "warning_threshold_ms": 3000,
        "critical_threshold_ms": 5000
      },
      
      "user_satisfaction": {
        "target": 0.8,
        "measurement": "feedback_score"
      }
    },
    
    "alerts": {
      "low_accuracy": {
        "condition": "selection_accuracy < 0.75",
        "action": "notify_admin",
        "frequency": "daily"
      },
      
      "slow_response": {
        "condition": "avg_response_time > 3000",
        "action": "performance_review",
        "frequency": "hourly"
      }
    },
    
    "reporting": {
      "daily_summary": true,
      "weekly_analytics": true,
      "export_format": ["json", "csv"]
    }
  }
}
```

---

**📅 Создано**: 2025-09-22  
**🎯 Статус**: Готов к использованию  
**🔗 Связанные модули**: 17-mcp-task-classifier.md, 18-mcp-selector.md  
**⚙️ Файлы**: .mcp-selection/config/, profiles/, schemas/