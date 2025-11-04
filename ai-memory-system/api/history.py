"""
Search History Management
Сохранение и управление историей поисковых запросов
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class SearchHistory:
    """Управление историей поиска с использованием SQLite"""

    def __init__(self, db_path: str = "data/search_history.db"):
        """
        Инициализация хранилища истории

        Args:
            db_path: Путь к SQLite базе данных
        """
        self.db_path = db_path
        self._ensure_db_exists()
        self._init_db()

    def _ensure_db_exists(self):
        """Создание директории для БД если не существует"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _get_connection(self):
        """Context manager для подключения к БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Возвращать строки как dict
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Инициализация таблиц БД"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Таблица истории поиска
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    query TEXT NOT NULL,
                    filters TEXT,
                    results_count INTEGER NOT NULL,
                    search_time_ms REAL NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Индексы для быстрого поиска
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON search_history(timestamp DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id
                ON search_history(user_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_query
                ON search_history(query)
            """)

            logger.info(f"✅ Search history database initialized at {self.db_path}")

    def add_entry(
        self,
        query: str,
        results_count: int,
        search_time_ms: float,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> int:
        """
        Добавить запись в историю

        Args:
            query: Поисковый запрос
            results_count: Количество найденных результатов
            search_time_ms: Время выполнения поиска в мс
            filters: Параметры фильтрации
            user_id: ID пользователя (опционально)

        Returns:
            ID созданной записи
        """
        try:
            timestamp = datetime.now().isoformat()
            filters_json = json.dumps(filters) if filters else None

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO search_history
                    (timestamp, user_id, query, filters, results_count, search_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (timestamp, user_id, query, filters_json, results_count, search_time_ms))

                entry_id = cursor.lastrowid
                logger.debug(f"Added search history entry #{entry_id}: '{query}'")
                return entry_id

        except Exception as e:
            logger.error(f"Failed to add history entry: {e}")
            raise

    def get_history(
        self,
        limit: int = 50,
        offset: int = 0,
        user_id: Optional[str] = None,
        query_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить историю поиска с пагинацией

        Args:
            limit: Максимальное количество записей
            offset: Смещение для пагинации
            user_id: Фильтр по пользователю
            query_filter: Фильтр по тексту запроса (подстрока)

        Returns:
            Список записей истории
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Построение запроса с фильтрами
                sql = "SELECT * FROM search_history WHERE 1=1"
                params = []

                if user_id:
                    sql += " AND user_id = ?"
                    params.append(user_id)

                if query_filter:
                    sql += " AND query LIKE ?"
                    params.append(f"%{query_filter}%")

                sql += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                cursor.execute(sql, params)
                rows = cursor.fetchall()

                # Преобразование в список словарей
                results = []
                for row in rows:
                    entry = dict(row)
                    # Парсинг JSON фильтров
                    if entry['filters']:
                        entry['filters'] = json.loads(entry['filters'])
                    results.append(entry)

                logger.debug(f"Retrieved {len(results)} history entries")
                return results

        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            raise

    def get_entry_by_id(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить конкретную запись по ID

        Args:
            entry_id: ID записи

        Returns:
            Запись истории или None
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM search_history WHERE id = ?",
                    (entry_id,)
                )
                row = cursor.fetchone()

                if row:
                    entry = dict(row)
                    if entry['filters']:
                        entry['filters'] = json.loads(entry['filters'])
                    return entry
                return None

        except Exception as e:
            logger.error(f"Failed to get entry #{entry_id}: {e}")
            raise

    def delete_entry(self, entry_id: int) -> bool:
        """
        Удалить запись из истории

        Args:
            entry_id: ID записи

        Returns:
            True если запись удалена
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM search_history WHERE id = ?",
                    (entry_id,)
                )
                deleted = cursor.rowcount > 0

                if deleted:
                    logger.info(f"Deleted history entry #{entry_id}")
                return deleted

        except Exception as e:
            logger.error(f"Failed to delete entry #{entry_id}: {e}")
            raise

    def clear_history(self, user_id: Optional[str] = None) -> int:
        """
        Очистить историю

        Args:
            user_id: Если указан, очищается только история этого пользователя

        Returns:
            Количество удаленных записей
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                if user_id:
                    cursor.execute(
                        "DELETE FROM search_history WHERE user_id = ?",
                        (user_id,)
                    )
                else:
                    cursor.execute("DELETE FROM search_history")

                deleted_count = cursor.rowcount
                logger.info(f"Cleared {deleted_count} history entries")
                return deleted_count

        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            raise

    def get_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Получить статистику по истории поиска

        Args:
            user_id: Фильтр по пользователю

        Returns:
            Словарь со статистикой
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Базовый запрос
                where_clause = "WHERE user_id = ?" if user_id else "WHERE 1=1"
                params = [user_id] if user_id else []

                # Общая статистика
                cursor.execute(f"""
                    SELECT
                        COUNT(*) as total_searches,
                        AVG(results_count) as avg_results,
                        AVG(search_time_ms) as avg_search_time,
                        MIN(timestamp) as first_search,
                        MAX(timestamp) as last_search
                    FROM search_history
                    {where_clause}
                """, params)

                stats = dict(cursor.fetchone())

                # Топ запросов
                cursor.execute(f"""
                    SELECT query, COUNT(*) as count
                    FROM search_history
                    {where_clause}
                    GROUP BY query
                    ORDER BY count DESC
                    LIMIT 10
                """, params)

                stats['top_queries'] = [
                    {'query': row['query'], 'count': row['count']}
                    for row in cursor.fetchall()
                ]

                logger.debug(f"Retrieved history statistics")
                return stats

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            raise

    def get_total_count(self, user_id: Optional[str] = None) -> int:
        """
        Получить общее количество записей

        Args:
            user_id: Фильтр по пользователю

        Returns:
            Количество записей
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                if user_id:
                    cursor.execute(
                        "SELECT COUNT(*) as count FROM search_history WHERE user_id = ?",
                        (user_id,)
                    )
                else:
                    cursor.execute("SELECT COUNT(*) as count FROM search_history")

                return cursor.fetchone()['count']

        except Exception as e:
            logger.error(f"Failed to get total count: {e}")
            raise


# Глобальный экземпляр для использования в API
search_history: Optional[SearchHistory] = None


def get_search_history() -> SearchHistory:
    """Получить глобальный экземпляр SearchHistory"""
    global search_history
    if search_history is None:
        search_history = SearchHistory()
    return search_history
