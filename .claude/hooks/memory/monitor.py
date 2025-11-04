#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hooks Monitoring Dashboard
Дашборд для мониторинга активности хуков
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

# Конфигурация путей
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.resolve()
CACHE_DIR = PROJECT_ROOT / "cache"

def read_jsonl(filepath):
    """Чтение JSONL файла"""
    records = []
    if not filepath.exists():
        return records

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

    return records

def analyze_task_analysis():
    """Анализ данных task-analysis-memory.jsonl"""
    filepath = CACHE_DIR / "task-analysis-memory.jsonl"
    records = read_jsonl(filepath)

    if not records:
        return None

    stats = {
        "total_tasks": len(records),
        "by_type": Counter(),
        "by_priority": Counter(),
        "by_complexity": Counter(),
        "recent_tasks": []
    }

    for record in records:
        params = record.get("params", {})
        metadata = params.get("metadata", {})

        # Подсчет по типам
        task_type = metadata.get("task_type", "unknown")
        stats["by_type"][task_type] += 1

        # Подсчет по приоритетам
        priority = metadata.get("priority", "unknown")
        stats["by_priority"][priority] += 1

        # Подсчет по сложности
        complexity = metadata.get("complexity", "unknown")
        stats["by_complexity"][complexity] += 1

        # Последние задачи (первые 5)
        if len(stats["recent_tasks"]) < 5:
            stats["recent_tasks"].append({
                "timestamp": record.get("timestamp", ""),
                "task_id": metadata.get("task_id", "unknown"),
                "type": task_type,
                "priority": priority,
                "complexity": complexity
            })

    return stats

def analyze_auto_save():
    """Анализ данных auto-save-memory.jsonl"""
    filepath = CACHE_DIR / "auto-save-memory.jsonl"
    records = read_jsonl(filepath)

    if not records:
        return None

    stats = {
        "total_saves": len(records),
        "by_tool": Counter(),
        "by_activity_type": Counter(),
        "recent_saves": []
    }

    for record in records:
        params = record.get("params", {})
        metadata = params.get("metadata", {})

        # Подсчет по инструментам
        tool = metadata.get("tool", "unknown")
        stats["by_tool"][tool] += 1

        # Подсчет по типу активности
        activity_type = metadata.get("activity_type", "unknown")
        if activity_type != "unknown":
            stats["by_activity_type"][activity_type] += 1

        # Последние сохранения (первые 10)
        if len(stats["recent_saves"]) < 10:
            content = params.get("content", "")
            # Берем первые 100 символов контента
            content_preview = content[:100] + "..." if len(content) > 100 else content

            stats["recent_saves"].append({
                "timestamp": record.get("timestamp", ""),
                "tool": tool,
                "activity_type": activity_type,
                "importance": params.get("importance", 0),
                "preview": content_preview
            })

    return stats

def analyze_memory_ai_hooks():
    """Анализ данных memory-ai-hooks.jsonl"""
    filepath = CACHE_DIR / "memory-ai-hooks.jsonl"
    records = read_jsonl(filepath)

    if not records:
        return None

    stats = {
        "total_records": len(records),
        "by_source": Counter(),
        "avg_importance": 0,
        "with_code": 0,
        "recent_records": []
    }

    total_importance = 0

    for record in records:
        # Источник
        source = record.get("source", "unknown")
        stats["by_source"][source] += 1

        # Важность
        importance = record.get("importance", 0)
        total_importance += importance

        # С кодом
        if record.get("has_code", False):
            stats["with_code"] += 1

        # Последние записи
        if len(stats["recent_records"]) < 5:
            content = record.get("content", "")
            content_preview = content[:80] + "..." if len(content) > 80 else content

            stats["recent_records"].append({
                "timestamp": record.get("timestamp", ""),
                "source": source,
                "importance": importance,
                "has_code": record.get("has_code", False),
                "preview": content_preview
            })

    if stats["total_records"] > 0:
        stats["avg_importance"] = round(total_importance / stats["total_records"], 2)

    return stats

def print_separator(char="=", length=80):
    """Печать разделителя"""
    print(char * length)

def print_section_header(title):
    """Печать заголовка секции"""
    print_separator()
    print(f"  {title}")
    print_separator()
    print()

