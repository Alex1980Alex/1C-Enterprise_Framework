# Руководство по производительности MCP серверов

## Оптимизация настроек

### Claude Code настройки (.claude/settings.json)
```json
{
  "mcpTimeout": 30000,
  "maxTokens": 8192,
  "temperature": 0.1
}
```

### Переменные окружения
```bash
# Загрузить оптимизированные настройки
source .env.performance
```

### Кэширование
- `.cache/mcp/` - кэш MCP операций
- `.cache/serena/` - кэш анализа Serena
- `.cache/taskmaster/` - кэш Task Master

## Мониторинг производительности

### Быстрая проверка
```bash
./scripts/quick-mcp-test.sh
```

### Детальная диагностика
```bash
./test-mcp-hooks-comprehensive.sh
```

## Рекомендации

1. **Серена Framework**: Ограничить размер анализируемых файлов до 10MB
2. **Task Master**: Использовать кэширование для больших проектов
3. **GitHub MCP**: Батчить операции с файлами
4. **Brave Search**: Кэшировать результаты поиска

## Troubleshooting

### Медленная работа Serena
1. Проверить размер анализируемых файлов
2. Включить параллельный анализ
3. Очистить кэш: `rm -rf .cache/serena/*`

### Таймауты MCP
1. Увеличить `mcpTimeout` в настройках
2. Проверить сетевое соединение
3. Перезапустить Claude Code
