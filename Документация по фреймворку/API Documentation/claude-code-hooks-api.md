# 🎣 Claude Code Hooks API Reference

## 📖 Обзор системы hooks

Claude Code Hooks обеспечивают автоматическое соблюдение правил 1C-Enterprise Cursor Framework через интеграцию с жизненным циклом Claude Code.

## ⚠️ РЕАЛЬНЫЕ ВОЗМОЖНОСТИ vs ИДЕАЛЬНАЯ ДОКУМЕНТАЦИЯ

**🚨 ВАЖНОЕ УТОЧНЕНИЕ:**
Данная документация описывает **идеальную систему hooks**, но в реальности Claude Code работает **упрощенно**:

### ✅ **Что работает в Claude Code:**
- **Системные напоминания** (`<system-reminder>`) - автоматически внедряются
- **Чтение CLAUDE.md** - автоматически при старте проекта
- **Правила фреймворка** - загружаются через файловую систему
- **Контекстные подсказки** - через встроенные механизмы Claude

### ❌ **Что НЕ работает как описано:**
- **Внешние bash-скрипты** - не выполняются автоматически
- **user-prompt-submit hooks как скрипты** - не поддерживаются
- **Автоматическая валидация через внешние команды** - недоступна
- **MCP команды в hooks** - не работают в среде Claude Code

### 🔄 **Реальный механизм работы:**
```
Пользователь → Claude Code читает CLAUDE.md → Загружает .claude-unified-rules.md → Применяет правила через внутренние механизмы
```

## 🏗️ Архитектура интеграции

### 🔄 Жизненный цикл hooks

```
User Question → user-prompt-submit hook → Context Loading → AI Processing → pre-response hook → Response Validation → User Response
```

### 📁 Структура файлов

```
~/.config/claude-code/
├── settings.json           # Основная конфигурация hooks
├── hooks.json             # Детальная конфигурация с таймаутами
└── config.json            # Локальные настройки проекта

/project/scripts/
├── load-framework-rules.sh # Скрипт автоматической загрузки правил
└── check-compliance.sh     # Скрипт проверки соответствия

/project/
├── activate-hooks.sh       # Скрипт полной активации системы
├── config.json            # Конфигурация проекта
└── .claude-code/
    └── settings.json      # Локальная конфигурация hooks
```

## 🎯 Конфигурация hooks

### settings.json (основная конфигурация)

```json
{
  "hooks": {
    "user-prompt-submit": {
      "name": "Load Framework Rules",
      "description": "Автоматически загружает правила 1C-Enterprise Cursor Framework",
      "command": "/path/to/scripts/load-framework-rules.sh",
      "args": ["{{prompt}}"],
      "timeout": 8000,
      "enabled": true,
      "output_mode": "context_injection",
      "working_directory": "/path/to/framework"
    },
    "pre-response": {
      "name": "Framework Compliance Check",
      "description": "Проверяет соблюдение правил фреймворка",
      "command": "/path/to/scripts/check-compliance.sh",
      "args": ["{{response_draft}}"],
      "timeout": 3000,
      "enabled": true,
      "output_mode": "validation",
      "working_directory": "/path/to/framework"
    }
  },
  "project_context": {
    "framework_name": "1C-Enterprise Cursor Framework",
    "auto_context_loading": true,
    "compliance_validation": true,
    "journal_logging": true,
    "git_automation": true
  }
}
```

### hooks.json (детальная конфигурация)

```json
{
  "version": "1.0",
  "context_analysis": {
    "keywords": {
      "architect": ["архитектура", "система", "дизайн", "структура"],
      "analyst": ["анализ", "требования", "процесс", "планирование"],
      "consultant": ["1С", "BSP", "конфигурация", "модуль"],
      "programmer": ["код", "программирование", "реализация", "отладка"],
      "git": ["git", "коммит", "версия", "файл"]
    },
    "priority_loading": [
      "CLAUDE.md",
      "00-role-selector.md", 
      "02-answer-structure.md",
      "03-quality-control.md",
      "04-file-management.md",
      "05-git-workflow.md"
    ]
  },
  "env": {
    "CLAUDE_CODE_PROJECT": "/path/to/framework",
    "CLAUDE_CODE_HOOKS_ENABLED": "true",
    "FRAMEWORK_RULES_PATH": "/path/to/cursor-rules",
    "FRAMEWORK_DOCS_PATH": "/path/to/docs"
  }
}
```

