"""
BSL Parser - парсер для анализа структуры BSL кода
Извлекает процедуры, функции, переменные и комментарии
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BSLFunction:
    """Структура для хранения информации о функции/процедуре"""
    name: str
    type: str  # "Процедура" или "Функция"
    parameters: List[str]
    body: str
    start_line: int
    end_line: int
    is_export: bool = False
    doc_comment: Optional[str] = None


@dataclass
class BSLVariable:
    """Структура для хранения информации о переменной"""
    name: str
    line_number: int


@dataclass
class BSLModule:
    """Структура для хранения информации о модуле"""
    file_path: str
    functions: List[BSLFunction]
    variables: List[BSLVariable]
    module_type: str  # ObjectModule, ManagerModule, CommonModule и т.д.


class BSLParser:
    """
    Парсер BSL кода для извлечения структуры
    """

    # Регулярные выражения для парсинга
    FUNCTION_PATTERN = re.compile(
        r'(Процедура|Функция|Procedure|Function)\s+(\w+)\s*\((.*?)\)\s*(Экспорт|Export)?',
        re.IGNORECASE
    )

    END_FUNCTION_PATTERN = re.compile(
        r'КонецПроцедуры|КонецФункции|EndProcedure|EndFunction',
        re.IGNORECASE
    )

    VARIABLE_PATTERN = re.compile(
        r'Перем\s+(\w+(?:\s*,\s*\w+)*)',
        re.IGNORECASE
    )

    COMMENT_PATTERN = re.compile(r'//(.*)$', re.MULTILINE)

    def __init__(self):
        """Инициализация парсера"""
        logger.info("BSLParser инициализирован")

    def parse_file(self, file_path: str) -> Optional[BSLModule]:
        """
        Парсинг BSL файла

        Args:
            file_path: Путь к файлу

        Returns:
            BSLModule с информацией о модуле или None при ошибке
        """
        try:
            # Чтение файла
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()

            # Определение типа модуля по пути
            module_type = self._detect_module_type(file_path)

            # Парсинг функций и процедур
            functions = self._parse_functions(content)

            # Парсинг переменных
            variables = self._parse_variables(content)

            module = BSLModule(
                file_path=file_path,
                functions=functions,
                variables=variables,
                module_type=module_type
            )

            logger.debug(
                f"Файл {Path(file_path).name}: "
                f"{len(functions)} функций, {len(variables)} переменных"
            )

            return module

        except FileNotFoundError:
            logger.error(f"Файл не найден: {file_path}")
            return None
        except UnicodeDecodeError:
            logger.error(f"Ошибка кодировки файла: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Ошибка парсинга {file_path}: {e}")
            return None

    def _detect_module_type(self, file_path: str) -> str:
        """Определение типа модуля по пути"""
        path_lower = file_path.lower()

        if 'objectmodule.bsl' in path_lower:
            return 'ObjectModule'
        elif 'managermodule.bsl' in path_lower:
            return 'ManagerModule'
        elif 'commonmodule' in path_lower:
            return 'CommonModule'
        elif 'formmodule.bsl' in path_lower:
            return 'FormModule'
        elif 'commandmodule.bsl' in path_lower:
            return 'CommandModule'
        else:
            return 'Unknown'

    def _parse_functions(self, content: str) -> List[BSLFunction]:
        """Парсинг функций и процедур"""
        functions = []
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]

            # Поиск начала функции/процедуры
            match = self.FUNCTION_PATTERN.search(line)
            if match:
                func_type = match.group(1)  # Процедура/Функция
                func_name = match.group(2)
                params_str = match.group(3)
                is_export = match.group(4) is not None

                # Парсинг параметров
                parameters = [
                    p.strip() for p in params_str.split(',') if p.strip()
                ]

                # Поиск конца функции
                start_line = i + 1
                func_body_lines = []
                i += 1

                while i < len(lines):
                    if self.END_FUNCTION_PATTERN.search(lines[i]):
                        break
                    func_body_lines.append(lines[i])
                    i += 1

                end_line = i + 1
                func_body = '\n'.join(func_body_lines)

                # Поиск комментария документации (строки перед функцией)
                doc_comment = self._extract_doc_comment(lines, start_line - 2)

                function = BSLFunction(
                    name=func_name,
                    type=func_type,
                    parameters=parameters,
                    body=func_body,
                    start_line=start_line,
                    end_line=end_line,
                    is_export=is_export,
                    doc_comment=doc_comment
                )

                functions.append(function)

            i += 1

        return functions

    def _parse_variables(self, content: str) -> List[BSLVariable]:
        """Парсинг переменных модуля"""
        variables = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            match = self.VARIABLE_PATTERN.search(line)
            if match:
                var_names = match.group(1)
                # Разбор нескольких переменных в одной строке
                for var_name in var_names.split(','):
                    var_name = var_name.strip()
                    if var_name:
                        variables.append(
                            BSLVariable(name=var_name, line_number=i)
                        )

        return variables

    def _extract_doc_comment(self, lines: List[str], line_index: int) -> Optional[str]:
        """
        Извлечение комментария документации перед функцией

        Args:
            lines: Все строки файла
            line_index: Индекс строки перед функцией

        Returns:
            Комментарий документации или None
        """
        if line_index < 0 or line_index >= len(lines):
            return None

        doc_lines = []
        i = line_index

        # Идем вверх, собирая комментарии
        while i >= 0:
            line = lines[i].strip()
            if line.startswith('//'):
                comment_text = line[2:].strip()
                doc_lines.insert(0, comment_text)
                i -= 1
            elif not line:  # Пустая строка - продолжаем
                i -= 1
            else:
                break

        if doc_lines:
            return '\n'.join(doc_lines)
        return None

    def extract_searchable_text(self, module: BSLModule) -> str:
        """
        Извлечение текста для поиска из модуля

        Args:
            module: Распарсенный модуль

        Returns:
            Текст для векторизации и поиска
        """
        parts = []

        # Название файла
        parts.append(f"Файл: {Path(module.file_path).name}")

        # Тип модуля
        parts.append(f"Тип: {module.module_type}")

        # Функции и процедуры
        for func in module.functions:
            func_text = f"{func.type} {func.name}("
            func_text += ", ".join(func.parameters)
            func_text += ")"

            if func.is_export:
                func_text += " Экспорт"

            parts.append(func_text)

            # Комментарий документации
            if func.doc_comment:
                parts.append(f"// {func.doc_comment}")

            # Первые 5 строк тела функции (для контекста)
            body_lines = func.body.strip().split('\n')[:5]
            if body_lines:
                parts.append('\n'.join(body_lines))

        # Переменные модуля
        if module.variables:
            var_names = ', '.join([v.name for v in module.variables])
            parts.append(f"Переменные: {var_names}")

        return '\n\n'.join(parts)


# Пример использования
if __name__ == "__main__":
    # Тестовый BSL код
    test_code = """
    // Модуль для работы с документами
    Перем СчетчикДокументов, МаксимальныйНомер;

    // Процедура записи документа
    // Выполняет проверку обязательных полей
    Процедура ПриЗаписи(Отказ) Экспорт
        Если НЕ ЗначениеЗаполнено(Дата) Тогда
            Дата = ТекущаяДата();
        КонецЕсли;

        Если НЕ ЗначениеЗаполнено(Номер) Тогда
            Сообщить("Не заполнен номер документа");
            Отказ = Истина;
        КонецЕсли;
    КонецПроцедуры

    // Получение следующего номера
    Функция ПолучитьНовыйНомер() Экспорт
        СчетчикДокументов = СчетчикДокументов + 1;
        Возврат СчетчикДокументов;
    КонецФункции
    """

    # Сохранение в файл для теста
    test_file = "D:/1C-Enterprise_Framework/ai-memory-system/test_module.bsl"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)

    # Парсинг
    parser = BSLParser()
    module = parser.parse_file(test_file)

    if module:
        print(f"✅ Файл распарсен успешно!")
        print(f"\n📁 Модуль: {module.module_type}")
        print(f"📊 Функций: {len(module.functions)}")
        print(f"📊 Переменных: {len(module.variables)}")

        print(f"\n🔧 Функции:")
        for func in module.functions:
            export_mark = " [Экспорт]" if func.is_export else ""
            print(f"   - {func.type} {func.name}({', '.join(func.parameters)}){export_mark}")
            if func.doc_comment:
                print(f"     Комментарий: {func.doc_comment[:50]}...")

        print(f"\n📝 Переменные:")
        for var in module.variables:
            print(f"   - {var.name}")

        # Извлечение текста для поиска
        searchable_text = parser.extract_searchable_text(module)
        print(f"\n🔍 Текст для поиска (первые 200 символов):")
        print(searchable_text[:200] + "...")

    # Удаление тестового файла
    import os
    os.remove(test_file)
