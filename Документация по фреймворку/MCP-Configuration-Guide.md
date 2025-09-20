# MCP Server Configuration Guide

## Обзор конфигурации

Данный документ описывает конфигурацию MCP серверов в `.mcp.json` файле для интеграции с Claude Code.

## Установленные MCP серверы

### 1. Task Master AI
**Назначение**: Управление задачами и планирование проектов
```json
"task-master-ai": {
    "type": "stdio",
    "command": "task-master-ai",
    "args": []
}
```

**Возможности:**
- Создание и управление задачами
- Планирование разработки
- Анализ сложности задач
- Парсинг PRD документов

### 2. Serena Framework Enhanced
**Назначение**: Продвинутый анализ и рефакторинг 1C кода
```json
"serena-framework": {
    "type": "stdio",
    "command": "/mnt/d/1C-Enterprise_Cursor_Framework/serena-unified/run_mcp_server.sh",
    "args": [],
    "env": {
        "PYTHONPATH": "/mnt/d/1C-Enterprise_Cursor_Framework/serena-unified/src"
    }
}
```

**Новые возможности:**
- 🌳 **AST анализ**: Глубокий анализ структуры BSL кода
- 🔧 **Рефакторинг**: Извлечение методов, переименование переменных
- 🔒 **Security сканирование**: Поиск уязвимостей и секретов
- ⚡ **Оптимизация**: Улучшение запросов и модернизация кода

### 3. GitHub Integration
**Назначение**: Работа с GitHub репозиториями
```json
"github": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "..."
    }
}
```

**Возможности:**
- Создание и управление репозиториями
- Работа с Issues и Pull Requests
- Управление файлами через GitHub API

### 4. Brave Search
**Назначение**: Поиск в интернете для исследований
```json
"brave-search": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
    "env": {
        "BRAVE_API_KEY": "..."
    }
}
```

**Возможности:**
- Веб-поиск для исследований
- Поиск документации
- Локальный поиск предприятий

### 5. Rust File System
**Назначение**: Работа с файловой системой
```json
"rust-filesystem": {
    "type": "stdio",
    "command": "/home/lex/.local/bin/rust-mcp-filesystem",
    "args": ["--allow-write", "/mnt/d/1C-Enterprise_Cursor_Framework"]
}
```

**Возможности:**
- Чтение и запись файлов
- Управление директориями
- Поиск файлов по паттернам
- Архивирование (ZIP)

### 6. Sequential Thinking
**Назначение**: Последовательный анализ сложных задач
```json
"sequential-thinking": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
}
```

**Возможности:**
- Пошаговый анализ задач
- Структурированное мышление
- Планирование сложных процессов

### 7. PostgreSQL MCP (Опционально)
**Назначение**: Работа с базами данных PostgreSQL
```json
"postgres": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "enhanced-postgres-mcp-server"],
    "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:password@localhost:5432/database"
    }
}
```

### 8. MySQL MCP (Опционально)
**Назначение**: Работа с базами данных MySQL
```json
"mysql": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@benborla29/mcp-server-mysql"],
    "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "root",
        "MYSQL_PASS": "password",
        "MYSQL_DB": "database",
        "ALLOW_WRITE": "false"
    }
}
```

## Workflow использования

### Для разработки 1C:Enterprise

1. **Планирование** (Task Master AI):
   ```bash
   task-master init
   task-master parse-prd .taskmaster/docs/prd.txt
   task-master next
   ```

2. **Анализ кода** (Serena Framework):
   ```python
   # AST анализ
   bsl_ast_analysis("/path/to/module.bsl", include_metrics=True)
   
   # Поиск проблем безопасности
   security_scan("/path/to/project/", export_report=True)
   ```

3. **Рефакторинг** (Serena Framework):
   ```python
   # Извлечение метода
   extract_method("/path/to/module.bsl", 45, 67, "НовыйМетод")
   
   # Оптимизация запроса
   optimize_query("ВЫБРАТЬ * ИЗ Справочник.Номенклатура...")
   ```

4. **Исследования** (Brave Search):
   ```python
   brave_web_search("1C Enterprise best practices 2025")
   brave_local_search("1C разработчики рядом")
   ```

5. **Работа с файлами** (Rust File System):
   ```python
   read_file("/path/to/module.bsl")
   search_files("/project/", "*.bsl")
   edit_file("/path/to/file.bsl", edits=[...])
   ```

6. **Git операции** (GitHub MCP):
   ```python
   create_pull_request("owner", "repo", "Feature branch", "main", "Новая функциональность")
   get_file_contents("owner", "repo", "path/to/file.bsl")
   ```

## Рекомендации по использованию

### Безопасность
- Храните API ключи в переменных окружения
- Используйте минимальные права доступа
- Регулярно обновляйте токены

### Производительность
- Используйте Sequential Thinking для сложных задач
- Кэшируйте результаты поиска
- Батчите операции с файлами

### Интеграция
- Комбинируйте инструменты для комплексных workflow
- Используйте Task Master для планирования
- Применяйте Serena для качественного анализа

## Структура проекта с MCP

```
project/
├── .mcp.json                    # Конфигурация MCP серверов
├── .taskmaster/                 # Task Master AI данные
│   ├── tasks/tasks.json
│   └── config.json
├── .claude/                     # Claude Code настройки
│   └── settings.json
└── src/                         # Исходный код проекта
    └── Configuration/
        ├── CommonModules/
        ├── Catalogs/
        └── Reports/
```

## Troubleshooting

### Проблемы подключения
1. Проверьте правильность путей в `.mcp.json`
2. Убедитесь в наличии необходимых зависимостей
3. Проверьте права доступа к файлам

### Проблемы с API ключами
1. Проверьте корректность токенов
2. Убедитесь в достаточных правах доступа
3. Проверьте лимиты API

### Производительность
1. Используйте фильтры для больших проектов
2. Оптимизируйте запросы к внешним API
3. Кэшируйте результаты анализа

---

**Создано:** 10.09.2025  
**Версия:** 1.0.0  
**Статус:** Production Ready

*Конфигурация обеспечивает полный цикл разработки 1C:Enterprise приложений с использованием современных AI инструментов.*