#!/usr/bin/env python3
"""
Гибридный поисковый движок для документации фреймворка 1C
Комбинирует полнотекстовый поиск (SQLite FTS5) и семантический поиск (sentence-transformers)
"""

import json
import sqlite3
import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Внимание: sentence-transformers не установлен. Семантический поиск недоступен.")

@dataclass
class Document:
    """Структура документа"""
    id: str
    title: str
    path: str
    content: str
    content_preview: str
    size: int
    modified: str
    tags: List[str]
    doc_type: str

@dataclass
class SearchResult:
    """Результат поиска"""
    document: Document
    score: float
    match_type: str  # 'fulltext', 'semantic', 'hybrid'
    snippet: str

class HybridSearchEngine:
    """Гибридный поисковый движок"""
    
    def __init__(self, db_path: str = "cache/docs-mcp/hybrid_search.db"):
        """Инициализация поискового движка"""
        # Настройка логирования
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Инициализация БД: {self.db_path}")
        
        self.embedding_model = None
        if EMBEDDINGS_AVAILABLE:
            try:
                # Многоязычная модель с поддержкой русского
                self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                self.logger.info("Модель эмбеддингов загружена: paraphrase-multilingual-MiniLM-L12-v2")
            except Exception as e:
                self.logger.warning(f"Не удалось загрузить модель эмбеддингов: {e}")
        else:
            self.logger.warning("sentence-transformers недоступен. Семантический поиск отключен.")
        
        try:
            self._init_database()
        except Exception as e:
            self.logger.error(f"Ошибка инициализации БД: {e}")
            raise
        
    def _init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица документов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                path TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                content_preview TEXT,
                size INTEGER,
                modified TEXT,
                tags TEXT,  -- JSON array
                doc_type TEXT,
                content_hash TEXT
            )
        """)
        
        # FTS5 таблица для полнотекстового поиска
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                id UNINDEXED,
                title,
                content,
                tags,
                content='documents',
                content_rowid='rowid'
            )
        """)
        
        # Таблица эмбеддингов (если доступны)
        if self.embedding_model:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    document_id TEXT PRIMARY KEY,
                    embedding BLOB,
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                )
            """)
        
        # Индексы для оптимизации
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_type ON documents(doc_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_modified ON documents(modified)")
        
        conn.commit()
        conn.close()
        
        print(f"[OK] База данных инициализирована: {self.db_path}")
    
    def _generate_doc_id(self, path: str) -> str:
        """Генерация уникального ID документа"""
        return hashlib.md5(path.encode()).hexdigest()[:12]
    
    def _get_content_hash(self, content: str) -> str:
        """Хеш содержимого для определения изменений"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def index_document(self, file_path: str, doc_type: str = "markdown") -> bool:
        """Индексация одного документа"""
        path = Path(file_path)
        
        if not path.exists():
            print(f"[ERROR] Файл не найден: {file_path}")
            return False
        
        try:
            # Читаем содержимое
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Генерируем метаданные
            doc_id = self._generate_doc_id(str(path))
            content_hash = self._get_content_hash(content)
            
            # Проверяем, нужно ли обновлять
            if self._is_document_current(doc_id, content_hash):
                print(f"⏭️ Документ актуален: {path.name}")
                return True
            
            # Создаем документ
            document = Document(
                id=doc_id,
                title=path.stem,
                path=str(path),
                content=content,
                content_preview=content[:500] + "..." if len(content) > 500 else content,
                size=len(content),
                modified=datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                tags=self._extract_tags(content),
                doc_type=doc_type
            )
            
            # Сохраняем в базу
            self._save_document(document, content_hash)
            
            # Генерируем эмбеддинги если доступны
            if self.embedding_model:
                self._generate_embedding(document)
            
            print(f"[OK] Проиндексирован: {path.name}")
            return True

        except Exception as e:
            print(f"[ERROR] Ошибка индексации {file_path}: {e}")
            return False
    
    def _is_document_current(self, doc_id: str, content_hash: str) -> bool:
        """Проверка актуальности документа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT content_hash FROM documents WHERE id = ?", 
            (doc_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        return result and result[0] == content_hash
    
    def _extract_tags(self, content: str) -> List[str]:
        """Извлечение тегов из содержимого"""
        tags = []
        
        # Простая эвристика для тегов
        if "Task Master" in content:
            tags.append("task-master")
        if "BSL" in content:
            tags.append("bsl")
        if "MCP" in content:
            tags.append("mcp")
        if "Claude" in content:
            tags.append("claude")
        if "1C" in content or "1С" in content:
            tags.append("1c")
        if "API" in content:
            tags.append("api")
        if "integration" in content.lower() or "интеграция" in content.lower():
            tags.append("integration")
            
        return tags
    
    def _save_document(self, document: Document, content_hash: str):
        """Сохранение документа в базу"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Основная таблица
        cursor.execute("""
            INSERT OR REPLACE INTO documents 
            (id, title, path, content, content_preview, size, modified, tags, doc_type, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            document.id, document.title, document.path, document.content,
            document.content_preview, document.size, document.modified,
            json.dumps(document.tags), document.doc_type, content_hash
        ))
        
        # FTS5 таблица
        cursor.execute("""
            INSERT OR REPLACE INTO documents_fts (id, title, content, tags)
            VALUES (?, ?, ?, ?)
        """, (
            document.id, document.title, document.content, 
            " ".join(document.tags)
        ))
        
        conn.commit()
        conn.close()
    
    def _generate_embedding(self, document: Document):
        """Генерация эмбеддинга для документа"""
        if not self.embedding_model:
            return
        
        try:
            # Комбинируем заголовок и содержимое для эмбеддинга
            text_to_embed = f"{document.title} {document.content}"
            
            # Генерируем эмбеддинг
            embedding = self.embedding_model.encode(text_to_embed)
            
            # Сохраняем в базу
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO embeddings (document_id, embedding)
                VALUES (?, ?)
            """, (document.id, embedding.tobytes()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[WARNING] Ошибка генерации эмбеддинга для {document.title}: {e}")
    
    def search(self, query: str, limit: int = 10, search_type: str = "hybrid") -> List[SearchResult]:
        """
        Основной метод поиска
        
        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов
            search_type: Тип поиска ('fulltext', 'semantic', 'hybrid')
        """
        if search_type == "fulltext":
            return self._fulltext_search(query, limit)
        elif search_type == "semantic" and self.embedding_model:
            return self._semantic_search(query, limit)
        elif search_type == "hybrid":
            return self._hybrid_search(query, limit)
        else:
            # Fallback на полнотекстовый поиск
            return self._fulltext_search(query, limit)
    
    def _fulltext_search(self, query: str, limit: int) -> List[SearchResult]:
        """Полнотекстовый поиск через FTS5"""
        try:
            self.logger.debug(f"Полнотекстовый поиск: '{query}', лимит: {limit}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # FTS5 запрос с правильным синтаксисом bm25
            cursor.execute("""
                SELECT d.*, bm25(documents_fts) as score
                FROM documents_fts
                JOIN documents d ON documents_fts.rowid = d.rowid
                WHERE documents_fts MATCH ?
                ORDER BY score
                LIMIT ?
            """, (query, limit))
            
            results = []
            for row in cursor.fetchall():
                try:
                    document = self._row_to_document(row[:-1])  # Исключаем score
                    score = row[-1]
                    
                    # Генерируем snippet
                    snippet = self._generate_snippet(document.content, query)
                    
                    results.append(SearchResult(
                        document=document,
                        score=abs(score),  # BM25 может быть отрицательным
                        match_type="fulltext",
                        snippet=snippet
                    ))
                except Exception as e:
                    self.logger.error(f"Ошибка обработки результата: {e}")
                    continue
            
            conn.close()
            self.logger.info(f"Найдено {len(results)} результатов (fulltext)")
            return results
            
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка SQL в fulltext_search: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка в fulltext_search: {e}")
            return []
    
    def _semantic_search(self, query: str, limit: int) -> List[SearchResult]:
        """Семантический поиск через эмбеддинги"""
        if not self.embedding_model:
            self.logger.warning("Семантический поиск недоступен: модель не загружена")
            return []
        
        try:
            self.logger.debug(f"Семантический поиск: '{query}', лимит: {limit}")
            
            # Генерируем эмбеддинг запроса
            query_embedding = self.embedding_model.encode(query)
            
            # Получаем все эмбеддинги из базы
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT e.document_id, e.embedding, d.*
                FROM embeddings e
                JOIN documents d ON e.document_id = d.id
            """)
            
            results = []
            for row in cursor.fetchall():
                try:
                    doc_id = row[0]
                    stored_embedding = np.frombuffer(row[1], dtype=np.float32)
                    document = self._row_to_document(row[2:])
                    
                    # Вычисляем косинусное сходство
                    similarity = np.dot(query_embedding, stored_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                    )
                    
                    snippet = self._generate_snippet(document.content, query)
                    
                    results.append(SearchResult(
                        document=document,
                        score=float(similarity),
                        match_type="semantic",
                        snippet=snippet
                    ))
                except Exception as e:
                    self.logger.error(f"Ошибка обработки документа {row[0] if row else 'unknown'}: {e}")
                    continue
            
            conn.close()
            
            # Сортируем по убыванию сходства
            results.sort(key=lambda x: x.score, reverse=True)
            self.logger.info(f"Найдено {len(results)} результатов (semantic)")
            return results[:limit]
            
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка SQL в semantic_search: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка в semantic_search: {e}")
            return []
    
    def _hybrid_search(self, query: str, limit: int) -> List[SearchResult]:
        """Гибридный поиск (комбинация fulltext + semantic)"""
        try:
            self.logger.debug(f"Гибридный поиск: '{query}', лимит: {limit}")
            
            # Получаем результаты от обоих методов
            fulltext_results = self._fulltext_search(query, limit * 2)
            semantic_results = self._semantic_search(query, limit * 2) if self.embedding_model else []
            
            # Создаем словарь результатов по document.id
            combined = {}
            
            # Добавляем полнотекстовые результаты
            for result in fulltext_results:
                doc_id = result.document.id
                combined[doc_id] = result
                combined[doc_id].score = result.score * 0.7  # Вес 70%
            
            # Добавляем/обновляем семантические результаты
            for result in semantic_results:
                doc_id = result.document.id
                if doc_id in combined:
                    # Комбинируем скоры
                    combined[doc_id].score += result.score * 0.3  # Вес 30%
                    combined[doc_id].match_type = "hybrid"
                else:
                    combined[doc_id] = result
                    combined[doc_id].score = result.score * 0.3
            
            # Сортируем и возвращаем топ результатов
            final_results = list(combined.values())
            final_results.sort(key=lambda x: x.score, reverse=True)
            
            self.logger.info(f"Найдено {len(final_results[:limit])} результатов (hybrid)")
            return final_results[:limit]
            
        except Exception as e:
            self.logger.error(f"Ошибка в hybrid_search: {e}")
            # Fallback на fulltext поиск
            self.logger.info("Переход на fulltext поиск как fallback")
            return self._fulltext_search(query, limit)
    
    def _row_to_document(self, row) -> Document:
        """Преобразование строки БД в объект Document"""
        return Document(
            id=row[0],
            title=row[1],
            path=row[2],
            content=row[3],
            content_preview=row[4],
            size=row[5],
            modified=row[6],
            tags=json.loads(row[7]) if row[7] else [],
            doc_type=row[8]
        )
    
    def _generate_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """Генерация сниппета с контекстом запроса"""
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Ищем первое вхождение запроса
        pos = content_lower.find(query_lower)
        
        if pos == -1:
            # Если точного совпадения нет, берем начало
            return content[:max_length] + "..." if len(content) > max_length else content
        
        # Определяем границы сниппета
        start = max(0, pos - max_length // 3)
        end = min(len(content), pos + len(query) + max_length // 3)
        
        snippet = content[start:end]
        
        # Добавляем многоточия
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
            
        return snippet
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики по индексу"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Общая статистика
        cursor.execute("SELECT COUNT(*) FROM documents")
        total_docs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        docs_with_embeddings = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(size) FROM documents")
        total_size = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT doc_type, COUNT(*) FROM documents GROUP BY doc_type")
        types_stats = dict(cursor.fetchall())
        
        cursor.execute("""
            SELECT COUNT(DISTINCT tags.value) 
            FROM documents, json_each(documents.tags) AS tags
        """)
        unique_tags = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_documents": total_docs,
            "documents_with_embeddings": docs_with_embeddings,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "document_types": types_stats,
            "unique_tags": unique_tags,
            "embeddings_enabled": EMBEDDINGS_AVAILABLE and self.embedding_model is not None,
            "model_name": "paraphrase-multilingual-MiniLM-L12-v2" if self.embedding_model else None
        }


def main():
    """Демонстрация работы поискового движка"""
    print("🚀 Демонстрация гибридного поискового движка")
    print("=" * 60)
    
    # Инициализация
    engine = HybridSearchEngine()
    
    # Индексация документации фреймворка
    docs_path = Path("Документация по фреймворку")
    
    if docs_path.exists():
        print(f"📚 Индексация документов из {docs_path}")
        
        for md_file in docs_path.rglob("*.md"):
            engine.index_document(str(md_file))
    
    # Статистика
    stats = engine.get_statistics()
    print(f"\n[STATS] Статистика индекса:")
    print(f"   Документов: {stats['total_documents']}")
    print(f"   С эмбеддингами: {stats['documents_with_embeddings']}")
    print(f"   Размер: {stats['total_size_mb']} MB")
    print(f"   Эмбеддинги: {'[OK]' if stats['embeddings_enabled'] else '[NO]'}")
    
    # Тестовые запросы
    test_queries = [
        "Task Master",
        "BSL анализ качества",
        "MCP сервер",
        "интеграция Claude"
    ]
    
    for query in test_queries:
        print(f"\n[SEARCH] Поиск: '{query}'")
        results = engine.search(query, limit=3)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.document.title}")
            print(f"     Релевантность: {result.score:.3f} ({result.match_type})")
            print(f"     Файл: {Path(result.document.path).name}")


if __name__ == "__main__":
    main()