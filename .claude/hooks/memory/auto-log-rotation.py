#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Log Rotation
Автоматическая ротация логов при превышении размера
Срабатывает периодически (не при каждом промпте) для минимального влияния на производительность
"""

import sys
import json
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
MAX_ARCHIVES = 5

# Файл для отслеживания последней проверки
CHECK_COUNTER_FILE = CACHE_DIR / ".rotation-counter"

def should_check_rotation():
    """
    Проверка нужно ли запускать ротацию сейчас
    Ротация срабатывает не каждый раз, а например раз в 10 промптов
    """
    try:
        # Создаем директорию если не существует
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # Читаем счетчик
        if CHECK_COUNTER_FILE.exists():
            try:
                with open(CHECK_COUNTER_FILE, 'r', encoding='utf-8') as f:
                    counter = int(f.read().strip())
            except:
                counter = 0
        else:
            counter = 0

        # Увеличиваем счетчик
        counter += 1

        # Сбрасываем счетчик и возвращаем True каждые 10 раз
        if counter >= 10:
            counter = 0
            should_check = True
        else:
            should_check = False

        # Сохраняем счетчик
        try:
            with open(CHECK_COUNTER_FILE, 'w', encoding='utf-8') as f:
                f.write(str(counter))
        except:
            pass

        return should_check

    except Exception:
        # При ошибке просто не проверяем
        return False

def get_file_size(file_path):
    """Получение размера файла"""
    try:
        return file_path.stat().st_size
    except:
        return 0

def rotate_file(file_path, max_size):
    """Ротация файла если он превышает максимальный размер"""
    if not file_path.exists():
        return False

    size = get_file_size(file_path)
    if size < max_size:
        return False

    # Создаем директорию для архивов
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Создаем имя архива с датой
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    archive_path = ARCHIVE_DIR / archive_name

    try:
        # Перемещаем файл в архив
        shutil.move(str(file_path), str(archive_path))
        return True
    except Exception:
        return False

def cleanup_old_archives(pattern, max_count):
    """Удаление старых архивов"""
    try:
        if not ARCHIVE_DIR.exists():
            return

        archives = sorted(
            ARCHIVE_DIR.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        # Удаляем старые архивы, оставляя только max_count последних
        for old_archive in archives[max_count:]:
            try:
                old_archive.unlink()
            except Exception:
                pass
    except Exception:
        pass

def perform_rotation():
    """Выполнение ротации логов"""
    rotated = []

    # Список файлов для ротации
    files_to_check = [
        (CACHE_DIR / "hooks-error.log", MAX_LOG_SIZE),
        (CACHE_DIR / "auto-save.log", MAX_LOG_SIZE),
        (CACHE_DIR / "memory-ai-mcp.log", MAX_LOG_SIZE),
        (CACHE_DIR / "auto-save-memory.jsonl", MAX_JSONL_SIZE),
        (CACHE_DIR / "memory-ai-hooks.jsonl", MAX_JSONL_SIZE),
        (CACHE_DIR / "task-analysis-memory.jsonl", MAX_JSONL_SIZE),
    ]

    for file_path, max_size in files_to_check:
        if rotate_file(file_path, max_size):
            rotated.append(file_path.name)

    # Очистка старых архивов
    if rotated:
        cleanup_old_archives("hooks-error_*.log", MAX_ARCHIVES)
        cleanup_old_archives("auto-save_*.log", MAX_ARCHIVES)
        cleanup_old_archives("auto-save-memory_*.jsonl", MAX_ARCHIVES)
        cleanup_old_archives("memory-ai-hooks_*.jsonl", MAX_ARCHIVES)
        cleanup_old_archives("task-analysis-memory_*.jsonl", MAX_ARCHIVES)

    return rotated

def main():
    """Основная функция"""
    try:
        # Проверяем нужно ли запускать ротацию (ПЕРЕД чтением stdin)
        should_rotate = should_check_rotation()

        # Читаем stdin (hook должен потребить stdin)
        # Используем простое чтение вместо json.load
        try:
            stdin_data = sys.stdin.read()
        except:
            pass

        # Если не нужна ротация - выходим
        if not should_rotate:
            sys.exit(0)

        # Выполняем ротацию
        rotated = perform_rotation()

        # Если были ротированы файлы, можно залогировать (опционально)
        if rotated:
            log_file = CACHE_DIR / "auto-rotation.log"
            try:
                with open(log_file, 'a', encoding='utf-8', errors='replace') as f:
                    timestamp = datetime.now().isoformat()
                    f.write(f"{timestamp} - Auto-rotated: {', '.join(rotated)}\n")
            except:
                pass

        # ВСЕГДА возвращаем успех
        sys.exit(0)

    except Exception:
        # Любая ошибка - не критична, просто выходим с успехом
        sys.exit(0)

if __name__ == "__main__":
    main()
