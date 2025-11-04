"""
Graph Analytics Module
Анализ зависимостей BSL кода через Neo4j Knowledge Graph
"""

import logging
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CircularDependency:
    """Циклическая зависимость"""
    cycle_path: List[str]  # Путь цикла
    cycle_length: int       # Длина цикла
    modules_involved: List[str]  # Вовлеченные модули
    severity: str          # critical, warning, info


@dataclass
class Hotspot:
    """Горячая точка (популярная функция/модуль)"""
    name: str
    node_type: str  # Function, Procedure, Module
    incoming_calls: int
    outgoing_calls: int
    fan_in: int    # Количество модулей, вызывающих эту функцию
    fan_out: int   # Количество модулей, которые вызывает эта функция
    severity: str  # high, medium, low


@dataclass
class DeadCode:
    """Мертвый код (неиспользуемые функции)"""
    name: str
    module: str
    node_type: str
    is_export: bool
    reason: str  # no_incoming_calls, orphan, etc


@dataclass
class ComplexityMetrics:
    """Метрики сложности модуля"""
    module_name: str
    file_path: str
    functions_count: int
    procedures_count: int
    total_incoming_calls: int
    total_outgoing_calls: int
    cyclomatic_complexity: int  # Приблизительная
    coupling: int  # Количество связанных модулей
    cohesion: float  # 0-1, насколько функции связаны между собой


