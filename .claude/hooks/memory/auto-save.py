#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-save important information to Memory-AI MCP
Улучшенная версия с правильным чтением hook JSON из stdin
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Конфигурация
CONFIG_FILE = Path(__file__).parent / "config.json"
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
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
        "min_content_length": 250,
        "save_to_timescale": True,
        "save_to_knowledge_graph": True
    }

def should_save(tool_name, config):
    """Проверка, нужно ли сохранять результат этого инструмента"""
    if not config.get("enabled", True):
        return False

    # ВАЖНО: Явная фильтрация инструментов записи файлов
    # Эти инструменты изменяют файлы и не должны триггерить hook
    # (защита на уровне кода в дополнение к matcher в settings.local.json)
    BLACKLIST = ["Write", "Edit", "MultiEdit", "NotebookEdit"]
    if tool_name in BLACKLIST:
        return False

    for pattern in config.get("auto_save_tools", []):
        if pattern in tool_name:
            return True
    return False

def read_hook_input():
    """Чтение JSON данных из stdin (hook input)"""
    try:
        # Хуки получают JSON через stdin
        hook_data = json.load(sys.stdin)
        return hook_data
    except json.JSONDecodeError as e:
        # Ошибка парсинга JSON - логируем но не падаем
        error_log = CACHE_DIR / "hooks-error.log"
        try:
            with open(error_log, 'a', encoding='utf-8', errors='replace') as f:
                # Безопасное кодирование строки ошибки для избежания суррогатных символов
                error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
                f.write(f"{datetime.now().isoformat()} - auto-save.py JSON parse error: {error_msg}\n")
        except:
            pass
        return None
    except Exception as e:
        # Другие ошибки чтения stdin
        error_log = CACHE_DIR / "hooks-error.log"
        try:
            with open(error_log, 'a', encoding='utf-8', errors='replace') as f:
                # Безопасное кодирование строки ошибки для избежания суррогатных символов
                error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
                f.write(f"{datetime.now().isoformat()} - auto-save.py stdin read error: {error_msg}\n")
        except:
            pass
        return None

def extract_context(hook_data):
    """Извлечение контекста из hook JSON"""
    if not hook_data:
        return None

    # Извлекаем данные согласно документации Claude Code
    tool_name = hook_data.get("tool_name", "unknown")
    tool_response = hook_data.get("tool_response", "")

    # Конвертируем tool_response в строку если это не строка
    if isinstance(tool_response, dict):
        tool_response = json.dumps(tool_response, ensure_ascii=False)
    elif not isinstance(tool_response, str):
        tool_response = str(tool_response)

    return {
        "tool_name": tool_name,
        "tool_response": tool_response,
        "working_dir": hook_data.get("cwd", str(PROJECT_ROOT)),
        "timestamp": datetime.now().isoformat(),
        "session_id": hook_data.get("session_id", "default")
    }

