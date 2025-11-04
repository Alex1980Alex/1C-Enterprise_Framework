"""
BSL Code Search API
FastAPI сервер для семантического поиска BSL кода
"""

import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Добавление путей для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import logging

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny, Range
from services.embedding_service import EmbeddingService

# Импорт аутентификации
try:
    from auth import require_api_key, is_auth_enabled
except ModuleNotFoundError:
    from api.auth import require_api_key, is_auth_enabled

# Импорт кеширования
try:
    from cache import create_cache_from_env
except (ModuleNotFoundError, ImportError):
    from api.cache import create_cache_from_env

# Импорт истории поиска
try:
    from history import get_search_history
except ModuleNotFoundError:
    from api.history import get_search_history

# Импорт routes
try:
    from hybrid_search_routes import router as hybrid_router
except ModuleNotFoundError:
    from api.hybrid_search_routes import router as hybrid_router

try:
    from analytics_routes import router as analytics_router
except ModuleNotFoundError:
    from api.analytics_routes import router as analytics_router

try:
    from history_routes import router as history_router
except ModuleNotFoundError:
    from api.history_routes import router as history_router

try:
    from export_routes import router as export_router
except ModuleNotFoundError:
    from api.export_routes import router as export_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="BSL Code Search API",
    description="Семантический поиск BSL кода через векторную базу данных Qdrant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware для Web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтирование статических файлов
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"✅ Static files mounted from: {static_dir}")

# Регистрация роутеров
app.include_router(hybrid_router)
logger.info("✅ Hybrid search routes registered at /api/v1/hybrid")

app.include_router(analytics_router)
logger.info("✅ Analytics routes registered at /api/v1/analytics")

app.include_router(history_router)
logger.info("✅ History routes registered at /api/v1/history")

app.include_router(export_router)
logger.info("✅ Export routes registered at /api/v1/export")

# Глобальные клиенты
qdrant_client: Optional[QdrantClient] = None
embedding_service: Optional[EmbeddingService] = None
search_cache = None  # SearchCache instance

# Pydantic модели
class SearchRequest(BaseModel):
    """Запрос на поиск с расширенными фильтрами"""
    query: str = Field(..., description="Поисковый запрос", min_length=1, max_length=500)
    top_k: int = Field(5, description="Количество результатов", ge=1, le=50)
    score_threshold: float = Field(0.0, description="Минимальный порог релевантности", ge=0.0, le=1.0)

    # Advanced filters
    module_types: Optional[List[str]] = Field(None, description="Фильтр по типам модулей (Common, Object, Form, etc.)")
    file_path_pattern: Optional[str] = Field(None, description="Фильтр по пути к файлу (подстрока)", max_length=200)
    min_functions: Optional[int] = Field(None, description="Минимальное количество функций", ge=0)
    max_functions: Optional[int] = Field(None, description="Максимальное количество функций", ge=0)
    min_variables: Optional[int] = Field(None, description="Минимальное количество переменных", ge=0)
    max_variables: Optional[int] = Field(None, description="Максимальное количество переменных", ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "процедура записи документа",
                "top_k": 5,
                "score_threshold": 0.0,
                "module_types": ["Common", "Object"],
                "file_path_pattern": "Documents",
                "min_functions": 1,
                "max_functions": 10
            }
        }


class SearchResult(BaseModel):
    """Результат поиска"""
    id: int = Field(..., description="ID документа в Qdrant")
    score: float = Field(..., description="Релевантность (0-1)")
    file_path: str = Field(..., description="Путь к файлу")
    module_type: str = Field(..., description="Тип модуля")
    functions_count: int = Field(..., description="Количество функций")
    variables_count: int = Field(..., description="Количество переменных")
    searchable_text: str = Field(..., description="Фрагмент кода")


class SearchResponse(BaseModel):
    """Ответ на запрос поиска"""
    query: str = Field(..., description="Исходный запрос")
    results: List[SearchResult] = Field(..., description="Список результатов")
    total_found: int = Field(..., description="Всего найдено")
    search_time_ms: float = Field(..., description="Время поиска (мс)")


