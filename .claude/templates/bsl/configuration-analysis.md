# {{CONFIG_NAME}} - Анализ конфигурации

**Дата анализа**: {{TIMESTAMP}}
**Проект**: {{PROJECT_NAME}}
**Версия конфигурации**: {{CONFIG_VERSION}}
**Платформа**: {{PLATFORM_VERSION}}
**Расположение**: {{CONFIG_PATH}}

## Обзор конфигурации

{{CONFIG_DESCRIPTION}}

## Архитектурный анализ

### Структура подсистем

{{#SUBSYSTEMS}}
#### {{SUBSYSTEM_NAME}}

**Назначение**: {{SUBSYSTEM_PURPOSE}}
**Состав объектов**: {{OBJECT_COUNT}} объектов
**Основные компоненты**:
{{#SUBSYSTEM_OBJECTS}}
- {{OBJECT_TYPE}}.{{OBJECT_NAME}} - {{OBJECT_DESCRIPTION}}
{{/SUBSYSTEM_OBJECTS}}

**Зависимости**:
{{#SUBSYSTEM_DEPENDENCIES}}
- {{DEPENDENCY_SUBSYSTEM}} - {{DEPENDENCY_TYPE}}
{{/SUBSYSTEM_DEPENDENCIES}}

{{/SUBSYSTEMS}}

### Граф зависимостей

```mermaid
graph TD
{{#DEPENDENCY_GRAPH}}
    {{FROM_SUBSYSTEM}} --> {{TO_SUBSYSTEM}}
{{/DEPENDENCY_GRAPH}}
```

## Метаданные

### Статистика объектов

| Тип объекта | Количество | Примечания |
|-------------|------------|------------|
{{#METADATA_STATS}}
| {{OBJECT_TYPE}} | {{COUNT}} | {{NOTES}} |
{{/METADATA_STATS}}

### Справочники

{{#CATALOGS}}
#### {{CATALOG_NAME}}

**Назначение**: {{CATALOG_PURPOSE}}
**Иерархия**: {{HIERARCHICAL}}
**Подчинение**: {{SUBORDINATE_TO}}
**Ключевые реквизиты**:
{{#CATALOG_ATTRIBUTES}}
- {{ATTRIBUTE_NAME}} ({{ATTRIBUTE_TYPE}}) - {{ATTRIBUTE_DESCRIPTION}}
{{/CATALOG_ATTRIBUTES}}

{{/CATALOGS}}

### Документы

{{#DOCUMENTS}}
#### {{DOCUMENT_NAME}}

**Назначение**: {{DOCUMENT_PURPOSE}}
**Движения регистров**:
{{#REGISTER_RECORDS}}
- {{REGISTER_NAME}} ({{REGISTER_TYPE}}) - {{MOVEMENT_DESCRIPTION}}
{{/REGISTER_RECORDS}}

**Последовательности**: {{SEQUENCES}}
**Нумерация**: {{NUMBERING_SETTINGS}}

{{/DOCUMENTS}}

### Регистры

{{#REGISTERS}}
#### {{REGISTER_NAME}} ({{REGISTER_TYPE}})

**Назначение**: {{REGISTER_PURPOSE}}
**Измерения**:
{{#DIMENSIONS}}
- {{DIMENSION_NAME}} ({{DIMENSION_TYPE}}) - {{DIMENSION_DESCRIPTION}}
{{/DIMENSIONS}}

**Ресурсы**:
{{#RESOURCES}}
- {{RESOURCE_NAME}} ({{RESOURCE_TYPE}}) - {{RESOURCE_DESCRIPTION}}
{{/RESOURCES}}

{{/REGISTERS}}

## Качество кода

### BSL Language Server анализ

**Общая статистика**:
- Всего файлов: {{TOTAL_FILES}}
- Проанализировано: {{ANALYZED_FILES}}
- Обнаружено замечаний: {{TOTAL_ISSUES}}

**Распределение по критичности**:
- 🔴 BLOCKER: {{BLOCKER_COUNT}}
- 🟠 CRITICAL: {{CRITICAL_COUNT}}
- 🟡 MAJOR: {{MAJOR_COUNT}}
- 🔵 MINOR: {{MINOR_COUNT}}
- ℹ️ INFO: {{INFO_COUNT}}

### Топ проблем

{{#TOP_ISSUES}}
#### {{ISSUE_RULE}} ({{SEVERITY}})

**Описание**: {{ISSUE_DESCRIPTION}}
**Файлов затронуто**: {{AFFECTED_FILES}}
**Рекомендации**: {{RECOMMENDATIONS}}

{{/TOP_ISSUES}}

### Модули с наибольшим количеством замечаний

{{#TOP_PROBLEMATIC_MODULES}}
1. {{MODULE_PATH}} - {{ISSUE_COUNT}} замечаний
{{/TOP_PROBLEMATIC_MODULES}}

## Производительность

### Анализ запросов

**Потенциально медленные запросы**:
{{#SLOW_QUERIES}}
- {{MODULE_NAME}}.{{PROCEDURE_NAME}} - {{QUERY_COMPLEXITY}}
{{/SLOW_QUERIES}}

### Рекомендации по оптимизации

{{#PERFORMANCE_RECOMMENDATIONS}}
#### {{RECOMMENDATION_CATEGORY}}

{{RECOMMENDATION_TEXT}}

**Приоритет**: {{PRIORITY}}
**Ожидаемый эффект**: {{EXPECTED_IMPACT}}

{{/PERFORMANCE_RECOMMENDATIONS}}

## Безопасность

### Анализ ролей и прав

{{#ROLES_ANALYSIS}}
#### {{ROLE_NAME}}

**Назначение**: {{ROLE_PURPOSE}}
**Права доступа**: {{ACCESS_RIGHTS_COUNT}}
**Критические права**: {{CRITICAL_RIGHTS}}

{{/ROLES_ANALYSIS}}

### Потенциальные уязвимости

{{#SECURITY_ISSUES}}
- {{VULNERABILITY_TYPE}} - {{VULNERABILITY_DESCRIPTION}} - {{RISK_LEVEL}}
{{/SECURITY_ISSUES}}

## Интеграции

### Внешние соединения

{{#EXTERNAL_CONNECTIONS}}
#### {{CONNECTION_NAME}}

**Тип**: {{CONNECTION_TYPE}}
**Назначение**: {{CONNECTION_PURPOSE}}
**Настройки**: {{CONNECTION_SETTINGS}}

{{/EXTERNAL_CONNECTIONS}}

### Веб-сервисы

{{#WEB_SERVICES}}
#### {{SERVICE_NAME}}

**Тип**: {{SERVICE_TYPE}}
**Операции**: {{OPERATIONS_COUNT}}
**Безопасность**: {{SECURITY_SETTINGS}}

{{/WEB_SERVICES}}

## Техническая задолженность

### Устаревший код

{{#TECHNICAL_DEBT}}
#### {{DEBT_CATEGORY}}

**Описание**: {{DEBT_DESCRIPTION}}
**Местоположение**: {{DEBT_LOCATION}}
**Влияние**: {{DEBT_IMPACT}}
**Рекомендации**: {{DEBT_RECOMMENDATIONS}}

{{/TECHNICAL_DEBT}}

### План рефакторинга

{{#REFACTORING_PLAN}}
1. {{REFACTORING_ITEM}} - {{PRIORITY}} - {{ESTIMATED_EFFORT}}
{{/REFACTORING_PLAN}}

## Соответствие стандартам

### Стандарты 1С
{{STANDARDS_COMPLIANCE_REPORT}}

### Лучшие практики
{{BEST_PRACTICES_ANALYSIS}}

## Рекомендации по развитию

### Краткосрочные (1-3 месяца)
{{#SHORT_TERM_RECOMMENDATIONS}}
- {{RECOMMENDATION}}
{{/SHORT_TERM_RECOMMENDATIONS}}

### Долгосрочные (6-12 месяцев)
{{#LONG_TERM_RECOMMENDATIONS}}
- {{RECOMMENDATION}}
{{/LONG_TERM_RECOMMENDATIONS}}

## Метрики качества

### Показатели сложности
- Цикломатическая сложность: {{CYCLOMATIC_COMPLEXITY}}
- Глубина вложенности: {{NESTING_DEPTH}}
- Размер модулей: {{MODULE_SIZE_METRICS}}

### Покрытие тестами
{{TEST_COVERAGE_REPORT}}

## Приложения

### Детальные отчеты
- [BSL анализ]({{BSL_REPORT_PATH}})
- [Граф зависимостей]({{DEPENDENCY_GRAPH_PATH}})
- [Метрики производительности]({{PERFORMANCE_METRICS_PATH}})

---
*Анализ выполнен автоматически Claude Code Auto-Documenter*
*Framework Version: {{FRAMEWORK_VERSION}}*
*Дата генерации: {{GENERATION_TIMESTAMP}}*