def save_to_knowledge_graph(context, config):
    """Сохранение в Memory-AI через save_conversation_fact"""
    tool_name = context["tool_name"]
    tool_response = context["tool_response"][:500]  # Первые 500 символов

    # Определяем тип активности и важность
    if "Read" in tool_name or "Grep" in tool_name:
        activity_type = "code_exploration"
        description = f"Чтение кода: {tool_response}"
        importance = 0.75
        has_code = True
    elif "WebFetch" in tool_name or "WebSearch" in tool_name:
        activity_type = "web_research"
        description = f"Поиск в интернете: {tool_response}"
        importance = 0.7
        has_code = False
    elif "mcp__github__" in tool_name:
        activity_type = "github_interaction"
        description = f"GitHub операция: {tool_response}"
        importance = 0.8
        has_code = False
    elif "Task" in tool_name:
        activity_type = "task_execution"
        description = f"Выполнение задачи: {tool_response}"
        importance = 0.85
        has_code = False
    elif "mcp__serena__" in tool_name:
        activity_type = "code_analysis"
        description = f"Анализ кода (Serena): {tool_response}"
        importance = 0.8
        has_code = True
    else:
        activity_type = "general_activity"
        description = f"{tool_name}: {tool_response}"
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
    tool_response_short = context["tool_response"][:100]  # Первые 100 символов

    content = f"[{tool_name}] {tool_response_short}"

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
        # 1. Сохраняем в формате JSONL для резервной копии и отладки
        log_file = CACHE_DIR / "auto-save-memory.jsonl"

        with open(log_file, 'a', encoding='utf-8', errors='replace') as f:
            # Используем ensure_ascii=True чтобы избежать проблем с суррогатами
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "mcp_tool": "mcp__memory-ai__save_conversation_fact",
                "params": memory_data
            }, f, ensure_ascii=True)
            f.write('\n')

        # 2. Реальный вызов Memory-AI через wrapper скрипт
        wrapper_path = Path(__file__).parent / "memory_ai_wrapper.py"

        if wrapper_path.exists():
            # Формируем JSON для wrapper с ensure_ascii=True
            wrapper_data = json.dumps(memory_data, ensure_ascii=True)

            result = subprocess.run([
                sys.executable,  # Используем тот же Python что и запустил скрипт
                str(wrapper_path),
                wrapper_data
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
            encoding='utf-8',
            errors='replace'
            )

            # Проверяем результат
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    if response.get('success'):
                        return True
                except json.JSONDecodeError:
                    pass

        # Если wrapper не сработал - не критично, данные в JSONL
        return True

    except subprocess.TimeoutExpired:
        # Timeout - не критично, данные уже в JSONL
        return True
    except FileNotFoundError:
        # wrapper не найден - не критично, работаем через JSONL
        return True
    except Exception as e:
        # Логируем ошибку но не прерываем работу
        error_log = CACHE_DIR / "hooks-error.log"
        try:
            with open(error_log, 'a', encoding='utf-8', errors='replace') as f:
                # Безопасное кодирование строки ошибки для избежания суррогатных символов
                error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
                f.write(f"{datetime.now().isoformat()} - auto-save.py ERROR: {error_msg}\n")
        except:
            pass  # Даже логирование ошибки не должно прерывать хук
        return False

def main():
    """Основная функция автосохранения"""
    try:
        # Загрузка конфигурации
        config = load_config()

        # Чтение hook input из stdin
        hook_data = read_hook_input()
        if not hook_data:
            # Нет данных - выходим с успехом
            sys.exit(0)

        # Извлечение контекста
        context = extract_context(hook_data)
        if not context:
            sys.exit(0)

        # Проверка нужно ли сохранять
        if not should_save(context["tool_name"], config):
            sys.exit(0)

        # Проверка минимальной длины контента
        if len(context["tool_response"]) < config.get("min_content_length", 250):
            sys.exit(0)

        saved_count = 0

        # Сохранение в Memory-AI Knowledge Graph
        if config.get("save_to_knowledge_graph", True):
            kg_data = save_to_knowledge_graph(context, config)
            if call_memory_ai_mcp(kg_data):
                saved_count += 1

        # Сохранение в Memory-AI Timeline
        if config.get("save_to_timescale", True):
            ts_data = save_to_timescale(context, config)
            if call_memory_ai_mcp(ts_data):
                saved_count += 1

        # Логирование только в verbose режиме
        if config.get("verbose", False) and saved_count > 0:
            log_file = CACHE_DIR / config.get("log_file", "auto-save.log")
            with open(log_file, 'a', encoding='utf-8', errors='replace') as f:
                f.write(f"{datetime.now().isoformat()} - Saved {saved_count} records from {context['tool_name']}\n")

        # Успешное завершение
        sys.exit(0)

    except Exception as e:
        # Критическая ошибка - логируем
        error_log = CACHE_DIR / "hooks-error.log"
        try:
            with open(error_log, 'a', encoding='utf-8', errors='replace') as f:
                # Безопасное кодирование строки ошибки для избежания суррогатных символов
                error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
                f.write(f"{datetime.now().isoformat()} - auto-save.py CRITICAL: {error_msg}\n")
        except:
            pass

        # Выходим с успехом чтобы не блокировать Claude
        sys.exit(0)

if __name__ == "__main__":
    main()