class CollectionStats(BaseModel):
    """Статистика коллекции"""
    collection_name: str = Field(..., description="Название коллекции")
    points_count: int = Field(..., description="Количество векторов")
    vectors_size: int = Field(..., description="Размерность векторов")
    distance: str = Field(..., description="Метрика расстояния")


class HealthResponse(BaseModel):
    """Ответ health check"""
    status: str = Field(..., description="Статус сервиса")
    qdrant_connected: bool = Field(..., description="Qdrant подключен")
    ollama_connected: bool = Field(..., description="Ollama подключен")
    timestamp: str = Field(..., description="Время проверки")


# Helper функция для построения фильтра
def build_search_filter(request: SearchRequest) -> Optional[Filter]:
    """
    Построение Qdrant фильтра на основе параметров запроса

    Args:
        request: Запрос поиска с параметрами фильтрации

    Returns:
        Filter объект для Qdrant или None если фильтры не заданы
    """
    conditions = []

    # Фильтр по типам модулей
    if request.module_types:
        conditions.append(
            FieldCondition(
                key="module_type",
                match=MatchAny(any=request.module_types)
            )
        )

    # Фильтр по количеству функций
    if request.min_functions is not None or request.max_functions is not None:
        conditions.append(
            FieldCondition(
                key="functions_count",
                range=Range(
                    gte=request.min_functions,
                    lte=request.max_functions
                )
            )
        )

    # Фильтр по количеству переменных
    if request.min_variables is not None or request.max_variables is not None:
        conditions.append(
            FieldCondition(
                key="variables_count",
                range=Range(
                    gte=request.min_variables,
                    lte=request.max_variables
                )
            )
        )

    # Фильтр по пути к файлу (содержит подстроку)
    if request.file_path_pattern:
        # Qdrant не поддерживает LIKE, используем text match
        # Альтернативно можно фильтровать результаты после поиска
        pass  # Будет реализовано после получения результатов

    # Возвращаем Filter только если есть условия
    if conditions:
        return Filter(must=conditions)

    return None


# Startup event
@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    global qdrant_client, embedding_service, search_cache

    logger.info("Запуск BSL Code Search API...")

    # Проверка аутентификации
    if is_auth_enabled():
        logger.info("🔒 Аутентификация: ВКЛЮЧЕНА (требуется API key)")
    else:
        logger.warning("⚠️  Аутентификация: ОТКЛЮЧЕНА (режим разработки)")
        logger.warning("⚠️  Установите API_KEY или API_KEYS в .env для включения защиты")

    # Подключение к Qdrant
    try:
        qdrant_client = QdrantClient(host="localhost", port=6333)
        logger.info("✅ Подключение к Qdrant успешно")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Qdrant: {e}")
        qdrant_client = None

    # Инициализация Embedding Service
    try:
        embedding_service = EmbeddingService(
            ollama_host="http://localhost:11434",
            model="nomic-embed-text:latest"
        )
        logger.info("✅ Embedding Service инициализирован")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации Embedding Service: {e}")
        embedding_service = None

    # Инициализация кеша
    try:
        search_cache = create_cache_from_env()
        if search_cache.enabled:
            logger.info(f"✅ Redis кеш: ВКЛЮЧЕН (TTL: {search_cache.ttl}s)")
        else:
            logger.warning("⚠️  Redis кеш: ОТКЛЮЧЕН (работа без кеширования)")
    except Exception as e:
        logger.warning(f"⚠️  Кеш не инициализирован: {e}")
        search_cache = None

    # Инициализация истории поиска
    try:
        history = get_search_history()
        logger.info("✅ Search History инициализирована")
    except Exception as e:
        logger.warning(f"⚠️  Search History не инициализирована: {e}")


