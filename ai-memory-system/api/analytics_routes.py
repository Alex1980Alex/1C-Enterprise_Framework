"""
Analytics REST API Routes
Эндпоинты для анализа зависимостей BSL кода через Neo4j Knowledge Graph
"""

from typing import List, Dict, Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
import logging
import sys
from pathlib import Path

# Добавление путей для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.graph_analytics import (
    GraphAnalyzer,
    CircularDependency,
    Hotspot,
    DeadCode,
    ComplexityMetrics
)

logger = logging.getLogger(__name__)

# Создание router
router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)

# Lazy initialization для GraphAnalyzer
_graph_analyzer: Optional[GraphAnalyzer] = None


def get_graph_analyzer() -> GraphAnalyzer:
    """Получение singleton instance GraphAnalyzer"""
    global _graph_analyzer
    if _graph_analyzer is None:
        _graph_analyzer = GraphAnalyzer(
            neo4j_uri="bolt://localhost:7687",
            neo4j_user="neo4j",
            neo4j_password="password123"
        )
    return _graph_analyzer


# Pydantic Models
class CircularDependencyResponse(BaseModel):
    """Модель циклической зависимости"""
    cycle_path: List[str] = Field(..., description="Путь цикла")
    cycle_length: int = Field(..., description="Длина цикла")
    modules_involved: List[str] = Field(..., description="Вовлеченные модули")
    severity: str = Field(..., description="Критичность: critical, warning, info")


class HotspotResponse(BaseModel):
    """Модель горячей точки"""
    name: str = Field(..., description="Имя функции/процедуры")
    node_type: str = Field(..., description="Тип: Function или Procedure")
    incoming_calls: int = Field(..., description="Количество входящих вызовов")
    outgoing_calls: int = Field(..., description="Количество исходящих вызовов")
    fan_in: int = Field(..., description="Количество модулей, вызывающих эту функцию")
    fan_out: int = Field(..., description="Количество модулей, которые вызывает эта функция")
    severity: str = Field(..., description="Критичность: high, medium, low")


class DeadCodeResponse(BaseModel):
    """Модель мертвого кода"""
    name: str = Field(..., description="Имя функции/процедуры")
    module: str = Field(..., description="Имя модуля")
    node_type: str = Field(..., description="Тип: Function или Procedure")
    is_export: bool = Field(..., description="Экспортируется ли функция")
    reason: str = Field(..., description="Причина")


class ComplexityMetricsResponse(BaseModel):
    """Модель метрик сложности"""
    module_name: str = Field(..., description="Имя модуля")
    file_path: str = Field(..., description="Путь к файлу")
    functions_count: int = Field(..., description="Количество функций")
    procedures_count: int = Field(..., description="Количество процедур")
    total_incoming_calls: int = Field(..., description="Всего входящих вызовов")
    total_outgoing_calls: int = Field(..., description="Всего исходящих вызовов")
    cyclomatic_complexity: int = Field(..., description="Цикломатическая сложность")
    coupling: int = Field(..., description="Связность (количество связанных модулей)")
    cohesion: float = Field(..., description="Cohesion (0-1)")


class AnalyticsSummaryResponse(BaseModel):
    """Общая сводка аналитики"""
    circular_dependencies: Dict = Field(..., description="Статистика по циклическим зависимостям")
    hotspots: Dict = Field(..., description="Статистика по популярным функциям")
    dead_code: Dict = Field(..., description="Статистика по мертвому коду")
    complexity: Dict = Field(..., description="Метрики сложности")


# Endpoints

