# BSL Language Server Configuration Guide

## Обзор

Serena теперь поддерживает расширенную конфигурацию BSL Language Server через несколько источников конфигурации с автоматическим слиянием настроек.

## Источники конфигурации (по приоритету)

1. **`.bsl-language-server.json`** - Нативная конфигурация BSL LS
2. **`.serena/bsl-config.json`** - Специфичная для Serena конфигурация
3. **`sonar-project.properties`** - Настройки SonarQube проекта

## Поддерживаемые конфигурации

### Базовые настройки

```json
{
  "language": "ru",              // Язык диагностики (ru/en)
  "diagnosticLanguage": "ru",    // Язык сообщений
  "traceLevel": "off"            // Уровень трассировки (off/messages/verbose)
}
```

### Диагностические правила

```json
{
  "diagnostics": {
    "computeTrigger": "onType",  // Когда запускать анализ (onType/onSave)
    "parameters": {
      "ExcessiveReturns": {
        "maxEnableReturns": 3    // Максимум возвратов в функции
      },
      "LineLength": {
        "maxLineLength": 120     // Максимальная длина строки
      },
      "MethodSize": {
        "maxMethodSize": 50      // Максимальный размер метода
      },
      "CyclomaticComplexity": {
        "maxComplexity": 20      // Максимальная цикломатическая сложность
      },
      "HardcodedPasswordInMethod": {
        "passwordFieldNames": "Пароль|Password|IMAP|SMTP"
      },
      "OneSymbolVariable": false, // Отключить правило односимвольных переменных
      "BooleanLiteral": false     // Отключить проверку булевых литералов
    },
    "subsystemsFilter": {
      "include": [               // Анализировать только эти подсистемы
        "Основная",
        "БизнесПроцессы"
      ],
      "exclude": [               // Исключить из анализа
        "Отчеты",
        "Обработки"
      ]
    }
  }
}
```

## Интеграция с SonarQube

### Автоматическая настройка через sonar_integration

Используйте модуль `sonar_integration` для автоматической настройки:

```bash
# Инициализация проекта
python -m sonar_integration init "my-1c-project" "Мой проект 1С" \
    --max-complexity 20 \
    --max-line-length 120 \
    --max-method-size 50

# Настройка CI/CD
python -m sonar_integration ci github "my-1c-project"

# Локальный анализ
python -m sonar_integration analyze --src-dir src/
```

### Ручная настройка sonar-project.properties

```properties
# Основные настройки проекта
sonar.projectKey=my-1c-project
sonar.projectName=Мой проект 1С
sonar.language=ru

# BSL специфичные настройки
sonar.bsl.ExcessiveReturns.maxEnableReturns=5
sonar.bsl.LineLength.maxLineLength=140
sonar.bsl.MethodSize.maxMethodSize=60
```

Эти настройки автоматически преобразуются в формат BSL Language Server.

## Примеры конфигураций

### Минимальная конфигурация

```json
{
  "language": "ru",
  "diagnostics": {
    "parameters": {
      "LineLength": {"maxLineLength": 120}
    }
  }
}
```

### Расширенная конфигурация

```json
{
  "$schema": "https://1c-syntax.github.io/bsl-language-server/configuration/schema.json",
  "language": "ru",
  "diagnosticLanguage": "ru",
  "traceLevel": "off",
  "diagnostics": {
    "computeTrigger": "onType",
    "parameters": {
      "ExcessiveReturns": {"maxEnableReturns": 3},
      "QuantityOptionalArguments": {"maxOptionalArgumentsCount": 3},
      "LineLength": {"maxLineLength": 120},
      "MethodSize": {"maxMethodSize": 50},
      "CyclomaticComplexity": {"maxComplexity": 20},
      "HardcodedPasswordInMethod": {
        "passwordFieldNames": "Пароль|Password|Пароль1|Пароль2"
      },
      "OneSymbolVariable": false,
      "BooleanLiteral": false
    },
    "subsystemsFilter": {
      "include": ["Основная", "БизнесПроцессы"],
      "exclude": ["Отчеты", "ТестовыеДанные"]
    }
  },
  "codeActions": {
    "quickFix": true
  }
}
```

## Использование

1. **Создайте конфигурационный файл** в корне проекта:
   - `.bsl-language-server.json` для стандартной конфигурации
   - `.serena/bsl-config.json` для Serena-специфичной настройки

2. **Перезапустите Serena** или переключитесь на проект для применения настроек

3. **Проверьте логи** Serena для подтверждения загрузки конфигурации:
   ```
   LOG: Loaded BSL config from: /path/to/.bsl-language-server.json
   LOG: BSL Language Server initialization with config: {...}
   ```

## Валидация и обработка ошибок

Serena автоматически:
- ✅ Валидирует значения параметров
- ✅ Устанавливает значения по умолчанию для некорректных настроек
- ✅ Логирует предупреждения о проблемах в конфигурации
- ✅ Объединяет настройки из разных источников

## Совместимость с SonarQube Rules

Поддерживаются все 793 правила из коллекции SonarQube для 1С, включая:

### По критичности
- **BLOCKER**: 9 правил
- **CRITICAL**: 47 правил
- **MAJOR**: 235 правил
- **MINOR**: 167 правил
- **INFO**: 42 правила

### По типу
- **BUG**: 221 правило
- **CODE_SMELL**: 260 правил
- **SECURITY_HOTSPOT**: 8 правил
- **VULNERABILITY**: 11 правил

## Поддержка

При возникновении проблем:

### Использование sonar_integration
```bash
# Проверка доступных правил
python -m sonar_integration rules --verbose

# Тестирование конфигурации
python -m sonar_integration analyze --src-dir src/ --output-dir test-reports/

# Генерация отчетов
python -m sonar_integration report test-reports/bsl-analysis.json --html --excel
```

### Общие проблемы
1. Проверьте синтаксис JSON в конфигурационных файлах
2. Просмотрите логи Serena для сообщений об ошибках
3. Убедитесь, что все пути к файлам указаны корректно
4. Используйте валидатор JSON Schema для проверки конфигурации
5. Обратитесь к документации в `Документация по фреймворку/SONAR_INTEGRATION.md`