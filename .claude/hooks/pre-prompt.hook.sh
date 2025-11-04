#!/bin/bash
# ==============================================================================
# AI Memory System - Pre-Prompt Hook
# Автоматически запускается перед каждым промптом в Claude Code
# ==============================================================================

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Флаг для однократной проверки за сессию
STATUS_FILE="/tmp/claude-code-infrastructure-checked"

# Если уже проверяли в этой сессии - пропускаем
if [ -f "$STATUS_FILE" ]; then
    exit 0
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 AI Memory System Infrastructure Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Функция проверки сервиса
check_service() {
    local name=$1
    local check_cmd=$2

    if eval "$check_cmd" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name"
        return 0
    else
        echo -e "${RED}✗${NC} $name"
        return 1
    fi
}

# Счетчик для статистики
SERVICES_OK=0
SERVICES_TOTAL=0

# Проверка Docker
((SERVICES_TOTAL++))
if check_service "Docker Desktop" "docker info"; then
    ((SERVICES_OK++))
    DOCKER_OK=1
else
    DOCKER_OK=0
fi

# Проверка Qdrant
((SERVICES_TOTAL++))
if check_service "Qdrant (port 6333)" "timeout 2 curl -s http://localhost:6333/health"; then
    ((SERVICES_OK++))
    QDRANT_OK=1
else
    QDRANT_OK=0
fi

# Проверка Neo4j
((SERVICES_TOTAL++))
if check_service "Neo4j (port 7474)" "timeout 2 curl -s http://localhost:7474"; then
    ((SERVICES_OK++))
    NEO4J_OK=1
else
    NEO4J_OK=0
fi

# Проверка Ollama
((SERVICES_TOTAL++))
if check_service "Ollama (port 11434)" "timeout 2 curl -s http://localhost:11434/api/tags"; then
    ((SERVICES_OK++))
    OLLAMA_OK=1
else
    OLLAMA_OK=0
fi

echo ""
echo "Status: $SERVICES_OK/$SERVICES_TOTAL services operational"
echo ""
echo "Note: Memory AI MCP checked by separate hook"
echo ""

# Если Docker не запущен - предлагаем запустить
if [ $DOCKER_OK -eq 0 ]; then
    echo -e "${YELLOW}⚠${NC} Docker is not running"
    echo ""
    echo "Would you like to start Docker services? (y/n)"
    read -r -n 1 -t 10 response
    echo ""

    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Starting Docker services..."
        # Конвертируем путь для Windows
        cmd.exe /c "D:\1C-Enterprise_Framework\scripts\infrastructure\start-docker-services.bat"

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} Docker services started"
        else
            echo -e "${RED}✗${NC} Failed to start Docker services"
        fi
    else
        echo "Skipping Docker startup"
        echo ""
        echo -e "${YELLOW}Note:${NC} Some AI Memory features will be limited without Docker:"
        echo "  • Semantic search (Qdrant) - unavailable"
        echo "  • Graph analytics (Neo4j) - unavailable"
        echo "  • Only LLM services will work"
    fi
elif [ $QDRANT_OK -eq 0 ] || [ $NEO4J_OK -eq 0 ]; then
    echo -e "${YELLOW}⚠${NC} Some Docker services are not responding"
    echo ""
    echo "Try running: scripts/infrastructure/start-docker-services.bat"
fi

# Если Ollama не запущен
if [ $OLLAMA_OK -eq 0 ]; then
    echo -e "${YELLOW}⚠${NC} Ollama is not running"
    echo ""
    echo "LLM features will be unavailable. Start Ollama manually if needed."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Создаем флаг что проверка выполнена
touch "$STATUS_FILE"

# Автоудаление флага через 1 час (3600 секунд)
(sleep 3600 && rm -f "$STATUS_FILE") &

exit 0
