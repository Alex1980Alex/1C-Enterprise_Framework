# Claude Code Hooks - Auto Memory Integration

Система автоматических хуков для интеграции с Memory MCP.

## Установленные хуки

### 1. pre-prompt-memory-check.sh
**Триггер:** Перед каждым промптом пользователя

**Функции:**
- Проверяет наличие конфигурации Memory MCP
- Проверяет активацию Memory в settings.local.json
- Напоминает о необходимости проверки релевантной информации в памяти

**Выход:**
```
✓ Memory MCP активен в конфигурации
💡 Напоминание: При ответе проверьте релевантную информацию в Memory MCP
```

### 2. post-tool-result-memory-save.sh
**Триггер:** После выполнения инструментов

**Функции:**
- Отслеживает выполнение важных инструментов (Read, Grep, WebFetch, и т.д.)
- Напоминает о сохранении важной информации в Memory MCP
- Подсказывает использовать соответствующие MCP функции

**Выход (для важных инструментов):**
```
💾 Подсказка: Если получена важная информация, сохраните её в Memory MCP
   Используйте mcp__memory__create_entities или mcp__memory__add_observations
```

## Настройка

### Активация хуков
Хуки автоматически активируются Claude Code при наличии исполняемых файлов в `.claude/hooks/`.

### Проверка работы
```bash
# Тест pre-prompt хука
.claude/hooks/pre-prompt-memory-check.sh

# Тест post-tool-result хука
CLAUDE_TOOL_NAME="Read" .claude/hooks/post-tool-result-memory-save.sh
```

### Настройка Memory MCP
1. Убедитесь, что файл `.claude/mcp-configs/memory-config.json` существует
2. Добавьте конфигурацию Memory в `.claude/settings.local.json`:
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

## Кастомизация

### Добавление новых инструментов для отслеживания
Отредактируйте `post-tool-result-memory-save.sh`:
```bash
IMPORTANT_TOOLS=(
    "Read"
    "Grep"
    "YourCustomTool"  # Добавьте ваш инструмент
)
```

### Изменение поведения
Хуки возвращают `exit 0` для непрерывной работы. Измените на `exit 1` для блокировки при проблемах.

## Интеграция с Memory MCP

### Основные функции Memory MCP
```javascript
// Создание сущностей
mcp__memory__create_entities({
  entities: [{
    name: "Entity Name",
    entityType: "Type",
    observations: ["Observation 1", "Observation 2"]
  }]
})

// Добавление наблюдений
mcp__memory__add_observations({
  observations: [{
    entityName: "Entity Name",
    contents: ["New observation"]
  }]
})

// Поиск в памяти
mcp__memory__search_nodes({
  query: "search query"
})

// Чтение графа знаний
mcp__memory__read_graph()
```

## Troubleshooting

### Хуки не выполняются
1. Проверьте права на выполнение: `ls -la .claude/hooks/`
2. Установите права: `chmod +x .claude/hooks/*.sh`
3. Проверьте синтаксис: `bash -n .claude/hooks/pre-prompt-memory-check.sh`

### Memory MCP не работает
1. Проверьте конфигурацию: `cat .claude/mcp-configs/memory-config.json`
2. Проверьте settings: `cat .claude/settings.local.json | grep memory`
3. Перезапустите Claude Code

## Дополнительная информация

- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [Memory MCP Server](https://github.com/modelcontextprotocol/servers)
- [Hooks System Overview](../../docs/API%20Documentation/hooks-system-overview.md)
