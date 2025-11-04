#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-save important information to Memory MCP
Используется хуками для автоматического сохранения контекста
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Конфигурация
CONFIG_FILE = Path(__file__).parent / "auto-save-config.json"
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
CACHE_DIR = PROJECT_ROOT / "cache"
CACHE_DIR.mkdir(exist_ok=True)

def load_config():
    """Загрузка конфигурации автосохранения"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "enabled": True,
        "auto_save_tools": [
            "Read", "Grep", "Glob", "WebFetch", "WebSearch",
            "mcp__github__", "mcp__1c", "Task",
            "mcp__serena__find_symbol", "mcp__serena__get_symbols_overview"
        ],
        "min_content_length": 100,
        "save_to_timescale": True,
        "save_to_knowledge_graph": True
    }

def should_save(tool_name, config):
    """Проверка, нужно ли сохранять результат этого инструмента"""
    if not config.get("enabled", True):
        return False

    for pattern in config.get("auto_save_tools", []):
        if pattern in tool_name:
            return True
    return False

def extract_context():
    """Извлечение контекста из переменных окружения"""
    return {
        "tool_name": os.getenv("CLAUDE_TOOL_NAME", "unknown"),
        "tool_result": os.getenv("CLAUDE_TOOL_RESULT", ""),
        "working_dir": os.getenv("PWD", str(PROJECT_ROOT)),
        "timestamp": datetime.now().isoformat(),
        "session_id": os.getenv("CLAUDE_SESSION_ID", "default")
    }

def save_to_knowledge_graph(context, config):
    """Сохранение в Knowledge Graph через Memory MCP"""
    tool_name = context["tool_name"]
    tool_result = context["tool_result"][:500]  # Первые 500 символов

    # Определяем тип сущности на основе инструмента
    if "Read" in tool_name or "Grep" in tool_name:
        entity_type = "code_exploration"
        observation = f"Чтение кода: {tool_result}"
    elif "WebFetch" in tool_name or "WebSearch" in tool_name:
        entity_type = "web_research"
        observation = f"Поиск в интернете: {tool_result}"
    elif "mcp__github__" in tool_name:
        entity_type = "github_interaction"
        observation = f"GitHub операция: {tool_result}"
    elif "Task" in tool_name:
        entity_type = "task_execution"
        observation = f"Выполнение задачи: {tool_result}"
    else:
        entity_type = "general_activity"
        observation = f"{tool_name}: {tool_result}"

    entity_name = f"Activity_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Формируем JSON для сохранения
    memory_data = {
        "entities": [{
            "name": entity_name,
            "entityType": entity_type,
            "observations": [
                observation,
                f"Timestamp: {context['timestamp']}",
                f"Working dir: {context['working_dir']}"
            ]
        }]
    }

    return memory_data

def save_to_timescale(context, config):
    """Сохранение в TimescaleDB через Memory-AI MCP"""
    # Здесь будет логика сохранения в TimescaleDB
    # Пока просто формируем данные
    return {
        "conversation_id": context.get("session_id"),
        "message": {
            "role": "system",
            "content": f"Tool execution: {context['tool_name']}",
            "timestamp": context["timestamp"],
            "metadata": {
                "tool": context["tool_name"],
                "working_dir": context["working_dir"]
            }
        }
    }

def call_claude_mcp(mcp_command):
    """Вызов Claude MCP для сохранения данных"""
    try:
        # Здесь должен быть вызов MCP через Claude CLI
        # Пока просто логируем
        log_file = CACHE_DIR / "auto-save.log"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - {json.dumps(mcp_command, ensure_ascii=False)}\n")

        return True
    except Exception as e:
        print(f"Error saving to MCP: {e}", file=sys.stderr)
        return False

def main():
    """Основная функция автосохранения"""
    config = load_config()
    context = extract_context()

    if not should_save(context["tool_name"], config):
        sys.exit(0)

    # Проверка минимальной длины контента
    if len(context["tool_result"]) < config.get("min_content_length", 100):
        sys.exit(0)

    # Сохранение в Knowledge Graph
    if config.get("save_to_knowledge_graph", True):
        kg_data = save_to_knowledge_graph(context, config)
        call_claude_mcp({"type": "knowledge_graph", "data": kg_data})

    # Сохранение в TimescaleDB
    if config.get("save_to_timescale", True):
        ts_data = save_to_timescale(context, config)
        call_claude_mcp({"type": "timescale", "data": ts_data})

    print("✓ Автосохранение в Memory MCP выполнено", file=sys.stderr)
    sys.exit(0)

if __name__ == "__main__":
    main()
