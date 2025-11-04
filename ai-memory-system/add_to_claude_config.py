#!/usr/bin/env python3
"""
Скрипт для добавления AI Memory MCP Server в конфигурацию Claude Code
"""

import json
import os
import sys

# Путь к конфигурации Claude Code
CLAUDE_CONFIG_PATH = os.path.join(os.getenv("APPDATA"), "Claude", "claude_desktop_config.json")

# Конфигурация AI Memory MCP Server
AI_MEMORY_CONFIG = {
    "ai-memory-system": {
        "command": "python",
        "args": [
            "D:/1C-Enterprise_Framework/ai-memory-system/mcp_server/server_fastmcp.py"
        ],
        "cwd": "D:/1C-Enterprise_Framework/ai-memory-system",
        "env": {
            "PYTHONPATH": "D:/1C-Enterprise_Framework/ai-memory-system",
            "NEO4J_PASSWORD": "your_password"  # ЗАМЕНИТЕ НА РЕАЛЬНЫЙ ПАРОЛЬ!
        },
        "description": "AI Memory System for BSL code analysis",
        "timeout": 30000
    }
}

def main():
    print("=" * 60)
    print("Добавление AI Memory MCP Server в Claude Code")
    print("=" * 60)
    print()

    # Проверка существования файла
    if not os.path.exists(CLAUDE_CONFIG_PATH):
        print(f"ERROR: Файл конфигурации не найден:")
        print(f"  {CLAUDE_CONFIG_PATH}")
        print()
        print("Убедитесь, что Claude Code установлен и запускался хотя бы один раз.")
        sys.exit(1)

    # Чтение текущей конфигурации
    print(f"Чтение конфигурации из: {CLAUDE_CONFIG_PATH}")
    with open(CLAUDE_CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Проверка наличия секции mcpServers
    if "mcpServers" not in config:
        config["mcpServers"] = {}
        print("Создана секция mcpServers")

    # Проверка, не существует ли уже ai-memory-system
    if "ai-memory-system" in config["mcpServers"]:
        print()
        print("ВНИМАНИЕ: Конфигурация 'ai-memory-system' уже существует!")
        print()
        response = input("Перезаписать существующую конфигурацию? (y/N): ")
        if response.lower() != 'y':
            print("Операция отменена.")
            sys.exit(0)

    # Добавление нашей конфигурации
    config["mcpServers"].update(AI_MEMORY_CONFIG)
    print("✓ Конфигурация добавлена")

    # Сохранение обновленной конфигурации
    with open(CLAUDE_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    print("✓ Файл конфигурации обновлен")
    print()
    print("=" * 60)
    print("УСПЕХ! AI Memory MCP Server добавлен в Claude Code")
    print("=" * 60)
    print()
    print("ВАЖНО: Перед использованием выполните следующие шаги:")
    print()
    print("1. Узнайте пароль Neo4j:")
    print("   - Откройте: http://localhost:7474")
    print("   - Попробуйте войти с паролями: neo4j, password, admin")
    print()
    print("2. Обновите пароль в конфигурации:")
    print(f"   - Файл: {CLAUDE_CONFIG_PATH}")
    print("   - Найдите: \"NEO4J_PASSWORD\": \"your_password\"")
    print("   - Замените на ваш реальный пароль")
    print()
    print("   ИЛИ установите переменную окружения:")
    print('   $env:NEO4J_PASSWORD="ваш_пароль"')
    print()
    print("3. ПЕРЕЗАПУСТИТЕ Claude Code полностью:")
    print("   - Закройте все окна Claude Code")
    print("   - Запустите Claude Code заново")
    print()
    print("4. Проверьте, что MCP сервер загружен:")
    print("   - В Claude Code должен появиться 'ai-memory-system' в списке инструментов")
    print()
    print("Для проверки пароля Neo4j используйте:")
    print("  python ai-memory-system/test_neo4j_password.py")
    print()
    print("Подробная инструкция:")
    print("  ai-memory-system/CHECK_NEO4J_PASSWORD.md")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print(f"ERROR: {e}")
        print()
        sys.exit(1)
