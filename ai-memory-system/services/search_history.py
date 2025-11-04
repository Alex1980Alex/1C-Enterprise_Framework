"""
Search History Service - заглушка для MCP Server

Минимальная реализация для хранения истории поиска.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class SearchHistoryService:
    """
    Сервис для хранения истории поисковых запросов

    Использует in-memory хранилище (deque) вместо Redis.
    """

    def __init__(
        self,
        redis_client=None,
        max_history_size: int = 100
    ):
        """
        Инициализация Search History Service

        Args:
            redis_client: Redis клиент (опционально, не используется)
            max_history_size: Максимальный размер истории
        """
        self.redis_client = redis_client
        self.max_history_size = max_history_size

        # In-memory хранилище истории
        self.history: deque = deque(maxlen=max_history_size)

        if redis_client:
            logger.info("SearchHistoryService инициализирован с Redis")
        else:
            logger.info("SearchHistoryService использует in-memory хранилище")

    def add_search(
        self,
        query: str,
        mode: str = "semantic",
        results_count: int = 0,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Добавить запрос в историю

        Args:
            query: Поисковый запрос
            mode: Режим поиска
            results_count: Количество результатов
            metadata: Дополнительные метаданные
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "mode": mode,
            "results_count": results_count,
            "metadata": metadata or {}
        }

        self.history.append(entry)
        logger.debug(f"Добавлен запрос в историю: {query[:50]}...")

    def get_recent_searches(self, limit: int = 10) -> List[Dict]:
        """
        Получить последние N запросов

        Args:
            limit: Количество запросов

        Returns:
            Список последних запросов
        """
        # Возвращаем последние N элементов в обратном порядке
        recent = list(self.history)[-limit:]
        recent.reverse()
        return recent

    def get_all_searches(self) -> List[Dict]:
        """Получить всю историю"""
        history = list(self.history)
        history.reverse()
        return history

    def clear_history(self) -> None:
        """Очистить историю"""
        self.history.clear()
        logger.info("История поиска очищена")
