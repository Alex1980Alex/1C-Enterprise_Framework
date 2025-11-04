"""
Export Routes
API endpoints для экспорта результатов поиска и истории
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
import logging
import io

try:
    from export import SearchResultsExporter, HistoryExporter
    from history import get_search_history
    from auth import require_api_key
except ModuleNotFoundError:
    from api.export import SearchResultsExporter, HistoryExporter
    from api.history import get_search_history
    from api.auth import require_api_key

logger = logging.getLogger(__name__)

# Создание роутера
router = APIRouter(
    prefix="/api/v1/export",
    tags=["Export"],
    responses={404: {"description": "Not found"}},
)


# Pydantic модели
class ExportSearchRequest(BaseModel):
    """Запрос на экспорт результатов поиска"""
    results: List[Dict[str, Any]] = Field(..., description="Результаты поиска для экспорта")
    query: str = Field("", description="Поисковый запрос (для метаданных)")
    format: Literal["csv", "json", "excel"] = Field("csv", description="Формат экспорта")
    include_code: bool = Field(False, description="Включать код функций (только для JSON)")


class ExportResponse(BaseModel):
    """Информация о экспорте"""
    success: bool = Field(..., description="Успешность экспорта")
    format: str = Field(..., description="Формат экспорта")
    size_bytes: int = Field(..., description="Размер файла в байтах")
    records_count: int = Field(..., description="Количество записей")


# Endpoints для экспорта результатов поиска

@router.post(
    "/search/csv",
    summary="Экспорт результатов в CSV",
    description="Экспортирует результаты поиска в CSV формат",
    response_class=Response
)
async def export_search_csv(
    results: List[Dict[str, Any]] = Body(..., description="Результаты для экспорта"),
    query: str = Body("", description="Поисковый запрос"),
    api_key: str = Depends(require_api_key)
):
    """
    Экспорт результатов поиска в CSV

    - **results**: Массив результатов поиска
    - **query**: Поисковый запрос (опционально)

    Returns:
        CSV файл для скачивания
    """
    try:
        exporter = SearchResultsExporter()
        csv_content = exporter.to_csv(results, query)

        return Response(
            content=csv_content,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=search_results.csv"
            }
        )

    except Exception as e:
        logger.error(f"Failed to export to CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/search/json",
    summary="Экспорт результатов в JSON",
    description="Экспортирует результаты поиска в JSON формат",
    response_class=Response
)
async def export_search_json(
    results: List[Dict[str, Any]] = Body(..., description="Результаты для экспорта"),
    query: str = Body("", description="Поисковый запрос"),
    include_code: bool = Body(False, description="Включать код функций"),
    api_key: str = Depends(require_api_key)
):
    """
    Экспорт результатов поиска в JSON

    - **results**: Массив результатов поиска
    - **query**: Поисковый запрос (опционально)
    - **include_code**: Включать ли код функций/процедур

    Returns:
        JSON файл для скачивания
    """
    try:
        exporter = SearchResultsExporter()
        json_content = exporter.to_json(results, query, include_code)

        return Response(
            content=json_content,
            media_type="application/json; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=search_results.json"
            }
        )

    except Exception as e:
        logger.error(f"Failed to export to JSON: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/search/excel",
    summary="Экспорт результатов в Excel",
    description="Экспортирует результаты поиска в Excel формат (.xlsx)",
    response_class=Response
)
async def export_search_excel(
    results: List[Dict[str, Any]] = Body(..., description="Результаты для экспорта"),
    query: str = Body("", description="Поисковый запрос"),
    api_key: str = Depends(require_api_key)
):
    """
    Экспорт результатов поиска в Excel

    - **results**: Массив результатов поиска
    - **query**: Поисковый запрос (опционально)

    Returns:
        Excel файл (.xlsx) для скачивания
    """
    try:
        exporter = SearchResultsExporter()
        excel_bytes = exporter.to_excel(results, query)

        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=search_results.xlsx"
            }
        )

    except RuntimeError as e:
        logger.error(f"Excel export not available: {e}")
        raise HTTPException(
            status_code=501,
            detail="Excel export requires openpyxl library. Install with: pip install openpyxl"
        )
    except Exception as e:
        logger.error(f"Failed to export to Excel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoints для экспорта истории поиска

@router.get(
    "/history/csv",
    summary="Экспорт истории в CSV",
    description="Экспортирует историю поиска в CSV формат",
    response_class=Response
)
async def export_history_csv(
    limit: int = Query(1000, ge=1, le=10000, description="Максимальное количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    user_id: Optional[str] = Query(None, description="Фильтр по пользователю"),
    query_filter: Optional[str] = Query(None, description="Фильтр по запросу"),
    api_key: str = Depends(require_api_key)
):
    """
    Экспорт истории поиска в CSV

    - **limit**: Максимальное количество записей (1-10000)
    - **offset**: Смещение для пагинации
    - **user_id**: Фильтр по ID пользователя (опционально)
    - **query_filter**: Фильтр по тексту запроса (опционально)

    Returns:
        CSV файл для скачивания
    """
    try:
        history = get_search_history()
        entries = history.get_history(
            limit=limit,
            offset=offset,
            user_id=user_id,
            query_filter=query_filter
        )

        exporter = HistoryExporter()
        csv_content = exporter.to_csv(entries)

        return Response(
            content=csv_content,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=search_history.csv"
            }
        )

    except Exception as e:
        logger.error(f"Failed to export history to CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/history/json",
    summary="Экспорт истории в JSON",
    description="Экспортирует историю поиска в JSON формат",
    response_class=Response
)
async def export_history_json(
    limit: int = Query(1000, ge=1, le=10000, description="Максимальное количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    user_id: Optional[str] = Query(None, description="Фильтр по пользователю"),
    query_filter: Optional[str] = Query(None, description="Фильтр по запросу"),
    api_key: str = Depends(require_api_key)
):
    """
    Экспорт истории поиска в JSON

    - **limit**: Максимальное количество записей (1-10000)
    - **offset**: Смещение для пагинации
    - **user_id**: Фильтр по ID пользователя (опционально)
    - **query_filter**: Фильтр по тексту запроса (опционально)

    Returns:
        JSON файл для скачивания
    """
    try:
        history = get_search_history()
        entries = history.get_history(
            limit=limit,
            offset=offset,
            user_id=user_id,
            query_filter=query_filter
        )

        exporter = HistoryExporter()
        json_content = exporter.to_json(entries)

        return Response(
            content=json_content,
            media_type="application/json; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=search_history.json"
            }
        )

    except Exception as e:
        logger.error(f"Failed to export history to JSON: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/history/excel",
    summary="Экспорт истории в Excel",
    description="Экспортирует историю поиска в Excel формат (.xlsx)",
    response_class=Response
)
async def export_history_excel(
    limit: int = Query(1000, ge=1, le=10000, description="Максимальное количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    user_id: Optional[str] = Query(None, description="Фильтр по пользователю"),
    query_filter: Optional[str] = Query(None, description="Фильтр по запросу"),
    api_key: str = Depends(require_api_key)
):
    """
    Экспорт истории поиска в Excel

    - **limit**: Максимальное количество записей (1-10000)
    - **offset**: Смещение для пагинации
    - **user_id**: Фильтр по ID пользователя (опционально)
    - **query_filter**: Фильтр по тексту запроса (опционально)

    Returns:
        Excel файл (.xlsx) для скачивания
    """
    try:
        history = get_search_history()
        entries = history.get_history(
            limit=limit,
            offset=offset,
            user_id=user_id,
            query_filter=query_filter
        )

        exporter = HistoryExporter()
        excel_bytes = exporter.to_excel(entries)

        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=search_history.xlsx"
            }
        )

    except RuntimeError as e:
        logger.error(f"Excel export not available: {e}")
        raise HTTPException(
            status_code=501,
            detail="Excel export requires openpyxl library. Install with: pip install openpyxl"
        )
    except Exception as e:
        logger.error(f"Failed to export history to Excel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Universal export endpoint
@router.post(
    "/search",
    summary="Универсальный экспорт результатов",
    description="Экспортирует результаты поиска в выбранном формате",
    response_class=Response
)
async def export_search_universal(
    request: ExportSearchRequest,
    api_key: str = Depends(require_api_key)
):
    """
    Универсальный endpoint для экспорта результатов

    Поддерживает три формата:
    - **csv**: Простой CSV для Excel
    - **json**: JSON с возможностью включения кода
    - **excel**: Форматированный .xlsx файл

    Returns:
        Файл в выбранном формате
    """
    try:
        exporter = SearchResultsExporter()

        if request.format == "csv":
            content = exporter.to_csv(request.results, request.query)
            media_type = "text/csv; charset=utf-8"
            filename = "search_results.csv"

        elif request.format == "json":
            content = exporter.to_json(request.results, request.query, request.include_code)
            media_type = "application/json; charset=utf-8"
            filename = "search_results.json"

        elif request.format == "excel":
            content = exporter.to_excel(request.results, request.query)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = "search_results.xlsx"

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {request.format}"
            )

        return Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except RuntimeError as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to export: {e}")
        raise HTTPException(status_code=500, detail=str(e))
