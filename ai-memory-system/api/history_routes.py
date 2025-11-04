"""
Search History Routes
API endpoints для работы с историей поиска
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

try:
    from history import get_search_history
    from auth import require_api_key
except ModuleNotFoundError:
    from api.history import get_search_history
    from api.auth import require_api_key

logger = logging.getLogger(__name__)

# Создание роутера
router = APIRouter(
    prefix="/api/v1/history",
    tags=["Search History"],
    responses={404: {"description": "Not found"}},
)

# Pydantic модели
class HistoryEntry(BaseModel):
    """Запись истории поиска"""
    id: int = Field(..., description="ID записи")
    timestamp: str = Field(..., description="Время запроса")
    query: str = Field(..., description="Поисковый запрос")
    filters: Optional[Dict[str, Any]] = Field(None, description="Параметры фильтрации")
    results_count: int = Field(..., description="Количество результатов")
    search_time_ms: float = Field(..., description="Время поиска (мс)")
    user_id: Optional[str] = Field(None, description="ID пользователя")


class HistoryResponse(BaseModel):
    """Ответ со списком истории"""
    total: int = Field(..., description="Всего записей")
    returned: int = Field(..., description="Возвращено записей")
    limit: int = Field(..., description="Лимит на страницу")
    offset: int = Field(..., description="Смещение")
    entries: List[HistoryEntry] = Field(..., description="Записи истории")


class HistoryStats(BaseModel):
    """Статистика по истории"""
    total_searches: int = Field(..., description="Всего поисков")
    avg_results: float = Field(..., description="Среднее кол-во результатов")
    avg_search_time: float = Field(..., description="Среднее время поиска (мс)")
    first_search: Optional[str] = Field(None, description="Первый поиск")
    last_search: Optional[str] = Field(None, description="Последний поиск")
    top_queries: List[Dict[str, Any]] = Field(..., description="Топ запросов")


class DeleteResponse(BaseModel):
    """Ответ на удаление"""
    deleted: bool = Field(..., description="Успешно удалено")
    message: str = Field(..., description="Сообщение")


class ClearResponse(BaseModel):
    """Ответ на очистку истории"""
    deleted_count: int = Field(..., description="Количество удаленных записей")
    message: str = Field(..., description="Сообщение")


# Endpoints

@router.get(
    "",
    response_model=HistoryResponse,
    summary="Получить историю поиска",
    description="Возвращает историю поисковых запросов с поддержкой пагинации и фильтрации"
)
async def get_history(
    limit: int = Query(50, ge=1, le=200, description="Максимальное количество записей"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    user_id: Optional[str] = Query(None, description="Фильтр по ID пользователя"),
    query_filter: Optional[str] = Query(None, description="Фильтр по тексту запроса"),
    api_key: str = Depends(require_api_key)
):
    """
    Получить историю поиска с пагинацией

    - **limit**: количество записей на страницу (1-200, по умолчанию 50)
    - **offset**: смещение для пагинации (по умолчанию 0)
    - **user_id**: фильтр по ID пользователя (опционально)
    - **query_filter**: фильтр по тексту запроса, подстрока (опционально)
    """
    try:
        history = get_search_history()

        # Получение записей
        entries = history.get_history(
            limit=limit,
            offset=offset,
            user_id=user_id,
            query_filter=query_filter
        )

        # Получение общего количества
        total = history.get_total_count(user_id=user_id)

        return HistoryResponse(
            total=total,
            returned=len(entries),
            limit=limit,
            offset=offset,
            entries=[HistoryEntry(**entry) for entry in entries]
        )

    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats",
    response_model=HistoryStats,
    summary="Статистика по истории",
    description="Возвращает статистику поисковых запросов"
)
async def get_history_statistics(
    user_id: Optional[str] = Query(None, description="Статистика для конкретного пользователя"),
    api_key: str = Depends(require_api_key)
):
    """
    Получить статистику по истории поиска

    - **user_id**: если указан, статистика только для этого пользователя

    Возвращает:
    - Общее количество поисков
    - Среднее количество результатов
    - Среднее время поиска
    - Время первого и последнего поиска
    - Топ-10 самых частых запросов
    """
    try:
        history = get_search_history()
        stats = history.get_statistics(user_id=user_id)

        return HistoryStats(**stats)

    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{entry_id}",
    response_model=HistoryEntry,
    summary="Получить конкретную запись",
    description="Возвращает конкретную запись из истории по ID"
)
async def get_history_entry(
    entry_id: int,
    api_key: str = Depends(require_api_key)
):
    """
    Получить конкретную запись из истории

    - **entry_id**: ID записи истории
    """
    try:
        history = get_search_history()
        entry = history.get_entry_by_id(entry_id)

        if not entry:
            raise HTTPException(
                status_code=404,
                detail=f"History entry #{entry_id} not found"
            )

        return HistoryEntry(**entry)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get entry #{entry_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{entry_id}",
    response_model=DeleteResponse,
    summary="Удалить запись из истории",
    description="Удаляет конкретную запись из истории по ID"
)
async def delete_history_entry(
    entry_id: int,
    api_key: str = Depends(require_api_key)
):
    """
    Удалить запись из истории

    - **entry_id**: ID записи для удаления
    """
    try:
        history = get_search_history()
        deleted = history.delete_entry(entry_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"History entry #{entry_id} not found"
            )

        return DeleteResponse(
            deleted=True,
            message=f"Entry #{entry_id} deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete entry #{entry_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "",
    response_model=ClearResponse,
    summary="Очистить историю",
    description="Удаляет все записи истории (опционально для конкретного пользователя)"
)
async def clear_history(
    user_id: Optional[str] = Query(None, description="Очистить только для этого пользователя"),
    api_key: str = Depends(require_api_key)
):
    """
    Очистить историю поиска

    - **user_id**: если указан, очищается только история этого пользователя
    """
    try:
        history = get_search_history()
        deleted_count = history.clear_history(user_id=user_id)

        if user_id:
            message = f"Cleared {deleted_count} entries for user {user_id}"
        else:
            message = f"Cleared all {deleted_count} history entries"

        return ClearResponse(
            deleted_count=deleted_count,
            message=message
        )

    except Exception as e:
        logger.error(f"Failed to clear history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