## 🔧 API скриптов hooks

### load-framework-rules.sh

**Назначение**: Автоматическая загрузка релевантных правил фреймворка на основе анализа user-prompt

**Входные параметры**:
- `$1` - текст вопроса пользователя

**Алгоритм работы**:
1. **Анализ контекста** - определение ключевых слов в промпте
2. **Загрузка обязательных правил** - CLAUDE.md, role-selector, answer-structure
3. **Контекстная загрузка** - релевантные роли + skills + процессы  
4. **Инжектирование документации** - 1С документация при упоминании BSP/конфигурация
5. **Генерация system-reminder** - создание контекстного файла для Claude Code

**Возвращает**: Путь к созданному файлу контекста

**Пример использования**:
```bash
./load-framework-rules.sh "Как создать новый общий модуль в конфигурации 1С?"

# Вывод:
# /tmp/claude-code-context-1756855745.md
# [02:29:05] 🔍 Обнаружены ключи контекста: consultant
# [02:29:05] ✅ Правила фреймворка загружены и готовы для Claude Code
```

### check-compliance.sh

**Назначение**: Проверка соответствия ответа правилам фреймворка перед отправкой пользователю

**Входные параметры**:
- `$1` - черновик ответа для проверки

**Алгоритм проверки**:
1. **Проверка структуры** - наличие цитат, пояснений, чек-листа, обязательных действий
2. **Валидация терминологии** - использование оригинальной терминологии 1С:Предприятие
3. **Контроль источников** - проверка упоминания документации при технических ответах
4. **Генерация отчета** - детальный отчет о соответствии с рекомендациями
5. **Подготовка записи** - заготовка для записи в журнал

**Возвращает**: 
- Код 0 - соответствие правилам
- Код 1 - критические нарушения обнаружены
- Отчет о соответствии в stdout

**Пример использования**:
```bash
./check-compliance.sh "📖 ЦИТАТЫ: тест 🔧 ПОЯСНЕНИЕ: тест 📋 ЧЕК-ЛИСТ: тест 🔔 ДЕЙСТВИЯ: тест"

# Вывод:
# ## 📊 ОТЧЕТ О СООТВЕТСТВИИ ПРАВИЛАМ ФРЕЙМВОРКА
# **Время проверки:** 2025-09-02 04:25:30
# ✅ **Структура ответа:** Соответствует требованиям
# ✅ **Терминология 1С:** Проверена
# 🎯 **ОБЩИЙ СТАТУС:** СООТВЕТСТВУЕТ ПРАВИЛАМ
```

## 🌍 Переменные окружения

### Основные переменные

- `CLAUDE_CODE_HOOKS_ENABLED=true` - активация системы hooks
- `CLAUDE_CODE_PROJECT="/path/to/framework"` - путь к проекту фреймворка
- `FRAMEWORK_RULES_PATH="/path/to/cursor-rules"` - путь к правилам
- `FRAMEWORK_DOCS_PATH="/path/to/docs"` - путь к документации

### Алиасы командной строки

```bash
# Управление hooks
claude-hooks-enable     # Включить hooks
claude-hooks-disable    # Отключить hooks
claude-hooks-status     # Проверить статус
claude-hooks-test       # Протестировать работу
```

## 🚀 Активация и настройка

### Автоматическая активация

```bash
# Полная активация системы hooks
./activate-hooks.sh

# Результат:
# 🎉 CLAUDE CODE HOOKS АКТИВИРОВАНЫ!
# ✅ user-prompt-submit hook работает  
# ✅ pre-response hook работает
# ✅ Claude Code процесс обнаружен
```

