# SonarQube Integration для 1С:Предприятие

Модуль интеграции SonarQube для автоматизации анализа кода в проектах 1С:Предприятие.

## Возможности

- 🔧 **Автоматическое создание конфигураций** SonarQube и BSL Language Server
- 📊 **Управление правилами анализа** с поддержкой 793 правил SonarQube
- 📈 **Генерация отчетов** в форматах Excel, CSV, HTML
- 🚀 **Интеграция с CI/CD** (GitHub Actions, GitLab CI, Jenkins, Azure DevOps)
- 📋 **Профили правил** для различных команд и проектов
- 🎯 **Локальный анализ** кода с детальными отчетами

## Установка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Установка BSL Language Server (требуется Node.js)
npm install -g @1c-syntax/bsl-language-server
```

## Быстрый старт

### 1. Инициализация проекта

```bash
python -m sonar_integration init "my-1c-project" "Мой проект 1С" \
    --max-complexity 20 \
    --max-line-length 120 \
    --max-method-size 50
```

Создаст файлы:
- `sonar-project.properties` - конфигурация SonarQube
- `.bsl-language-server.json` - конфигурация BSL Language Server

### 2. Анализ кода

```bash
# Локальный анализ
python -m sonar_integration analyze --src-dir src/ --output-dir reports/

# С пользовательскими настройками
python -m sonar_integration analyze \
    --src-dir "src/Configuration/" \
    --output-dir "analysis-results/"
```

### 3. Генерация отчетов

```bash
# Из результатов BSL Language Server
python -m sonar_integration report reports/bsl-analysis.json \
    --format bsl \
    --excel --csv --html

# Из результатов SonarQube
python -m sonar_integration report sonar-report.json \
    --format sonar \
    --excel
```

## Использование в коде

### ConfigManager - Управление конфигурациями

```python
from sonar_integration import ConfigManager

config_manager = ConfigManager()

# Синхронизация конфигураций
success = config_manager.sync_configs(
    project_key="my-project",
    project_name="Мой проект",
    custom_rules={
        "CyclomaticComplexity.maxComplexity": 15,
        "LineLength.maxLineLength": 100
    }
)
```

### RulesManager - Управление правилами

```python
from sonar_integration import RulesManager

rules_manager = RulesManager()

# Получение правил по критичности
critical_rules = rules_manager.get_rules_by_severity("CRITICAL")

# Создание профиля правил
profile = rules_manager.create_rules_profile(
    "Строгий профиль",
    severity_levels=["BLOCKER", "CRITICAL", "MAJOR"],
    categories=["security", "reliability"]
)

# Экспорт в SonarQube формат
sonar_config = rules_manager.export_sonar_rules(profile)
```

### ReportGenerator - Генерация отчетов

```python
from sonar_integration import ReportGenerator

report_gen = ReportGenerator(output_dir="reports")

# Парсинг результатов анализа
results = report_gen.parse_bsl_json_report("bsl-analysis.json")

# Генерация отчетов
excel_file = report_gen.export_to_excel(results)
html_file = report_gen.export_to_html(results)

# Сводный отчет
summary = report_gen.generate_summary_report(results)
print(f"Найдено проблем: {summary['total_issues']}")
```

### CIIntegration - Интеграция с CI/CD

```python
from sonar_integration import CIIntegration

ci = CIIntegration()

# Создание GitHub Actions workflow
ci.create_ci_config_files("github", "my-project-key")

# Настройка pre-commit хука
ci.setup_pre_commit_hook()

# Локальный анализ
result = ci.run_local_analysis(src_dir="src", output_dir="reports")
if result["success"]:
    print(f"Найдено проблем: {result['total_issues']}")
```

## Команды CLI

### Управление правилами

```bash
# Список всех правил
python -m sonar_integration rules

# Правила по критичности
python -m sonar_integration rules --severity CRITICAL

# Правила по категории
python -m sonar_integration rules --category security --verbose

# Создание профиля правил
python -m sonar_integration profile "Мой профиль" \
    --severity "BLOCKER,CRITICAL" \
    --category "security,reliability" \
    --output my_profile.json
```

### Настройка CI/CD

```bash
# GitHub Actions
python -m sonar_integration ci github "my-project-key" --pre-commit

# GitLab CI
python -m sonar_integration ci gitlab "my-project-key"

