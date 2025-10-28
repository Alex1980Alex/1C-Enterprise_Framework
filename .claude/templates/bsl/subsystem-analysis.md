# {{SUBSYSTEM_NAME}} - Анализ подсистемы

**Дата анализа**: {{TIMESTAMP}}
**Проект**: {{PROJECT_NAME}}
**Подсистема**: {{SUBSYSTEM_FULL_NAME}}
**Уровень**: {{SUBSYSTEM_LEVEL}}
**Расположение**: {{SUBSYSTEM_PATH}}

## Описание подсистемы

{{SUBSYSTEM_DESCRIPTION}}

## Назначение

{{SUBSYSTEM_PURPOSE}}

## Архитектура

### Состав объектов

| Тип объекта | Количество | Список объектов |
|-------------|------------|-----------------|
{{#OBJECT_TYPES}}
| {{OBJECT_TYPE}} | {{COUNT}} | {{OBJECT_LIST}} |
{{/OBJECT_TYPES}}

### Ключевые компоненты

{{#KEY_COMPONENTS}}
#### {{COMPONENT_TYPE}}.{{COMPONENT_NAME}}

**Роль в подсистеме**: {{COMPONENT_ROLE}}
**Взаимодействие**: {{COMPONENT_INTERACTIONS}}
**Критичность**: {{COMPONENT_CRITICALITY}}

{{/KEY_COMPONENTS}}

## Бизнес-процессы

### Основные сценарии

{{#BUSINESS_SCENARIOS}}
#### {{SCENARIO_NAME}}

**Описание**: {{SCENARIO_DESCRIPTION}}
**Участники**: {{SCENARIO_PARTICIPANTS}}
**Шаги процесса**:
{{#SCENARIO_STEPS}}
1. {{STEP_DESCRIPTION}} ({{RESPONSIBLE_OBJECT}})
{{/SCENARIO_STEPS}}

**Результат**: {{SCENARIO_RESULT}}

{{/BUSINESS_SCENARIOS}}

### Потоки данных

```mermaid
graph LR
{{#DATA_FLOWS}}
    {{SOURCE_OBJECT}} -->|{{DATA_TYPE}}| {{TARGET_OBJECT}}
{{/DATA_FLOWS}}
```

## Зависимости

### Входящие зависимости

**От других подсистем**:
{{#INCOMING_DEPENDENCIES}}
- {{SOURCE_SUBSYSTEM}} → {{DEPENDENCY_TYPE}} → {{TARGET_OBJECT}}
{{/INCOMING_DEPENDENCIES}}

### Исходящие зависимости

**К другим подсистемам**:
{{#OUTGOING_DEPENDENCIES}}
- {{SOURCE_OBJECT}} → {{DEPENDENCY_TYPE}} → {{TARGET_SUBSYSTEM}}
{{/OUTGOING_DEPENDENCIES}}

### Общие модули

{{#SHARED_MODULES}}
#### {{MODULE_NAME}}

**Использование**: {{MODULE_USAGE}}
**Ключевые функции**: {{KEY_FUNCTIONS}}
**Зависимые объекты**: {{DEPENDENT_OBJECTS}}

{{/SHARED_MODULES}}

## Анализ качества

### BSL Language Server

**Статистика по подсистеме**:
- Проанализировано модулей: {{ANALYZED_MODULES}}
- Всего замечаний: {{TOTAL_ISSUES}}
- Плотность дефектов: {{DEFECT_DENSITY}} замечаний/KLOC

**Распределение по типам модулей**:
{{#MODULE_QUALITY}}
| Тип модуля | Файлов | Замечаний | Средняя плотность |
|------------|--------|-----------|-------------------|
| {{MODULE_TYPE}} | {{FILE_COUNT}} | {{ISSUE_COUNT}} | {{DENSITY}} |
{{/MODULE_QUALITY}}

### Критические проблемы

{{#CRITICAL_ISSUES}}
#### {{ISSUE_TYPE}} - {{SEVERITY}}

**Описание**: {{ISSUE_DESCRIPTION}}
**Модуль**: {{AFFECTED_MODULE}}
**Строка**: {{LINE_NUMBER}}
**Рекомендации**: {{FIX_RECOMMENDATIONS}}

{{/CRITICAL_ISSUES}}

## Производительность

### Анализ запросов

{{#QUERY_PERFORMANCE}}
#### {{QUERY_LOCATION}}

**Запрос**: {{QUERY_DESCRIPTION}}
**Сложность**: {{QUERY_COMPLEXITY}}
**Потенциальные проблемы**: {{PERFORMANCE_ISSUES}}

```sql
{{QUERY_TEXT_SAMPLE}}
```

**Рекомендации по оптимизации**:
{{OPTIMIZATION_RECOMMENDATIONS}}

{{/QUERY_PERFORMANCE}}

### Узкие места

{{#BOTTLENECKS}}
- {{BOTTLENECK_LOCATION}} - {{BOTTLENECK_DESCRIPTION}} - {{IMPACT_ASSESSMENT}}
{{/BOTTLENECKS}}

## Интеграции

### Внешние системы

{{#EXTERNAL_INTEGRATIONS}}
#### {{EXTERNAL_SYSTEM}}

**Тип интеграции**: {{INTEGRATION_TYPE}}
**Объекты взаимодействия**: {{INTEGRATION_OBJECTS}}
**Частота обмена**: {{EXCHANGE_FREQUENCY}}
**Критичность**: {{INTEGRATION_CRITICALITY}}

{{/EXTERNAL_INTEGRATIONS}}

### Веб-сервисы

{{#WEB_SERVICES}}
#### {{SERVICE_NAME}}

**Назначение**: {{SERVICE_PURPOSE}}
**Операции**: {{SERVICE_OPERATIONS}}
**Безопасность**: {{SECURITY_LEVEL}}

{{/WEB_SERVICES}}

## Безопасность

### Права доступа

{{#ACCESS_RIGHTS}}
#### {{RIGHT_CATEGORY}}

**Объекты**: {{PROTECTED_OBJECTS}}
**Роли**: {{AUTHORIZED_ROLES}}
**Ограничения**: {{ACCESS_RESTRICTIONS}}

{{/ACCESS_RIGHTS}}

### Аудит безопасности

{{#SECURITY_AUDIT}}
- {{SECURITY_ISSUE}} - {{RISK_LEVEL}} - {{MITIGATION_STRATEGY}}
{{/SECURITY_AUDIT}}

## Тестирование

### Покрытие тестами

**Статус тестирования**: {{TEST_COVERAGE_STATUS}}
- Модулей с тестами: {{TESTED_MODULES}}/{{TOTAL_MODULES}}
- Покрытие функций: {{FUNCTION_COVERAGE}}%

### Тестовые сценарии

{{#TEST_SCENARIOS}}
#### {{TEST_NAME}}

**Цель**: {{TEST_GOAL}}
**Тип**: {{TEST_TYPE}}
**Статус**: {{TEST_STATUS}}
**Автоматизация**: {{AUTOMATION_STATUS}}

{{/TEST_SCENARIOS}}

## Метрики сложности

### Цикломатическая сложность

{{#COMPLEXITY_METRICS}}
| Модуль | Функций | Средняя сложность | Максимальная |
|--------|---------|-------------------|---------------|
| {{MODULE_NAME}} | {{FUNCTION_COUNT}} | {{AVG_COMPLEXITY}} | {{MAX_COMPLEXITY}} |
{{/COMPLEXITY_METRICS}}

### Размер модулей

{{#MODULE_SIZE}}
- {{MODULE_NAME}}: {{LINE_COUNT}} строк, {{FUNCTION_COUNT}} функций
{{/MODULE_SIZE}}

## Рекомендации по улучшению

### Высокий приоритет

{{#HIGH_PRIORITY_RECOMMENDATIONS}}
#### {{RECOMMENDATION_TITLE}}

**Описание**: {{RECOMMENDATION_DESCRIPTION}}
**Ожидаемый эффект**: {{EXPECTED_BENEFIT}}
**Трудозатраты**: {{ESTIMATED_EFFORT}}
**Риски**: {{ASSOCIATED_RISKS}}

{{/HIGH_PRIORITY_RECOMMENDATIONS}}

### Средний приоритет

{{#MEDIUM_PRIORITY_RECOMMENDATIONS}}
- {{RECOMMENDATION_TEXT}}
{{/MEDIUM_PRIORITY_RECOMMENDATIONS}}

### Низкий приоритет

{{#LOW_PRIORITY_RECOMMENDATIONS}}
- {{RECOMMENDATION_TEXT}}
{{/LOW_PRIORITY_RECOMMENDATIONS}}

## План развития

### Ближайшие изменения (1-3 месяца)

{{#SHORT_TERM_PLANS}}
- {{PLAN_ITEM}} - {{RESPONSIBLE}} - {{DEADLINE}}
{{/SHORT_TERM_PLANS}}

### Долгосрочные планы (6-12 месяцев)

{{#LONG_TERM_PLANS}}
- {{PLAN_ITEM}} - {{STRATEGIC_GOAL}}
{{/LONG_TERM_PLANS}}

## Связанная документация

### Техническая документация
{{#TECHNICAL_DOCS}}
- [{{DOC_TITLE}}]({{DOC_LINK}}) - {{DOC_DESCRIPTION}}
{{/TECHNICAL_DOCS}}

### Пользовательская документация
{{#USER_DOCS}}
- [{{DOC_TITLE}}]({{DOC_LINK}}) - {{DOC_DESCRIPTION}}
{{/USER_DOCS}}

## Контакты

### Ответственные лица
{{#RESPONSIBLE_PERSONS}}
- **{{ROLE}}**: {{PERSON_NAME}} ({{CONTACT_INFO}})
{{/RESPONSIBLE_PERSONS}}

---
*Анализ подсистемы выполнен автоматически Claude Code Auto-Documenter*
*BSL Framework Version: {{FRAMEWORK_VERSION}}*
*Дата генерации: {{GENERATION_TIMESTAMP}}*
*Следующий анализ: {{NEXT_ANALYSIS_DATE}}*