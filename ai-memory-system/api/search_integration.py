"""
Search Integration для FastAPI
Интеграция семантического поиска с REST API

Endpoints:
- GET /api/v1/search - Semantic search
- GET /api/v1/search/similar - Find similar code
- GET /api/v1/collections/stats - Collection statistics
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
import sys
from pathlib import Path

# Добавление путей для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.search.semantic_search_enhanced import SemanticSearchEngine, SearchResult as EngineSearchResult


# Pydantic модели
class SearchResultModel(BaseModel):
    """Модель результата поиска"""
    file_path: str
    module_type: str
    score: float
    functions_count: int
    variables_count: int
    preview: str
    file_size: int
    indexed_at: str
    relevance_label: str


class SearchResponse(BaseModel):
    """Ответ на поисковый запрос"""
    query: str
    total_results: int
    results: List[SearchResultModel]
    filters_applied: dict


class CollectionStats(BaseModel):
    """Статистика коллекции"""
    collection_name: str
    total_points: int
    vector_size: int
    distance_metric: str
    status: str


# Router
router = APIRouter(prefix="/api/v1", tags=["search"])

# Глобальный экземпляр поискового движка
search_engine: Optional[SemanticSearchEngine] = None


def get_search_engine() -> SemanticSearchEngine:
    """Получение экземпляра поискового движка"""
    global search_engine

    if search_engine is None:
        search_engine = SemanticSearchEngine(
            qdrant_url="http://localhost:6333",
            collection_name="bsl_code"
        )

    return search_engine


@router.get("/search", response_model=SearchResponse)
async def search_code(
    q: str = Query(..., description="Поисковый запрос", min_length=2),
    limit: int = Query(10, description="Количество результатов", ge=1, le=50),
    min_score: float = Query(0.3, description="Минимальный score", ge=0.0, le=1.0),
    module_type: Optional[str] = Query(None, description="Фильтр по типу модуля"),
    min_functions: Optional[int] = Query(None, description="Минимальное количество функций", ge=0)
):
    """
    Семантический поиск BSL кода

    **Примеры запросов:**
    - `получить данные из базы`
    - `обработка документа поступление`
    - `формирование отчета`
    - `работа с регистрами`

    **Параметры:**
    - **q**: Поисковый запрос (обязательный)
    - **limit**: Количество результатов (1-50, default: 10)
    - **min_score**: Минимальный score релевантности (0.0-1.0, default: 0.3)
    - **module_type**: Фильтр по типу модуля (optional)
    - **min_functions**: Минимальное количество функций (optional)
    """
    try:
        engine = get_search_engine()

        # Выполнение поиска
        results = engine.search(
            query=q,
            limit=limit,
            min_score=min_score,
            module_type=module_type,
            min_functions=min_functions
        )

        # Конвертация результатов
        search_results = [
            SearchResultModel(
                file_path=r.file_path,
                module_type=r.module_type,
                score=r.score,
                functions_count=r.functions_count,
                variables_count=r.variables_count,
                preview=r.preview,
                file_size=r.file_size,
                indexed_at=r.indexed_at,
                relevance_label=r.relevance_label
            )
            for r in results
        ]

        # Формирование ответа
        return SearchResponse(
            query=q,
            total_results=len(search_results),
            results=search_results,
            filters_applied={
                "module_type": module_type,
                "min_functions": min_functions,
                "min_score": min_score
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")


@router.post("/search/similar", response_model=SearchResponse)
async def search_similar_code(
    code_snippet: str = Query(..., description="Фрагмент кода для поиска"),
    limit: int = Query(5, description="Количество результатов", ge=1, le=20)
):
    """
    Поиск похожего кода

    Позволяет найти файлы с похожим кодом на основе предоставленного фрагмента.

    **Пример использования:**
    ```json
    {
      "code_snippet": "Функция ПолучитьДанныеИзБазы()\\n    Запрос = Новый Запрос;\\n    Возврат Запрос.Выполнить();\\nКонецФункции"
    }
    ```
    """
    try:
        engine = get_search_engine()

        # Поиск похожего кода
        results = engine.search_similar_code(
            code_snippet=code_snippet,
            limit=limit
        )

        # Конвертация результатов
        search_results = [
            SearchResultModel(
                file_path=r.file_path,
                module_type=r.module_type,
                score=r.score,
                functions_count=r.functions_count,
                variables_count=r.variables_count,
                preview=r.preview,
                file_size=r.file_size,
                indexed_at=r.indexed_at,
                relevance_label=r.relevance_label
            )
            for r in results
        ]

        return SearchResponse(
            query=f"[Code Similarity Search] {code_snippet[:50]}...",
            total_results=len(search_results),
            results=search_results,
            filters_applied={"search_type": "code_similarity"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")


@router.get("/collections/stats", response_model=CollectionStats)
async def get_collection_statistics():
    """
    Получение статистики коллекции

    Возвращает информацию о коллекции BSL кода в Qdrant:
    - Количество проиндексированных файлов
    - Размер векторов
    - Метрика расстояния
    - Статус коллекции
    """
    try:
        engine = get_search_engine()
        stats = engine.get_statistics()

        if not stats:
            raise HTTPException(status_code=404, detail="Коллекция не найдена")

        return CollectionStats(**stats)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")


# Health check для поисковой системы
@router.get("/search/health")
async def search_health_check():
    """
    Проверка работоспособности поисковой системы

    Проверяет доступность Qdrant и наличие коллекции
    """
    try:
        engine = get_search_engine()
        stats = engine.get_statistics()

        if stats and stats.get('total_points', 0) > 0:
            return {
                "status": "healthy",
                "qdrant": "available",
                "collection": "ready",
                "total_documents": stats.get('total_points', 0)
            }
        else:
            return {
                "status": "degraded",
                "qdrant": "available",
                "collection": "empty or not found",
                "total_documents": 0
            }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