# Jenkins Pipeline
python -m sonar_integration ci jenkins "my-project-key"

# Azure DevOps
python -m sonar_integration ci azure "my-project-key"
```

## Интеграция с существующими проектами

### 1. Перенос существующих конфигураций

Если у вас уже есть конфигурации SonarQube или BSL LS:

```python
from sonar_integration import ConfigManager
import json

# Загрузка существующей конфигурации BSL LS
with open('.bsl-language-server.json', 'r') as f:
    existing_config = json.load(f)

config_manager = ConfigManager()

# Объединение с новыми настройками
custom_params = {
    "parameters": existing_config.get("diagnostics", {}).get("parameters", {}),
    "subsystemsFilter": existing_config.get("diagnostics", {}).get("subsystemsFilter", {})
}

# Генерация обновленной конфигурации
new_config = config_manager.generate_bsl_config(custom_params)
config_manager.save_bsl_config(new_config)
```

### 2. Миграция правил SonarQube

```python
from sonar_integration import RulesManager

rules_manager = RulesManager()

# Создание профиля на основе существующих правил SonarQube
existing_rules = {
    "CyclomaticComplexity": {"maxComplexity": 25},
    "LineLength": {"maxLineLength": 140},
    # ... другие правила
}

profile = rules_manager.create_rules_profile(
    "Миграционный профиль",
    custom_rules=existing_rules
)

# Экспорт в BSL конфигурацию
bsl_config = rules_manager.export_bsl_config(profile)
```

## Структура каталога правил

Правила организованы по уровням критичности:

- **BLOCKER** (9 правил): Критические ошибки, блокирующие релиз
- **CRITICAL** (47 правил): Важные проблемы качества кода
- **MAJOR** (235 правил): Значительные нарушения стандартов
- **MINOR** (167 правил): Незначительные улучшения
- **INFO** (42 правила): Информационные сообщения

### Категории правил

- **reliability**: Надежность (221 правило)
- **maintainability**: Сопровождаемость (260 правил)
- **security**: Безопасность (19 правил)
- **performance**: Производительность
- **style**: Стиль кода

## Примеры конфигураций

### Минимальная конфигурация для нового проекта

```json
{
  "language": "ru",
  "diagnostics": {
    "parameters": {
      "LineLength": {"maxLineLength": 120},
      "MethodSize": {"maxMethodSize": 50},
      "CyclomaticComplexity": {"maxComplexity": 15}
    }
  }
}
```

### Строгая конфигурация для критического проекта

```json
{
  "language": "ru",
  "diagnostics": {
    "parameters": {
      "LineLength": {"maxLineLength": 100},
      "MethodSize": {"maxMethodSize": 30},
      "CyclomaticComplexity": {"maxComplexity": 10},
      "ExcessiveReturns": {"maxEnableReturns": 2},
      "OneSymbolVariable": true,
      "CommentedCode": true,
      "TodoComment": true
    },
    "subsystemsFilter": {
      "exclude": ["ТестовыеДанные", "Отладка"]
    }
  }
}
```

## Интеграция с SonarQube Server

### Настройка подключения

```properties
# sonar-project.properties
sonar.host.url=http://your-sonarqube-server:9000
sonar.login=your-token

# Настройки проекта
sonar.projectKey=1c-enterprise-project
sonar.projectName=Проект 1С:Предприятие
sonar.sources=src/Configuration/
```

### Запуск анализа

```bash
# С помощью SonarScanner
sonar-scanner

# Или с помощью нашего модуля
python -m sonar_integration analyze && sonar-scanner
```

## Troubleshooting

### Проблема: BSL Language Server не найден

```bash
# Установите Node.js и BSL LS
npm install -g @1c-syntax/bsl-language-server

# Проверьте установку
bsl-language-server --version
```

### Проблема: Ошибки парсинга JSON отчетов

Убедитесь, что:
1. Файл отчета создан корректно
2. Используется правильный формат (BSL или SonarQube)
3. Файл не поврежден

### Проблема: Много ложных срабатываний

Настройте фильтры по подсистемам:

```json
{
  "diagnostics": {
    "subsystemsFilter": {
      "exclude": ["ТестовыеДанные", "Устаревшие", "Временные"]
    }
  }
}
```

## Лицензия

MIT License. См. файл LICENSE для деталей.