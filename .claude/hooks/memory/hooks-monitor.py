#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hooks Monitor
Мониторинг состояния hooks: проверка логов, ошибок, статистика работы
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Конфигурация
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CACHE_DIR = PROJECT_ROOT / "cache"

def get_file_size(file_path):
    """Получение размера файла"""
    try:
        return file_path.stat().st_size
    except:
        return 0

def format_size(size_bytes):
    """Форматирование размера в человекочитаемый вид"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def read_error_log():
    """Чтение лога ошибок"""
    error_log = CACHE_DIR / "hooks-error.log"
    if not error_log.exists():
        return []

    errors = []
    try:
        with open(error_log, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if line:
                    errors.append(line)
    except Exception as e:
        print(f"Error reading error log: {e}", file=sys.stderr)

    return errors

def count_jsonl_entries(file_path):
    """Подсчет записей в JSONL файле"""
    if not file_path.exists():
        return 0

    count = 0
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for _ in f:
                count += 1
    except Exception as e:
        print(f"Error counting entries in {file_path.name}: {e}", file=sys.stderr)

    return count

def analyze_task_analysis():
    """Анализ task-analysis-memory.jsonl"""
    jsonl_path = CACHE_DIR / "task-analysis-memory.jsonl"
    if not jsonl_path.exists():
        return None

    stats = {
        "total_tasks": 0,
        "task_types": defaultdict(int),
        "priorities": defaultdict(int),
        "complexities": defaultdict(int),
        "latest_task": None
    }

    try:
        with open(jsonl_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    stats["total_tasks"] += 1

                    metadata = entry.get("params", {}).get("metadata", {})
                    stats["task_types"][metadata.get("task_type", "unknown")] += 1
                    stats["priorities"][metadata.get("priority", "unknown")] += 1
                    stats["complexities"][metadata.get("complexity", "unknown")] += 1

                    stats["latest_task"] = {
                        "task_id": metadata.get("task_id"),
                        "task_type": metadata.get("task_type"),
                        "timestamp": entry.get("timestamp")
                    }
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error analyzing task-analysis: {e}", file=sys.stderr)
        return None

    return stats

def analyze_auto_save():
    """Анализ auto-save-memory.jsonl"""
    jsonl_path = CACHE_DIR / "auto-save-memory.jsonl"
    if not jsonl_path.exists():
        return None

    stats = {
        "total_saves": 0,
        "tools": defaultdict(int),
        "activity_types": defaultdict(int),
        "latest_save": None
    }

    try:
        with open(jsonl_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    stats["total_saves"] += 1

                    metadata = entry.get("params", {}).get("metadata", {})
                    tool = metadata.get("tool", "unknown")
                    activity_type = metadata.get("activity_type", "unknown")

                    stats["tools"][tool] += 1
                    stats["activity_types"][activity_type] += 1

                    stats["latest_save"] = {
                        "tool": tool,
                        "activity_type": activity_type,
                        "timestamp": entry.get("timestamp")
                    }
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error analyzing auto-save: {e}", file=sys.stderr)
        return None

    return stats

def print_logs_status():
    """Вывод статуса логов"""
    print("\n" + "=" * 70)
    print("HOOKS MONITORING REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Статус файлов логов
    print("LOG FILES STATUS:")
    print("-" * 70)

    log_files = [
        CACHE_DIR / "hooks-error.log",
        CACHE_DIR / "auto-save.log",
        CACHE_DIR / "memory-ai-mcp.log",
        CACHE_DIR / "auto-save-memory.jsonl",
        CACHE_DIR / "memory-ai-hooks.jsonl",
        CACHE_DIR / "task-analysis-memory.jsonl",
    ]

    for log_path in log_files:
        if log_path.exists():
            size = get_file_size(log_path)
            size_str = format_size(size)

            if log_path.suffix == '.jsonl':
                entries = count_jsonl_entries(log_path)
                print(f"{log_path.name:35} {size_str:>12}  ({entries} entries)")
            else:
                print(f"{log_path.name:35} {size_str:>12}")
        else:
            print(f"{log_path.name:35} {'NOT FOUND':>12}")

    # Ошибки
    print("\n" + "-" * 70)
    print("RECENT ERRORS:")
    print("-" * 70)
    errors = read_error_log()
    if errors:
        for error in errors[-5:]:  # Последние 5 ошибок
            print(f"  {error}")
    else:
        print("  No errors logged")

    # Статистика задач
    print("\n" + "-" * 70)
    print("TASK ANALYSIS STATISTICS:")
    print("-" * 70)
    task_stats = analyze_task_analysis()
    if task_stats:
        print(f"Total tasks analyzed: {task_stats['total_tasks']}")
        print(f"\nTask types:")
        for task_type, count in sorted(task_stats['task_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {task_type:20} {count:>5}")
        print(f"\nPriorities:")
        for priority, count in sorted(task_stats['priorities'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {priority:20} {count:>5}")
        print(f"\nComplexities:")
        for complexity, count in sorted(task_stats['complexities'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {complexity:20} {count:>5}")
        if task_stats['latest_task']:
            print(f"\nLatest task:")
            print(f"  ID: {task_stats['latest_task']['task_id']}")
            print(f"  Type: {task_stats['latest_task']['task_type']}")
            print(f"  Time: {task_stats['latest_task']['timestamp']}")
    else:
        print("  No task analysis data")

    # Статистика автосохранения
    print("\n" + "-" * 70)
    print("AUTO-SAVE STATISTICS:")
    print("-" * 70)
    auto_save_stats = analyze_auto_save()
    if auto_save_stats:
        print(f"Total auto-saves: {auto_save_stats['total_saves']}")
        print(f"\nTop tools:")
        top_tools = sorted(auto_save_stats['tools'].items(), key=lambda x: x[1], reverse=True)[:5]
        for tool, count in top_tools:
            print(f"  {tool:30} {count:>5}")
        print(f"\nActivity types:")
        for activity, count in sorted(auto_save_stats['activity_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {activity:30} {count:>5}")
        if auto_save_stats['latest_save']:
            print(f"\nLatest save:")
            print(f"  Tool: {auto_save_stats['latest_save']['tool']}")
            print(f"  Type: {auto_save_stats['latest_save']['activity_type']}")
            print(f"  Time: {auto_save_stats['latest_save']['timestamp']}")
    else:
        print("  No auto-save data")

    print("\n" + "=" * 70)

def check_health():
    """Проверка здоровья hooks"""
    issues = []

    # Проверка размеров файлов
    log_files = {
        CACHE_DIR / "hooks-error.log": 5 * 1024 * 1024,  # 5 MB
        CACHE_DIR / "auto-save-memory.jsonl": 10 * 1024 * 1024,  # 10 MB
        CACHE_DIR / "memory-ai-hooks.jsonl": 10 * 1024 * 1024,  # 10 MB
        CACHE_DIR / "task-analysis-memory.jsonl": 10 * 1024 * 1024,  # 10 MB
    }

    for log_path, max_size in log_files.items():
        if log_path.exists():
            size = get_file_size(log_path)
            if size > max_size:
                issues.append(f"LARGE FILE: {log_path.name} ({format_size(size)}, recommend rotation)")

    # Проверка ошибок
    errors = read_error_log()
    if len(errors) > 50:
        issues.append(f"HIGH ERROR COUNT: {len(errors)} errors in log (consider investigating)")

    # Вывод результатов
    print("\nHEALTH CHECK:")
    print("-" * 70)
    if issues:
        for issue in issues:
            print(f"  [!] {issue}")
    else:
        print("  [OK] All checks passed")

def main():
    """Основная функция"""
    if len(sys.argv) > 1 and sys.argv[1] == "health":
        check_health()
    else:
        print_logs_status()
        check_health()

if __name__ == "__main__":
    main()
