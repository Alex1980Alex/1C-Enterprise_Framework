"""
Embedding Service для векторизации BSL кода
Использует Ollama с моделью nomic-embed-text
"""

import os
import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Сервис для создания векторных представлений BSL кода
    """

    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        model: str = "nomic-embed-text",
        cache_embeddings: bool = True,
        timeout: int = 90
    ):
        """
        Инициализация сервиса

        Args:
            ollama_host: URL Ollama сервера
            model: Модель для создания эмбеддингов
            cache_embeddings: Кэшировать эмбеддинги в памяти
            timeout: Timeout для запросов к Ollama в секундах
        """
        self.ollama_host = ollama_host
        self.model = model
        self.cache_embeddings = cache_embeddings
        self.timeout = timeout
        self.cache: Dict[str, List[float]] = {}

        # Проверка доступности Ollama
        self._check_ollama_health()

        logger.info(f"EmbeddingService инициализирован: {ollama_host}, модель: {model}")

    def _check_ollama_health(self) -> bool:
        """Проверка доступности Ollama"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]

                if self.model not in model_names:
                    logger.warning(f"Модель {self.model} не найдена. Доступны: {model_names}")
                    return False

                logger.info(f"Ollama доступен. Модель {self.model} готова к использованию")
                return True
            else:
                logger.error(f"Ollama недоступен. Status: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка подключения к Ollama: {e}")
            return False

    def create_embedding(self, text: str) -> Optional[List[float]]:
        """
        Создание векторного представления для текста

        Args:
            text: Текст для векторизации (BSL код)

        Returns:
            Вектор эмбеддинга или None при ошибке
        """
        # Проверка кэша
        if self.cache_embeddings and text in self.cache:
            logger.debug(f"Эмбеддинг найден в кэше (длина текста: {len(text)})")
            return self.cache[text]

        try:
            # Запрос к Ollama
            response = requests.post(
                f"{self.ollama_host}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=self.timeout  # Настраиваемый timeout
            )

            if response.status_code == 200:
                embedding = response.json()["embedding"]

                # Кэширование
                if self.cache_embeddings:
                    self.cache[text] = embedding

                logger.debug(f"Создан эмбеддинг размерности {len(embedding)}")
                return embedding
            else:
                logger.error(f"Ошибка создания эмбеддинга: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к Ollama: {e}")
            return None
        except KeyError as e:
            logger.error(f"Неожиданный формат ответа: {e}")
            return None

    def create_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Создание эмбеддингов для списка текстов

        Args:
            texts: Список текстов для векторизации

        Returns:
            Список эмбеддингов (None для текстов с ошибками)
        """
        embeddings = []
        total = len(texts)

        logger.info(f"Создание эмбеддингов для {total} текстов...")

        for i, text in enumerate(texts, 1):
            if i % 10 == 0:
                logger.info(f"Прогресс: {i}/{total} ({i*100//total}%)")

            embedding = self.create_embedding(text)
            embeddings.append(embedding)

        success_count = sum(1 for e in embeddings if e is not None)
        logger.info(f"Завершено. Успешно: {success_count}/{total}")

        return embeddings

    def clear_cache(self):
        """Очистка кэша эмбеддингов"""
        cache_size = len(self.cache)
        self.cache.clear()
        logger.info(f"Кэш очищен. Удалено записей: {cache_size}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Получение статистики кэша

        Returns:
            Словарь со статистикой
        """
        return {
            "cache_size": len(self.cache),
            "cache_enabled": self.cache_embeddings,
            "model": self.model,
            "ollama_host": self.ollama_host
        }

    def save_cache(self, filepath: str):
        """
        Сохранение кэша в файл

        Args:
            filepath: Путь к файлу для сохранения
        """
        try:
            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "model": self.model,
                "cache": self.cache
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Кэш сохранен: {filepath} ({len(self.cache)} записей)")

        except Exception as e:
            logger.error(f"Ошибка сохранения кэша: {e}")

    def load_cache(self, filepath: str) -> bool:
        """
        Загрузка кэша из файла

        Args:
            filepath: Путь к файлу кэша

        Returns:
            True если загрузка успешна
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            if cache_data.get("model") != self.model:
                logger.warning(
                    f"Модель в кэше ({cache_data.get('model')}) "
                    f"не совпадает с текущей ({self.model})"
                )

            self.cache = cache_data.get("cache", {})
            logger.info(f"Кэш загружен: {filepath} ({len(self.cache)} записей)")
            return True

        except FileNotFoundError:
            logger.warning(f"Файл кэша не найден: {filepath}")
            return False
        except Exception as e:
            logger.error(f"Ошибка загрузки кэша: {e}")
            return False


# Пример использования
if __name__ == "__main__":
    # Создание сервиса
    service = EmbeddingService()

    # Тестовый BSL код
    test_code = """
    Процедура ПриЗаписи(Отказ)
        Если НЕ ЗначениеЗаполнено(Дата) Тогда
            Дата = ТекущаяДата();
        КонецЕсли;
    КонецПроцедуры
    """

    # Создание эмбеддинга
    embedding = service.create_embedding(test_code)

    if embedding:
        print(f"✅ Эмбеддинг создан успешно!")
        print(f"   Размерность: {len(embedding)}")
        print(f"   Первые 5 значений: {embedding[:5]}")

    # Статистика
    stats = service.get_cache_stats()
    print(f"\n📊 Статистика:")
    print(f"   Модель: {stats['model']}")
    print(f"   Кэш: {stats['cache_size']} записей")
