# Быстрые справочники Claude Code

## 🎯 Наиболее часто используемые команды

### Основные CLI команды
```bash
# Навигация и информация
claude --help              # Справка
claude --version           # Версия
claude --status            # Статус аккаунта
claude --config            # Настройки

# Управление навыками
claude                     # Запуск (навыки автоматически доступны)
/help                      # Справка по слэш-командам

# MCP управление
claude mcp add --transport http notion https://mcp.notion.com/mcp
claude mcp list            # Список MCP серверов
claude mcp remove <name>   # Удаление MCP сервера

# Отладка
claude --debug             # Режим отладки
```

### Слэш-команды (в интерфейсе Claude)
```
/agents       # Управление подагентами
/bug          # Сообщить об ошибке
/clear        # Очистить историю
/config       # Открыть настройки
/help         # Справка
/init         # Инициализация проекта
/mcp          # Управление MCP
/permissions  # Управление разрешениями
/review       # Запросить проверку кода
/status       # Показать статус
```

## 📁 Структуры файлов и конфигураций

### Навык (Skill) - минимальная структура
```
my-skill/
└── SKILL.md

# SKILL.md содержание:
---
name: my-skill-name
description: Краткое описание того, что делает навык и когда его использовать
---

# Название навыка

## Инструкции
Пошаговые инструкции для Claude
```

### Навык с дополнительными файлами
```
advanced-skill/
├── SKILL.md              # Основной файл навыка
├── reference.md          # Дополнительная документация
├── examples/
│   ├── example1.md
│   └── example2.md
└── scripts/
    ├── helper.py
    └── process.sh
```

### Проектная структура Claude Code
```
your-project/
├── .claude/
│   ├── skills/           # Проектные навыки
│   │   ├── skill1/
│   │   └── skill2/
│   ├── commands/         # Пользовательские команды
│   └── agents/           # Подагенты
├── CLAUDE.md            # Инструкции для проекта
└── src/                 # Исходный код проекта
```

## ⚙️ Популярные MCP серверы

### Инструменты разработки
```bash
# Sentry - мониторинг ошибок
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# GitHub
claude mcp add --transport stdio github --env GITHUB_TOKEN=$TOKEN -- npx -y @anthropic/github-mcp

# Socket - безопасность зависимостей
claude mcp add --transport http socket https://mcp.socket.dev/
```

### Управление проектами
```bash
# Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Linear
claude mcp add --transport http linear https://mcp.linear.app/mcp

# Asana
claude mcp add --transport sse asana https://mcp.asana.com/sse

# Atlassian (Jira/Confluence)
claude mcp add --transport sse atlassian https://mcp.atlassian.com/v1/sse
```

## 🔧 Конфигурационные файлы

### VS Code settings.json (пример)
```json
{
    "claude-code.enabled": true,
    "claude-code.model": "claude-3-5-sonnet-20241022",
    "claude-code.statusLine.enabled": true,
    "claude-code.memory.enabled": true
}
```

### GitHub Actions workflow (пример)
```yaml
name: Claude Code Quality Check
on: [push, pull_request]

jobs:
  claude-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Claude Code Review
        uses: anthropics/claude-code-action@v1
        with:
          api-key: ${{ secrets.CLAUDE_API_KEY }}
```

### Хук (Hook) - пример pre-commit
```bash
#!/bin/bash
# .git/hooks/pre-commit
claude --review --staged-only
if [ $? -ne 0 ]; then
    echo "Claude Code review failed. Fix issues before committing."
    exit 1
fi
```

## 🚨 Устранение неполадок - быстрые решения

### Навык не активируется
```bash
# 1. Проверить синтаксис YAML
head -n 10 .claude/skills/my-skill/SKILL.md

# 2. Проверить местоположение
ls .claude/skills/*/SKILL.md

# 3. Перезапустить Claude Code
claude --restart

# 4. Режим отладки
claude --debug
```

### MCP сервер не подключается
```bash
# Проверить список серверов
claude mcp list

# Проверить статус
claude mcp status <server-name>

# Переподключить
claude mcp remove <server-name>
claude mcp add --transport <transport> <server-name> <url>
```

### Проблемы с разрешениями
```bash
# Просмотр разрешений
/permissions

# Сброс разрешений
claude --reset-permissions

# Проверка конфигурации
/config
```

## 📋 Чек-лист создания навыка

### ✅ Обязательные элементы
- [ ] Папка навыка с понятным именем
- [ ] Файл `SKILL.md` в корне папки
- [ ] YAML заголовок с `name` и `description`
- [ ] Поле `name` - только строчные буквы, цифры, дефисы (макс. 64 символа)
- [ ] Поле `description` - включает ЧТО делает и КОГДА использовать (макс. 1024 символа)

### ✅ Хорошие практики
- [ ] Конкретные триггерные слова в описании
- [ ] Четкие пошаговые инструкции
- [ ] Примеры использования
- [ ] Ссылки на дополнительные файлы (если есть)
- [ ] Тестирование с реальными запросами

### ✅ Опциональные улучшения
- [ ] Поле `allowed-tools` для ограничения инструментов
- [ ] Дополнительные файлы документации
- [ ] Скрипты и утилиты
- [ ] Примеры в отдельных файлах
- [ ] Версионирование в содержимом

## 🔄 Workflow разработки с навыками

### 1. Создание навыка
```bash
mkdir -p .claude/skills/my-new-skill
cd .claude/skills/my-new-skill
```

### 2. Написание SKILL.md
```markdown
---
name: my-new-skill
description: Конкретное описание с триггерными словами
---

# Навык

## Инструкции
1. Шаг 1
2. Шаг 2
3. Шаг 3
```

### 3. Тестирование
```
Привет Claude! [Задать вопрос, соответствующий описанию навыка]
```

### 4. Итерация и улучшение
- Наблюдать поведение Claude
- Уточнять описание при необходимости
- Добавлять примеры и документацию
- Расширять функциональность

## 💡 Советы по эффективному использованию

### Для навыков
- Делайте описания конкретными с триггерными словами
- Один навык = одна основная возможность
- Используйте `allowed-tools` для безопасности
- Тестируйте с командой

### Для MCP
- Начинайте с популярных серверов
- Настраивайте окружение переменные
- Используйте для интеграции с внешними системами
- Мониторьте производительность

### Для плагинов
- Изучайте маркетплейс перед созданием
- Комбинируйте навыки + команды + агенты
- Документируйте для пользователей
- Следуйте руководящим принципам публикации