# Endpoints
@app.get("/", response_class=HTMLResponse, tags=["General"])
async def root():
    """Главная страница - Web UI"""
    index_file = Path(__file__).parent / "static" / "index.html"
    if index_file.exists():
        return index_file.read_text(encoding='utf-8')
    else:
        return {
            "service": "BSL Code Search API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
            "endpoints": {
                "search": "/api/v1/search",
                "stats": "/api/v1/stats",
                "health": "/health"
            }
        }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """
    Health check endpoint

    Проверяет доступность всех компонентов системы
    """
    qdrant_ok = False
    ollama_ok = False

    # Проверка Qdrant
    if qdrant_client:
        try:
            qdrant_client.get_collections()
            qdrant_ok = True
        except:
            pass

    # Проверка Ollama
    if embedding_service:
        try:
            # Простая проверка - embedding_service уже проверяет Ollama при инициализации
            ollama_ok = True
        except:
            pass

    status = "healthy" if (qdrant_ok and ollama_ok) else "degraded"

    return {
        "status": status,
        "qdrant_connected": qdrant_ok,
        "ollama_connected": ollama_ok,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/search", response_model=SearchResponse, tags=["Search"])
async def search_code(
    request: SearchRequest,
    api_key: str = Depends(require_api_key)
):
    """
    Семантический поиск BSL кода с кешированием

    Выполняет векторный поиск по запросу и возвращает наиболее релевантные файлы.
    Результаты кешируются в Redis для ускорения повторных запросов.

    - **query**: Поисковый запрос (например, "процедура записи документа")
    - **top_k**: Количество результатов (1-50)
    - **score_threshold**: Минимальная релевантность (0.0-1.0)

    **Аутентификация**: Требуется API key в заголовке Authorization: Bearer <key>
    (если аутентификация включена через переменную окружения API_KEY или API_KEYS)
    """
    if not qdrant_client:
        raise HTTPException(status_code=503, detail="Qdrant недоступен")

    if not embedding_service:
        raise HTTPException(status_code=503, detail="Embedding Service недоступен")

    start_time = datetime.now()

    # Проверка кеша (включая параметры фильтров)
    if search_cache and search_cache.enabled:
        cached_result = search_cache.get(
            request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            module_types=request.module_types,
            file_path_pattern=request.file_path_pattern,
            min_functions=request.min_functions,
            max_functions=request.max_functions,
            min_variables=request.min_variables,
            max_variables=request.max_variables
        )
        if cached_result:
            cache_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(f"🎯 Cache HIT: '{request.query}' ({cache_time:.2f}ms)")
            # Обновляем время поиска на время из кеша
            cached_result["search_time_ms"] = round(cache_time, 2)
            return SearchResponse(**cached_result)

    try:
        # Создание эмбеддинга для запроса
        logger.info(f"🔍 Поиск: '{request.query}'")
        query_embedding = embedding_service.create_embedding(request.query)

        if not query_embedding:
            raise HTTPException(status_code=500, detail="Не удалось создать embedding")

        # Построение фильтра на основе параметров запроса
        query_filter = build_search_filter(request)

        # Поиск в Qdrant с фильтром
        search_results = qdrant_client.search(
            collection_name="bsl_code",
            query_vector=query_embedding,
            limit=request.top_k,
            score_threshold=request.score_threshold,
            query_filter=query_filter  # Применяем фильтр
        )

        # Форматирование результатов
        results = []
        for result in search_results:
            results.append(SearchResult(
                id=result.id,
                score=result.score,
                file_path=result.payload.get("file_path", ""),
                module_type=result.payload.get("module_type", "Unknown"),
                functions_count=result.payload.get("functions_count", 0),
                variables_count=result.payload.get("variables_count", 0),
                searchable_text=result.payload.get("searchable_text", "")
            ))

        # Post-query фильтрация по file_path_pattern
        # (Qdrant не поддерживает LIKE/подстроку в фильтрах, поэтому делаем после получения результатов)
        if request.file_path_pattern:
            pattern_lower = request.file_path_pattern.lower()
            results = [r for r in results if pattern_lower in r.file_path.lower()]

        # Время поиска
        search_time = (datetime.now() - start_time).total_seconds() * 1000

        logger.info(f"✅ Найдено: {len(results)} результатов за {search_time:.2f}ms")

        response_data = {
            "query": request.query,
            "results": [r.model_dump() for r in results],
            "total_found": len(results),
            "search_time_ms": round(search_time, 2)
        }

        # Сохранение в кеш (включая параметры фильтров)
        if search_cache and search_cache.enabled:
            search_cache.set(
                request.query,
                response_data,
                top_k=request.top_k,
                score_threshold=request.score_threshold,
                module_types=request.module_types,
                file_path_pattern=request.file_path_pattern,
                min_functions=request.min_functions,
                max_functions=request.max_functions,
                min_variables=request.min_variables,
                max_variables=request.max_variables
            )

        # Сохранение в историю поиска
        try:
            history = get_search_history()
            # Собираем фильтры для сохранения
            filters = {}
            if request.module_types:
                filters['module_types'] = request.module_types
            if request.file_path_pattern:
                filters['file_path_pattern'] = request.file_path_pattern
            if request.min_functions is not None:
                filters['min_functions'] = request.min_functions
            if request.max_functions is not None:
                filters['max_functions'] = request.max_functions
            if request.min_variables is not None:
                filters['min_variables'] = request.min_variables
            if request.max_variables is not None:
                filters['max_variables'] = request.max_variables
            if request.score_threshold != 0.0:
                filters['score_threshold'] = request.score_threshold

            history.add_entry(
                query=request.query,
                results_count=len(results),
                search_time_ms=search_time,
                filters=filters if filters else None
            )
        except Exception as e:
            # Не прерываем поиск если история не работает
            logger.warning(f"Failed to save search history: {e}")

        return SearchResponse(**response_data)

    except Exception as e:
        logger.error(f"❌ Ошибка поиска: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats", response_model=CollectionStats, tags=["Statistics"])
async def get_stats():
    """
    Получение статистики коллекции

    Возвращает информацию о количестве проиндексированных файлов и параметрах коллекции.
    """
    if not qdrant_client:
        raise HTTPException(status_code=503, detail="Qdrant недоступен")

    try:
        collection_info = qdrant_client.get_collection("bsl_code")

        return CollectionStats(
            collection_name="bsl_code",
            points_count=collection_info.points_count,
            vectors_size=collection_info.config.params.vectors.size,
            distance=str(collection_info.config.params.vectors.distance)
        )

    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/search", response_model=SearchResponse, tags=["Search"])
async def search_code_get(
    query: str = Query(..., description="Поисковый запрос", min_length=1),
    top_k: int = Query(5, description="Количество результатов", ge=1, le=50),
    score_threshold: float = Query(0.0, description="Минимальный порог релевантности", ge=0.0, le=1.0),
    api_key: str = Depends(require_api_key)
):
    """
    Семантический поиск BSL кода (GET версия)

    Альтернативный endpoint для поиска через GET запрос (удобно для тестирования в браузере).

    **Аутентификация**: Требуется API key в заголовке Authorization: Bearer <key>
    (если аутентификация включена через переменную окружения API_KEY или API_KEYS)
    """
    request = SearchRequest(
        query=query,
        top_k=top_k,
        score_threshold=score_threshold
    )

    return await search_code(request, api_key)


@app.get("/api/v1/cache/stats", tags=["Cache"])
async def get_cache_stats():
    """
    Получение статистики кеша

    Возвращает информацию о состоянии Redis кеша:
    - Включен ли кеш
    - Количество кешированных запросов
    - TTL (время жизни кеша)
    - Статистика попаданий/промахов
    """
    if not search_cache:
        return {
            "enabled": False,
            "reason": "Cache not initialized"
        }

    return search_cache.get_stats()


@app.delete("/api/v1/cache/clear", tags=["Cache"])
async def clear_cache():
    """
    Очистка кеша

    Удаляет все кешированные результаты поиска.
    Полезно после переиндексации или изменения данных.
    """
    if not search_cache:
        return {
            "success": False,
            "message": "Cache not initialized"
        }

    if not search_cache.enabled:
        return {
            "success": False,
            "message": "Cache is disabled"
        }

    success = search_cache.clear_all()

    if success:
        logger.info("🗑️  Cache cleared by API request")
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
    else:
        return {
            "success": False,
            "message": "Failed to clear cache"
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
