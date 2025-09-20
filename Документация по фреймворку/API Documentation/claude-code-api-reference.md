# 🤖 Claude Code API Reference - Команды и возможности

## 📖 Обзор Claude Code

Claude Code — это агентный инструмент программирования от Anthropic, который работает непосредственно в терминале и интегрируется с экосистемой разработки через различные API и команды.

**Официальная документация:** https://docs.anthropic.com/en/docs/claude-code/

---

## 🚀 Установка и запуск

### **Установка:**
```bash
npm install -g @anthropic-ai/claude-code
cd your-awesome-project
claude
```

**Требования:**
- Node.js 18+
- Учетная запись Claude.ai или Anthropic Console

### **Основные режимы запуска:**
```bash
# Интерактивный режим REPL
claude

# Запуск с начальным запросом
claude "Проанализируй этот проект 1С"

# Одноразовый запрос через SDK
claude -p "Создай функцию валидации ИНН"

# Продолжение последней беседы
claude -c
```

---

## 🔧 CLI команды и флаги

### **Основные CLI флаги:**
```bash
--print, -p          # Вывод ответа без интерактивного режима
--model              # Выбор модели для текущей сессии
--verbose            # Подробное логирование
--output-format      # Формат вывода (text, json, stream-json)
--max-turns          # Ограничение количества агентных итераций
--continue, -c       # Продолжение последней беседы
```

### **Примеры использования:**
```bash
# JSON вывод для скриптов и автоматизации
claude -p "Анализ проекта" --output-format json

# Подробное логирование для отладки
claude --verbose

# Ограничение количества итераций
claude --max-turns 5 "Создай модуль обработки данных"
```

---

## ⌨️ Интерактивный режим

### **Горячие клавиши:**
| Команда | Действие |
|---------|----------|
| `Ctrl+C` | Отмена текущего ввода или генерации |
| `Ctrl+D` | Выход из сессии Claude Code |
| `Ctrl+L` | Очистка экрана терминала |
| `↑/↓` | Навигация по истории команд |

### **Многострочный ввод:**
```bash
# Универсальный escape во всех терминалах
\<Enter>

# По умолчанию на macOS  
Option+Enter

# После /terminal-setup
Shift+Enter
```

### **Быстрые команды:**
```bash
# Добавление в память (выбор файла)
#<текст>

# Вызов slash команды
/<команда>

# Режим Bash
!<команда>
```

---

## 🔀 Slash команды (21 команда)

### **🏗️ Управление проектом:**
```bash
/add-dir        # Добавить дополнительные рабочие директории
/init           # Инициализация проекта с CLAUDE.md
/memory         # Редактирование файлов памяти CLAUDE.md
/config         # Просмотр/изменение конфигурации
/permissions    # Просмотр или обновление разрешений
```

### **🤖 AI и агенты:**
```bash
/agents         # Управление пользовательскими AI субагентами
/model          # Выбор или изменение AI модели
/review         # Запрос обзора кода
/compact        # Сжатие беседы с инструкциями
```

### **🔗 Интеграция и подключения:**
```bash
/mcp            # Управление подключениями MCP серверов
/pr_comments    # Просмотр комментариев pull request
/terminal-setup # Установка привязок клавиш для новых строк
```

### **📊 Мониторинг и диагностика:**
```bash
/status         # Просмотр статуса аккаунта и системы
/cost           # Показать статистику использования токенов
/doctor         # Проверка работоспособности Claude Code
/bug            # Сообщить об ошибке в Anthropic
```

### **🎛️ Управление сессией:**
```bash
/clear          # Очистка истории беседы
/login          # Переключение аккаунтов Anthropic
/logout         # Выход из аккаунта
/help           # Получение справки по использованию
/vim            # Вход в vim режим
```

---

## 🔧 Hooks система

Hooks — это настраиваемые скрипты, выполняющиеся в определенные моменты сессии Claude Code.

### **Типы событий:**
```json
{
  "PreToolUse": "Выполняется перед использованием инструмента",
  "PostToolUse": "Выполняется после успешного завершения инструмента", 
  "UserPromptSubmit": "Срабатывает при отправке запроса пользователя",
  "SessionStart": "Запускается в начале сессии",
  "SessionEnd": "Выполняется при завершении сессии"
}
```

### **Структура hook:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command", 
            "command": "bsl-language-server --analyze $FILE"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "git add $FILE && git commit -m 'Auto commit via Claude Code'"
          }
        ]
      }
    ]
  }
}
```

### **Примеры hooks для 1С проектов:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Валидация BSL файла перед записью...'"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command", 
            "command": "echo 'Пользователь: $USER_PROMPT' >> /logs/claude-requests.log"
          }
        ]
      }
    ]
  }
}
```

---

## 🔌 MCP Integration

Model Context Protocol обеспечивает интеграцию с внешними системами.

### **Управление MCP:**
```bash
# Управление MCP серверами
/mcp

# Просмотр доступных серверов
/mcp list

# Подключение к серверу
/mcp connect <server-name>

# Отключение от сервера  
/mcp disconnect <server-name>
```

### **Интеграция с 1C-Enterprise Framework:**
В контексте нашего фреймворка MCP команды `serena__*` доступны через:
```bash
# Активация проекта 1С
serena__activate_project("/path/to/1c-project")

# Анализ качества кода
serena__get_diagnostics("CommonModules/Utils.bsl")

# Чтение памяти проекта
serena__read_memory("architecture_analysis")
```

