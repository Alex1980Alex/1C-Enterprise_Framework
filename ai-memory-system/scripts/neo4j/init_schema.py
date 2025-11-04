"""
Инициализация схемы Knowledge Graph в Neo4j
Создание constraints, indexes и базовой структуры
"""

from neo4j import GraphDatabase
import logging
from typing import List, Dict
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jSchemaInitializer:
    """Класс для инициализации схемы Neo4j"""

    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password123"):
        """
        Инициализация

        Args:
            uri: URI подключения
            user: Пользователь
            password: Пароль
        """
        self.uri = uri
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info(f"✅ Подключение к Neo4j: {uri}")

    def close(self):
        """Закрытие подключения"""
        if self.driver:
            self.driver.close()
            logger.info("🔌 Подключение закрыто")

    def clear_database(self, confirm=False):
        """
        Очистка всей базы данных

        Args:
            confirm: Подтверждение очистки
        """
        if not confirm:
            logger.warning("⚠️  Очистка БД требует подтверждения (confirm=True)")
            return

        logger.warning("🗑️  Очистка базы данных...")
        with self.driver.session() as session:
            # Удаление всех узлов и связей
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("✅ База данных очищена")

    def create_constraints(self):
        """Создание constraints для уникальности ID"""
        logger.info("\n📌 Создание constraints...")

        constraints = [
            "CREATE CONSTRAINT project_id_unique IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT module_id_unique IF NOT EXISTS FOR (m:Module) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT function_id_unique IF NOT EXISTS FOR (f:Function) REQUIRE f.id IS UNIQUE",
            "CREATE CONSTRAINT procedure_id_unique IF NOT EXISTS FOR (p:Procedure) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT variable_id_unique IF NOT EXISTS FOR (v:Variable) REQUIRE v.id IS UNIQUE",
            "CREATE CONSTRAINT query_id_unique IF NOT EXISTS FOR (q:Query) REQUIRE q.id IS UNIQUE",

            # Constraints на обязательные свойства
            "CREATE CONSTRAINT module_name_exists IF NOT EXISTS FOR (m:Module) REQUIRE m.name IS NOT NULL",
            "CREATE CONSTRAINT function_name_exists IF NOT EXISTS FOR (f:Function) REQUIRE f.name IS NOT NULL",
            "CREATE CONSTRAINT procedure_name_exists IF NOT EXISTS FOR (p:Procedure) REQUIRE p.name IS NOT NULL",
        ]

        with self.driver.session() as session:
            created = 0
            for constraint in constraints:
                try:
                    session.run(constraint)
                    created += 1
                    constraint_name = constraint.split()[2]  # Имя constraint
                    logger.info(f"  ✅ {constraint_name}")
                except Exception as e:
                    logger.warning(f"  ⚠️  Constraint уже существует или ошибка: {str(e)[:50]}")

        logger.info(f"✅ Создано constraints: {created}/{len(constraints)}")

    def create_indexes(self):
        """Создание индексов для ускорения поиска"""
        logger.info("\n📌 Создание индексов...")

        indexes = [
            # Индексы для Project
            "CREATE INDEX project_name_idx IF NOT EXISTS FOR (p:Project) ON (p.name)",

            # Индексы для Module
            "CREATE INDEX module_type_idx IF NOT EXISTS FOR (m:Module) ON (m.module_type)",
            "CREATE INDEX module_path_idx IF NOT EXISTS FOR (m:Module) ON (m.file_path)",

            # Индексы для Function
            "CREATE INDEX function_export_idx IF NOT EXISTS FOR (f:Function) ON (f.is_export)",

            # Индексы для Procedure
            "CREATE INDEX procedure_export_idx IF NOT EXISTS FOR (p:Procedure) ON (p.is_export)",

            # Индексы для Variable
            "CREATE INDEX variable_scope_idx IF NOT EXISTS FOR (v:Variable) ON (v.scope)",

            # Индексы для Query
            "CREATE INDEX query_type_idx IF NOT EXISTS FOR (q:Query) ON (q.query_type)",
        ]

        with self.driver.session() as session:
            created = 0
            for index in indexes:
                try:
                    session.run(index)
                    created += 1
                    index_name = index.split()[2]  # Имя индекса
                    logger.info(f"  ✅ {index_name}")
                except Exception as e:
                    logger.warning(f"  ⚠️  Индекс уже существует или ошибка: {str(e)[:50]}")

        logger.info(f"✅ Создано индексов: {created}/{len(indexes)}")

    def create_fulltext_indexes(self):
        """Создание полнотекстовых индексов"""
        logger.info("\n📌 Создание полнотекстовых индексов...")

        fulltext_indexes = [
            "CREATE FULLTEXT INDEX module_name_search IF NOT EXISTS FOR (m:Module) ON EACH [m.name]",
            "CREATE FULLTEXT INDEX function_name_search IF NOT EXISTS FOR (f:Function) ON EACH [f.name]",
            "CREATE FULLTEXT INDEX procedure_name_search IF NOT EXISTS FOR (p:Procedure) ON EACH [p.name]",
        ]

        with self.driver.session() as session:
            created = 0
            for index in fulltext_indexes:
                try:
                    session.run(index)
                    created += 1
                    index_name = index.split()[3]  # Имя индекса
                    logger.info(f"  ✅ {index_name}")
                    time.sleep(0.1)  # Небольшая пауза между созданием индексов
                except Exception as e:
                    logger.warning(f"  ⚠️  Полнотекстовый индекс уже существует или ошибка: {str(e)[:50]}")

        logger.info(f"✅ Создано fulltext индексов: {created}/{len(fulltext_indexes)}")

    def verify_schema(self):
        """Проверка созданной схемы"""
        logger.info("\n📊 Проверка схемы...")

        with self.driver.session() as session:
            # Проверка constraints
            result = session.run("SHOW CONSTRAINTS")
            constraints = list(result)
            logger.info(f"  Constraints: {len(constraints)}")

            # Проверка индексов
            result = session.run("SHOW INDEXES")
            indexes = list(result)
            logger.info(f"  Indexes: {len(indexes)}")

        logger.info("✅ Схема проверена")

    def create_sample_data(self):
        """Создание примера данных для тестирования"""
        logger.info("\n📌 Создание тестовых данных...")

        with self.driver.session() as session:
            # Проект
            session.run("""
                CREATE (p:Project {
                    id: 'test-project-001',
                    name: '1C Framework Test',
                    path: '/test/src',
                    created_at: datetime(),
                    indexed_at: datetime(),
                    description: 'Тестовый проект для проверки Knowledge Graph'
                })
            """)
            logger.info("  ✅ Проект создан")

            # Модуль
            session.run("""
                MATCH (p:Project {id: 'test-project-001'})
                CREATE (m:Module {
                    id: 'test-module-001',
                    name: 'УправлениеДокументами',
                    file_path: 'CommonModules/УправлениеДокументами.bsl',
                    module_type: 'CommonModule',
                    functions_count: 2,
                    procedures_count: 1,
                    variables_count: 0,
                    lines_count: 50,
                    file_size: 1024,
                    indexed_at: datetime(),
                    is_export: true
                })
                CREATE (p)-[:CONTAINS {created_at: datetime()}]->(m)
            """)
            logger.info("  ✅ Модуль создан")

            # Функции
            session.run("""
                MATCH (m:Module {id: 'test-module-001'})
                CREATE (f1:Function {
                    id: 'test-func-001',
                    name: 'ПолучитьДанные',
                    signature: 'Функция ПолучитьДанные(Параметр1)',
                    parameters: ['Параметр1'],
                    is_export: true,
                    line_start: 10,
                    line_end: 20,
                    calls_count: 1
                }),
                (f2:Function {
                    id: 'test-func-002',
                    name: 'ВыполнитьЗапрос',
                    signature: 'Функция ВыполнитьЗапрос(ТекстЗапроса)',
                    parameters: ['ТекстЗапроса'],
                    is_export: false,
                    line_start: 25,
                    line_end: 35,
                    calls_count: 0
                })
                CREATE (m)-[:CONTAINS {created_at: datetime()}]->(f1)
                CREATE (m)-[:CONTAINS {created_at: datetime()}]->(f2)
                CREATE (f1)-[:CALLS {
                    call_count: 1,
                    line_numbers: [15],
                    is_conditional: false
                }]->(f2)
            """)
            logger.info("  ✅ Функции созданы")

            # Процедура
            session.run("""
                MATCH (m:Module {id: 'test-module-001'})
                CREATE (proc:Procedure {
                    id: 'test-proc-001',
                    name: 'ОбработатьДокумент',
                    signature: 'Процедура ОбработатьДокумент(Документ)',
                    parameters: ['Документ'],
                    is_export: true,
                    line_start: 40,
                    line_end: 48,
                    calls_count: 1
                })
                CREATE (m)-[:CONTAINS {created_at: datetime()}]->(proc)
            """)
            logger.info("  ✅ Процедура создана")

        logger.info("✅ Тестовые данные созданы")

    def get_statistics(self):
        """Получение статистики графа"""
        logger.info("\n📊 Статистика Knowledge Graph...")

        with self.driver.session() as session:
            # Количество узлов по типам
            node_stats = session.run("""
                MATCH (n)
                RETURN labels(n)[0] AS label, count(n) AS count
                ORDER BY count DESC
            """)

            logger.info("  Узлы:")
            total_nodes = 0
            for record in node_stats:
                logger.info(f"    {record['label']}: {record['count']}")
                total_nodes += record['count']
            logger.info(f"  Всего узлов: {total_nodes}")

            # Количество связей по типам
            rel_stats = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) AS type, count(r) AS count
                ORDER BY count DESC
            """)

            logger.info("  Связи:")
            total_rels = 0
            for record in rel_stats:
                logger.info(f"    {record['type']}: {record['count']}")
                total_rels += record['count']
            logger.info(f"  Всего связей: {total_rels}")


def main():
    """Основная функция инициализации схемы"""
    logger.info("🚀 Инициализация схемы Knowledge Graph...")
    logger.info("=" * 70)

    # Создание инициализатора
    initializer = Neo4jSchemaInitializer()

    try:
        # Опционально: очистка БД (для чистой установки)
        # initializer.clear_database(confirm=True)

        # Создание constraints
        initializer.create_constraints()

        # Создание индексов
        initializer.create_indexes()

        # Создание fulltext индексов
        initializer.create_fulltext_indexes()

        # Проверка схемы
        initializer.verify_schema()

        # Создание примера данных
        logger.info("\n❓ Создать тестовые данные? (yes/no)")
        create_sample = input().lower() == 'yes'
        if create_sample:
            initializer.create_sample_data()
            initializer.get_statistics()

        logger.info("\n" + "=" * 70)
        logger.info("✅ Инициализация схемы завершена!")
        logger.info("\n📝 Следующие шаги:")
        logger.info("  1. Реализовать BSL dependency analyzer")
        logger.info("  2. Загрузить данные из существующего индекса")
        logger.info("  3. Интегрировать с semantic search")
        logger.info("  4. Создать визуализацию графа")

    finally:
        # Закрытие подключения
        initializer.close()


if __name__ == "__main__":
    main()