### Ручная настройка

```bash
# 1. Создание конфигурации
mkdir -p ~/.config/claude-code
cp .claude-code/settings.json ~/.config/claude-code/

# 2. Установка переменных окружения
export CLAUDE_CODE_HOOKS_ENABLED=true
export CLAUDE_CODE_PROJECT="/path/to/framework"

# 3. Настройка исполняемости скриптов
chmod +x scripts/*.sh
```

## 📊 Мониторинг и отладка

### Проверка статуса hooks

```bash
# Статус переменных окружения
echo "Hooks enabled: $CLAUDE_CODE_HOOKS_ENABLED"
echo "Project: $CLAUDE_CODE_PROJECT"

# Тестирование загрузки правил  
./scripts/load-framework-rules.sh "тестовый вопрос"

# Тестирование проверки соответствия
./scripts/check-compliance.sh "тестовый ответ"
```

### Файлы логов и отладки

- `/tmp/claude-code-context-*.md` - созданные файлы контекста
- `/tmp/journal-entry-*.md` - заготовки записей для журнала
- `~/.config/claude-code/.hooks-activated` - маркер активации hooks
- Stderr output скриптов с timestamp'ами

### Типичные проблемы и решения

1. **Скрипты не выполняются**
   ```bash
   chmod +x scripts/*.sh
   ```

2. **Не находится CLAUDE.md**
   ```bash
   export CLAUDE_CODE_PROJECT="/correct/path/to/framework"
   ```

3. **Timeout hooks**
   ```json
   {
     "timeout": 15000  // увеличить в settings.json
   }
   ```

4. **Символы возврата каретки**
   ```bash
   sed -i 's/\r$//' scripts/*.sh
   ```

## 🔄 Интеграция с workflow

### Полный цикл автоматизации

1. **При запуске Claude Code** - загружаются настройки hooks
2. **При user-prompt** - автоматически вызывается `load-framework-rules.sh`
3. **Анализ контекста** - определяются релевантные правила фреймворка
4. **Инжектирование контекста** - Claude получает актуальные правила
5. **Обработка запроса** - Claude формирует ответ с учетом правил
6. **Pre-response валидация** - вызывается `check-compliance.sh`
7. **Проверка соответствия** - анализируется структура и содержание
8. **Отправка ответа** - пользователь получает валидированный ответ

### Преимущества автоматизации

- ✅ **100% покрытие** - каждый ответ проходит проверку правил
- ✅ **Контекстная загрузка** - релевантные правила для каждого типа задач
- ✅ **Автоматическое журналирование** - подготовка записей без участия пользователя
- ✅ **Предупреждение нарушений** - проактивное выявление несоответствий
- ✅ **Консистентность качества** - единообразное соблюдение стандартов

## 🔗 Интеграция с другими компонентами

### Связь с MCP Commands

Claude Code Hooks дополняют MCP команды:
- Hooks обеспечивают **автоматическое** соблюдение правил
- MCP команды предоставляют **программный** доступ к функциональности
- Совместное использование дает максимальную автоматизацию

### Связь с Git Automation  

Hooks интегрированы с Git workflow:
- Автоматическая подготовка commit сообщений через `serena__auto_git_commit_with_template`
- Проверка качества перед коммитом
- Стандартизированные шаблоны коммитов с атрибуцией Claude Code

### Связь с BSL Language Server

Hooks используют BSL для валидации:
- 793 правила BSL Language Server для проверки качества
- Автоматическое форматирование и линтинг кода
- Интеграция с `serena__validate_standards` и `serena__get_diagnostics`

---

**📅 Дата обновления:** 02.09.2025  
**🔄 Версия API:** 1.0  
**🔧 Совместимость:** Claude Code 1.0+, 1C:Enterprise 8.3.26, BSP 3.1.11+