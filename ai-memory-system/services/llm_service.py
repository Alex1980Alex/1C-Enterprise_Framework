"""
LLM Service для AI Memory System

Этот сервис обеспечивает:
1. Intent Classification - классификация намерений поискового запроса
2. Results Re-ranking - переранжирование результатов поиска с помощью LLM
3. Code Generation - генерация кода (опционально)

Использует Ollama для работы с локальными LLM моделями:
- DeepSeek-Coder 6.7B - для re-ranking результатов
- Qwen2.5-Coder 7B - для генерации кода
"""

import logging
import requests
import json
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class SearchIntent(Enum):
    """Типы поисковых запросов"""
    FIND_FUNCTION = "find_function"  # Поиск конкретной функции
    FIND_MODULE = "find_module"  # Поиск модуля
    UNDERSTAND_CODE = "understand_code"  # Понимание как работает код
    FIND_EXAMPLES = "find_examples"  # Поиск примеров использования
    DEBUG_ISSUE = "debug_issue"  # Отладка проблемы
    GENERAL_SEARCH = "general_search"  # Общий поиск


@dataclass
class IntentClassification:
    """Результат классификации намерения"""
    intent: SearchIntent
    confidence: float
    reasoning: str
    suggested_filters: Dict[str, Any]


@dataclass
class RerankedResult:
    """Результат после переранжирования"""
    original_index: int
    new_score: float
    original_score: float
    reasoning: str
    result: Dict[str, Any]


