"""
Full Dataset Indexer with Resume Capability
Оптимизированная индексация всех BSL файлов в Qdrant и Neo4j
"""

import sys
import json
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
import logging

# Добавление путей
sys.path.insert(0, str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from services.embedding_service import EmbeddingService
from services.bsl_parser import BSLParser
from services.neo4j_indexer import Neo4jIndexer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('indexing.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class IndexingProgress:
    """Прогресс индексации"""
    total_files: int
    processed_files: int
    failed_files: List[str]
    qdrant_indexed: Set[str]
    neo4j_indexed: Set[str]
    start_time: float
    last_checkpoint: float

    def to_dict(self) -> Dict:
        """Сериализация для JSON"""
        return {
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'failed_files': self.failed_files,
            'qdrant_indexed': list(self.qdrant_indexed),
            'neo4j_indexed': list(self.neo4j_indexed),
            'start_time': self.start_time,
            'last_checkpoint': self.last_checkpoint
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'IndexingProgress':
        """Десериализация из JSON"""
        return cls(
            total_files=data['total_files'],
            processed_files=data['processed_files'],
            failed_files=data['failed_files'],
            qdrant_indexed=set(data['qdrant_indexed']),
            neo4j_indexed=set(data['neo4j_indexed']),
            start_time=data['start_time'],
            last_checkpoint=data['last_checkpoint']
        )


class FullDatasetIndexer:
    """
    Оптимизированный indexer с resume capability

    Улучшения:
    - Увеличенный timeout для Ollama (90 сек)
    - Resume capability через checkpoints
    - Пропуск уже проиндексированных файлов
    - Retry logic с exponential backoff
    - Real-time progress monitoring
    - Пониженная нагрузка (batch=5)
    """

    def __init__(
        self,
        source_path: str,
        checkpoint_file: str = "data/indexing_progress.json",
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        ollama_host: str = "http://localhost:11434",
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password123",
        batch_size: int = 5,
        max_retries: int = 3,
        ollama_timeout: int = 90
    ):
        self.source_path = Path(source_path)
        self.checkpoint_file = Path(checkpoint_file)
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.ollama_timeout = ollama_timeout

        # Создание директории для checkpoints
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

        # Инициализация сервисов
        logger.info("Инициализация сервисов...")

        self.qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.embedding_service = EmbeddingService(
            ollama_host=ollama_host,
            model="nomic-embed-text:latest",
            timeout=ollama_timeout  # Увеличенный timeout
        )
        self.parser = BSLParser()
        self.neo4j = Neo4jIndexer(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password
        )

        # Загрузка прогресса
        self.progress = self._load_progress()

        logger.info(f"✅ Сервисы инициализированы (Ollama timeout: {ollama_timeout}s)")

    def _load_progress(self) -> IndexingProgress:
        """Загрузка прогресса из checkpoint"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                progress = IndexingProgress.from_dict(data)
                logger.info(f"📂 Загружен checkpoint: {progress.processed_files}/{progress.total_files} файлов")
                return progress
            except Exception as e:
                logger.warning(f"Не удалось загрузить checkpoint: {e}")

        # Новый прогресс
        all_files = list(self.source_path.rglob("*.bsl"))
        return IndexingProgress(
            total_files=len(all_files),
            processed_files=0,
            failed_files=[],
            qdrant_indexed=set(),
            neo4j_indexed=set(),
            start_time=time.time(),
            last_checkpoint=time.time()
        )

    def _save_progress(self):
        """Сохранение прогресса в checkpoint"""
        self.progress.last_checkpoint = time.time()
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress.to_dict(), f, indent=2, ensure_ascii=False)
            logger.debug(f"💾 Checkpoint сохранен")
        except Exception as e:
            logger.error(f"Ошибка сохранения checkpoint: {e}")

    def _get_pending_files(self) -> List[Path]:
        """Получение списка файлов для обработки"""
        all_files = list(self.source_path.rglob("*.bsl"))

        # Фильтрация уже обработанных
        pending = []
        for file in all_files:
            file_str = str(file)
            if file_str not in self.progress.qdrant_indexed or file_str not in self.progress.neo4j_indexed:
                pending.append(file)

        return pending

    async def _index_file_to_qdrant(self, file_path: Path, retry_count: int = 0) -> bool:
        """
        Индексация файла в Qdrant с retry logic

        Returns:
            True если успешно, False если ошибка
        """
        try:
            # Парсинг
            metadata = self.parser.parse_file(str(file_path))

            if not metadata:
                logger.warning(f"Пустой файл: {file_path.name}")
                return True

            # Создание searchable text
            searchable_text = self.parser.create_searchable_text(metadata)

            # Embedding с увеличенным timeout
            embedding = self.embedding_service.create_embedding(searchable_text)

            if not embedding:
                logger.error(f"Не удалось создать embedding для {file_path.name}")
                return False

            # Индексация в Qdrant
            point_id = hash(str(file_path)) & 0x7FFFFFFF  # Positive int

            self.qdrant.upsert(
                collection_name="bsl_code",
                points=[{
                    "id": point_id,
                    "vector": embedding,
                    "payload": {
                        "file_path": str(file_path),
                        "module_type": metadata.get('module_type', 'Unknown'),
                        "functions_count": len(metadata.get('functions', [])),
                        "procedures_count": len(metadata.get('procedures', [])),
                        "variables_count": len(metadata.get('variables', [])),
                        "searchable_text": searchable_text[:500]  # Первые 500 символов
                    }
                }]
            )

            return True

        except Exception as e:
            if retry_count < self.max_retries:
                # Exponential backoff
                wait_time = 2 ** retry_count
                logger.warning(f"Retry {retry_count + 1}/{self.max_retries} для {file_path.name} через {wait_time}s")
                await asyncio.sleep(wait_time)
                return await self._index_file_to_qdrant(file_path, retry_count + 1)
            else:
                logger.error(f"❌ Ошибка индексации в Qdrant {file_path.name}: {e}")
                return False

    async def _index_file_to_neo4j(self, file_path: Path, retry_count: int = 0) -> bool:
        """
        Индексация файла в Neo4j с retry logic

        Returns:
            True если успешно, False если ошибка
        """
        try:
            # Парсинг
            metadata = self.parser.parse_file(str(file_path))

            if not metadata:
                return True

            # Индексация в Neo4j
            self.neo4j.index_module(metadata)

            return True

        except Exception as e:
            if retry_count < self.max_retries:
                wait_time = 2 ** retry_count
                logger.warning(f"Retry {retry_count + 1}/{self.max_retries} для {file_path.name} (Neo4j) через {wait_time}s")
                await asyncio.sleep(wait_time)
                return await self._index_file_to_neo4j(file_path, retry_count + 1)
            else:
                logger.error(f"❌ Ошибка индексации в Neo4j {file_path.name}: {e}")
                return False

    async def _process_batch(self, batch: List[Path]) -> Dict[str, int]:
        """Обработка батча файлов"""
        stats = {
            'qdrant_success': 0,
            'qdrant_failed': 0,
            'neo4j_success': 0,
            'neo4j_failed': 0
        }

        for file_path in batch:
            file_str = str(file_path)

            # Qdrant indexing
            if file_str not in self.progress.qdrant_indexed:
                success = await self._index_file_to_qdrant(file_path)
                if success:
                    self.progress.qdrant_indexed.add(file_str)
                    stats['qdrant_success'] += 1
                else:
                    stats['qdrant_failed'] += 1
                    if file_str not in self.progress.failed_files:
                        self.progress.failed_files.append(file_str)

            # Neo4j indexing
            if file_str not in self.progress.neo4j_indexed:
                success = await self._index_file_to_neo4j(file_path)
                if success:
                    self.progress.neo4j_indexed.add(file_str)
                    stats['neo4j_success'] += 1
                else:
                    stats['neo4j_failed'] += 1
                    if file_str not in self.progress.failed_files:
                        self.progress.failed_files.append(file_str)

            self.progress.processed_files += 1

        return stats

    def _print_progress(self, batch_stats: Dict[str, int]):
        """Вывод прогресса"""
        elapsed = time.time() - self.progress.start_time
        processed = self.progress.processed_files
        total = self.progress.total_files

        if processed > 0:
            rate = processed / elapsed
            eta = (total - processed) / rate if rate > 0 else 0
        else:
            rate = 0
            eta = 0

        qdrant_total = len(self.progress.qdrant_indexed)
        neo4j_total = len(self.progress.neo4j_indexed)

        logger.info(f"""
╔════════════════════════════════════════════════════════════════
║ Прогресс индексации: {processed}/{total} файлов ({processed/total*100:.1f}%)
║ ────────────────────────────────────────────────────────────────
║ Qdrant:  {qdrant_total} проиндексировано (✅ {batch_stats['qdrant_success']} / ❌ {batch_stats['qdrant_failed']})
║ Neo4j:   {neo4j_total} проиндексировано (✅ {batch_stats['neo4j_success']} / ❌ {batch_stats['neo4j_failed']})
║ ────────────────────────────────────────────────────────────────
║ Скорость: {rate:.2f} файлов/сек
║ Время:    {elapsed/60:.1f} минут
║ ETA:      {eta/60:.1f} минут
║ Failed:   {len(self.progress.failed_files)} файлов
╚════════════════════════════════════════════════════════════════
        """)

    async def run(self):
        """Запуск индексации"""
        logger.info("🚀 Старт полной индексации BSL кода")
        logger.info(f"📊 Всего файлов: {self.progress.total_files}")

        # Получение файлов для обработки
        pending_files = self._get_pending_files()
        logger.info(f"📝 Осталось обработать: {len(pending_files)} файлов")

        if not pending_files:
            logger.info("✅ Все файлы уже проиндексированы!")
            return

        # Обработка батчами
        total_batches = (len(pending_files) + self.batch_size - 1) // self.batch_size

        for i in range(0, len(pending_files), self.batch_size):
            batch = pending_files[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1

            logger.info(f"\n📦 Батч {batch_num}/{total_batches} ({len(batch)} файлов)")

            # Обработка батча
            batch_stats = await self._process_batch(batch)

            # Вывод прогресса
            self._print_progress(batch_stats)

            # Сохранение checkpoint каждые 10 батчей
            if batch_num % 10 == 0:
                self._save_progress()
                logger.info("💾 Checkpoint сохранен")

            # Короткая пауза между батчами
            await asyncio.sleep(0.5)

        # Финальное сохранение
        self._save_progress()

        # Итоговая статистика
        total_time = time.time() - self.progress.start_time
        logger.info(f"""
╔════════════════════════════════════════════════════════════════
║ ✅ ИНДЕКСАЦИЯ ЗАВЕРШЕНА
║ ────────────────────────────────────────────────────────────────
║ Всего файлов:        {self.progress.total_files}
║ Qdrant indexed:      {len(self.progress.qdrant_indexed)}
║ Neo4j indexed:       {len(self.progress.neo4j_indexed)}
║ Failed:              {len(self.progress.failed_files)}
║ ────────────────────────────────────────────────────────────────
║ Время:               {total_time/60:.1f} минут
║ Скорость:            {self.progress.processed_files/total_time:.2f} файлов/сек
╚════════════════════════════════════════════════════════════════
        """)

        if self.progress.failed_files:
            logger.warning(f"\n⚠️  Failed файлы ({len(self.progress.failed_files)}):")
            for failed in self.progress.failed_files[:10]:
                logger.warning(f"  - {failed}")
            if len(self.progress.failed_files) > 10:
                logger.warning(f"  ... и ещё {len(self.progress.failed_files) - 10}")

    def close(self):
        """Закрытие соединений"""
        if hasattr(self, 'neo4j'):
            self.neo4j.close()
        logger.info("Соединения закрыты")


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Full Dataset Indexer for BSL code")
    parser.add_argument(
        "--source",
        default="D:/1C-Enterprise_Framework/src",
        help="Путь к исходникам BSL"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Размер батча (default: 5)"
    )
    parser.add_argument(
        "--ollama-timeout",
        type=int,
        default=90,
        help="Timeout для Ollama в секундах (default: 90)"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Максимум попыток при ошибке (default: 3)"
    )

    args = parser.parse_args()

    indexer = FullDatasetIndexer(
        source_path=args.source,
        batch_size=args.batch_size,
        ollama_timeout=args.ollama_timeout,
        max_retries=args.max_retries
    )

    try:
        await indexer.run()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Прервано пользователем. Сохранение прогресса...")
        indexer._save_progress()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        indexer._save_progress()
    finally:
        indexer.close()


if __name__ == "__main__":
    asyncio.run(main())
