#!/bin/bash
# Auto Memory Check Hook
# Проверка доступности Memory MCP перед отправкой промпта

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Проверка активности Memory MCP через claude mcp list
if command -v claude &> /dev/null; then
    MEMORY_STATUS=$(claude mcp list 2>/dev/null | grep -i "^memory:" | grep "Connected")

    if [ -n "$MEMORY_STATUS" ]; then
        printf "${GREEN}✓ Memory MCP активен и подключен${NC}\n" >&2

        # Напоминание о проверке памяти перед ответом
        printf "${YELLOW}💡 Напоминание: Проверьте релевантную информацию в Memory MCP перед ответом${NC}\n" >&2
        printf "${YELLOW}   → mcp__memory__search_nodes({query: \"ключевые слова\"})${NC}\n" >&2
    else
        printf "${RED}✗ Memory MCP не подключен${NC}\n" >&2
        printf "${YELLOW}📝 Проверьте конфигурацию в claude_desktop_config.json${NC}\n" >&2
    fi
else
    # Если claude CLI недоступен, проверяем наличие конфигурации
    CLAUDE_CONFIG="$APPDATA/Claude/claude_desktop_config.json"
    if [ -f "$CLAUDE_CONFIG" ] && grep -q '"memory"' "$CLAUDE_CONFIG" 2>/dev/null; then
        printf "${GREEN}✓ Memory MCP настроен в конфигурации${NC}\n" >&2
        printf "${YELLOW}💡 Напоминание: Проверьте Memory MCP перед ответом${NC}\n" >&2
    else
        printf "${YELLOW}⚠ Memory MCP может быть не настроен${NC}\n" >&2
    fi
fi

# Всегда возвращаем успех (0), чтобы не блокировать промпт
exit 0