@router.get(
    "/circular-dependencies",
    response_model=List[CircularDependencyResponse],
    summary="Поиск циклических зависимостей",
    description="Анализирует граф вызовов и находит циклические зависимости между функциями"
)
async def get_circular_dependencies(
    max_depth: int = Query(10, ge=2, le=20, description="Максимальная глубина поиска"),
    min_cycle_length: int = Query(2, ge=2, le=10, description="Минимальная длина цикла")
):
    """
    Поиск циклических зависимостей в графе вызовов

    - **max_depth**: Максимальная глубина поиска циклов (2-20)
    - **min_cycle_length**: Минимальная длина цикла для отчета (2-10)

    Returns:
        Список найденных циклических зависимостей с severity и путями
    """
    try:
        analyzer = get_graph_analyzer()
        cycles = analyzer.find_circular_dependencies(
            max_depth=max_depth,
            min_cycle_length=min_cycle_length
        )

        return [
            CircularDependencyResponse(
                cycle_path=c.cycle_path,
                cycle_length=c.cycle_length,
                modules_involved=c.modules_involved,
                severity=c.severity
            )
            for c in cycles
        ]
    except Exception as e:
        logger.error(f"Error finding circular dependencies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/hotspots",
    response_model=List[HotspotResponse],
    summary="Поиск горячих точек (популярных функций)",
    description="Находит наиболее часто вызываемые функции и процедуры"
)
async def get_hotspots(
    top_n: int = Query(20, ge=5, le=100, description="Количество результатов"),
    min_calls: int = Query(5, ge=1, le=50, description="Минимальное количество вызовов")
):
    """
    Поиск горячих точек (hotspots) - популярных функций

    - **top_n**: Количество топ результатов (5-100)
    - **min_calls**: Минимальное количество вызовов для включения (1-50)

    Returns:
        Список hotspots с метриками вызовов и fan-in/fan-out
    """
    try:
        analyzer = get_graph_analyzer()
        hotspots = analyzer.find_hotspots(
            top_n=top_n,
            min_calls=min_calls
        )

        return [
            HotspotResponse(
                name=h.name,
                node_type=h.node_type,
                incoming_calls=h.incoming_calls,
                outgoing_calls=h.outgoing_calls,
                fan_in=h.fan_in,
                fan_out=h.fan_out,
                severity=h.severity
            )
            for h in hotspots
        ]
    except Exception as e:
        logger.error(f"Error finding hotspots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/dead-code",
    response_model=List[DeadCodeResponse],
    summary="Поиск мертвого кода",
    description="Находит неиспользуемые функции и процедуры"
)
async def get_dead_code(
    include_exports: bool = Query(False, description="Включать ли экспортируемые функции")
):
    """
    Поиск мертвого кода (неиспользуемых функций)

    - **include_exports**: Включать ли экспортируемые функции в результаты

    Returns:
        Список неиспользуемых функций с причинами
    """
    try:
        analyzer = get_graph_analyzer()
        dead_code = analyzer.find_dead_code(
            include_exports=include_exports
        )

        return [
            DeadCodeResponse(
                name=d.name,
                module=d.module,
                node_type=d.node_type,
                is_export=d.is_export,
                reason=d.reason
            )
            for d in dead_code
        ]
    except Exception as e:
        logger.error(f"Error finding dead code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/complexity",
    response_model=List[ComplexityMetricsResponse],
    summary="Метрики сложности модулей",
    description="Вычисляет метрики сложности для модулей: cyclomatic complexity, coupling, cohesion"
)
async def get_complexity_metrics(
    module_name: Optional[str] = Query(None, description="Имя конкретного модуля (опционально)")
):
    """
    Вычисление метрик сложности для модулей

    - **module_name**: Имя конкретного модуля (опционально, если не указано - все модули)

    Returns:
        Список модулей с метриками сложности
    """
    try:
        analyzer = get_graph_analyzer()
        metrics = analyzer.calculate_module_complexity(
            module_name=module_name
        )

        return [
            ComplexityMetricsResponse(
                module_name=m.module_name,
                file_path=m.file_path,
                functions_count=m.functions_count,
                procedures_count=m.procedures_count,
                total_incoming_calls=m.total_incoming_calls,
                total_outgoing_calls=m.total_outgoing_calls,
                cyclomatic_complexity=m.cyclomatic_complexity,
                coupling=m.coupling,
                cohesion=m.cohesion
            )
            for m in metrics
        ]
    except Exception as e:
        logger.error(f"Error calculating complexity metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
    summary="Общая сводка аналитики",
    description="Возвращает сводку по всем видам аналитики: циклы, hotspots, dead code, complexity"
)
async def get_analytics_summary():
    """
    Получение общей сводки по аналитике

    Комбинирует все виды анализа в одном запросе:
    - Циклические зависимости
    - Hotspots (популярные функции)
    - Dead code
    - Complexity metrics

    Returns:
        Полная сводка со статистикой и примерами
    """
    try:
        analyzer = get_graph_analyzer()
        summary = analyzer.get_analytics_summary()

        return AnalyticsSummaryResponse(
            circular_dependencies=summary['circular_dependencies'],
            hotspots=summary['hotspots'],
            dead_code=summary['dead_code'],
            complexity=summary['complexity']
        )
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Health check для Analytics API",
    description="Проверка доступности Neo4j и готовности GraphAnalyzer"
)
async def analytics_health():
    """
    Health check для Analytics API

    Returns:
        Статус подключения к Neo4j и готовность сервиса
    """
    try:
        analyzer = get_graph_analyzer()
        # Простая проверка подключения
        with analyzer.driver.session() as session:
            result = session.run("RETURN 1 as test")
            test = result.single()
            neo4j_ok = test['test'] == 1

        return {
            "status": "healthy" if neo4j_ok else "degraded",
            "neo4j_connected": neo4j_ok,
            "message": "Analytics API is operational"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "neo4j_connected": False,
            "error": str(e)
        }