class LLMService:
    """
    Сервис для работы с LLM моделями через Ollama

    Основные возможности:
    - Классификация намерений поисковых запросов
    - Переранжирование результатов поиска на основе семантического понимания
    - Генерация кода и пояснений
    """

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        reranking_model: str = "deepseek-coder:6.7b",
        generation_model: str = "deepseek-coder:6.7b",
        timeout: int = 180  # Увеличен до 3 минут для больших моделей
    ):
        """
        Инициализация LLM Service

        Args:
            ollama_url: URL Ollama сервера
            reranking_model: Модель для re-ranking (по умолчанию DeepSeek-Coder 6.7B)
            generation_model: Модель для генерации кода (по умолчанию Qwen2.5-Coder 7B)
            timeout: Таймаут запросов в секундах
        """
        self.ollama_url = ollama_url
        self.reranking_model = reranking_model
        self.generation_model = generation_model
        self.timeout = timeout

        logger.info(f"LLMService инициализирован:")
        logger.info(f"  Ollama URL: {ollama_url}")
        logger.info(f"  Re-ranking model: {reranking_model}")
        logger.info(f"  Generation model: {generation_model}")

        # Проверка доступности Ollama
        self._check_ollama_availability()

    def _check_ollama_availability(self) -> bool:
        """Проверка доступности Ollama сервера"""
        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                logger.info(f"✅ Ollama доступен. Модели: {len(model_names)}")

                # Проверка наличия необходимых моделей
                if self.reranking_model not in model_names:
                    logger.warning(f"⚠️  Модель {self.reranking_model} не найдена")
                if self.generation_model not in model_names:
                    logger.warning(f"⚠️  Модель {self.generation_model} не найдена")

                return True
            else:
                logger.error(f"❌ Ollama вернул статус {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Не удалось подключиться к Ollama: {e}")
            return False

    def classify_intent(self, query: str) -> IntentClassification:
        """
        Классификация намерения поискового запроса

        Args:
            query: Поисковый запрос пользователя

        Returns:
            IntentClassification с типом намерения и рекомендованными фильтрами
        """
        prompt = f"""Проанализируй следующий поисковый запрос в контексте поиска по 1C BSL коду:

Запрос: "{query}"

Определи тип намерения пользователя из следующих категорий:
1. find_function - поиск конкретной функции или процедуры
2. find_module - поиск модуля или файла
3. understand_code - понимание как работает определенная функциональность
4. find_examples - поиск примеров использования
5. debug_issue - отладка проблемы или ошибки
6. general_search - общий поиск без конкретного намерения

Ответь в формате JSON:
{{
  "intent": "<тип намерения>",
  "confidence": <уровень уверенности 0.0-1.0>,
  "reasoning": "<краткое объяснение>",
  "suggested_filters": {{
    "module_types": ["<типы модулей если применимо>"],
    "other_filters": {{}}
  }}
}}"""

        try:
            response = self._call_llm(
                model=self.reranking_model,
                prompt=prompt,
                temperature=0.1  # Низкая температура для более предсказуемых результатов
            )

            # Парсинг JSON ответа
            result = self._extract_json_from_response(response)

            return IntentClassification(
                intent=SearchIntent(result.get("intent", "general_search")),
                confidence=float(result.get("confidence", 0.5)),
                reasoning=result.get("reasoning", ""),
                suggested_filters=result.get("suggested_filters", {})
            )

        except Exception as e:
            logger.error(f"Ошибка классификации намерения: {e}")
            # Возвращаем безопасное значение по умолчанию
            return IntentClassification(
                intent=SearchIntent.GENERAL_SEARCH,
                confidence=0.5,
                reasoning="Ошибка классификации, используется общий поиск",
                suggested_filters={}
            )

    def rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[RerankedResult]:
        """
        Переранжирование результатов поиска с помощью LLM

        Args:
            query: Исходный поисковый запрос
            results: Список результатов для переранжирования
            top_k: Количество лучших результатов для возврата

        Returns:
            Список RerankedResult, отсортированный по релевантности
        """
        if not results:
            return []

        # Ограничиваем количество результатов для LLM (слишком много токенов)
        results_to_rerank = results[:min(20, len(results))]

        # Формируем prompt с результатами
        results_text = self._format_results_for_llm(results_to_rerank)

        prompt = f"""Ты эксперт по 1C BSL коду. Переранжируй результаты поиска по релевантности к запросу.

Запрос пользователя: "{query}"

Результаты поиска (с индексами):
{results_text}

Оцени каждый результат по релевантности к запросу (0.0-1.0).
Учитывай:
- Соответствие названия и описания запросу
- Релевантность типа модуля
- Количество и качество функций в модуле
- Семантическое соответствие

Ответь в формате JSON массива:
[
  {{
    "index": 0,
    "score": 0.95,
    "reasoning": "Очень релевантно потому что..."
  }},
  ...
]

Отсортируй от наиболее релевантного к наименее релевантному."""

        try:
            response = self._call_llm(
                model=self.reranking_model,
                prompt=prompt,
                temperature=0.2
            )

            # Парсинг JSON ответа
            rankings = self._extract_json_from_response(response)

            # Создаем RerankedResult объекты
            reranked = []
            for rank in rankings:
                idx = rank.get("index", 0)
                if 0 <= idx < len(results_to_rerank):
                    reranked.append(RerankedResult(
                        original_index=idx,
                        new_score=float(rank.get("score", 0.5)),
                        original_score=results_to_rerank[idx].get("score", 0.0),
                        reasoning=rank.get("reasoning", ""),
                        result=results_to_rerank[idx]
                    ))

            # Сортируем по новому score
            reranked.sort(key=lambda x: x.new_score, reverse=True)

            return reranked[:top_k]

        except Exception as e:
            logger.error(f"Ошибка переранжирования результатов: {e}")
            # В случае ошибки возвращаем оригинальные результаты
            return [
                RerankedResult(
                    original_index=i,
                    new_score=r.get("score", 0.5),
                    original_score=r.get("score", 0.5),
                    reasoning="Ошибка LLM re-ranking, используется оригинальный score",
                    result=r
                )
                for i, r in enumerate(results[:top_k])
            ]

    def generate_code_explanation(
        self,
        code: str,
        context: str = ""
    ) -> str:
        """
        Генерация объяснения для фрагмента кода

        Args:
            code: Фрагмент кода BSL
            context: Дополнительный контекст (опционально)

        Returns:
            Текстовое объяснение кода
        """
        prompt = f"""Объясни следующий фрагмент 1C BSL кода простым языком:

```bsl
{code}
```

{f"Контекст: {context}" if context else ""}

Объяснение должно быть понятным для разработчика средней квалификации.
Укажи:
1. Что делает этот код
2. Ключевые моменты реализации
3. Возможные проблемы или улучшения (если есть)"""

        try:
            response = self._call_llm(
                model=self.generation_model,
                prompt=prompt,
                temperature=0.3
            )
            return response
        except Exception as e:
            logger.error(f"Ошибка генерации объяснения: {e}")
            return "Не удалось сгенерировать объяснение кода"

    def _call_llm(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Вызов LLM через Ollama API

        Args:
            model: Название модели
            prompt: Текст промпта
            temperature: Температура генерации
            max_tokens: Максимальное количество токенов

        Returns:
            Ответ модели
        """
        url = f"{self.ollama_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        response = requests.post(
            url,
            json=payload,
            timeout=self.timeout
        )

        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

    def _format_results_for_llm(self, results: List[Dict[str, Any]]) -> str:
        """Форматирование результатов для включения в промпт"""
        formatted = []
        for i, result in enumerate(results):
            formatted.append(f"""[{i}] {result.get('file_path', 'Unknown')}
  Тип: {result.get('module_type', 'Unknown')}
  Описание: {result.get('summary', 'Нет описания')[:200]}
  Функций: {result.get('functions_count', 0)}
  Оригинальный score: {result.get('score', 0.0):.3f}""")

        return "\n\n".join(formatted)

    def _extract_json_from_response(self, response: str) -> Any:
        """
        Извлечение JSON из ответа LLM

        LLM иногда возвращает JSON с дополнительным текстом,
        эта функция пытается извлечь чистый JSON
        """
        # Попытка 1: прямой парсинг
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Попытка 2: поиск JSON в тексте между ```json и ```
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end != -1:
                try:
                    return json.loads(response[start:end].strip())
                except json.JSONDecodeError:
                    pass

        # Попытка 3: поиск JSON между { и } или [ и ]
        for start_char, end_char in [('{', '}'), ('[', ']')]:
            start = response.find(start_char)
            end = response.rfind(end_char)
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(response[start:end+1])
                except json.JSONDecodeError:
                    pass

        # Если ничего не помогло, возвращаем пустой dict/list
        logger.warning(f"Не удалось извлечь JSON из ответа LLM: {response[:200]}")
        return {} if '{' in response else []


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service(
    ollama_url: str = "http://localhost:11434",
    reranking_model: str = "deepseek-coder:6.7b",
    generation_model: str = "deepseek-coder:6.7b"
) -> LLMService:
    """
    Получение singleton instance LLMService

    Args:
        ollama_url: URL Ollama сервера
        reranking_model: Модель для re-ranking
        generation_model: Модель для генерации кода

    Returns:
        LLMService instance
    """
    global _llm_service

    if _llm_service is None:
        _llm_service = LLMService(
            ollama_url=ollama_url,
            reranking_model=reranking_model,
            generation_model=generation_model
        )

    return _llm_service
