# Интеграция Serena MCP для 1C-Enterprise Framework

## 🎯 Обзор

Данная интеграция предоставляет доступ к мощным инструментам Serena через Model Context Protocol (MCP) для работы с проектами 1C:Предприятие.

## 🔧 Доступные инструменты

### Основные инструменты:
- `activate_project` - Активация проекта по имени
- `find_symbol` - Поиск символов в коде BSL
- `find_referencing_symbols` - Поиск ссылок на символы
- `get_symbols_overview` - Обзор символов в файле
- `read_file` - Чтение файлов проекта
- `create_text_file` - Создание файлов
- `search_for_pattern` - Поиск по шаблонам

### Опциональные инструменты:
- `get_current_config` - Диагностика конфигурации
- `initial_instructions` - Инструкции для проекта
- `restart_language_server` - Перезапуск BSL Language Server
- `summarize_changes` - Сводка изменений
- `switch_modes` - Переключение режимов работы
- `delete_lines` - Удаление строк
- `insert_at_line` - Вставка в строку
- `replace_lines` - Замена строк

## 🚀 Быстрый запуск

### Windows:
```cmd
start-serena-mcp.bat
```

### Linux/macOS:
```bash
./start-serena-mcp.sh
```

## ⚙️ Настройка Claude Desktop

Добавьте в файл конфигурации Claude Desktop:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "serena": {
      "command": "uv",
      "args": ["run", "serena-mcp-server", "--project", "1C-Enterprise_Framework"],
      "cwd": "D:/1C-Enterprise_Framework/serena"
    }
  }
}
```

## 📋 Требования

- **Python 3.11+**
- **uv** - менеджер пакетов Python
- **Java 11+** - для BSL Language Server

### Установка uv:
```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 🏗️ Структура проектов

```
1C-Enterprise_Framework/
├── serena/                          # Serena как подмодуль
├── src/
│   ├── .serena/
│   │   └── global.yml              # Глобальные настройки
│   ├── example-1c-project/
│   │   └── .serena/
│   │       └── project.yml         # Настройки проекта
│   └── projects/
│       └── demo-accounting/
│           └── .serena/
│               └── project.yml     # Настройки проекта
├── mcp_settings.json              # MCP конфигурация
└── start-serena-mcp.*            # Скрипты запуска
```

## 🔍 Использование

### 1. Активация проекта:
```
Активируй проект example-1c-project
```

### 2. Поиск символов:
```
Найди все процедуры в проекте
```

### 3. Анализ кода:
```
Покажи обзор символов в файле CommonModules/ОбщегоНазначения.bsl
```

### 4. Редактирование:
```
Замени содержимое процедуры ИнициализироватьСистему
```

## 🐛 Устранение неполадок

### BSL Language Server не запускается:
1. Проверьте наличие Java: `java -version`
2. Перезапустите сервер: используйте инструмент `restart_language_server`

### MCP сервер не подключается:
1. Проверьте пути в конфигурации
2. Убедитесь что uv установлен: `uv --version`
3. Проверьте логи Claude Desktop

### Проект не найден:
1. Убедитесь что файл `.serena/project.yml` существует
2. Проверьте настройки `project_name` в конфигурации

## 📚 Дополнительные ресурсы

- [Документация Serena](https://github.com/oraios/serena)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [BSL Language Server](https://github.com/1c-syntax/bsl-language-server)
- [Документация 1C:Предприятие](https://its.1c.ru/db/v8std)

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте логи в консоли
2. Убедитесь что все зависимости установлены
3. Проверьте конфигурацию проектов в `.serena/project.yml`