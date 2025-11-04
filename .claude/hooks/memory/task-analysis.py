#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task Analysis Script
Анализирует новую задачу через stdin (hook JSON) и сохраняет в Memory-AI MCP
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

# Конфигурация
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.resolve()
CACHE_DIR = PROJECT_ROOT / "cache"
CACHE_DIR.mkdir(exist_ok=True)

def read_hook_input():
    """Чтение JSON данных из stdin (hook input)"""
    try:
        hook_data = json.load(sys.stdin)
        return hook_data
    except json.JSONDecodeError as e:
        error_log = CACHE_DIR / "hooks-error.log"
        with open(error_log, 'a', encoding='utf-8', errors='replace') as f:
            f.write(f"{datetime.now().isoformat()} - task-analysis.py JSON parse error: {str(e)}\n")
        return None
    except Exception as e:
        error_log = CACHE_DIR / "hooks-error.log"
        with open(error_log, 'a', encoding='utf-8', errors='replace') as f:
            f.write(f"{datetime.now().isoformat()} - task-analysis.py stdin read error: {str(e)}\n")
        return None

def extract_context(hook_data):
    """Извлечение контекста задачи из hook JSON"""
    if not hook_data:
        return None

    # Пытаемся извлечь user prompt из разных возможных полей
    user_prompt = (
        hook_data.get("user_message") or
        hook_data.get("prompt") or
        hook_data.get("user_prompt") or
        hook_data.get("message") or
        ""
    )

    if isinstance(user_prompt, dict):
        # Возможно промпт в виде объекта с полем text
        user_prompt = user_prompt.get("text", "")

    if not user_prompt or len(user_prompt) < 10:
        return None

    return {
        "user_prompt": user_prompt,
        "task_type": determine_task_type(user_prompt),
        "task_id": f"Task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "session_id": hook_data.get("session_id", "unknown"),
        "working_dir": hook_data.get("cwd", str(PROJECT_ROOT)),
        "timestamp": datetime.now().isoformat()
    }

def determine_task_type(text):
    """Определение типа задачи по ключевым словам"""
    text_lower = text.lower()

    # Паттерны для определения типа задачи
    patterns = {
        'bug_fix': r'(исправ|баг|ошибк|починк|не работает|проблем|фикс)',
        'feature_development': r'(добав|создай|реализ|разработай|новый|функци|feature)',
        'code_review': r'(провер|ревью|review|посмотри|оцен)',
        'refactoring': r'(рефактор|оптимиз|улучш|переписа|реорганиз)',
        'documentation': r'(документ|описа|комментар|readme)',
        'testing': r'(тест|провер|юнит)',
        'analysis': r'(анализ|изуч|разбер|понять|объясн)'
    }

    for task_type, pattern in patterns.items():
        if re.search(pattern, text_lower):
            return task_type

    return 'general'

def extract_keywords(text):
    """Извлечение ключевых слов из текста задачи"""
    stop_words = {
        'добавь', 'создай', 'реализуй', 'сделай', 'напиши', 'разработай',
        'исправь', 'починь', 'нужно', 'необходимо', 'пожалуйста',
        'можешь', 'можно', 'хочу', 'надо', 'требуется'
    }

    words = re.findall(r'\b[а-яА-Яa-zA-Z]{4,}\b', text.lower())
    keywords = [w for w in words if w not in stop_words]

    unique_keywords = []
    for kw in keywords:
        if kw not in unique_keywords:
            unique_keywords.append(kw)
        if len(unique_keywords) >= 10:
            break

    return unique_keywords

def determine_priority(task_type, keywords):
    """Определение приоритета задачи"""
    high_priority_words = ['баг', 'ошибка', 'критический', 'срочно', 'не', 'работает']

    if task_type == 'bug_fix':
        return 'high'

    if any(word in keywords for word in high_priority_words):
        return 'high'

    if task_type == 'feature_development':
        return 'medium'

    return 'low'

def estimate_complexity(user_prompt, keywords):
    """Оценка сложности задачи"""
    length = len(user_prompt)
    keyword_count = len(keywords)

    complex_words = ['интеграция', 'архитектура', 'рефакторинг', 'миграция', 'оптимизация']
    has_complex = any(word in keywords for word in complex_words)

    if length > 200 or keyword_count > 7 or has_complex:
        return 'high'
    elif length > 100 or keyword_count > 4:
        return 'medium'
    else:
        return 'low'

def format_task_analysis(context):
    """Форматирование анализа задачи для Memory-AI"""
    keywords = extract_keywords(context['user_prompt'])
    priority = determine_priority(context['task_type'], keywords)
    complexity = estimate_complexity(context['user_prompt'], keywords)

    analysis = f"""Новая задача: {context['task_id']}

ЗАПРОС: {context['user_prompt']}

АНАЛИЗ:
- Тип задачи: {context['task_type']}
- Приоритет: {priority}
- Сложность: {complexity}
- Ключевые слова: {', '.join(keywords)}

МЕТАДАННЫЕ:
- Session ID: {context['session_id']}
- Working Dir: {context['working_dir']}
- Timestamp: {context['timestamp']}

СЛЕДУЮЩИЕ ШАГИ:
1. Проверить похожие задачи (similar-task-finder)
2. Создать план задачи (TodoWrite)
3. Начать реализацию
"""

    return {
        "content": analysis,
        "importance": 0.85 if priority == 'high' else 0.75,
        "has_code": False,
        "metadata": {
            "task_id": context['task_id'],
            "task_type": context['task_type'],
            "priority": priority,
            "complexity": complexity,
            "keywords": keywords,
            "session_id": context['session_id']
        }
    }

def save_to_memory_ai(analysis_data):
    """Сохранение анализа в Memory-AI MCP"""
    try:
        log_file = CACHE_DIR / "task-analysis-memory.jsonl"

        with open(log_file, 'a', encoding='utf-8', errors='replace') as f:
            # Используем ensure_ascii=True чтобы избежать проблем с суррогатами
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "mcp_tool": "mcp__memory-ai__save_conversation_fact",
                "params": analysis_data
            }, f, ensure_ascii=True)
            f.write('\n')

        # Попытка вызова Memory-AI wrapper
        import subprocess

        wrapper_path = SCRIPT_DIR / "memory_ai_wrapper.py"

        if wrapper_path.exists():
            wrapper_data = json.dumps(analysis_data, ensure_ascii=True)

            result = subprocess.run([
                sys.executable,
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

            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    if response.get('success'):
                        return True
                except json.JSONDecodeError:
                    pass

        return True

    except subprocess.TimeoutExpired:
        return True
    except Exception as e:
        error_log = CACHE_DIR / "hooks-error.log"
        try:
            with open(error_log, 'a', encoding='utf-8', errors='replace') as f:
                f.write(f"{datetime.now().isoformat()} - task-analysis.py ERROR: {str(e)}\n")
        except:
            pass
        return False

def main():
    """Основная функция анализа задачи"""
    try:
        # Читаем hook input из stdin
        hook_data = read_hook_input()
        if not hook_data:
            sys.exit(0)

        # Извлекаем контекст из JSON
        context = extract_context(hook_data)
        if not context:
            sys.exit(0)

        # Анализ задачи
        analysis = format_task_analysis(context)

        # Сохранение в Memory-AI
        save_to_memory_ai(analysis)

        sys.exit(0)

    except Exception:
        # Тихо игнорируем ошибки
        sys.exit(0)

if __name__ == "__main__":
    main()