class GraphAnalyzer:
    """
    Анализатор Knowledge Graph для BSL кода

    Выполняет:
    - Поиск циклических зависимостей
    - Анализ популярных функций (hotspots)
    - Поиск мертвого кода
    - Вычисление метрик сложности
    """

    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password123"
    ):
        """
        Инициализация анализатора

        Args:
            neo4j_uri: URI Neo4j
            neo4j_user: Пользователь
            neo4j_password: Пароль
        """
        self.driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )
        logger.info("GraphAnalyzer инициализирован")

    def close(self):
        """Закрытие подключения"""
        if self.driver:
            self.driver.close()

    def find_circular_dependencies(
        self,
        max_depth: int = 10,
        min_cycle_length: int = 2
    ) -> List[CircularDependency]:
        """
        Поиск циклических зависимостей в графе вызовов

        Args:
            max_depth: Максимальная глубина поиска
            min_cycle_length: Минимальная длина цикла

        Returns:
            Список циклических зависимостей
        """
        logger.info(f"Поиск циклических зависимостей (depth={max_depth})...")

        with self.driver.session() as session:
            # Cypher запрос для поиска циклов
            query = """
                MATCH path = (f1:Function)-[:CALLS*1..%d]->(f1)
                WHERE f1:Function OR f1:Procedure
                WITH path, length(path) as cycle_length
                WHERE cycle_length >= $min_length
                RETURN
                    [node in nodes(path) | node.name] as cycle_path,
                    cycle_length,
                    [node in nodes(path) | node.module] as modules
                ORDER BY cycle_length DESC
                LIMIT 100
            """ % max_depth

            result = session.run(query, min_length=min_cycle_length)

            cycles = []
            seen_cycles = set()

            for record in result:
                cycle_path = record['cycle_path']
                cycle_length = record['cycle_length']
                modules = list(set([m for m in record['modules'] if m]))

                # Нормализация цикла (избежание дубликатов)
                normalized = tuple(sorted(cycle_path))
                if normalized in seen_cycles:
                    continue
                seen_cycles.add(normalized)

                # Определение severity
                if cycle_length >= 5:
                    severity = "critical"
                elif cycle_length >= 3:
                    severity = "warning"
                else:
                    severity = "info"

                cycles.append(CircularDependency(
                    cycle_path=cycle_path,
                    cycle_length=cycle_length,
                    modules_involved=modules,
                    severity=severity
                ))

        logger.info(f"Найдено {len(cycles)} циклических зависимостей")
        return cycles

    def find_hotspots(
        self,
        top_n: int = 20,
        min_calls: int = 5
    ) -> List[Hotspot]:
        """
        Поиск горячих точек (популярных функций)

        Args:
            top_n: Количество топ результатов
            min_calls: Минимальное количество вызовов

        Returns:
            Список hotspots
        """
        logger.info(f"Поиск hotspots (top={top_n}, min_calls={min_calls})...")

        with self.driver.session() as session:
            query = """
                MATCH (f)
                WHERE f:Function OR f:Procedure
                OPTIONAL MATCH (f)<-[incoming:CALLS]-()
                OPTIONAL MATCH (f)-[outgoing:CALLS]->()
                WITH f,
                     count(DISTINCT incoming) as in_calls,
                     count(DISTINCT outgoing) as out_calls
                WHERE in_calls >= $min_calls OR out_calls >= $min_calls

                // Fan-in: сколько РАЗНЫХ модулей вызывают эту функцию
                OPTIONAL MATCH (caller)-[:CALLS]->(f)
                WHERE caller:Function OR caller:Procedure
                OPTIONAL MATCH (m_caller:Module)-[:CONTAINS]->(caller)
                WITH f, in_calls, out_calls,
                     count(DISTINCT m_caller) as fan_in

                // Fan-out: сколько РАЗНЫХ модулей вызывает эта функция
                OPTIONAL MATCH (f)-[:CALLS]->(callee)
                WHERE callee:Function OR callee:Procedure
                OPTIONAL MATCH (m_callee:Module)-[:CONTAINS]->(callee)
                WITH f, in_calls, out_calls, fan_in,
                     count(DISTINCT m_callee) as fan_out

                RETURN
                    f.name as name,
                    labels(f)[0] as node_type,
                    in_calls,
                    out_calls,
                    fan_in,
                    fan_out
                ORDER BY in_calls + out_calls DESC
                LIMIT $top_n
            """

            result = session.run(query, min_calls=min_calls, top_n=top_n)

            hotspots = []
            for record in result:
                in_calls = record['in_calls']
                out_calls = record['out_calls']
                total_calls = in_calls + out_calls

                # Severity на основе количества вызовов
                if total_calls >= 50:
                    severity = "high"
                elif total_calls >= 20:
                    severity = "medium"
                else:
                    severity = "low"

                hotspots.append(Hotspot(
                    name=record['name'],
                    node_type=record['node_type'],
                    incoming_calls=in_calls,
                    outgoing_calls=out_calls,
                    fan_in=record['fan_in'],
                    fan_out=record['fan_out'],
                    severity=severity
                ))

        logger.info(f"Найдено {len(hotspots)} hotspots")
        return hotspots

    def find_dead_code(
        self,
        include_exports: bool = False
    ) -> List[DeadCode]:
        """
        Поиск мертвого кода (неиспользуемые функции)

        Args:
            include_exports: Включать ли экспортируемые функции

        Returns:
            Список мертвого кода
        """
        logger.info("Поиск мертвого кода...")

        with self.driver.session() as session:
            # Поиск функций без входящих вызовов
            query = """
                MATCH (m:Module)-[:CONTAINS]->(f)
                WHERE f:Function OR f:Procedure
                OPTIONAL MATCH (f)<-[incoming:CALLS]-()
                WITH f, m, count(incoming) as in_calls
                WHERE in_calls = 0
            """

            if not include_exports:
                query += " AND (f.is_export = false OR f.is_export IS NULL)"

            query += """
                RETURN
                    f.name as name,
                    m.name as module,
                    labels(f)[0] as node_type,
                    COALESCE(f.is_export, false) as is_export
                ORDER BY module, name
            """

            result = session.run(query)

            dead_code_list = []
            for record in result:
                is_export = record['is_export']

                # Определение причины
                if is_export:
                    reason = "no_incoming_calls_but_exported"
                else:
                    reason = "no_incoming_calls_not_exported"

                dead_code_list.append(DeadCode(
                    name=record['name'],
                    module=record['module'],
                    node_type=record['node_type'],
                    is_export=is_export,
                    reason=reason
                ))

        logger.info(f"Найдено {len(dead_code_list)} неиспользуемых функций")
        return dead_code_list

    def calculate_module_complexity(
        self,
        module_name: Optional[str] = None
    ) -> List[ComplexityMetrics]:
        """
        Вычисление метрик сложности для модулей

        Args:
            module_name: Имя конкретного модуля (опционально)

        Returns:
            Список метрик сложности
        """
        logger.info(f"Вычисление метрик сложности (module={module_name})...")

        with self.driver.session() as session:
            query = """
                MATCH (m:Module)
            """

            if module_name:
                query += " WHERE m.name = $module_name"

            query += """
                OPTIONAL MATCH (m)-[:CONTAINS]->(f:Function)
                OPTIONAL MATCH (m)-[:CONTAINS]->(p:Procedure)
                WITH m,
                     count(DISTINCT f) as func_count,
                     count(DISTINCT p) as proc_count

                // Входящие вызовы к функциям модуля
                OPTIONAL MATCH (m)-[:CONTAINS]->(func)
                WHERE func:Function OR func:Procedure
                OPTIONAL MATCH (func)<-[in_call:CALLS]-()
                WITH m, func_count, proc_count,
                     count(DISTINCT in_call) as total_in

                // Исходящие вызовы из функций модуля
                OPTIONAL MATCH (m)-[:CONTAINS]->(func2)
                WHERE func2:Function OR func2:Procedure
                OPTIONAL MATCH (func2)-[out_call:CALLS]->()
                WITH m, func_count, proc_count, total_in,
                     count(DISTINCT out_call) as total_out

                // Coupling: количество связанных модулей
                OPTIONAL MATCH (m)-[:CONTAINS]->(f1)
                WHERE f1:Function OR f1:Procedure
                OPTIONAL MATCH (f1)-[:CALLS]-(f2)
                WHERE f2:Function OR f2:Procedure
                OPTIONAL MATCH (m2:Module)-[:CONTAINS]->(f2)
                WHERE m2 <> m
                WITH m, func_count, proc_count, total_in, total_out,
                     count(DISTINCT m2) as coupling

                RETURN
                    m.name as module_name,
                    m.file_path as file_path,
                    func_count,
                    proc_count,
                    total_in,
                    total_out,
                    coupling
                ORDER BY total_in + total_out DESC
            """

            params = {}
            if module_name:
                params['module_name'] = module_name

            result = session.run(query, **params)

            metrics_list = []
            for record in result:
                func_count = record['func_count']
                proc_count = record['proc_count']
                total_count = func_count + proc_count

                # Приблизительная cyclomatic complexity
                # Базируется на количестве функций и их взаимодействий
                cyclomatic = total_count + record['total_out']

                # Cohesion: насколько функции модуля связаны между собой
                # Упрощенная формула: отношение внутренних связей к возможным
                if total_count > 1:
                    max_possible_connections = total_count * (total_count - 1)
                    internal_connections = record['total_out']  # Упрощение
                    cohesion = min(internal_connections / max_possible_connections, 1.0)
                else:
                    cohesion = 1.0

                metrics_list.append(ComplexityMetrics(
                    module_name=record['module_name'],
                    file_path=record['file_path'],
                    functions_count=func_count,
                    procedures_count=proc_count,
                    total_incoming_calls=record['total_in'],
                    total_outgoing_calls=record['total_out'],
                    cyclomatic_complexity=cyclomatic,
                    coupling=record['coupling'],
                    cohesion=round(cohesion, 3)
                ))

        logger.info(f"Вычислено метрик для {len(metrics_list)} модулей")
        return metrics_list

    def get_analytics_summary(self) -> Dict:
        """
        Получение общей сводки по аналитике

        Returns:
            Словарь со статистикой
        """
        logger.info("Получение сводки по аналитике...")

        cycles = self.find_circular_dependencies(max_depth=5, min_cycle_length=2)
        hotspots = self.find_hotspots(top_n=10, min_calls=5)
        dead_code = self.find_dead_code(include_exports=False)
        complexity = self.calculate_module_complexity()

        # Топ самых сложных модулей
        top_complex = sorted(
            complexity,
            key=lambda x: x.cyclomatic_complexity,
            reverse=True
        )[:5]

        # Топ самых связанных модулей (high coupling)
        top_coupled = sorted(
            complexity,
            key=lambda x: x.coupling,
            reverse=True
        )[:5]

        return {
            'circular_dependencies': {
                'total': len(cycles),
                'critical': len([c for c in cycles if c.severity == 'critical']),
                'warning': len([c for c in cycles if c.severity == 'warning']),
                'examples': [
                    {
                        'path': c.cycle_path[:5],  # Первые 5 узлов
                        'length': c.cycle_length,
                        'severity': c.severity
                    }
                    for c in cycles[:3]
                ]
            },
            'hotspots': {
                'total': len(hotspots),
                'high_severity': len([h for h in hotspots if h.severity == 'high']),
                'top_functions': [
                    {
                        'name': h.name,
                        'incoming_calls': h.incoming_calls,
                        'outgoing_calls': h.outgoing_calls,
                        'fan_in': h.fan_in
                    }
                    for h in hotspots[:5]
                ]
            },
            'dead_code': {
                'total': len(dead_code),
                'by_type': {
                    'functions': len([d for d in dead_code if d.node_type == 'Function']),
                    'procedures': len([d for d in dead_code if d.node_type == 'Procedure'])
                },
                'examples': [
                    {
                        'name': d.name,
                        'module': d.module,
                        'reason': d.reason
                    }
                    for d in dead_code[:5]
                ]
            },
            'complexity': {
                'total_modules': len(complexity),
                'avg_cyclomatic': round(sum(c.cyclomatic_complexity for c in complexity) / len(complexity), 2) if complexity else 0,
                'avg_coupling': round(sum(c.coupling for c in complexity) / len(complexity), 2) if complexity else 0,
                'top_complex_modules': [
                    {
                        'name': c.module_name,
                        'cyclomatic': c.cyclomatic_complexity,
                        'coupling': c.coupling,
                        'cohesion': c.cohesion
                    }
                    for c in top_complex
                ],
                'high_coupling_modules': [
                    {
                        'name': c.module_name,
                        'coupling': c.coupling,
                        'functions': c.functions_count + c.procedures_count
                    }
                    for c in top_coupled
                ]
            }
        }