---

## 🎯 Sub-agents (Субагенты)

Claude Code поддерживает создание специализированных AI агентов для конкретных задач.

### **Управление субагентами:**
```bash
/agents                    # Список всех агентов
/agents create <name>      # Создание нового агента
/agents edit <name>        # Редактирование агента
/agents delete <name>      # Удаление агента
/agents activate <name>    # Активация агента
```

### **Пример субагента для 1С:**
```json
{
  "name": "1c-expert",
  "description": "Специалист по разработке 1С:Предприятие",
  "instructions": "Ты эксперт по 1С:Предприятие 8.3.26. Всегда используй стандарты БСП, проверяй код через BSL Language Server и следуй принципам архитектуры фреймворка.",
  "tools": ["Read", "Write", "Edit", "Bash"],
  "model": "claude-3-5-sonnet-20241022"
}
```

---

## 📊 SDK интеграция

Claude Code предоставляет SDK для программной интеграции.

### **Python SDK:**
```python
from claude_code import ClaudeCode

# Инициализация
claude = ClaudeCode(api_key="your-key")

# Выполнение запроса
response = claude.query(
    "Создай функцию валидации ИНН для 1С",
    working_directory="/path/to/1c-project"
)

# Обработка ответа
print(response.content)
```

### **TypeScript SDK:**
```typescript
import { ClaudeCode } from '@anthropic-ai/claude-code';

const claude = new ClaudeCode({
  apiKey: process.env.CLAUDE_API_KEY
});

const response = await claude.query({
  prompt: "Анализируй архитектуру этого 1С проекта",
  workingDirectory: "/path/to/project"
});

console.log(response.content);
```

---

## ⚙️ Конфигурация и настройки

### **Основные настройки:**
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4096,
  "temperature": 0.7,
  "working_directory": "/current/project",
  "auto_save": true,
  "git_integration": true,
  "permissions": {
    "read_files": true,
    "write_files": true,
    "execute_commands": true
  }
}
```

### **Настройки для 1С проектов:**
```json
{
  "1c_integration": {
    "bsl_language_server": {
      "enabled": true,
      "path": "./tools/bsl-language-server.jar",
      "config": ".bsl-language-server.json"
    },
    "encoding": "utf8bom",
    "file_associations": {
      "*.bsl": "1c-bsl",
      "*.os": "1c-bsl"
    }
  }
}
```

---

## 🔐 Безопасность и разрешения

### **Система разрешений:**
```json
{
  "permissions": {
    "read_files": ["src/**", "docs/**"],
    "write_files": ["src/**", "!src/generated/**"], 
    "execute_commands": ["git", "npm", "bsl-language-server"],
    "network_access": false
  }
}
```

### **Безопасные практики:**
```bash
# Просмотр текущих разрешений
/permissions

# Ограничение доступа к файлам
claude --permissions-mode restricted

# Аудит выполненных команд
claude --audit-log /logs/claude-audit.log
```

---

## 📈 Мониторинг и аналитика

### **Статистика использования:**
```bash
# Информация о токенах
/cost

# Статус системы
/status

# Диагностика здоровья
/doctor
```

### **Метрики сессии:**
```json
{
  "session_stats": {
    "duration": "45 minutes",
    "tokens_used": 15420,
    "files_modified": 8,
    "commands_executed": 23,
    "errors_encountered": 1
  }
}
```

---

## 🔄 Интеграция с 1C-Enterprise Framework

### **Специфичные для фреймворка команды:**
```bash
# Активация правил cursor-rules
/config load cursor-rules/

# Интеграция с BSL Language Server
/mcp connect bsl-server

# Запуск анализа качества
claude -p "Проанализируй качество BSL кода" --output-format json
```

### **Автоматизированные workflow:**
```bash
# Создание feature ветки с Claude Code
claude "Создай ветку для задачи GKSTCPLK-1234 и настрой окружение"

# Автоматический code review
/review --include-bsl-analysis --format detailed

# Генерация коммита с правильным форматом
claude "Создай коммит для этих изменений согласно стандартам фреймворка"
```

---

## 🚨 Важные замечания

### **⚠️ Безопасность hooks:**
**ВНИМАНИЕ:** Hooks выполняют произвольные shell команды. Используйте на свой страх и риск!

### **🔧 Производительность:**
- JSON формат вывода особенно полезен для скриптов и автоматизации
- История команд сохраняется для каждой рабочей директории
- Рекомендуется ограничение `--max-turns` для сложных задач

### **📋 Лучшие практики:**
- Используйте `CLAUDE.md` для сохранения контекста проекта
- Настройте hooks для автоматической валидации кода
- Интегрируйте с системами версионного контроля
- Регулярно проверяйте `/cost` для мониторинга использования

---

**📅 Версия документа:** 1.0  
**🗓️ Последнее обновление:** 03.09.2025  
**👤 Ответственный:** Команда 1C-Enterprise Cursor Framework  
**🔗 Связанные документы:** `claude-code-hooks-api.md`, `Framework documentation claude.md`

*Полная документация доступна на: https://docs.anthropic.com/en/docs/claude-code/*