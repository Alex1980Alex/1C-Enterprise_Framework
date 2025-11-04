"""
Redis Cache Module for BSL Code Search API
Опциональное кеширование результатов поиска
"""

import os
import json
import hashlib
import logging
from typing import Optional, Any
from datetime import timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class SearchCache:
    """
    Кеш для результатов поиска с использованием Redis

    Если Redis недоступен, работает в режиме pass-through (без кеширования)
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        ttl: int = 3600  # 1 час по умолчанию
    ):
        """
        Инициализация кеша

        Args:
            host: Redis хост
            port: Redis порт
            db: Redis database number
            password: Redis пароль (опционально)
            ttl: Время жизни кеша в секундах (по умолчанию 1 час)
        """
        self.ttl = ttl
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = False

        if not REDIS_AVAILABLE:
            logger.warning("⚠️  Redis module not installed. Caching disabled.")
            return

        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,  # Автоматическая декодировка в строки
                socket_timeout=2,
                socket_connect_timeout=2
            )

            # Проверка подключения
            self.redis_client.ping()
            self.enabled = True
            logger.info(f"✅ Redis cache connected: {host}:{port} (TTL: {ttl}s)")

        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning(f"⚠️  Redis unavailable: {e}. Caching disabled.")
            self.redis_client = None
            self.enabled = False
        except Exception as e:
            logger.error(f"❌ Redis initialization error: {e}. Caching disabled.")
            self.redis_client = None
            self.enabled = False

    def _generate_key(self, query: str, **params) -> str:
        """
        Генерация ключа кеша на основе запроса и параметров

        Args:
            query: Поисковый запрос
            **params: Дополнительные параметры (top_k, score_threshold, etc.)

        Returns:
            Хеш-ключ для Redis
        """
        # Сортируем параметры для консистентности ключей
        sorted_params = json.dumps(params, sort_keys=True)
        cache_string = f"{query}:{sorted_params}"

        # SHA-256 хеш для компактности
        key_hash = hashlib.sha256(cache_string.encode()).hexdigest()
        return f"search:{key_hash}"

    def get(self, query: str, **params) -> Optional[dict]:
        """
        Получение результата из кеша

        Args:
            query: Поисковый запрос
            **params: Параметры запроса

        Returns:
            Кешированный результат или None
        """
        if not self.enabled or not self.redis_client:
            return None

        try:
            key = self._generate_key(query, **params)
            cached_data = self.redis_client.get(key)

            if cached_data:
                logger.info(f"🎯 Cache HIT: {query[:50]}...")
                return json.loads(cached_data)
            else:
                logger.debug(f"❌ Cache MISS: {query[:50]}...")
                return None

        except Exception as e:
            logger.error(f"❌ Cache get error: {e}")
            return None

    def set(self, query: str, result: dict, **params) -> bool:
        """
        Сохранение результата в кеш

        Args:
            query: Поисковый запрос
            result: Результат для кеширования
            **params: Параметры запроса

        Returns:
            True если успешно сохранено
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            key = self._generate_key(query, **params)
            cached_data = json.dumps(result, ensure_ascii=False)

            self.redis_client.setex(
                name=key,
                time=self.ttl,
                value=cached_data
            )

            logger.debug(f"💾 Cached: {query[:50]}... (TTL: {self.ttl}s)")
            return True

        except Exception as e:
            logger.error(f"❌ Cache set error: {e}")
            return False

    def delete(self, query: str, **params) -> bool:
        """
        Удаление результата из кеша

        Args:
            query: Поисковый запрос
            **params: Параметры запроса

        Returns:
            True если успешно удалено
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            key = self._generate_key(query, **params)
            deleted = self.redis_client.delete(key)

            if deleted:
                logger.debug(f"🗑️  Deleted from cache: {query[:50]}...")

            return bool(deleted)

        except Exception as e:
            logger.error(f"❌ Cache delete error: {e}")
            return False

    def clear_all(self) -> bool:
        """
        Очистка всего кеша (только ключи search:*)

        Returns:
            True если успешно очищено
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            # Получаем все ключи search:*
            keys = list(self.redis_client.scan_iter(match="search:*"))

            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"🗑️  Cache cleared: {deleted} keys deleted")
                return True
            else:
                logger.info("ℹ️  Cache already empty")
                return True

        except Exception as e:
            logger.error(f"❌ Cache clear error: {e}")
            return False

    def get_stats(self) -> dict:
        """
        Получение статистики кеша

        Returns:
            Словарь со статистикой
        """
        if not self.enabled or not self.redis_client:
            return {
                "enabled": False,
                "reason": "Redis not available"
            }

        try:
            # Подсчет ключей search:*
            keys = list(self.redis_client.scan_iter(match="search:*", count=1000))

            # Получение info от Redis
            info = self.redis_client.info("stats")

            return {
                "enabled": True,
                "cached_queries": len(keys),
                "ttl_seconds": self.ttl,
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }

        except Exception as e:
            logger.error(f"❌ Cache stats error: {e}")
            return {
                "enabled": True,
                "error": str(e)
            }


def create_cache_from_env() -> SearchCache:
    """
    Создание инстанса кеша из переменных окружения

    Returns:
        Настроенный SearchCache
    """
    return SearchCache(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "0")),
        password=os.getenv("REDIS_PASSWORD"),
        ttl=int(os.getenv("REDIS_TTL", "3600"))  # 1 час по умолчанию
    )