class GraphAnalyticsService:
    """
    MCP-совместимый сервис для анализа графа зависимостей

    Предоставляет упрощенный интерфейс для MCP server:
    - get_dependencies(file_path) - зависимости файла
    - calculate_centrality() - важность модулей
    - detect_communities() - группы связанных модулей
    """

    def __init__(self, neo4j_service):
        """
        Инициализация через Neo4j service

        Args:
            neo4j_service: Экземпляр Neo4jService с подключением
        """
        self.neo4j = neo4j_service
        self.driver = neo4j_service.driver if neo4j_service else None
        logger.info("GraphAnalyticsService инициализирован")

    def get_dependencies(self, file_path: str) -> Dict:
        """
        Получить зависимости для конкретного файла

        Args:
            file_path: Путь к файлу BSL

        Returns:
            Dict с 'imports' и 'imported_by'
        """
        if not self.driver:
            logger.warning("Neo4j не подключен")
            return {'imports': [], 'imported_by': []}

        with self.driver.session() as session:
            # Найти модуль по пути
            query = """
                MATCH (m:Module {file_path: $file_path})

                // Исходящие зависимости (что импортирует этот модуль)
                OPTIONAL MATCH (m)-[:CONTAINS]->(f1)
                WHERE f1:Function OR f1:Procedure
                OPTIONAL MATCH (f1)-[:CALLS]->(f2)
                WHERE f2:Function OR f2:Procedure
                OPTIONAL MATCH (m2:Module)-[:CONTAINS]->(f2)
                WHERE m2 <> m
                WITH m, collect(DISTINCT m2.file_path) as imports

                // Входящие зависимости (что импортирует этот модуль)
                OPTIONAL MATCH (m3:Module)-[:CONTAINS]->(f3)
                WHERE f3:Function OR f3:Procedure
                OPTIONAL MATCH (f3)-[:CALLS]->(f4)
                WHERE f4:Function OR f4:Procedure
                OPTIONAL MATCH (m)-[:CONTAINS]->(f4)
                WHERE m3 <> m

                RETURN
                    imports,
                    collect(DISTINCT m3.file_path) as imported_by
            """

            result = session.run(query, file_path=file_path)
            record = result.single()

            if not record:
                logger.warning(f"Модуль не найден: {file_path}")
                return {'imports': [], 'imported_by': []}

            return {
                'imports': [imp for imp in record['imports'] if imp],
                'imported_by': [imp for imp in record['imported_by'] if imp]
            }

    def calculate_centrality(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Рассчитать центральность модулей (важность)

        Args:
            top_n: Количество топ результатов

        Returns:
            List[(module_path, centrality_score)]
        """
        if not self.driver:
            logger.warning("Neo4j не подключен")
            return []

        with self.driver.session() as session:
            # PageRank-подобная метрика на основе входящих связей
            query = """
                MATCH (m:Module)

                // Подсчет входящих вызовов к функциям модуля
                OPTIONAL MATCH (m)-[:CONTAINS]->(f)
                WHERE f:Function OR f:Procedure
                OPTIONAL MATCH (caller)-[:CALLS]->(f)
                WHERE caller:Function OR caller:Procedure
                OPTIONAL MATCH (m_caller:Module)-[:CONTAINS]->(caller)
                WHERE m_caller <> m

                WITH m, count(DISTINCT m_caller) as incoming_modules

                // Подсчет исходящих вызовов из функций модуля
                OPTIONAL MATCH (m)-[:CONTAINS]->(f2)
                WHERE f2:Function OR f2:Procedure
                OPTIONAL MATCH (f2)-[:CALLS]->(callee)
                WHERE callee:Function OR callee:Procedure
                OPTIONAL MATCH (m_callee:Module)-[:CONTAINS]->(callee)
                WHERE m_callee <> m

                WITH m, incoming_modules, count(DISTINCT m_callee) as outgoing_modules

                // Centrality = входящие связи * 2 + исходящие связи
                // (входящие важнее, т.к. показывают популярность)
                WITH m,
                     incoming_modules * 2.0 + outgoing_modules as centrality_score

                WHERE centrality_score > 0

                RETURN
                    m.file_path as module,
                    centrality_score
                ORDER BY centrality_score DESC
                LIMIT $top_n
            """

            result = session.run(query, top_n=top_n)

            centrality_list = []
            for record in result:
                module = record['module']
                score = float(record['centrality_score'])
                centrality_list.append((module, score))

            logger.info(f"Рассчитана центральность для {len(centrality_list)} модулей")
            return centrality_list

    def detect_communities(self, max_communities: int = 10) -> List[List[str]]:
        """
        Обнаружить сообщества (группы связанных модулей)

        Args:
            max_communities: Максимальное количество сообществ

        Returns:
            List[List[module_path]] - список сообществ
        """
        if not self.driver:
            logger.warning("Neo4j не подключен")
            return []

        with self.driver.session() as session:
            # Упрощенная кластеризация на основе связности
            query = """
                MATCH (m1:Module)-[:CONTAINS]->(f1)
                WHERE f1:Function OR f1:Procedure
                MATCH (f1)-[:CALLS]->(f2)
                WHERE f2:Function OR f2:Procedure
                MATCH (m2:Module)-[:CONTAINS]->(f2)
                WHERE m1 <> m2

                WITH m1, m2, count(*) as connection_strength
                WHERE connection_strength >= 2

                // Группировка по связности
                WITH m1, collect({module: m2.file_path, strength: connection_strength}) as connected_modules

                RETURN
                    m1.file_path as core_module,
                    [x in connected_modules | x.module] as community_members
                ORDER BY size(community_members) DESC
                LIMIT $max_communities
            """

            result = session.run(query, max_communities=max_communities)

            communities = []
            seen_modules = set()

            for record in result:
                core = record['core_module']
                members = record['community_members']

                # Избежать дубликатов
                if core in seen_modules:
                    continue

                community = [core] + [m for m in members if m not in seen_modules]
                communities.append(community)

                seen_modules.update(community)

            logger.info(f"Обнаружено {len(communities)} сообществ")
            return communities


# Пример использования
if __name__ == "__main__":
    logger.info("Testing Graph Analytics...")

    analyzer = GraphAnalyzer()

    try:
        # Получение общей сводки
        logger.info("\n=== Analytics Summary ===")
        summary = analyzer.get_analytics_summary()

        import json
        print(json.dumps(summary, indent=2, ensure_ascii=False))

        logger.info("\n✅ Analytics completed!")

    finally:
        analyzer.close()
