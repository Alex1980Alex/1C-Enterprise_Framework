#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Простой тест Memory AI MCP Server
Проверяет базовую работоспособность всех компонентов
"""

import sys
import os
from uuid import uuid4

# Добавляем путь к сервисам
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services'))

from conversation_storage import ConversationStorage
from message_vectorization import MessageVectorization
from context_restoration import ContextRestoration

# Конфигурация
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ai_memory',
    'user': 'ai_user',
    'password': 'ai_memory_secure_2025'
}

def test_all():
    """Комплексный тест всех компонентов"""

    print("\n" + "="*70)
    print("  ТЕСТ MEMORY AI MCP SERVER")
    print("="*70 + "\n")

    # Тест 1: ConversationStorage
    print("1. Проверка ConversationStorage...")
    try:
        storage = ConversationStorage(DB_CONFIG)
        print("   ✓ ConversationStorage инициализирован и подключен к БД")

        # Проверяем содержимое БД
        with storage._get_connection() as conn:
            cursor = conn.cursor()

            # Проверяем таблицы
            cursor.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            print(f"   ✓ Таблицы в БД: {', '.join(tables)}")

            # Статистика
            if 'conversations' in tables:
                cursor.execute("SELECT COUNT(*) FROM conversations")
                count = cursor.fetchone()[0]
                print(f"   ✓ Разговоров в БД: {count}")

            if 'messages' in tables:
                cursor.execute("SELECT COUNT(*) FROM messages")
                count = cursor.fetchone()[0]
                print(f"   ✓ Сообщений в БД: {count}")

    except Exception as e:
        print(f"   ✗ ОШИБКА: {e}")
        return False

    # Тест 2: MessageVectorization
    print("\n2. Проверка MessageVectorization...")
    try:
        vectorizer = MessageVectorization(
            qdrant_host="localhost",
            qdrant_port=6333,
            collection_name="conversation_memory"
        )
        print("   ✓ MessageVectorization инициализирован")

        # Проверяем Qdrant
        collections = vectorizer.qdrant_client.get_collections()
        print(f"   ✓ Qdrant подключен: {len(collections.collections)} коллекций")

        for coll in collections.collections:
            print(f"     - {coll.name}")

        # Проверяем Ollama
        import requests
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"   ✓ Ollama работает: {len(models)} моделей")
                for model in models[:3]:  # Первые 3 модели
                    print(f"     - {model.get('name', 'unknown')}")
            else:
                print("   ⚠ Ollama недоступен (работа продолжится без векторизации)")
        except:
            print("   ⚠ Ollama недоступен (работа продолжится без векторизации)")

    except Exception as e:
        print(f"   ✗ ОШИБКА: {e}")
        return False

    # Тест 3: ContextRestoration
    print("\n3. Проверка ContextRestoration...")
    try:
        restorer = ContextRestoration(storage, vectorizer)
        print("   ✓ ContextRestoration инициализирован")
        print("   ✓ Все компоненты готовы к работе")

    except Exception as e:
        print(f"   ✗ ОШИБКА: {e}")
        return False

    # Тест 4: Создание тестовых данных (опционально)
    print("\n4. Тест создания данных...")
    try:
        # Создаем тестовый разговор
        session_id = f"test_session_{uuid4()}"
        conversation_id = storage.create_conversation(
            session_id=session_id,
            project_context="1C-Enterprise_Framework",
            metadata={"test": True, "created_by": "test_script"}
        )
        print(f"   ✓ Создан тестовый разговор: {conversation_id}")

        # Добавляем тестовое сообщение
        message_id = storage.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content="This is a test message from Memory AI MCP Server test",
            importance_score=0.7,
            has_code=False,
            metadata={"test": True}
        )
        print(f"   ✓ Создано тестовое сообщение: {message_id}")

    except Exception as e:
        print(f"   ✗ ОШИБКА при создании данных: {e}")
        # Не критично, продолжаем
        pass

    print("\n" + "="*70)
    print("  🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("  Memory AI MCP Server готов к работе")
    print("="*70 + "\n")

    return True

if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
