#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test auto-log-rotation.py by calling it multiple times"""

import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent / "auto-log-rotation.py"
COUNTER_FILE = Path(__file__).parent.parent.parent / "cache" / ".rotation-counter"

# Удаляем старый счетчик
COUNTER_FILE.unlink(missing_ok=True)

print("Testing auto-log-rotation.py with multiple calls:")
print("-" * 60)

for i in range(1, 13):
    # Вызываем скрипт с данными через stdin
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            input='{"test": "data"}\n',
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # Читаем значение счетчика
        if COUNTER_FILE.exists():
            counter_value = COUNTER_FILE.read_text().strip()
        else:
            counter_value = "N/A"

        status = "[OK]" if result.returncode == 0 else "[FAIL]"
        print(f"Call {i:2d}: {status} counter={counter_value}")

        if result.stdout:
            print(f"         stdout: {result.stdout.strip()}")
        if result.stderr:
            print(f"         stderr: {result.stderr.strip()}")

    except Exception as e:
        print(f"Call {i:2d}: ERROR - {e}")

print("-" * 60)
print(f"Final counter value: {COUNTER_FILE.read_text() if COUNTER_FILE.exists() else 'N/A'}")

# Проверяем есть ли лог ротации
rotation_log = Path(__file__).parent.parent.parent / "cache" / "auto-rotation.log"
if rotation_log.exists():
    print("\nAuto-rotation log:")
    print(rotation_log.read_text())
