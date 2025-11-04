"""
ContextRestoration Service

Сервис для автоматического восстановления контекста разговоров.
Объединяет ConversationStorage и MessageVectorization для
интеллектуального восстановления релевантной истории.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging

from conversation_storage import ConversationStorage
from message_vectorization import MessageVectorization

logger = logging.getLogger(__name__)


class ContextRestoration:
    """
    Сервис для восстановления контекста разговоров

    Функциональность:
    - Автоматическое восстановление релевантного контекста
    - Комбинирование временного и семантического поиска
    - Генерация context summary для Claude
    - Приоритизация важных сообщений
    """

    def __init__(
        self,
        storage: ConversationStorage,
        vectorizer: MessageVectorization
    ):
        """
        Инициализация сервиса

        Args:
            storage: Экземпляр ConversationStorage
            vectorizer: Экземпляр MessageVectorization
        """
        self.storage = storage
        self.vectorizer = vectorizer
        logger.info("ContextRestoration initialized")

    def get_relevant_context(
        self,
        query: Optional[str] = None,
        project_context: Optional[str] = None,
        session_id: Optional[str] = None,
        max_messages: int = 20,
        include_recent: bool = True,
        include_semantic: bool = True,
        min_importance: float = 0.5
    ) -> Dict[str, Any]:
        """
        Получить релевантный контекст для новой сессии

        Args:
            query: Опциональный запрос для семантического поиска
            project_context: Контекст проекта (например, путь к проекту)
            session_id: ID предыдущей сессии для продолжения
            max_messages: Максимальное количество сообщений в контексте
            include_recent: Включить недавние сообщения
            include_semantic: Включить семантически похожие
            min_importance: Минимальная важность сообщений

        Returns:
            Dict с восстановленным контекстом
        """
        context = {
            "recent_conversations": [],
            "recent_messages": [],
            "semantic_matches": [],
            "important_messages": [],
            "context_summary": "",
            "total_messages": 0
        }

        try:
            # 1. Get recent conversations for the project
            if project_context:
                recent_convs = self.storage.get_recent_conversations(
                    limit=5,
                    project_context=project_context,
                    status='active'
                )
                context["recent_conversations"] = recent_convs
                logger.info(f"Found {len(recent_convs)} recent conversations for {project_context}")

            # 2. Get recent messages (temporal context)
            if include_recent:
                recent_msgs = self.storage.get_important_messages(
                    limit=max_messages // 2,
                    min_score=min_importance,
                    project_context=project_context
                )
                context["recent_messages"] = recent_msgs
                logger.info(f"Found {len(recent_msgs)} recent messages")

            # 3. Get semantically similar messages
            if include_semantic and query:
                semantic_msgs = self.vectorizer.search_similar_messages(
                    query=query,
                    limit=max_messages // 2,
                    min_score=0.6
                )
                context["semantic_matches"] = semantic_msgs
                logger.info(f"Found {len(semantic_msgs)} semantic matches for query")

            # 4. Get important messages
            important_msgs = self.storage.get_important_messages(
                limit=10,
                min_score=0.7,
                project_context=project_context
            )
            context["important_messages"] = important_msgs

            # 5. Build context summary
            context["context_summary"] = self._build_context_summary(context)
            context["total_messages"] = (
                len(context["recent_messages"]) +
                len(context["semantic_matches"]) +
                len(context["important_messages"])
            )

            logger.info(f"Restored context with {context['total_messages']} total messages")
            return context

        except Exception as e:
            logger.error(f"Failed to get relevant context: {e}")
            raise

    def _build_context_summary(self, context: Dict) -> str:
        """
        Построить текстовое резюме контекста

        Args:
            context: Словарь с контекстными данными

        Returns:
            Текстовое резюме для injection в Claude
        """
        summary_parts = []

        # Recent conversations summary
        if context["recent_conversations"]:
            summary_parts.append("=== Recent Conversations ===")
            for conv in context["recent_conversations"][:3]:
                summary_parts.append(
                    f"- Session: {conv['session_id']} "
                    f"({conv['total_messages']} messages, "
                    f"avg importance: {conv.get('avg_importance', 0):.2f})"
                )

        # Important messages summary
        if context["important_messages"]:
            summary_parts.append("\n=== Important Messages ===")
            for msg in context["important_messages"][:5]:
                role_marker = "👤" if msg["role"] == "user" else "🤖"
                summary_parts.append(
                    f"{role_marker} [{msg['importance_score']:.2f}] "
                    f"{msg['content_preview'][:100]}..."
                )

        # Semantic matches summary
        if context["semantic_matches"]:
            summary_parts.append("\n=== Semantically Related ===")
            for match in context["semantic_matches"][:3]:
                summary_parts.append(
                    f"[Score: {match['score']:.2f}] "
                    f"{match['content_preview'][:100]}..."
                )

        # Recent messages summary
        if context["recent_messages"]:
            summary_parts.append("\n=== Recent Activity ===")
            for msg in context["recent_messages"][:5]:
                role = "User" if msg["role"] == "user" else "Assistant"
                summary_parts.append(
                    f"- {role}: {msg['content_preview'][:80]}..."
                )

        return "\n".join(summary_parts)

    def restore_conversation_context(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Восстановить полный контекст конкретного разговора

        Args:
            conversation_id: UUID разговора

        Returns:
            Dict с полным контекстом разговора
        """
        try:
            # Get conversation metadata
            conversation = self.storage.get_conversation(conversation_id)
            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found")
                return {}

            # Get all messages
            messages = self.storage.get_conversation_messages(
                conversation_id,
                limit=None
            )

            # Get vectorized context
            vector_context = self.vectorizer.get_conversation_context(
                conversation_id,
                limit=100
            )

            return {
                "conversation": conversation,
                "messages": messages,
                "message_count": len(messages),
                "vector_count": len(vector_context),
                "session_id": conversation["session_id"],
                "project_context": conversation.get("project_context"),
                "status": conversation["status"]
            }

        except Exception as e:
            logger.error(f"Failed to restore conversation context: {e}")
            raise

    def search_conversation_history(
        self,
        query: str,
        project_context: Optional[str] = None,
        days_back: int = 30,
        limit: int = 50
    ) -> List[Dict]:
        """
        Поиск по истории разговоров

        Args:
            query: Поисковый запрос
            project_context: Фильтр по проекту
            days_back: Количество дней для поиска назад
            limit: Максимальное количество результатов

        Returns:
            List найденных сообщений
        """
        try:
            # Combine full-text search and semantic search
            fts_results = self.storage.search_messages_by_text(
                search_text=query,
                limit=limit // 2,
                project_context=project_context
            )

            semantic_results = self.vectorizer.search_similar_messages(
                query=query,
                limit=limit // 2,
                min_score=0.5
            )

            # Merge and deduplicate
            all_results = fts_results + [
                {
                    "message_id": r["message_id"],
                    "content_preview": r["content_preview"],
                    "score": r["score"],
                    "role": r["role"],
                    "source": "semantic"
                }
                for r in semantic_results
            ]

            # Remove duplicates by message_id
            seen_ids = set()
            unique_results = []
            for result in all_results:
                msg_id = result.get("message_id")
                if msg_id and msg_id not in seen_ids:
                    seen_ids.add(msg_id)
                    unique_results.append(result)

            logger.info(f"Search found {len(unique_results)} unique results for query: {query[:50]}...")
            return unique_results[:limit]

        except Exception as e:
            logger.error(f"Failed to search conversation history: {e}")
            raise

    def restore_context(
        self,
        conversation_id: str,
        query: Optional[str] = None,
        max_messages: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Восстановить контекст для разговора (используется MCP сервером)

        Args:
            conversation_id: UUID разговора или session_id
            query: Опциональный запрос для семантического поиска
            max_messages: Максимальное количество сообщений

        Returns:
            List сообщений с контекстом
        """
        try:
            # Try to get conversation messages
            messages = self.storage.get_conversation_messages(
                conversation_id,
                limit=max_messages
            )

            if not messages:
                logger.warning(f"No messages found for conversation {conversation_id}")
                return []

            # Format messages for MCP response
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg.get("role", "unknown"),
                    "content": msg.get("content", ""),
                    "importance_score": msg.get("importance_score", 0.0),
                    "timestamp": msg.get("created_at", "").isoformat() if hasattr(msg.get("created_at", ""), "isoformat") else str(msg.get("created_at", ""))
                })

            logger.info(f"Restored {len(formatted_messages)} messages for conversation {conversation_id}")
            return formatted_messages

        except Exception as e:
            logger.error(f"Failed to restore context for conversation {conversation_id}: {e}")
            # Return empty list instead of raising to avoid breaking MCP server
            return []

    def get_project_summary(
        self,
        project_context: str,
        include_stats: bool = True
    ) -> Dict[str, Any]:
        """
        Получить сводку по проекту

        Args:
            project_context: Контекст проекта
            include_stats: Включить статистику

        Returns:
            Dict со сводкой по проекту
        """
        try:
            # Get recent conversations
            conversations = self.storage.get_recent_conversations(
                limit=10,
                project_context=project_context,
                status='active'
            )

            # Get important messages
            important = self.storage.get_important_messages(
                limit=20,
                min_score=0.7,
                project_context=project_context
            )

            summary = {
                "project_context": project_context,
                "active_conversations": len(conversations),
                "important_messages": len(important),
                "total_messages": sum(c["total_messages"] for c in conversations)
            }

            if include_stats:
                stats = self.storage.get_stats()
                summary["global_stats"] = stats

            logger.info(f"Generated summary for project: {project_context}")
            return summary

        except Exception as e:
            logger.error(f"Failed to get project summary: {e}")
            raise


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

    # Initialize services
    storage = ConversationStorage(DB_CONFIG)
    vectorizer = MessageVectorization(
        qdrant_host="localhost",
        qdrant_port=6333,
        collection_name="conversation_memory"
    )
    restoration = ContextRestoration(storage, vectorizer)

    # Test context restoration
    print("=== Testing Context Restoration ===\n")

    # Get relevant context
    context = restoration.get_relevant_context(
        query="векторизация и TimescaleDB",
        project_context="1C-Enterprise_Framework",
        max_messages=10
    )

    print(f"Total messages in context: {context['total_messages']}")
    print(f"Recent conversations: {len(context['recent_conversations'])}")
    print(f"Semantic matches: {len(context['semantic_matches'])}")
    print("\n=== Context Summary ===")
    print(context["context_summary"])

    # Search conversation history
    print("\n=== Searching History ===")
    results = restoration.search_conversation_history(
        query="Qdrant embedding",
        limit=5
    )
    print(f"Found {len(results)} results")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['content_preview'][:80]}...")

    # Get project summary
    print("\n=== Project Summary ===")
    summary = restoration.get_project_summary(
        project_context="1C-Enterprise_Framework"
    )
    print(f"Active conversations: {summary['active_conversations']}")
    print(f"Important messages: {summary['important_messages']}")
    print(f"Total messages: {summary['total_messages']}")
