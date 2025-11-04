"""
MessageVectorization Service

Сервис для векторизации сообщений и семантического поиска по истории разговоров.
Интегрируется с Qdrant и Ollama для создания и хранения embeddings.
"""

import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Optional, Any
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class MessageVectorization:
    """
    Сервис для векторизации сообщений разговоров

    Функциональность:
    - Создание embeddings через Ollama
    - Сохранение векторов в Qdrant
    - Семантический поиск по истории
    - Batch processing для оптимизации
    """

    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        ollama_host: str = "localhost",
        ollama_port: int = 11434,
        collection_name: str = "conversation_memory",
        embedding_model: str = "nomic-embed-text"
    ):
        """
        Инициализация сервиса

        Args:
            qdrant_host: Хост Qdrant
            qdrant_port: Порт Qdrant
            ollama_host: Хост Ollama
            ollama_port: Порт Ollama
            collection_name: Имя коллекции в Qdrant
            embedding_model: Модель для создания embeddings
        """
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.ollama_url = f"http://{ollama_host}:{ollama_port}/api/embeddings"
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.vector_size = 768  # nomic-embed-text dimension

        self._ensure_collection_exists()
        logger.info(f"MessageVectorization initialized with collection '{collection_name}'")

    def _ensure_collection_exists(self):
        """Создать коллекцию если не существует"""
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection '{self.collection_name}'")
            else:
                logger.info(f"Collection '{self.collection_name}' already exists")

        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {e}")
            raise

    def create_embedding(self, text: str) -> List[float]:
        """
        Создать embedding для текста

        Args:
            text: Текст для векторизации

        Returns:
            List embedding вектора (768 размерность)
        """
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.embedding_model,
                    "prompt": text
                },
                timeout=30
            )
            response.raise_for_status()
            embedding = response.json()["embedding"]

            logger.debug(f"Created embedding for text (length: {len(text)})")
            return embedding

        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            raise

    def vectorize_message(
        self,
        message_id: int,
        message_timestamp: str,
        conversation_id: str,
        role: str,
        content: str,
        importance_score: float = 0.0,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Векторизовать сообщение и сохранить в Qdrant

        Args:
            message_id: ID сообщения в TimescaleDB
            message_timestamp: Timestamp сообщения
            conversation_id: UUID разговора
            role: Роль (user, assistant, system, tool)
            content: Текст сообщения
            importance_score: Оценка важности
            metadata: Дополнительные метаданные

        Returns:
            Vector ID в Qdrant
        """
        try:
            # Create embedding
            embedding = self.create_embedding(content)

            # Generate vector ID
            vector_id = str(uuid4())

            # Prepare payload
            payload = {
                "message_id": message_id,
                "message_timestamp": message_timestamp,
                "conversation_id": conversation_id,
                "role": role,
                "content_preview": content[:500],  # First 500 chars
                "importance_score": importance_score,
                "metadata": metadata or {}
            }

            # Store in Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=vector_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )

            logger.info(f"Vectorized message {message_id} as {vector_id}")
            return vector_id

        except Exception as e:
            logger.error(f"Failed to vectorize message: {e}")
            raise

    def vectorize_messages_batch(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Векторизовать несколько сообщений batch-ом

        Args:
            messages: List сообщений для векторизации
                Каждое сообщение должно содержать:
                - message_id, message_timestamp, conversation_id
                - role, content, importance_score, metadata

        Returns:
            List vector IDs
        """
        vector_ids = []

        for msg in messages:
            try:
                vector_id = self.vectorize_message(
                    message_id=msg["message_id"],
                    message_timestamp=msg["message_timestamp"],
                    conversation_id=msg["conversation_id"],
                    role=msg["role"],
                    content=msg["content"],
                    importance_score=msg.get("importance_score", 0.0),
                    metadata=msg.get("metadata")
                )
                vector_ids.append(vector_id)

            except Exception as e:
                logger.error(f"Failed to vectorize message {msg.get('message_id')}: {e}")
                vector_ids.append(None)

        logger.info(f"Vectorized {len(vector_ids)} messages in batch")
        return vector_ids

    def search_similar_messages(
        self,
        query: str,
        limit: int = 10,
        conversation_id: Optional[str] = None,
        min_score: float = 0.0,
        role_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Семантический поиск похожих сообщений

        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов
            conversation_id: Фильтр по разговору (опционально)
            min_score: Минимальный score similarity
            role_filter: Фильтр по роли (user/assistant)

        Returns:
            List найденных сообщений с scores
        """
        try:
            # Create query embedding
            query_embedding = self.create_embedding(query)

            # Build filter
            filter_conditions = []

            if conversation_id:
                filter_conditions.append(
                    FieldCondition(
                        key="conversation_id",
                        match=MatchValue(value=conversation_id)
                    )
                )

            if role_filter:
                filter_conditions.append(
                    FieldCondition(
                        key="role",
                        match=MatchValue(value=role_filter)
                    )
                )

            search_filter = Filter(must=filter_conditions) if filter_conditions else None

            # Search in Qdrant
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit,
                score_threshold=min_score
            )

            # Format results
            results = []
            for scored_point in search_result:
                result = {
                    "vector_id": scored_point.id,
                    "score": scored_point.score,
                    "message_id": scored_point.payload.get("message_id"),
                    "conversation_id": scored_point.payload.get("conversation_id"),
                    "role": scored_point.payload.get("role"),
                    "content_preview": scored_point.payload.get("content_preview"),
                    "importance_score": scored_point.payload.get("importance_score"),
                    "metadata": scored_point.payload.get("metadata")
                }
                results.append(result)

            logger.info(f"Found {len(results)} similar messages for query: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"Failed to search similar messages: {e}")
            raise

    def get_conversation_context(
        self,
        conversation_id: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Получить все векторизованные сообщения разговора

        Args:
            conversation_id: UUID разговора
            limit: Максимальное количество сообщений

        Returns:
            List сообщений разговора
        """
        try:
            # Search with filter
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="conversation_id",
                        match=MatchValue(value=conversation_id)
                    )
                ]
            )

            # Get all points (using scroll)
            points = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                scroll_filter=search_filter,
                limit=limit
            )[0]  # Returns (points, next_page_offset)

            # Format results
            results = []
            for point in points:
                result = {
                    "vector_id": point.id,
                    "message_id": point.payload.get("message_id"),
                    "role": point.payload.get("role"),
                    "content_preview": point.payload.get("content_preview"),
                    "importance_score": point.payload.get("importance_score")
                }
                results.append(result)

            logger.info(f"Retrieved {len(results)} messages for conversation {conversation_id}")
            return results

        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            raise

    def delete_message_vector(self, vector_id: str):
        """
        Удалить вектор сообщения

        Args:
            vector_id: ID вектора в Qdrant
        """
        try:
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=[vector_id]
            )
            logger.info(f"Deleted vector {vector_id}")

        except Exception as e:
            logger.error(f"Failed to delete vector: {e}")
            raise

    def get_collection_stats(self) -> Dict:
        """
        Получить статистику коллекции

        Returns:
            Dict со статистикой
        """
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)

            return {
                "collection_name": self.collection_name,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "indexed": collection_info.status == "green",
                "vector_size": self.vector_size,
                "distance_metric": "cosine"
            }

        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            raise


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Initialize vectorization service
    vectorizer = MessageVectorization(
        qdrant_host="localhost",
        qdrant_port=6333,
        collection_name="conversation_memory"
    )

    # Test message vectorization
    vector_id = vectorizer.vectorize_message(
        message_id=1,
        message_timestamp="2025-10-31T00:00:00Z",
        conversation_id="test-conv-001",
        role="user",
        content="Как работает векторизация в Qdrant для долгосрочной памяти Claude?",
        importance_score=0.9
    )
    print(f"Created vector: {vector_id}")

    # Test batch vectorization
    messages = [
        {
            "message_id": 2,
            "message_timestamp": "2025-10-31T00:01:00Z",
            "conversation_id": "test-conv-001",
            "role": "assistant",
            "content": "Векторизация в Qdrant работает через создание embeddings...",
            "importance_score": 0.8
        },
        {
            "message_id": 3,
            "message_timestamp": "2025-10-31T00:02:00Z",
            "conversation_id": "test-conv-001",
            "role": "user",
            "content": "Расскажи подробнее про TimescaleDB hypertables",
            "importance_score": 0.7
        }
    ]
    vector_ids = vectorizer.vectorize_messages_batch(messages)
    print(f"Batch vectorized: {len(vector_ids)} messages")

    # Test semantic search
    results = vectorizer.search_similar_messages(
        query="векторное хранилище для AI памяти",
        limit=5
    )
    print(f"\nSemantic search results: {len(results)}")
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.3f} | {result['content_preview'][:80]}...")

    # Get collection stats
    stats = vectorizer.get_collection_stats()
    print(f"\nCollection stats: {stats}")
