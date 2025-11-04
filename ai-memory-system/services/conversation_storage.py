"""
ConversationStorage Service

Сервис для сохранения и загрузки разговоров в TimescaleDB.
Обеспечивает persistence памяти между сессиями Claude.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Dict, Optional, Any
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class ConversationStorage:
    """
    Сервис для работы с долгосрочной памятью разговоров

    Функциональность:
    - Создание новых разговоров
    - Добавление сообщений в разговоры
    - Загрузка истории разговоров
    - Поиск по контексту проекта
    - Закрытие разговоров
    """

    def __init__(self, db_config: Dict[str, Any]):
        """
        Инициализация сервиса

        Args:
            db_config: Конфигурация базы данных
                - host: Хост БД
                - port: Порт БД
                - database: Имя базы данных
                - user: Пользователь
                - password: Пароль
        """
        self.db_config = db_config
        self._test_connection()
        logger.info("ConversationStorage initialized")

    def _test_connection(self):
        """Тест подключения к БД"""
        try:
            conn = self._get_connection()
            conn.close()
            logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def _get_connection(self):
        """Получить подключение к БД"""
        return psycopg2.connect(**self.db_config)

    def create_conversation(
        self,
        session_id: str,
        project_context: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> UUID:
        """
        Создать новый разговор

        Args:
            session_id: Уникальный ID сессии
            project_context: Контекст проекта (например, путь к проекту)
            user_id: ID пользователя
            metadata: Дополнительные метаданные

        Returns:
            UUID созданного разговора
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            query = """
                INSERT INTO conversations (session_id, project_context, user_id, metadata)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """

            cursor.execute(query, (
                session_id,
                project_context,
                user_id,
                psycopg2.extras.Json(metadata or {})
            ))

            conversation_id = cursor.fetchone()[0]
            conn.commit()

            logger.info(f"Created conversation {conversation_id} for session {session_id}")
            return conversation_id

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create conversation: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def add_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        importance_score: float = 0.0,
        has_code: bool = False,
        has_entities: bool = False,
        tokens_count: Optional[int] = None,
        metadata: Optional[Dict] = None,
        vector_id: Optional[str] = None
    ) -> int:
        """
        Добавить сообщение в разговор

        Args:
            conversation_id: UUID разговора
            role: Роль (user, assistant, system, tool)
            content: Текст сообщения
            importance_score: Оценка важности (0.0-1.0)
            has_code: Содержит ли код
            has_entities: Содержит ли сущности
            tokens_count: Количество токенов
            metadata: Дополнительные метаданные
            vector_id: ID вектора в Qdrant

        Returns:
            ID созданного сообщения
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            query = """
                INSERT INTO messages (
                    conversation_id, role, content, importance_score,
                    has_code, has_entities, tokens_count, metadata, vector_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """

            cursor.execute(query, (
                str(conversation_id),
                role,
                content,
                importance_score,
                has_code,
                has_entities,
                tokens_count,
                psycopg2.extras.Json(metadata or {}),
                vector_id
            ))

            message_id = cursor.fetchone()[0]
            conn.commit()

            logger.debug(f"Added {role} message {message_id} to conversation {conversation_id}")
            return message_id

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to add message: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_conversation(self, conversation_id: UUID) -> Optional[Dict]:
        """
        Получить разговор по ID

        Args:
            conversation_id: UUID разговора

        Returns:
            Dict с данными разговора или None
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT * FROM conversations
                WHERE id = %s
            """

            cursor.execute(query, (str(conversation_id),))
            result = cursor.fetchone()

            return dict(result) if result else None

        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_conversation_messages(
        self,
        conversation_id: UUID,
        limit: Optional[int] = None,
        min_importance: float = 0.0
    ) -> List[Dict]:
        """
        Получить сообщения разговора

        Args:
            conversation_id: UUID разговора
            limit: Максимальное количество сообщений
            min_importance: Минимальная важность сообщений

        Returns:
            List сообщений
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT * FROM messages
                WHERE conversation_id = %s
                AND importance_score >= %s
                ORDER BY timestamp DESC
            """

            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query, (str(conversation_id), min_importance))
            results = cursor.fetchall()

            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_recent_conversations(
        self,
        limit: int = 10,
        project_context: Optional[str] = None,
        status: str = 'active'
    ) -> List[Dict]:
        """
        Получить недавние разговоры

        Args:
            limit: Максимальное количество разговоров
            project_context: Фильтр по контексту проекта
            status: Фильтр по статусу (active/closed/archived)

        Returns:
            List разговоров с метриками
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT * FROM v_recent_conversations
                WHERE status = %s
            """
            params = [status]

            if project_context:
                query += " AND project_context = %s"
                params.append(project_context)

            query += f" ORDER BY started_at DESC LIMIT {limit}"

            cursor.execute(query, params)
            results = cursor.fetchall()

            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Failed to get recent conversations: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_important_messages(
        self,
        limit: int = 50,
        min_score: float = 0.7,
        project_context: Optional[str] = None
    ) -> List[Dict]:
        """
        Получить важные сообщения

        Args:
            limit: Максимальное количество сообщений
            min_score: Минимальная оценка важности
            project_context: Фильтр по контексту проекта

        Returns:
            List важных сообщений
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT * FROM v_important_messages
                WHERE importance_score >= %s
            """
            params = [min_score]

            if project_context:
                query += " AND project_context = %s"
                params.append(project_context)

            query += f" ORDER BY importance_score DESC LIMIT {limit}"

            cursor.execute(query, params)
            results = cursor.fetchall()

            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Failed to get important messages: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def close_conversation(self, conversation_id: UUID):
        """
        Закрыть разговор

        Args:
            conversation_id: UUID разговора
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            query = """
                UPDATE conversations
                SET status = 'closed', ended_at = NOW()
                WHERE id = %s
            """

            cursor.execute(query, (str(conversation_id),))
            conn.commit()

            logger.info(f"Closed conversation {conversation_id}")

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to close conversation: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def search_messages_by_text(
        self,
        search_text: str,
        limit: int = 20,
        project_context: Optional[str] = None
    ) -> List[Dict]:
        """
        Полнотекстовый поиск по сообщениям

        Args:
            search_text: Текст для поиска
            limit: Максимальное количество результатов
            project_context: Фильтр по контексту проекта

        Returns:
            List найденных сообщений
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT
                    m.*,
                    c.session_id,
                    c.project_context,
                    ts_rank(to_tsvector('russian', m.content), query) as rank
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                CROSS JOIN plainto_tsquery('russian', %s) query
                WHERE to_tsvector('russian', m.content) @@ query
            """
            params = [search_text]

            if project_context:
                query += " AND c.project_context = %s"
                params.append(project_context)

            query += f" ORDER BY rank DESC LIMIT {limit}"

            cursor.execute(query, params)
            results = cursor.fetchall()

            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Failed to search messages: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_stats(self) -> Dict:
        """
        Получить общую статистику

        Returns:
            Dict со статистикой
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT
                    (SELECT COUNT(*) FROM conversations) as total_conversations,
                    (SELECT COUNT(*) FROM conversations WHERE status = 'active') as active_conversations,
                    (SELECT COUNT(*) FROM messages) as total_messages,
                    (SELECT AVG(total_messages) FROM conversations) as avg_messages_per_conversation,
                    (SELECT AVG(importance_score) FROM messages) as avg_importance_score
            """

            cursor.execute(query)
            result = cursor.fetchone()

            return dict(result) if result else {}

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise
        finally:
            cursor.close()
            conn.close()


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Database configuration
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'ai_memory',
        'user': 'ai_user',
        'password': 'ai_memory_secure_2025'
    }

    # Initialize storage
    storage = ConversationStorage(DB_CONFIG)

    # Create conversation
    conv_id = storage.create_conversation(
        session_id="test_session_002",
        project_context="1C-Enterprise_Framework",
        metadata={"environment": "development"}
    )
    print(f"Created conversation: {conv_id}")

    # Add messages
    msg1_id = storage.add_message(
        conversation_id=conv_id,
        role="user",
        content="Как работает векторизация в Qdrant?",
        importance_score=0.8
    )
    print(f"Added user message: {msg1_id}")

    msg2_id = storage.add_message(
        conversation_id=conv_id,
        role="assistant",
        content="Векторизация в Qdrant работает через создание embedding vectors...",
        importance_score=0.7,
        has_code=True
    )
    print(f"Added assistant message: {msg2_id}")

    # Get conversation
    conv = storage.get_conversation(conv_id)
    print(f"Conversation: {conv}")

    # Get messages
    messages = storage.get_conversation_messages(conv_id)
    print(f"Messages: {len(messages)}")

    # Get stats
    stats = storage.get_stats()
    print(f"Stats: {stats}")

    # Get recent conversations
    recent = storage.get_recent_conversations(limit=5)
    print(f"Recent conversations: {len(recent)}")

    # Search messages
    results = storage.search_messages_by_text("векторизация")
    print(f"Search results: {len(results)}")
