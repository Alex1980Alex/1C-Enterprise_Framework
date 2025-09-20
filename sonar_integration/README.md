# SonarQube Integration для 1С:Предприятие

Модуль интеграции SonarQube для автоматизации анализа кода в проектах 1С:Предприятие.

## Документация

Полная документация доступна в файле:
`Документация по фреймворку/SONAR_INTEGRATION.md`

## Быстрый старт

```bash
# Инициализация проекта
python -m sonar_integration init "my-1c-project" "Мой проект 1С"

# Локальный анализ
python -m sonar_integration analyze --src-dir src/

# Генерация отчетов
python -m sonar_integration report reports/bsl-analysis.json --html --excel
```

## Структура модуля

- `config_manager.py` - Управление конфигурациями
- `rules_manager.py` - Управление правилами анализа  
- `report_generator.py` - Генерация отчетов
- `ci_integration.py` - Интеграция с CI/CD
- `cli.py` - Интерфейс командной строки
- `rules/` - Каталог правил BSL Language Server
- `templates/` - Шаблоны конфигураций