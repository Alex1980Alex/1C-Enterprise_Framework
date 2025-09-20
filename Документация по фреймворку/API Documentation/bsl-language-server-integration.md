# 🔍 BSL Language Server - API Documentation

## 📖 Обзор инструмента

BSL Language Server — это мощный инструмент статического анализа кода для платформы 1С:Предприятие 8. Интегрирован в 1C-Enterprise_Cursor_Framework через несколько механизмов взаимодействия.

## 🎯 Основные возможности

### **793 правила анализа кода:**
- **Синтаксические ошибки** - проверка корректности синтаксиса BSL
- **Стилистические замечания** - соответствие стандартам кодирования
- **Потенциальные ошибки** - выявление проблемных конструкций
- **Оптимизация производительности** - рекомендации по улучшению
- **Безопасность кода** - анализ уязвимостей

### **Уровни критичности:**
- 🔴 **BLOCKER** - блокирующие ошибки
- 🟠 **CRITICAL** - критические проблемы  
- 🟡 **MAJOR** - значительные замечания
- 🔵 **MINOR** - незначительные проблемы
- ⚪ **INFO** - информационные сообщения

---

## 🔗 Способы интеграции

### **1️⃣ Через MCP команды serena__***

#### `serena__get_diagnostics(file)`
**Назначение**: Получение диагностики для конкретного файла
```python
diagnostics = serena__get_diagnostics("CommonModules/Utils.bsl")
```
**Возвращает**: 
```json
{
  "file": "CommonModules/Utils.bsl",
  "issues": [
    {
      "rule": "LineLength",
      "severity": "MINOR", 
      "message": "Длина строки превышает 120 символов",
      "line": 45,
      "column": 125
    }
  ]
}
```

#### `serena__get_code_metrics(path)`
**Назначение**: Получение метрик качества кода
```python
metrics = serena__get_code_metrics("src/CommonModules/")
```
**Возвращает**:
```json
{
  "cyclomatic_complexity": 12,
  "lines_of_code": 1520,
  "issues_count": {
    "BLOCKER": 0,
    "CRITICAL": 2,
    "MAJOR": 15,
    "MINOR": 28,
    "INFO": 5
  }
}
```

#### `serena__validate_standards(file)`
**Назначение**: Проверка соответствия стандартам кодирования
```python
violations = serena__validate_standards("ObjectModules/Document.bsl")
```

### **2️⃣ Через BSL Quality Check Tool**

#### Интеграция в Serena Framework
```yaml
# serena_config.yml
included_optional_tools: 
  - bsl_quality_check
```

#### Использование в Claude Desktop
```
Проверь качество 1С кода в проекте с помощью BSL Language Server
```

#### Параметры инструмента
- `source_path` - путь к анализируемой директории
- `reporter` - формат отчета (json, console, sarif, junit)
- `config_path` - путь к конфигурации BSL
- `severity_filter` - минимальный уровень серьезности

---

## ⚙️ Конфигурация

### **Файл .bsl-language-server.json**
```json
{
  "diagnostics": {
    "parameters": {
      "LineLength": {
        "maxLineLength": 120
      },
      "CyclomaticComplexity": {
        "complexityThreshold": 15
      }
    },
    "exclude": [
      "**/*Test*.bsl"
    ]
  },
  "formatting": {
    "indentSize": 4,
    "insertFinalNewline": true
  }
}
```

### **Настройки в cursor-rules**
Интеграция с правилами качества в `cursor-rules/03-quality-control.md`:
- Автоматический запуск BSL анализа
- Фильтрация по критичности
- Интеграция с Git hooks

---

## 📊 Форматы отчетов

### **JSON Report**
```json
{
  "files": [
    {
      "path": "CommonModules/Utils.bsl",
      "issues": [
        {
          "ruleKey": "LineLength",
          "severity": "MINOR",
          "message": "Длина строки превышает лимит",
          "range": {
            "start": {"line": 45, "character": 0},
            "end": {"line": 45, "character": 125}
          }
        }
      ]
    }
  ],
  "summary": {
    "total_issues": 50,
    "by_severity": {
      "BLOCKER": 0,
      "CRITICAL": 2,
      "MAJOR": 15,
      "MINOR": 28,
      "INFO": 5
    }
  }
}
```

