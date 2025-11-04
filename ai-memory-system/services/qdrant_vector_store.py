"""
Qdrant Vector Store Service - заглушка для MCP Server

Минимальная реализация для инициализации MCP сервера.
"""

import logging
from typing import Optional
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """
    Обертка над Qdrant Client для MCP Server

    Предоставляет базовый интерфейс для работы с векторной базой.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "bsl_code",
        **kwargs
    ):
        """
        Инициализация Qdrant Vector Store

        Args:
            host: Хост Qdrant сервера
            port: Порт Qdrant сервера
            collection_name: Имя коллекции
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name

        try:
            self.client = QdrantClient(host=host, port=port)
            logger.info(f"QdrantVectorStore подключен к {host}:{port}, коллекция: {collection_name}")
        except Exception as e:
            logger.warning(f"Не удалось подключиться к Qdrant: {e}")
            self.client = None

    def is_connected(self) -> bool:
        """Проверить подключение к Qdrant"""
        return self.client is not None

    def get_client(self) -> Optional[QdrantClient]:
        """Получить клиент Qdrant"""
        return self.client
