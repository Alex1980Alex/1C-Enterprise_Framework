#!/bin/bash
# Post Tool Result Auto-Save Hook
# Автоматическое сохранение важной информации в Memory MCP после операций

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Получаем имя инструмента и результат из переменных окружения
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
TOOL_RESULT="${CLAUDE_TOOL_RESULT:-}"

# Путь к скрипту автосохранения
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTO_SAVE_SCRIPT="$SCRIPT_DIR/auto-save-to-memory.py"
CONFIG_FILE="$SCRIPT_DIR/auto-save-config.json"

# Проверка наличия конфигурации
if [ ! -f "$CONFIG_FILE" ]; then
    printf "${YELLOW}⚠ Конфигурация автосохранения не найдена${NC}\n" >&2
    exit 0
fi

# Чтение настройки enabled из конфига
ENABLED=$(grep -o '"enabled"[[:space:]]*:[[:space:]]*[^,}]*' "$CONFIG_FILE" | grep -o 'true\|false')

if [ "$ENABLED" != "true" ]; then
    # Автосохранение отключено, показываем только напоминание
    printf "${BLUE}💾 Подсказка: Автосохранение отключено. Включите в auto-save-config.json${NC}\n" >&2
    exit 0
fi

# Список инструментов для автосохранения
IMPORTANT_TOOLS=(
    "Read"
    "Grep"
    "Glob"
    "WebFetch"
    "WebSearch"
    "mcp__github__"
    "mcp__1c"
    "Task"
    "mcp__serena__find_symbol"
    "mcp__serena__get_symbols_overview"
)

# Проверка, является ли инструмент важным
SHOULD_SAVE=false
for tool in "${IMPORTANT_TOOLS[@]}"; do
    if [[ "$TOOL_NAME" == *"$tool"* ]]; then
        SHOULD_SAVE=true
        break
    fi
done

# Если инструмент не важный, выходим
if [ "$SHOULD_SAVE" = false ]; then
    exit 0
fi

# Вывод информации
printf "${CYAN}🔄 Инструмент: $TOOL_NAME${NC}\n" >&2
printf "${BLUE}💾 Автосохранение в Memory MCP...${NC}\n" >&2

# Вызов Python скрипта автосохранения
if [ -f "$AUTO_SAVE_SCRIPT" ]; then
    export CLAUDE_TOOL_NAME="$TOOL_NAME"
    export CLAUDE_TOOL_RESULT="$TOOL_RESULT"

    # Запуск с обработкой ошибок (используем python вместо python3 на Windows)
    if python "$AUTO_SAVE_SCRIPT" 2>&1; then
        printf "${GREEN}✓ Данные сохранены в Memory MCP${NC}\n" >&2
    else
        printf "${YELLOW}⚠ Ошибка автосохранения, см. логи${NC}\n" >&2
    fi
else
    printf "${YELLOW}⚠ Скрипт автосохранения не найден: $AUTO_SAVE_SCRIPT${NC}\n" >&2
fi

# Всегда возвращаем успех
exit 0
