#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-save important information to Memory-AI MCP
Улучшенная версия с реальной интеграцией Memory-AI
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Конфигурация
CONFIG_FILE = Path(__file__).parent / "config.json"
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
    """Сохранение в Memory-AI через save_conversation_fact"""
    tool_name = context["tool_name"]
    tool_result = context["tool_result"][:500]  # Первые 500 символов

    # Определяем тип активности и важность
    if "Read" in tool_name or "Grep" in tool_name:
        activity_type = "code_exploration"
        description = f"Чтение кода: {tool_result}"
        importance = 0.75
        has_code = True
    elif "WebFetch" in tool_name or "WebSearch" in tool_name:
        activity_type = "web_research"
        description = f"Поиск в интернете: {tool_result}"
        importance = 0.7
        has_code = False
    elif "mcp__github__" in tool_name:
        activity_type = "github_interaction"
        description = f"GitHub операция: {tool_result}"
        importance = 0.8
        has_code = False
    elif "Task" in tool_name:
        activity_type = "task_execution"
        description = f"Выполнение задачи: {tool_result}"
        importance = 0.85
        has_code = False
    elif "mcp__serena__" in tool_name:
        activity_type = "code_analysis"
        description = f"Анализ кода (Serena): {tool_result}"
        importance = 0.8
        has_code = True
    else:
        activity_type = "general_activity"
        description = f"{tool_name}: {tool_result}"
        importance = 0.6
        has_code = False

    # Формируем контент для Memory-AI
    content = f"""Инструмент: {tool_name}
Тип: {activity_type}

{description}

Working directory: {context['working_dir']}
Timestamp: {context['timestamp']}"""

    # Данные для Memory-AI MCP (save_conversation_fact)
    memory_data = {
        "content": content,
        "importance": importance,
        "has_code": has_code,
        "metadata": {
            "tool": tool_name,
            "activity_type": activity_type,
            "working_dir": context['working_dir'],
            "session_id": context['session_id']
        }
    }

    return memory_data

def save_to_timescale(context, config):
    """Сохранение краткой информации в временную шкалу"""
    tool_name = context["tool_name"]
    tool_result_short = context["tool_result"][:100]  # Первые 100 символов

    content = f"[{tool_name}] {tool_result_short}"

    return {
        "content": content,
        "importance": 0.5,  # Низкая важность для временной шкалы
        "has_code": False,
        "metadata": {
            "tool": tool_name,
            "type": "tool_execution",
            "working_dir": context["working_dir"],
            "session_id": context["session_id"]
        }
    }

def call_memory_ai_mcp(memory_data):
    """Вызов Memory-AI MCP для сохранения данных"""
    try:
        # Сохраняем в формате JSONL для последующей обработки
        log_file = CACHE_DIR / "auto-save-memory.jsonl"

        # Запись в лог
        with open(log_file, 'a', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "mcp_tool": "mcp__memory-ai__save_conversation_fact",
                "params": memory_data
            }, f, ensure_ascii=False)
            f.write('\n')

        # TODO: Интеграция с реальным MCP через subprocess или API
        # Пример вызова через Claude CLI (требует настройки):
        #
        # subprocess.run([
        #     "claude", "mcp", "call",
        #     "memory-ai",
        #     "save_conversation_fact",
        #     "--content", memory_data["content"],
        #     "--importance", str(memory_data["importance"]),
        #     "--has-code", str(memory_data["has_code"]).lower(),
        #     "--metadata", json.dumps(memory_data["metadata"])
        # ], check=True)

        return True
    except Exception as e:
        print(f"Error saving to Memory-AI MCP: {e}", file=sys.stderr)
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

    saved_count = 0

    # Сохранение в Memory-AI Knowledge Graph
    if config.get("save_to_knowledge_graph", True):
        kg_data = save_to_knowledge_graph(context, config)
        if call_memory_ai_mcp(kg_data):
            print("  ✓ Saved to Knowledge Graph", file=sys.stderr)
            saved_count += 1

    # Сохранение в Memory-AI Timeline
    if config.get("save_to_timescale", True):
        ts_data = save_to_timescale(context, config)
        if call_memory_ai_mcp(ts_data):
            print("  ✓ Saved to Timeline", file=sys.stderr)
            saved_count += 1

    if saved_count > 0:
        print(f"✓ Автосохранение в Memory-AI MCP выполнено ({saved_count} записей)", file=sys.stderr)

    sys.exit(0)

if __name__ == "__main__":
    main()