### **SARIF Report**
Совместимость с системами безопасности и CI/CD:
```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [{
    "tool": {
      "driver": {
        "name": "BSL Language Server"
      }
    }
  }]
}
```

---

## 🔄 Рабочие процессы

### **1. Анализ перед коммитом**
```bash
# Через Git hook
bsl-language-server --analyze src/ --reporter json --config .bsl-language-server.json
```

### **2. Интеграция с Claude Code**
```python
# Автоматический анализ при работе с проектом
serena__activate_project("/path/to/1c-project")
diagnostics = serena__get_diagnostics("target_file.bsl")
```

### **3. Continuous Integration**
```yaml
# CI/CD pipeline
- name: BSL Quality Check
  run: |
    serena bsl_quality_check --reporter junit --output quality-report.xml
```

---

## 📋 Категории правил BSL

### **🔧 Основные категории:**

#### **Code Smell (Запахи кода)**
- LineLength - длина строк
- CyclomaticComplexity - цикломатическая сложность
- MethodSize - размер методов
- TooManyParams - количество параметров

#### **Bug (Потенциальные ошибки)**
- UnreachableCode - недостижимый код
- DuplicateCondition - дублирование условий
- AssignAnotherValueToParameter - переназначение параметров
- UsingHardcodePaths - использование жестко заданных путей

#### **Vulnerability (Уязвимости)**
- UsingObjectNotAvailableUnixOS - объекты недоступные в Unix
- QueryToMissingTable - запросы к несуществующим таблицам
- SQLInjection - SQL инъекции

#### **Security Hotspot (Точки безопасности)**
- UsingFindElementByString - поиск элементов по строке
- UsingExternalCodeTools - использование внешних инструментов

---

## 🚀 Интеграция с фреймворком

### **Автоматические проверки**
- Запуск при каждом сохранении через Cursor IDE
- Интеграция с Git workflow
- Автоматическое создание отчетов

### **Система уведомлений**
- Критические ошибки блокируют коммит
- Уведомления в Claude Code интерфейсе
- Интеграция с системой логирования

### **Метрики качества**
- Отслеживание динамики качества кода
- Интеграция с системой мониторинга фреймворка
- Автоматические рекомендации по улучшению

---

## 🔍 Примеры использования

### **Базовый анализ файла:**
```python
# Через MCP команды
diagnostics = serena__get_diagnostics("CommonModules/MyModule.bsl")
print(f"Найдено проблем: {len(diagnostics['issues'])}")
```

### **Анализ всего проекта:**
```python
# Анализ качества всех модулей
metrics = serena__get_code_metrics("src/")
if metrics['issues_count']['BLOCKER'] > 0:
    print("ВНИМАНИЕ: Найдены блокирующие ошибки!")
```

### **Фильтрация по критичности:**
```bash
# Через BSL Quality Check Tool
serena bsl_quality_check --severity-filter MAJOR --reporter console
```

---

## ⚠️ Ограничения и рекомендации

### **Производительность:**
- Анализ больших проектов может занимать время
- Рекомендуется использовать инкрементальный анализ
- Кэширование результатов через систему памяти

### **Конфигурация:**
- Настройка правил под специфику проекта
- Исключение тестовых и сгенерированных файлов
- Адаптация порогов под команду

### **Интеграция:**
- Обязательное использование в Git workflow
- Интеграция с системой review кода
- Автоматизация через CI/CD процессы

---

**📅 Версия документа:** 1.0  
**🗓️ Последнее обновление:** 03.09.2025  
**👤 Ответственный:** Команда 1C-Enterprise Cursor Framework  
**🔗 Связанные документы:** `ultimate-hooks-system.md`, `mcp-commands-reference.md`

*Полный список правил и их описания доступны в официальной документации BSL Language Server*