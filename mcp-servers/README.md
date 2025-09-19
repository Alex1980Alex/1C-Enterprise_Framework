# Локальные MCP серверы

Эта папка содержит локальные MCP (Model Context Protocol) серверы для проекта 1C-Enterprise_Framework.

## Установленные серверы

- **@modelcontextprotocol/server-brave-search** - Поиск через Brave Search API
- **@modelcontextprotocol/server-filesystem** - Работа с файловой системой
- **@modelcontextprotocol/server-github** - Интеграция с GitHub API
- **@modelcontextprotocol/server-memory** - Управление памятью и контекстом
- **@modelcontextprotocol/server-sequential-thinking** - Последовательное мышление

## Установка

```bash
cd mcp-servers
npm install
```

## Конфигурация

MCP серверы настроены в файле Claude Desktop:
`C:\Users\AlexT\AppData\Roaming\Claude\claude_desktop_config.json`

Все серверы запускаются локально через Node.js из папки проекта.

## Переменные окружения

- `GITHUB_PERSONAL_ACCESS_TOKEN` - токен для GitHub API
- `BRAVE_API_KEY` - ключ для Brave Search API

## Обновление

Для обновления серверов до последних версий:
```bash
cd mcp-servers
npm update
```