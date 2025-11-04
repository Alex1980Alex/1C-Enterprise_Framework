"""
Hybrid Search REST API Routes
Endpoints для гибридного поиска (Qdrant + Neo4j)
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
import sys
from pathlib import Path

# Добавление путей
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.hybrid_search_engine import HybridSearchEngine, HybridSearchResult

# Router
router = APIRouter(prefix="/api/v1/hybrid", tags=["Hybrid Search"])

# Глобальный экземпляр
_hybrid_engine: Optional[HybridSearchEngine] = None


def get_hybrid_engine() -> HybridSearchEngine:
    """Получение экземпляра hybrid engine"""
    global _hybrid_engine

    if _hybrid_engine is None:
        _hybrid_engine = HybridSearchEngine()

    return _hybrid_engine


# Pydantic модели
class HybridSearchResponse(BaseModel):
    """Ответ на гибридный поиск"""
    query: str
    total_results: int
    results: List[dict]
    metadata: dict


class GraphRelatedResponse(BaseModel):
    """Ответ на запрос связанных модулей"""
    source_file: str
    related_files: List[str]
    depth: int


class HybridStatsResponse(BaseModel):
    """Статистика гибридной системы"""
    qdrant: dict
    neo4j: dict
    hybrid: dict


@router.get("/search", response_model=HybridSearchResponse)
async def hybrid_search(
    q: str = Query(..., description="Поисковый запрос", min_length=2),
    limit: int = Query(10, description="Количество результатов", ge=1, le=50),
    min_score: float = Query(0.3, description="Минимальный semantic score", ge=0.0, le=1.0),
    include_graph: bool = Query(True, description="Включить graph контекст"),
    semantic_weight: float = Query(0.6, description="Вес semantic search (0-1)", ge=0.0, le=1.0)
):
    """
    Гибридный поиск (Semantic + Graph)

    Объединяет:
    - **Semantic Search** (Qdrant) - поиск по смыслу кода
    - **Graph Search** (Neo4j) - анализ зависимостей

    **Параметры:**
    - **q**: Поисковый запрос
    - **limit**: Количество результатов (1-50)
    - **min_score**: Минимальный semantic score
    - **include_graph**: Включить graph метрики (вызовы, связи)
    - **semantic_weight**: Вес semantic score в итоговом ranking

    **Пример:**
    ```
    GET /api/v1/hybrid/search?q=получить+данные&limit=5&include_graph=true
    ```
    """
    try:
        engine = get_hybrid_engine()

        # Веса для гибридного score
        weights = {
            'semantic': semantic_weight,
            'incoming_calls': (1 - semantic_weight) * 0.5,
            'outgoing_calls': (1 - semantic_weight) * 0.3,
            'connections': (1 - semantic_weight) * 0.2
        }

        # Выполнение поиска
        results = engine.search(
            query=q,
            limit=limit,
            min_semantic_score=min_score,
            include_graph_context=include_graph,
            score_weights=weights
        )

        # Конвертация результатов
        results_dict = []
        for r in results:
            results_dict.append({
                'file_path': r.file_path,
                'module_name': r.module_name,
                'module_type': r.module_type,
                'semantic_score': r.semantic_score,
                'hybrid_score': r.hybrid_score,
                'relevance_label': r.relevance_label,
                'functions_count': r.functions_count,
                'incoming_calls': r.incoming_calls,
                'outgoing_calls': r.outgoing_calls,
                'called_by': r.called_by[:5],  # Top 5
                'calls_to': r.calls_to[:5],
                'related_modules': r.related_modules,
                'preview': r.preview[:200]  # Shortened
            })

        return HybridSearchResponse(
            query=q,
            total_results=len(results_dict),
            results=results_dict,
            metadata={
                'include_graph': include_graph,
                'semantic_weight': semantic_weight,
                'min_score': min_score
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")


@router.get("/related", response_model=GraphRelatedResponse)
async def get_related_modules(
    file_path: str = Query(..., description="Путь к файлу"),
    depth: int = Query(2, description="Глубина поиска в графе", ge=1, le=5),
    limit: int = Query(10, description="Максимум связанных модулей", ge=1, le=50)
):
    """
    Поиск связанных модулей через Knowledge Graph

    Находит модули, связанные через вызовы функций.

    **Параметры:**
    - **file_path**: Путь к исходному файлу
    - **depth**: Глубина поиска (1-5, рекомендуется 2)
    - **limit**: Максимальное количество результатов

    **Пример:**
    ```
    GET /api/v1/hybrid/related?file_path=src/CommonModules/Module.bsl&depth=2
    ```
    """
    try:
        engine = get_hybrid_engine()

        related_files = engine.find_related_by_graph(
            file_path=file_path,
            depth=depth,
            limit=limit
        )

        return GraphRelatedResponse(
            source_file=file_path,
            related_files=related_files,
            depth=depth
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")


@router.get("/stats", response_model=HybridStatsResponse)
async def get_hybrid_statistics():
    """
    Статистика гибридной системы

    Возвращает статистику:
    - **Qdrant**: количество проиндексированных документов
    - **Neo4j**: количество модулей, функций, связей
    - **Hybrid**: покрытие графом, общая статистика

    **Пример:**
    ```
    GET /api/v1/hybrid/stats
    ```
    """
    try:
        engine = get_hybrid_engine()
        stats = engine.get_statistics()

        return HybridStatsResponse(**stats)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")


@router.get("/health")
async def hybrid_health_check():
    """
    Health check гибридной системы

    Проверяет доступность:
    - Qdrant (Semantic Search)
    - Neo4j (Graph Database)

    **Пример:**
    ```
    GET /api/v1/hybrid/health
    ```
    """
    try:
        engine = get_hybrid_engine()
        stats = engine.get_statistics()

        qdrant_ok = stats['qdrant'].get('total_points', 0) > 0
        neo4j_ok = stats['neo4j'].get('modules', 0) > 0

        if qdrant_ok and neo4j_ok:
            return {
                "status": "healthy",
                "qdrant": "available",
                "neo4j": "available",
                "qdrant_documents": stats['qdrant'].get('total_points', 0),
                "neo4j_modules": stats['neo4j'].get('modules', 0),
                "graph_coverage": f"{stats['hybrid']['graph_coverage']*100:.1f}%"
            }
        else:
            return {
                "status": "degraded",
                "qdrant": "available" if qdrant_ok else "unavailable",
                "neo4j": "available" if neo4j_ok else "unavailable"
            }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
