#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory-AI Wrapper для хуков
Прямой вызов функций Memory-AI без MCP протокола
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Добавляем путь к модулям Memory-AI
MEMORY_AI_PATH = Path(__file__).parent.parent.parent.parent / "ai-memory-system"
sys.path.insert(0, str(MEMORY_AI_PATH / "services"))

def save_to_memory(content: str, importance: float = 0.5, has_code: bool = False, metadata: dict = None):
    """
    Сохранение факта в Memory-AI систему напрямую

    ПРИМЕЧАНИЕ: В текущей реализации сохраняет только в JSONL.
    Прямое подключение к БД требует наличия PostgreSQL.

    Args:
        content: Содержимое для сохранения
        importance: Важность (0.0-1.0)
        has_code: Содержит ли код
        metadata: Дополнительные метаданные

    Returns:
        bool: Успех операции
    """
    try:
        # УПРОЩЕННАЯ ВЕРСИЯ: Сохранение в JSONL
        # Полная интеграция с БД требует активного PostgreSQL

        # Подготовка данных для JSONL
        if metadata is None:
            metadata = {}

        record = {
            'timestamp': datetime.now().isoformat(),
            'content': content,
            'importance': importance,
            'has_code': has_code,
            'metadata': metadata,
            'source': 'claude_hooks_wrapper'
        }

        # Сохранение в JSONL файл (в корне проекта/cache)
        cache_dir = MEMORY_AI_PATH.parent / "cache"
        cache_dir.mkdir(exist_ok=True)

        jsonl_file = cache_dir / "memory-ai-hooks.jsonl"

        with open(jsonl_file, 'a', encoding='utf-8', errors='replace') as f:
            json.dump(record, f, ensure_ascii=False)
            f.write('\n')

        # TODO: Интеграция с БД при наличии активного PostgreSQL
        # try:
        #     from conversation_storage import ConversationStorage
        #     storage = ConversationStorage(db_config)
        #     storage.save_message(session_id, message_data)
        # except Exception:
        #     pass  # БД недоступна - не критично

        return True

    except Exception as e:
        # Ошибка при сохранении - логируем но не падаем
        error_msg = f"Error saving to Memory-AI: {str(e)}\n"
        sys.stderr.write(error_msg)
        return False


def main():
    """Основная функция - вызывается из командной строки"""
    try:
        # Читаем данные из stdin или переменных окружения
        if len(sys.argv) > 1:
            # JSON из аргумента командной строки
            data = json.loads(sys.argv[1])
        else:
            # JSON из stdin
            data = json.load(sys.stdin)

        # Извлекаем параметры
        content = data.get('content', '')
        importance = float(data.get('importance', 0.5))
        has_code = bool(data.get('has_code', False))
        metadata = data.get('metadata', {})

        # Сохранение
        success = save_to_memory(content, importance, has_code, metadata)

        # Возвращаем результат
        result = {
            'success': success,
            'timestamp': datetime.now().isoformat()
        }

        print(json.dumps(result))
        sys.exit(0 if success else 1)

    except Exception as e:
        error = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error))
        sys.exit(1)


if __name__ == "__main__":
    main()
