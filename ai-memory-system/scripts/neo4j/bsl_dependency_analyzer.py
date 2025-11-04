"""
BSL Dependency Analyzer
Анализ зависимостей BSL кода и загрузка в Neo4j Knowledge Graph

Извлекает:
- Модули и их метаданные
- Функции и процедуры
- Переменные
- Вызовы между функциями
- Зависимости между модулями
"""

import re
import uuid
import hashlib
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime
import logging
import json
import sys

# Добавление путей для импорта
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from neo4j import GraphDatabase
from utils.bsl_parser import BSLParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BSLDependencyAnalyzer:
    """Анализатор зависимостей BSL кода"""

    def __init__(self, neo4j_uri="bolt://localhost:7687", neo4j_user="neo4j", neo4j_password="password123"):
        """
        Инициализация анализатора

        Args:
            neo4j_uri: URI подключения к Neo4j
            neo4j_user: Пользователь Neo4j
            neo4j_password: Пароль Neo4j
        """
        self.parser = BSLParser()
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        logger.info(f"✅ BSLDependencyAnalyzer инициализирован")

    def close(self):
        """Закрытие подключения"""
        if self.driver:
            self.driver.close()
            logger.info("🔌 Подключение к Neo4j закрыто")

    def _generate_id(self, prefix: str, *args) -> str:
        """
        Генерация уникального ID

        Args:
            prefix: Префикс ID (module, function, etc.)
            *args: Аргументы для генерации ID

        Returns:
            Уникальный ID
        """
        content = "-".join(str(arg) for arg in args)
        hash_id = hashlib.md5(content.encode()).hexdigest()[:12]
        return f"{prefix}-{hash_id}"

    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Вычисление SHA256 хэша файла

        Args:
            file_path: Путь к файлу

        Returns:
            SHA256 хэш
        """
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Ошибка вычисления хэша: {e}")
            return ""

    def _detect_module_type(self, file_path: Path, content: str) -> str:
        """
        Определение типа модуля

        Args:
            file_path: Путь к файлу
            content: Содержимое файла

        Returns:
            Тип модуля
        """
        path_lower = str(file_path).lower()

        if 'commonmodules' in path_lower or 'общиемодули' in path_lower:
            return 'CommonModule'
        elif 'objectmodule' in path_lower or 'модульобъекта' in path_lower:
            return 'ObjectModule'
        elif 'managermodule' in path_lower or 'модульменеджера' in path_lower:
            return 'ManagerModule'
        elif 'formmodule' in path_lower or 'модульформы' in path_lower:
            return 'FormModule'
        elif 'commandmodule' in path_lower or 'модулькоманды' in path_lower:
            return 'CommandModule'
        else:
            return 'Unknown'

    def _find_function_calls(self, function_name: str, function_body: str, all_functions: List) -> List[Dict]:
        """
        Поиск вызовов функций в теле функции

        Args:
            function_name: Имя анализируемой функции
            function_body: Тело функции
            all_functions: Список всех доступных функций (BSLFunction objects)

        Returns:
            Список вызовов
        """
        calls = []

        for func in all_functions:
            target_name = func.name

            # Пропускаем саму функцию
            if target_name == function_name:
                continue

            # Паттерн для поиска вызова функции
            # Ищем: ИмяФункции(...) или Результат = ИмяФункции(...)
            pattern = rf'\b{re.escape(target_name)}\s*\('

            matches = list(re.finditer(pattern, function_body, re.IGNORECASE))

            if matches:
                # Находим номера строк вызовов
                line_numbers = []
                for match in matches:
                    # Подсчет строк до позиции match
                    lines_before = function_body[:match.start()].count('\n')
                    line_numbers.append(lines_before + 1)

                calls.append({
                    'target_function': target_name,
                    'call_count': len(matches),
                    'line_numbers': line_numbers
                })

        return calls

    def analyze_file(self, file_path: Path, project_root: Path) -> Dict:
        """
        Анализ одного BSL файла

        Args:
            file_path: Путь к файлу
            project_root: Корневая директория проекта

        Returns:
            Словарь с данными для Neo4j
        """
        try:
            # Чтение файла
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()

            # Парсинг BSL кода
            parsed = self.parser.parse_file(str(file_path))

            if not parsed:
                return None

            # Относительный путь
            relative_path = file_path.relative_to(project_root)

            # Разделение функций и процедур
            functions_list = [f for f in parsed.functions if f.type.lower() in ['функция', 'function']]
            procedures_list = [p for p in parsed.functions if p.type.lower() in ['процедура', 'procedure']]

            # Метаданные модуля
            module_data = {
                'id': self._generate_id('module', relative_path),
                'name': file_path.stem,
                'file_path': str(relative_path).replace('\\', '/'),
                'module_type': parsed.module_type,
                'functions_count': len(functions_list),
                'procedures_count': len(procedures_list),
                'variables_count': len(parsed.variables),
                'lines_count': len(content.split('\n')),
                'file_size': file_path.stat().st_size,
                'content_hash': self._calculate_file_hash(file_path),
                'indexed_at': datetime.now().isoformat(),
                'is_export': False  # TODO: определить по содержимому
            }

            # Функции с детальным анализом
            functions = []

            for func in functions_list:
                func_id = self._generate_id('function', relative_path, func.name)

                # Формирование сигнатуры
                params_str = ', '.join(func.parameters)
                signature = f"{func.type} {func.name}({params_str})"
                if func.is_export:
                    signature += " Экспорт"

                # Поиск вызовов в теле функции
                calls = self._find_function_calls(
                    func.name,
                    func.body,
                    parsed.functions
                )

                functions.append({
                    'id': func_id,
                    'name': func.name,
                    'signature': signature,
                    'parameters': func.parameters,
                    'is_export': func.is_export,
                    'line_start': func.start_line,
                    'line_end': func.end_line,
                    'calls': calls
                })

            # Процедуры с анализом вызовов
            procedures = []
            for proc in procedures_list:
                proc_id = self._generate_id('procedure', relative_path, proc.name)

                # Формирование сигнатуры
                params_str = ', '.join(proc.parameters)
                signature = f"{proc.type} {proc.name}({params_str})"
                if proc.is_export:
                    signature += " Экспорт"

                # Поиск вызовов
                calls = self._find_function_calls(
                    proc.name,
                    proc.body,
                    parsed.functions
                )

                procedures.append({
                    'id': proc_id,
                    'name': proc.name,
                    'signature': signature,
                    'parameters': proc.parameters,
                    'is_export': proc.is_export,
                    'line_start': proc.start_line,
                    'line_end': proc.end_line,
                    'calls': calls
                })

            # Переменные
            variables = []
            for var in parsed.variables:
                var_id = self._generate_id('variable', relative_path, var.name)
                variables.append({
                    'id': var_id,
                    'name': var.name,
                    'scope': 'module',  # TODO: определить scope
                    'is_export': False,
                    'line_number': var.line_number
                })

            return {
                'module': module_data,
                'functions': functions,
                'procedures': procedures,
                'variables': variables
            }

        except Exception as e:
            logger.error(f"Ошибка анализа файла {file_path}: {e}")
            return None

    def load_module_to_neo4j(self, module_data: Dict, project_id: str):
        """
        Загрузка модуля и его компонентов в Neo4j

        Args:
            module_data: Данные модуля
            project_id: ID проекта
        """
        with self.driver.session() as session:
            # 1. Создание модуля
            mod = module_data['module']
            session.run("""
                MATCH (p:Project {id: $project_id})
                MERGE (m:Module {id: $module_id})
                SET m.name = $name,
                    m.file_path = $file_path,
                    m.module_type = $module_type,
                    m.functions_count = $functions_count,
                    m.procedures_count = $procedures_count,
                    m.variables_count = $variables_count,
                    m.lines_count = $lines_count,
                    m.file_size = $file_size,
                    m.content_hash = $content_hash,
                    m.indexed_at = datetime($indexed_at),
                    m.is_export = $is_export
                MERGE (p)-[:CONTAINS {created_at: datetime()}]->(m)
            """,
                project_id=project_id,
                module_id=mod['id'],
                name=mod['name'],
                file_path=mod['file_path'],
                module_type=mod['module_type'],
                functions_count=mod['functions_count'],
                procedures_count=mod['procedures_count'],
                variables_count=mod['variables_count'],
                lines_count=mod['lines_count'],
                file_size=mod['file_size'],
                content_hash=mod['content_hash'],
                indexed_at=mod['indexed_at'],
                is_export=mod['is_export']
            )

            # 2. Создание функций
            for func in module_data.get('functions', []):
                session.run("""
                    MATCH (m:Module {id: $module_id})
                    MERGE (f:Function {id: $func_id})
                    SET f.name = $name,
                        f.signature = $signature,
                        f.parameters = $func_parameters,
                        f.is_export = $is_export,
                        f.line_start = $line_start,
                        f.line_end = $line_end,
                        f.calls_count = $calls_count
                    MERGE (m)-[:CONTAINS {created_at: datetime()}]->(f)
                """,
                    module_id=module_data['module']['id'],
                    func_id=func['id'],
                    name=func['name'],
                    signature=func['signature'],
                    func_parameters=func['parameters'],
                    is_export=func['is_export'],
                    line_start=func['line_start'],
                    line_end=func['line_end'],
                    calls_count=len(func.get('calls', []))
                )

            # 3. Создание процедур
            for proc in module_data.get('procedures', []):
                session.run("""
                    MATCH (m:Module {id: $module_id})
                    MERGE (p:Procedure {id: $proc_id})
                    SET p.name = $name,
                        p.signature = $signature,
                        p.parameters = $proc_parameters,
                        p.is_export = $is_export,
                        p.line_start = $line_start,
                        p.line_end = $line_end,
                        p.calls_count = $calls_count
                    MERGE (m)-[:CONTAINS {created_at: datetime()}]->(p)
                """,
                    module_id=module_data['module']['id'],
                    proc_id=proc['id'],
                    name=proc['name'],
                    signature=proc['signature'],
                    proc_parameters=proc['parameters'],
                    is_export=proc['is_export'],
                    line_start=proc['line_start'],
                    line_end=proc['line_end'],
                    calls_count=len(proc.get('calls', []))
                )

            # 4. Создание переменных
            for var in module_data.get('variables', []):
                session.run("""
                    MATCH (m:Module {id: $module_id})
                    MERGE (v:Variable {id: $var_id})
                    SET v.name = $name,
                        v.scope = $scope,
                        v.is_export = $is_export,
                        v.line_number = $line_number
                    MERGE (m)-[:CONTAINS {created_at: datetime()}]->(v)
                """,
                    module_id=module_data['module']['id'],
                    var_id=var['id'],
                    name=var['name'],
                    scope=var['scope'],
                    is_export=var['is_export'],
                    line_number=var['line_number']
                )

    def create_function_calls_relationships(self, module_data: Dict):
        """
        Создание связей CALLS между функциями/процедурами

        Args:
            module_data: Данные модуля
        """
        with self.driver.session() as session:
            # Обработка вызовов из функций
            for func in module_data.get('functions', []):
                for call in func.get('calls', []):
                    session.run("""
                        MATCH (source:Function {id: $source_id})
                        MATCH (target)
                        WHERE target.name = $target_name
                          AND (target:Function OR target:Procedure)
                        MERGE (source)-[c:CALLS]->(target)
                        SET c.call_count = $call_count,
                            c.line_numbers = $line_numbers,
                            c.is_conditional = false
                    """,
                        source_id=func['id'],
                        target_name=call['target_function'],
                        call_count=call['call_count'],
                        line_numbers=call['line_numbers']
                    )

            # Обработка вызовов из процедур
            for proc in module_data.get('procedures', []):
                for call in proc.get('calls', []):
                    session.run("""
                        MATCH (source:Procedure {id: $source_id})
                        MATCH (target)
                        WHERE target.name = $target_name
                          AND (target:Function OR target:Procedure)
                        MERGE (source)-[c:CALLS]->(target)
                        SET c.call_count = $call_count,
                            c.line_numbers = $line_numbers,
                            c.is_conditional = false
                    """,
                        source_id=proc['id'],
                        target_name=call['target_function'],
                        call_count=call['call_count'],
                        line_numbers=call['line_numbers']
                    )

    def create_or_get_project(self, project_name: str, project_path: Path) -> str:
        """
        Создание или получение проекта

        Args:
            project_name: Название проекта
            project_path: Путь к проекту

        Returns:
            ID проекта
        """
        project_id = self._generate_id('project', project_name)

        with self.driver.session() as session:
            session.run("""
                MERGE (p:Project {id: $id})
                SET p.name = $name,
                    p.path = $path,
                    p.created_at = datetime(),
                    p.indexed_at = datetime()
            """,
                id=project_id,
                name=project_name,
                path=str(project_path)
            )

        logger.info(f"✅ Проект: {project_name} (ID: {project_id})")
        return project_id

    def analyze_project(self, project_path: Path, project_name: str = None, max_files: int = None):
        """
        Анализ всего проекта

        Args:
            project_path: Путь к корню проекта
            project_name: Название проекта (по умолчанию - имя директории)
            max_files: Максимальное количество файлов для анализа
        """
        project_path = Path(project_path)

        if not project_name:
            project_name = project_path.name

        logger.info(f"🚀 Анализ проекта: {project_name}")
        logger.info(f"   Путь: {project_path}")

        # Создание проекта в Neo4j
        project_id = self.create_or_get_project(project_name, project_path)

        # Поиск всех BSL файлов
        bsl_files = list(project_path.rglob("*.bsl"))

        if max_files:
            bsl_files = bsl_files[:max_files]

        logger.info(f"   Найдено BSL файлов: {len(bsl_files)}")

        # Анализ файлов
        analyzed = 0
        for i, file_path in enumerate(bsl_files, 1):
            logger.info(f"   [{i}/{len(bsl_files)}] {file_path.name}")

            # Анализ файла
            module_data = self.analyze_file(file_path, project_path)

            if module_data:
                # Загрузка в Neo4j
                self.load_module_to_neo4j(module_data, project_id)

                # Создание связей вызовов
                self.create_function_calls_relationships(module_data)

                analyzed += 1

        logger.info(f"✅ Анализ завершен. Обработано файлов: {analyzed}/{len(bsl_files)}")


def main():
    """Основная функция"""
    logger.info("🚀 BSL Dependency Analyzer")
    logger.info("=" * 70)

    # Создание анализатора
    analyzer = BSLDependencyAnalyzer()

    try:
        # Путь к проекту
        project_path = Path(__file__).parent.parent.parent.parent / "src"

        # Анализ проекта (для теста - 10 файлов)
        analyzer.analyze_project(
            project_path=project_path,
            project_name="1C Framework",
            max_files=10
        )

        logger.info("\n✅ Готово! Данные загружены в Neo4j Knowledge Graph")
        logger.info("\n📊 Для просмотра графа откройте: http://localhost:7474")

    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