def format_timestamp(timestamp_str):
    """Форматирование timestamp для вывода"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str

def main():
    """Основная функция дашборда"""
    print()
    print_separator("=")
    print("  HOOKS MONITORING DASHBOARD")
    print(f"  Проект: {PROJECT_ROOT.name}")
    print(f"  Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator("=")
    print()

    # 1. Анализ задач
    task_stats = analyze_task_analysis()
    if task_stats:
        print_section_header("[ЗАДАЧИ] АНАЛИЗ ЗАДАЧ")
        print(f"Всего задач проанализировано: {task_stats['total_tasks']}")
        print()

        print("По типам задач:")
        for task_type, count in task_stats['by_type'].most_common():
            print(f"  • {task_type}: {count}")
        print()

        print("По приоритетам:")
        for priority, count in task_stats['by_priority'].most_common():
            print(f"  • {priority}: {count}")
        print()

        print("По сложности:")
        for complexity, count in task_stats['by_complexity'].most_common():
            print(f"  • {complexity}: {count}")
        print()

        if task_stats['recent_tasks']:
            print("Последние задачи:")
            for task in task_stats['recent_tasks']:
                print(f"  [{format_timestamp(task['timestamp'])}] {task['task_id']}")
                print(f"    Тип: {task['type']} | Приоритет: {task['priority']} | Сложность: {task['complexity']}")
            print()
    else:
        print_section_header("[ЗАДАЧИ] АНАЛИЗ ЗАДАЧ")
        print("Нет данных по анализу задач")
        print()

    # 2. Анализ автосохранения
    auto_save_stats = analyze_auto_save()
    if auto_save_stats:
        print_section_header("[AUTO-SAVE] АВТОСОХРАНЕНИЕ ИНСТРУМЕНТОВ")
        print(f"Всего сохранений: {auto_save_stats['total_saves']}")
        print()

        print("Топ-10 инструментов:")
        for tool, count in auto_save_stats['by_tool'].most_common(10):
            print(f"  • {tool}: {count}")
        print()

        if auto_save_stats['by_activity_type']:
            print("По типам активности:")
            for activity, count in auto_save_stats['by_activity_type'].most_common():
                print(f"  • {activity}: {count}")
            print()

        if auto_save_stats['recent_saves']:
            print("Последние сохранения:")
            for save in auto_save_stats['recent_saves'][:5]:
                print(f"  [{format_timestamp(save['timestamp'])}] {save['tool']}")
                print(f"    Важность: {save['importance']} | Тип: {save['activity_type']}")
                print(f"    {save['preview']}")
                print()
    else:
        print_section_header("[AUTO-SAVE] АВТОСОХРАНЕНИЕ ИНСТРУМЕНТОВ")
        print("Нет данных по автосохранению")
        print()

    # 3. Анализ Memory-AI хуков
    memory_stats = analyze_memory_ai_hooks()
    if memory_stats:
        print_section_header("[MEMORY-AI] ИНТЕГРАЦИЯ")
        print(f"Всего записей: {memory_stats['total_records']}")
        print(f"Средняя важность: {memory_stats['avg_importance']}")
        print(f"Записей с кодом: {memory_stats['with_code']}")
        print()

        print("По источникам:")
        for source, count in memory_stats['by_source'].most_common():
            print(f"  • {source}: {count}")
        print()

        if memory_stats['recent_records']:
            print("Последние записи:")
            for rec in memory_stats['recent_records']:
                code_marker = "[CODE]" if rec['has_code'] else "[TEXT]"
                print(f"  {code_marker} [{format_timestamp(rec['timestamp'])}] Важность: {rec['importance']}")
                print(f"    {rec['preview']}")
                print()
    else:
        print_section_header("[MEMORY-AI] ИНТЕГРАЦИЯ")
        print("Нет данных по Memory-AI")
        print()

    # 4. Общая статистика
    print_section_header("[STATS] ОБЩАЯ СТАТИСТИКА")

    total_records = 0
    if task_stats:
        total_records += task_stats['total_tasks']
    if auto_save_stats:
        total_records += auto_save_stats['total_saves']
    if memory_stats:
        total_records += memory_stats['total_records']

    print(f"Всего записей во всех системах: {total_records}")
    print()

    print("Активные JSONL файлы:")
    for jsonl_file in CACHE_DIR.glob("*.jsonl"):
        size = jsonl_file.stat().st_size
        size_kb = round(size / 1024, 2)
        print(f"  • {jsonl_file.name}: {size_kb} KB")

    print()
    print_separator("=")
    print()

if __name__ == "__main__":
    main()
