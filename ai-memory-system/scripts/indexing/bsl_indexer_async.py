"""
BSL Async Indexer - асинхронная индексация BSL файлов для семантического поиска
Версия: 2.0 с async/batch processing для Week 2, Day 3

Возможности:
- Асинхронная обработка файлов (asyncio)
- Batch processing для эффективности
- Progress monitoring с real-time отчетами
- Error handling и retry logic
- Загрузка в Qdrant для векторного поиска
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import time

# Добавление путей для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.embedding_service import EmbeddingService
from utils.bsl_parser import BSLParser, BSLModule

# Конфигурация логирования
log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'indexing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class IndexedFile:
    """Структура для индексированного файла"""
    file_path: str
    module_type: str
    functions_count: int
    variables_count: int
    searchable_text: str
    embedding: List[float]
    indexed_at: str
    file_size: int
    processing_time_ms: float = 0.0


@dataclass
class IndexingProgress:
    """Прогресс индексации"""
    total_files: int = 0
    processed_files: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    start_time: float = 0.0

    @property
    def progress_percent(self) -> float:
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100

    @property
    def elapsed_time(self) -> float:
        return time.time() - self.start_time

    @property
    def files_per_second(self) -> float:
        if self.elapsed_time == 0:
            return 0.0
        return self.processed_files / self.elapsed_time

    @property
    def estimated_remaining_seconds(self) -> float:
        if self.files_per_second == 0:
            return 0.0
        remaining_files = self.total_files - self.processed_files
        return remaining_files / self.files_per_second


class AsyncBSLIndexer:
    """
    Асинхронный индексатор BSL файлов с batch processing
    """

    def __init__(
        self,
        output_dir: str = "D:/1C-Enterprise_Framework/ai-memory-system/data/index",
        embedding_model: str = "nomic-embed-text:latest",
        batch_size: int = 10,
        max_workers: int = 4,
        retry_attempts: int = 3
    ):
        """
        Инициализация асинхронного индексатора

        Args:
            output_dir: Директория для сохранения индекса
            embedding_model: Модель для создания эмбеддингов
            batch_size: Размер batch для обработки
            max_workers: Максимальное количество worker threads
            retry_attempts: Количество попыток при ошибке
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.embedding_service = EmbeddingService(model=embedding_model)
        self.parser = BSLParser()

        self.batch_size = batch_size
        self.max_workers = max_workers
        self.retry_attempts = retry_attempts

        self.indexed_files: List[IndexedFile] = []
        self.progress = IndexingProgress()

        # Файлы с ошибками для retry
        self.failed_files: List[str] = []

        logger.info(f"AsyncBSLIndexer инициализирован")
        logger.info(f"  Batch size: {batch_size}")
        logger.info(f"  Max workers: {max_workers}")
        logger.info(f"  Retry attempts: {retry_attempts}")

    async def index_directory_async(
        self,
        directory: str,
        max_files: Optional[int] = None,
        file_pattern: str = "*.bsl"
    ) -> int:
        """
        Асинхронная индексация директории с BSL файлами

        Args:
            directory: Путь к директории
            max_files: Максимальное количество файлов (None = все)
            file_pattern: Паттерн для поиска файлов

        Returns:
            Количество проиндексированных файлов
        """
        logger.info(f"🚀 Начало асинхронной индексации: {directory}")

        # Поиск BSL файлов
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.error(f"❌ Директория не найдена: {directory}")
            return 0

        bsl_files = list(dir_path.rglob(file_pattern))
        self.progress.total_files = len(bsl_files)

        if max_files:
            bsl_files = bsl_files[:max_files]
            self.progress.total_files = len(bsl_files)
            logger.info(f"⚠️  Ограничение: {max_files} файлов из {len(list(dir_path.rglob(file_pattern)))}")

        logger.info(f"📊 Найдено файлов: {self.progress.total_files}")

        # Инициализация прогресса
        self.progress.start_time = time.time()

        # Обработка батчами
        batches = [
            bsl_files[i:i + self.batch_size]
            for i in range(0, len(bsl_files), self.batch_size)
        ]

        logger.info(f"📦 Создано батчей: {len(batches)}")

        # Асинхронная обработка батчей
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            tasks = []
            for batch_idx, batch in enumerate(batches, 1):
                task = asyncio.create_task(
                    self._process_batch_async(batch, batch_idx, len(batches), executor)
                )
                tasks.append(task)

            # Ожидание завершения всех батчей
            await asyncio.gather(*tasks)

        # Retry для файлов с ошибками
        if self.failed_files and self.retry_attempts > 0:
            logger.info(f"🔄 Повторная обработка {len(self.failed_files)} файлов с ошибками...")
            await self._retry_failed_files()

        # Финальная статистика
        self._print_final_statistics()

        logger.info(f"✅ Завершено. Успешно: {self.progress.successful}/{self.progress.total_files}")
        return self.progress.successful

    async def _process_batch_async(
        self,
        batch: List[Path],
        batch_idx: int,
        total_batches: int,
        executor: ThreadPoolExecutor
    ):
        """
        Асинхронная обработка одного батча

        Args:
            batch: Список файлов в батче
            batch_idx: Номер батча
            total_batches: Общее количество батчей
            executor: Thread pool executor
        """
        logger.info(f"📦 Батч {batch_idx}/{total_batches}: обработка {len(batch)} файлов...")

        # Обработка файлов в батче параллельно
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, self._index_file_sync, str(file_path))
            for file_path in batch
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Подсчет результатов
        for result in results:
            self.progress.processed_files += 1

            if isinstance(result, Exception):
                self.progress.failed += 1
                logger.error(f"❌ Ошибка в батче {batch_idx}: {result}")
            elif result:
                self.progress.successful += 1
            else:
                self.progress.skipped += 1

        # Прогресс после батча
        self._print_progress()

    def _index_file_sync(self, file_path: str) -> bool:
        """
        Синхронная индексация одного файла (для executor)

        Args:
            file_path: Путь к файлу

        Returns:
            True если успешно
        """
        start_time = time.time()

        for attempt in range(1, self.retry_attempts + 1):
            try:
                # Парсинг файла
                module = self.parser.parse_file(file_path)
                if not module:
                    logger.warning(f"⚠️  Не удалось распарсить: {Path(file_path).name}")
                    return False

                # Извлечение текста для поиска
                searchable_text = self.parser.extract_searchable_text(module)

                # Создание эмбеддинга
                embedding = self.embedding_service.create_embedding(searchable_text)
                if not embedding:
                    logger.warning(f"⚠️  Не удалось создать эмбеддинг: {Path(file_path).name}")
                    return False

                # Получение размера файла
                file_size = Path(file_path).stat().st_size

                # Время обработки
                processing_time = (time.time() - start_time) * 1000  # ms

                # Создание записи индекса
                indexed_file = IndexedFile(
                    file_path=file_path,
                    module_type=module.module_type,
                    functions_count=len(module.functions),
                    variables_count=len(module.variables),
                    searchable_text=searchable_text,
                    embedding=embedding,
                    indexed_at=datetime.now().isoformat(),
                    file_size=file_size,
                    processing_time_ms=processing_time
                )

                self.indexed_files.append(indexed_file)
                return True

            except Exception as e:
                if attempt < self.retry_attempts:
                    logger.warning(f"⚠️  Попытка {attempt}/{self.retry_attempts} не удалась для {Path(file_path).name}: {e}")
                    time.sleep(0.1 * attempt)  # Экспоненциальная задержка
                else:
                    logger.error(f"❌ Ошибка после {self.retry_attempts} попыток {Path(file_path).name}: {e}")
                    self.failed_files.append(file_path)
                    return False

        return False

    async def _retry_failed_files(self):
        """Повторная обработка файлов с ошибками"""
        files_to_retry = self.failed_files.copy()
        self.failed_files.clear()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, self._index_file_sync, file_path)
                for file_path in files_to_retry
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            retry_success = sum(1 for r in results if r is True)
            logger.info(f"🔄 Повторная обработка: успешно {retry_success}/{len(files_to_retry)}")

    def _print_progress(self):
        """Вывод прогресса индексации"""
        progress_bar = self._create_progress_bar(self.progress.progress_percent)

        logger.info(
            f"\n📊 Прогресс: {progress_bar} {self.progress.progress_percent:.1f}%\n"
            f"   Обработано: {self.progress.processed_files}/{self.progress.total_files}\n"
            f"   ✅ Успешно: {self.progress.successful}\n"
            f"   ❌ Ошибок: {self.progress.failed}\n"
            f"   ⏱️  Скорость: {self.progress.files_per_second:.1f} файлов/сек\n"
            f"   ⏳ Осталось: ~{self.progress.estimated_remaining_seconds:.0f} сек"
        )

    def _print_final_statistics(self):
        """Вывод финальной статистики"""
        total_time = self.progress.elapsed_time

        logger.info(
            f"\n{'='*60}\n"
            f"📊 ФИНАЛЬНАЯ СТАТИСТИКА\n"
            f"{'='*60}\n"
            f"✅ Успешно:        {self.progress.successful}\n"
            f"❌ Ошибок:         {self.progress.failed}\n"
            f"⏭️  Пропущено:      {self.progress.skipped}\n"
            f"📁 Всего:          {self.progress.total_files}\n"
            f"⏱️  Общее время:    {total_time:.1f} сек ({total_time/60:.1f} мин)\n"
            f"⚡ Средняя скорость: {self.progress.files_per_second:.2f} файлов/сек\n"
            f"{'='*60}"
        )

    @staticmethod
    def _create_progress_bar(percent: float, length: int = 30) -> str:
        """Создание текстовой progress bar"""
        filled = int(length * percent / 100)
        bar = '█' * filled + '░' * (length - filled)
        return f"[{bar}]"

    def save_index(self, filename: str = "bsl_index_full.json"):
        """
        Сохранение индекса в файл

        Args:
            filename: Имя файла для сохранения
        """
        output_path = self.output_dir / filename

        try:
            # Статистика по типам модулей
            module_types = {}
            for f in self.indexed_files:
                module_types[f.module_type] = module_types.get(f.module_type, 0) + 1

            # Средняя скорость обработки
            avg_processing_time = sum(f.processing_time_ms for f in self.indexed_files) / len(self.indexed_files) if self.indexed_files else 0

            index_data = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "total_files": len(self.indexed_files),
                    "embedding_model": self.embedding_service.model,
                    "embedding_dimension": len(self.indexed_files[0].embedding) if self.indexed_files else 0,
                    "batch_size": self.batch_size,
                    "max_workers": self.max_workers,
                    "total_processing_time_sec": self.progress.elapsed_time,
                    "avg_processing_time_ms": avg_processing_time,
                    "module_types": module_types,
                    "indexing_stats": {
                        "successful": self.progress.successful,
                        "failed": self.progress.failed,
                        "skipped": self.progress.skipped,
                        "total": self.progress.total_files
                    }
                },
                "files": [asdict(f) for f in self.indexed_files]
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)

            file_size_mb = output_path.stat().st_size / 1024 / 1024
            logger.info(f"💾 Индекс сохранен: {output_path}")
            logger.info(f"📦 Размер файла: {file_size_mb:.2f} MB")

        except Exception as e:
            logger.error(f"❌ Ошибка сохранения индекса: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики индексации

        Returns:
            Словарь со статистикой
        """
        if not self.indexed_files:
            return {"total_files": 0}

        total_functions = sum(f.functions_count for f in self.indexed_files)
        total_variables = sum(f.variables_count for f in self.indexed_files)
        total_size = sum(f.file_size for f in self.indexed_files)
        avg_processing_time = sum(f.processing_time_ms for f in self.indexed_files) / len(self.indexed_files)

        module_types = {}
        for f in self.indexed_files:
            module_types[f.module_type] = module_types.get(f.module_type, 0) + 1

        return {
            "total_files": len(self.indexed_files),
            "total_functions": total_functions,
            "total_variables": total_variables,
            "total_size_mb": total_size / 1024 / 1024,
            "module_types": module_types,
            "embedding_model": self.embedding_service.model,
            "embedding_dimension": len(self.indexed_files[0].embedding) if self.indexed_files else 0,
            "avg_processing_time_ms": avg_processing_time,
            "total_processing_time_sec": self.progress.elapsed_time,
            "files_per_second": self.progress.files_per_second,
            "indexing_stats": {
                "successful": self.progress.successful,
                "failed": self.progress.failed,
                "skipped": self.progress.skipped
            }
        }


# Главная функция
async def main_async():
    """Асинхронная главная функция"""
    import argparse

    parser = argparse.ArgumentParser(description="Async BSL Indexer - асинхронная индексация BSL файлов")
    parser.add_argument(
        "directory",
        help="Директория с BSL файлами"
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Максимальное количество файлов (default: все файлы)"
    )
    parser.add_argument(
        "--output",
        default="D:/1C-Enterprise_Framework/ai-memory-system/data/index",
        help="Директория для сохранения индекса"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Размер batch для обработки (default: 10)"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Максимальное количество worker threads (default: 4)"
    )
    parser.add_argument(
        "--retry-attempts",
        type=int,
        default=3,
        help="Количество попыток при ошибке (default: 3)"
    )

    args = parser.parse_args()

    # Создание асинхронного индексатора
    indexer = AsyncBSLIndexer(
        output_dir=args.output,
        batch_size=args.batch_size,
        max_workers=args.max_workers,
        retry_attempts=args.retry_attempts
    )

    # Асинхронная индексация
    success_count = await indexer.index_directory_async(
        args.directory,
        max_files=args.max_files
    )

    if success_count > 0:
        # Сохранение индекса
        indexer.save_index()

        # Детальная статистика
        stats = indexer.get_statistics()
        print(f"\n{'='*60}")
        print(f"📊 ИТОГОВАЯ СТАТИСТИКА ИНДЕКСАЦИИ")
        print(f"{'='*60}")
        print(f"📁 Файлов:              {stats['total_files']}")
        print(f"🔧 Функций:             {stats['total_functions']}")
        print(f"📦 Переменных:          {stats['total_variables']}")
        print(f"💾 Размер:              {stats['total_size_mb']:.2f} MB")
        print(f"🤖 Модель:              {stats['embedding_model']}")
        print(f"📏 Размерность:         {stats['embedding_dimension']}")
        print(f"⏱️  Время обработки:     {stats['total_processing_time_sec']:.1f} сек")
        print(f"⚡ Средняя скорость:     {stats['avg_processing_time_ms']:.1f} ms/файл")
        print(f"📈 Файлов/сек:          {stats['files_per_second']:.2f}")
        print(f"\n📊 Типы модулей:")
        for module_type, count in stats['module_types'].items():
            print(f"   {module_type}: {count}")
        print(f"{'='*60}\n")


def main():
    """Точка входа для командной строки"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
