# {{MODULE_NAME}} - Общий модуль

**Дата создания**: {{TIMESTAMP}}
**Проект**: {{PROJECT_NAME}}
**Тип**: Общий модуль 1С
**Расположение**: {{MODULE_PATH}}

## Описание модуля

{{MODULE_DESCRIPTION}}

## Назначение

Общий модуль предназначен для {{MODULE_PURPOSE}}.

## Функциональность

### Экспортные процедуры и функции

{{#EXPORT_PROCEDURES}}
#### {{PROCEDURE_NAME}}()

**Назначение**: {{PROCEDURE_DESCRIPTION}}

**Параметры**:
{{#PARAMETERS}}
- `{{PARAM_NAME}}` ({{PARAM_TYPE}}) - {{PARAM_DESCRIPTION}}
{{/PARAMETERS}}

**Возвращаемое значение**: {{RETURN_VALUE}}

**Примеры использования**:
```bsl
{{USAGE_EXAMPLE}}
```

{{/EXPORT_PROCEDURES}}

### Внутренние процедуры и функции

{{#INTERNAL_PROCEDURES}}
#### {{PROCEDURE_NAME}}()
{{PROCEDURE_DESCRIPTION}}
{{/INTERNAL_PROCEDURES}}

## Зависимости

### Используемые общие модули
{{#DEPENDENCIES}}
- {{MODULE_NAME}} - {{USAGE_DESCRIPTION}}
{{/DEPENDENCIES}}

### Обращения к метаданным
{{#METADATA_REFS}}
- {{METADATA_TYPE}}.{{METADATA_NAME}} - {{USAGE_CONTEXT}}
{{/METADATA_REFS}}

## Контекст использования

### Где используется модуль
{{#USAGE_CONTEXT}}
- {{CONTEXT_LOCATION}} - {{CONTEXT_DESCRIPTION}}
{{/USAGE_CONTEXT}}

### Рекомендации по использованию

{{USAGE_RECOMMENDATIONS}}

## Соответствие стандартам

### BSL Language Server
- ✅ Проверено BSL Language Server
- {{BSL_COMPLIANCE_STATUS}}

### Стандарты 1С
- {{STANDARDS_COMPLIANCE}}

## История изменений

{{#CHANGE_HISTORY}}
- {{CHANGE_DATE}} - {{CHANGE_DESCRIPTION}}
{{/CHANGE_HISTORY}}

---
*Документация сгенерирована автоматически Claude Code Auto-Documenter*
*Последнее обновление: {{LAST_UPDATE}}*