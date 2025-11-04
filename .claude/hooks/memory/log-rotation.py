#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Rotation Script
Ротация логов для hooks: архивирование старых логов и очистка больших файлов
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import shutil

# Конфигурация
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CACHE_DIR = PROJECT_ROOT / "cache"
ARCHIVE_DIR = CACHE_DIR / "logs-archive"

# Настройки ротации
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_JSONL_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_ARCHIVES = 5  # Хранить максимум 5 архивов

def ensure_archive_dir():
    """Создание директории для архивов"""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

def get_file_size(file_path):
    """Получение размера файла"""
    try:
        return file_path.stat().st_size
    except:
        return 0

def rotate_log_file(log_path, max_size):
    """Ротация одного лог файла"""
    if not log_path.exists():
        return False

    size = get_file_size(log_path)
    if size < max_size:
        return False

    # Создаем имя архива с датой
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"{log_path.stem}_{timestamp}{log_path.suffix}"
    archive_path = ARCHIVE_DIR / archive_name

    try:
        # Перемещаем файл в архив
        shutil.move(str(log_path), str(archive_path))
        print(f"Rotated: {log_path.name} -> {archive_name} ({size} bytes)")
        return True
    except Exception as e:
        print(f"Error rotating {log_path.name}: {e}", file=sys.stderr)
        return False

def cleanup_old_archives(pattern, max_count):
    """Удаление старых архивов, оставляя только последние max_count"""
    try:
        archives = sorted(ARCHIVE_DIR.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

        if len(archives) > max_count:
            for old_archive in archives[max_count:]:
                try:
                    old_archive.unlink()
                    print(f"Deleted old archive: {old_archive.name}")
                except Exception as e:
                    print(f"Error deleting {old_archive.name}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error cleaning up archives: {e}", file=sys.stderr)

def rotate_all_logs():
    """Ротация всех логов"""
    ensure_archive_dir()

    rotated_count = 0

    # Список файлов для ротации
    log_files = [
        (CACHE_DIR / "hooks-error.log", MAX_LOG_SIZE),
        (CACHE_DIR / "auto-save.log", MAX_LOG_SIZE),
        (CACHE_DIR / "memory-ai-mcp.log", MAX_LOG_SIZE),
        (CACHE_DIR / "auto-save-memory.jsonl", MAX_JSONL_SIZE),
        (CACHE_DIR / "memory-ai-hooks.jsonl", MAX_JSONL_SIZE),
        (CACHE_DIR / "task-analysis-memory.jsonl", MAX_JSONL_SIZE),
    ]

    for log_path, max_size in log_files:
        if rotate_log_file(log_path, max_size):
            rotated_count += 1

    # Очистка старых архивов
    cleanup_old_archives("hooks-error_*.log", MAX_ARCHIVES)
    cleanup_old_archives("auto-save_*.log", MAX_ARCHIVES)
    cleanup_old_archives("auto-save-memory_*.jsonl", MAX_ARCHIVES)
    cleanup_old_archives("memory-ai-hooks_*.jsonl", MAX_ARCHIVES)
    cleanup_old_archives("task-analysis-memory_*.jsonl", MAX_ARCHIVES)

    return rotated_count

def get_logs_status():
    """Получение статуса логов"""
    status = []

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
            size_mb = size / (1024 * 1024)
            status.append({
                "name": log_path.name,
                "size": size,
                "size_mb": f"{size_mb:.2f}",
                "path": str(log_path)
            })

    return status

def main():
    """Основная функция"""
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        # Вывод статуса логов
        print("Log Files Status:")
        print("-" * 60)
        for log in get_logs_status():
            print(f"{log['name']:30} {log['size_mb']:>10} MB")
        print("-" * 60)
    else:
        # Ротация логов
        print("Starting log rotation...")
        rotated = rotate_all_logs()
        print(f"Rotation complete. {rotated} file(s) rotated.")

if __name__ == "__main__":
    main()
