# {{OBJECT_NAME}} - Модуль объекта

**Дата создания**: {{TIMESTAMP}}
**Проект**: {{PROJECT_NAME}}
**Тип объекта**: {{OBJECT_TYPE}}
**Модуль**: {{MODULE_TYPE}}
**Расположение**: {{MODULE_PATH}}

## Описание объекта

{{OBJECT_DESCRIPTION}}

## Назначение модуля

Модуль {{MODULE_TYPE}} для {{OBJECT_TYPE}}.{{OBJECT_NAME}} обеспечивает {{MODULE_PURPOSE}}.

## Обработчики событий

### События объекта

{{#OBJECT_EVENTS}}
#### {{EVENT_NAME}}()

**Контекст выполнения**: {{EVENT_CONTEXT}}
**Назначение**: {{EVENT_DESCRIPTION}}

```bsl
{{EVENT_CODE_SAMPLE}}
```

**Особенности реализации**:
{{EVENT_IMPLEMENTATION_NOTES}}

{{/OBJECT_EVENTS}}

### События формы (для модулей форм)

{{#FORM_EVENTS}}
#### {{EVENT_NAME}}()

**Элемент**: {{FORM_ELEMENT}}
**Событие**: {{EVENT_TYPE}}
**Описание**: {{EVENT_DESCRIPTION}}

{{/FORM_EVENTS}}

## Процедуры и функции

### Экспортные

{{#EXPORT_PROCEDURES}}
#### {{PROCEDURE_NAME}}()

**Назначение**: {{PROCEDURE_DESCRIPTION}}
**Параметры**:
{{#PARAMETERS}}
- `{{PARAM_NAME}}` ({{PARAM_TYPE}}) - {{PARAM_DESCRIPTION}}
{{/PARAMETERS}}

**Алгоритм**:
{{ALGORITHM_DESCRIPTION}}

{{/EXPORT_PROCEDURES}}

### Внутренние

{{#INTERNAL_PROCEDURES}}
#### {{PROCEDURE_NAME}}()
{{PROCEDURE_DESCRIPTION}}
{{/INTERNAL_PROCEDURES}}

## Бизнес-логика

### Алгоритмы обработки

{{#BUSINESS_LOGIC}}
#### {{ALGORITHM_NAME}}

**Описание**: {{ALGORITHM_DESCRIPTION}}
**Входные данные**: {{INPUT_DATA}}
**Результат**: {{OUTPUT_DATA}}
**Особенности**: {{SPECIAL_NOTES}}

{{/BUSINESS_LOGIC}}

### Проведение документа (для документов)

{{#POSTING_ALGORITHM}}
**Алгоритм проведения**:
{{POSTING_DESCRIPTION}}

**Движения регистров**:
{{#REGISTER_RECORDS}}
- {{REGISTER_NAME}} - {{MOVEMENT_TYPE}} - {{MOVEMENT_DESCRIPTION}}
{{/REGISTER_RECORDS}}

**Контроль остатков**:
{{BALANCE_CONTROL}}

{{/POSTING_ALGORITHM}}

## Интеграции

### Подсистемы

{{#SUBSYSTEMS}}
- {{SUBSYSTEM_NAME}} - {{INTEGRATION_DESCRIPTION}}
{{/SUBSYSTEMS}}

### Внешние системы

{{#EXTERNAL_INTEGRATIONS}}
- {{SYSTEM_NAME}} - {{INTEGRATION_TYPE}} - {{INTEGRATION_DESCRIPTION}}
{{/EXTERNAL_INTEGRATIONS}}

### Веб-сервисы и HTTP-сервисы

{{#WEB_SERVICES}}
- {{SERVICE_NAME}} - {{SERVICE_DESCRIPTION}}
{{/WEB_SERVICES}}

## Производительность

### Анализ запросов

{{#QUERY_ANALYSIS}}
#### {{QUERY_NAME}}

**Назначение**: {{QUERY_PURPOSE}}
**Сложность**: {{QUERY_COMPLEXITY}}
**Рекомендации по оптимизации**: {{OPTIMIZATION_NOTES}}

```sql
{{QUERY_TEXT_SAMPLE}}
```

{{/QUERY_ANALYSIS}}

### Рекомендации по производительности

{{PERFORMANCE_RECOMMENDATIONS}}

## Безопасность

### Права доступа

{{#ACCESS_RIGHTS}}
- {{RIGHT_TYPE}} - {{RIGHT_DESCRIPTION}}
{{/ACCESS_RIGHTS}}

### Проверки безопасности

{{SECURITY_CHECKS}}

## Тестирование

### Сценарии тестирования

{{#TEST_SCENARIOS}}
#### {{SCENARIO_NAME}}

**Цель**: {{TEST_GOAL}}
**Шаги**:
{{#TEST_STEPS}}
1. {{STEP_DESCRIPTION}}
{{/TEST_STEPS}}

**Ожидаемый результат**: {{EXPECTED_RESULT}}

{{/TEST_SCENARIOS}}

## Соответствие стандартам

### BSL Language Server
{{BSL_COMPLIANCE_REPORT}}

### Стандарты разработки 1С
{{DEVELOPMENT_STANDARDS_COMPLIANCE}}

## Связанные объекты

### Зависимости

{{#DEPENDENCIES}}
- {{DEPENDENCY_TYPE}}.{{DEPENDENCY_NAME}} - {{DEPENDENCY_DESCRIPTION}}
{{/DEPENDENCIES}}

### Используется в

{{#USED_IN}}
- {{USAGE_LOCATION}} - {{USAGE_CONTEXT}}
{{/USED_IN}}

## История изменений

{{#CHANGE_HISTORY}}
- {{CHANGE_DATE}} - {{CHANGE_AUTHOR}} - {{CHANGE_DESCRIPTION}}
{{/CHANGE_HISTORY}}

---
*Документация сгенерирована автоматически Claude Code Auto-Documenter*
*Анализ модуля: {{ANALYSIS_TIMESTAMP}}*
*BSL проверка: {{BSL_CHECK_STATUS}}*