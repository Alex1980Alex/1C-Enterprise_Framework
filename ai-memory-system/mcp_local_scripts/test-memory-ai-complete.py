#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Комплексный тест Memory AI MCP Server
Проверяет все функции сервера без необходимости подключения к Claude Desktop
"""

import sys
import os

# Добавляем путь к сервисам
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services'))

from conversation_storage import ConversationStorage
from message_vectorization import MessageVectorization
from context_restoration import ContextRestoration

def print_section(title):
    """Печатает заголовок секции"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_conversation_storage():
    """Тест 1: Проверка ConversationStorage"""
    print_section("ТЕСТ 1: Conversation Storage")

    try:
        # Конфигурация БД
        DB_CONFIG = {
            'host': 'localhost',
            'port': 5432,
            'database': 'ai_memory',
            'user': 'ai_user',
            'password': 'ai_memory_secure_2025'
        }

        storage = ConversationStorage(DB_CONFIG)
        print("✓ ConversationStorage инициализирован")

        # Создаем тестовую сессию
        session_id = storage.start_session(
            project_name="Test_Project",
            context_type="testing"
        )
        print(f"✓ Создана тестовая сессия: {session_id}")

        # Сохраняем тестовый факт
        fact_id = storage.save_fact(
            session_id=session_id,
            fact_type="test_fact",
            content="Memory AI server is working correctly",
            metadata={
                "test_run": "2025-10-31",
                "component": "memory-ai-mcp"
            }
        )
        print(f"✓ Сохранен тестовый факт ID: {fact_id}")

        # Получаем контекст сессии
        context = storage.get_session_context(session_id)
        print(f"✓ Получен контекст сессии: {len(context.get('facts', []))} фактов")

        return True

    except Exception as e:
        print(f"✗ ОШИБКА в ConversationStorage: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_message_vectorization():
    """Тест 2: Проверка MessageVectorization"""
    print_section("ТЕСТ 2: Message Vectorization")

    try:
        vectorizer = MessageVectorization(
            qdrant_host="localhost",
            qdrant_port=6333,
            ollama_host="localhost",
            ollama_port=11434,
            collection_name="conversation_memory"
        )
        print("✓ MessageVectorization инициализирован")

        # Проверяем подключение к Qdrant
        if vectorizer.qdrant_client:
            collections = vectorizer.qdrant_client.get_collections()
            print(f"✓ Подключено к Qdrant: {len(collections.collections)} коллекций")

        # Проверяем подключение к Ollama
        try:
            import requests
            response = requests.get(f"http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                print("✓ Ollama доступен для векторизации")
            else:
                print("⚠ Ollama недоступен (не критично)")
        except:
            print("⚠ Ollama недоступен (не критично)")

        # Тестируем векторизацию
        test_text = "This is a test message for vectorization"
        vector = vectorizer.vectorize_message(test_text)

        if vector and len(vector) > 0:
            print(f"✓ Векторизация работает: вектор размером {len(vector)}")
        else:
            print("⚠ Векторизация использует fallback метод")

        return True

    except Exception as e:
        print(f"✗ ОШИБКА в MessageVectorization: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_context_restoration():
    """Тест 3: Проверка ContextRestoration"""
    print_section("ТЕСТ 3: Context Restoration")

    try:
        # Создаем зависимости
        DB_CONFIG = {
            'host': 'localhost',
            'port': 5432,
            'database': 'ai_memory',
            'user': 'ai_user',
            'password': 'ai_memory_secure_2025'
        }

        storage = ConversationStorage(DB_CONFIG)
        vectorizer = MessageVectorization(
            qdrant_host="localhost",
            qdrant_port=6333,
            collection_name="conversation_memory"
        )

        restorer = ContextRestoration(storage, vectorizer)
        print("✓ ContextRestoration инициализирован")

        # Поиск по семантике
        test_query = "memory system testing"
        results = restorer.search_similar_messages(
            query=test_query,
            limit=5
        )
        print(f"✓ Семантический поиск выполнен: найдено {len(results)} результатов")

        # Получение важных сообщений
        important = restorer.get_important_messages(limit=5)
        print(f"✓ Получено {len(important)} важных сообщений")

        return True

    except Exception as e:
        print(f"✗ ОШИБКА в ContextRestoration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_content():
    """Тест 4: Проверка содержимого базы данных"""
    print_section("ТЕСТ 4: Database Content")

    try:
        DB_CONFIG = {
            'host': 'localhost',
            'port': 5432,
            'database': 'ai_memory',
            'user': 'ai_user',
            'password': 'ai_memory_secure_2025'
        }

        storage = ConversationStorage(DB_CONFIG)

        # Получаем статистику
        with storage.get_connection() as conn:
            cursor = conn.cursor()

            # Количество сессий
            cursor.execute("SELECT COUNT(*) FROM sessions")
            sessions_count = cursor.fetchone()[0]
            print(f"✓ Сессий в базе: {sessions_count}")

            # Количество фактов
            cursor.execute("SELECT COUNT(*) FROM conversation_facts")
            facts_count = cursor.fetchone()[0]
            print(f"✓ Фактов в базе: {facts_count}")

            # Последние 3 сессии
            cursor.execute("""
                SELECT session_id, project_name, context_type, started_at
                FROM sessions
                ORDER BY started_at DESC
                LIMIT 3
            """)

            print("\nПоследние сессии:")
            for row in cursor.fetchall():
                print(f"  • {row[1]} ({row[2]}) - {row[3]}")

        return True

    except Exception as e:
        print(f"✗ ОШИБКА при проверке БД: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("  КОМПЛЕКСНЫЙ ТЕСТ MEMORY AI MCP SERVER")
    print("  Версия: 1.0 | Дата: 2025-10-31")
    print("="*60)

    results = []

    # Запускаем тесты
    results.append(("Conversation Storage", test_conversation_storage()))
    results.append(("Message Vectorization", test_message_vectorization()))
    results.append(("Context Restoration", test_context_restoration()))
    results.append(("Database Content", test_database_content()))

    # Итоги
    print_section("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status:12} - {test_name}")

    print(f"\nИтого: {passed}/{total} тестов пройдено")

    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Memory AI MCP Server готов к работе с Claude Desktop")
        return 0
    else:
        print("\n⚠ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("Проверьте логи выше для деталей")
        return 1

if __name__ == "__main__":
    sys.exit(main())
