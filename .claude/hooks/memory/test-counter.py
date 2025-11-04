#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test counter logic"""

import sys
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent))

# Импортируем функцию из auto-log-rotation
from pathlib import Path

CACHE_DIR = Path(__file__).parent.parent.parent / "cache"
CHECK_COUNTER_FILE = CACHE_DIR / ".rotation-counter"

def should_check_rotation():
    """Проверка нужно ли запускать ротацию сейчас"""
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

    except Exception as e:
        print(f"Error: {e}")
        return False

# Удаляем старый счетчик
CHECK_COUNTER_FILE.unlink(missing_ok=True)

print("Testing should_check_rotation:")
print("-" * 50)
for i in range(12):
    result = should_check_rotation()
    counter_value = CHECK_COUNTER_FILE.read_text() if CHECK_COUNTER_FILE.exists() else "N/A"
    print(f"Call {i+1:2d}: should_rotate={str(result):5s}, counter={counter_value}")

print("-" * 50)
print(f"Final counter value: {CHECK_COUNTER_FILE.read_text() if CHECK_COUNTER_FILE.exists() else 'N/A'}")
