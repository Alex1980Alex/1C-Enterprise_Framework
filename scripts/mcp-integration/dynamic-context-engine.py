#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dynamic Context Engine v1.0
Интеллектуальная система выбора MCP инструментов для фреймворка 1C-Enterprise

Автоматически анализирует контекст запроса и предлагает оптимальный набор инструментов
для выполнения задачи с учетом семантики, типа файлов и сложности задачи.
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskComplexity(Enum):
    """Уровни сложности задач"""
    SIMPLE = "simple"           # Простые операции (чтение, поиск)
    MEDIUM = "medium"           # Семантический анализ, замены
    COMPLEX = "complex"         # Многоступенчатый анализ, архитектурные задачи
    STRATEGIC = "strategic"     # Планирование, стратегические решения

class FileType(Enum):
    """Типы файлов для обработки"""
    BSL = "bsl"                 # 1C:Enterprise BSL модули
    METADATA = "metadata"       # XML метаданные конфигурации
    DOCUMENT = "document"       # PDF, DOCX, PPTX документы
    WEB = "web"                # HTML, веб-страницы
    CONFIG = "config"          # Файлы конфигурации
    CODE = "code"              # Другие языки программирования
    TEXT = "text"              # Обычные текстовые файлы

class ToolCategory(Enum):
    """Категории инструментов"""
    MCP_SEMANTIC = "mcp_semantic"       # MCP для семантического анализа
    MCP_EXTERNAL = "mcp_external"       # MCP для внешних ресурсов
    MCP_THINKING = "mcp_thinking"       # MCP для сложного анализа
    STANDARD = "standard"               # Стандартные инструменты

@dataclass
class ToolRecommendation:
    """Рекомендация по использованию инструмента"""
    tool_name: str
    category: ToolCategory
    confidence: float           # 0.0 - 1.0
    reason: str
    parameters: Dict
    fallback_tool: Optional[str] = None
    estimated_time: Optional[str] = None

@dataclass
class TaskContext:
    """Контекст задачи для анализа"""
    user_request: str
    file_paths: List[str]
    file_types: List[FileType]
    complexity: TaskComplexity
    keywords: List[str]
    intent: str                 # основное намерение пользователя
    domain: str                 # предметная область (1c, web, docs, etc.)

class DynamicContextEngine:
    """
    Движок интеллектуального выбора инструментов

    Анализирует запрос пользователя и автоматически предлагает
    наиболее подходящие MCP инструменты с учетом:
    - Типа файлов и их содержимого
    - Сложности задачи
    - Семантики запроса
    - Доступности инструментов
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "D:/1C-Enterprise_Framework/.claude/dynamic-context-config.json"
        self.rules_path = "D:/1C-Enterprise_Framework/.claude/mcp-priority-rules.md"
        self.cache_path = "D:/1C-Enterprise_Framework/cache/context-engine/"

        # Инициализация кэша и конфигурации
        Path(self.cache_path).mkdir(parents=True, exist_ok=True)
        self.load_configuration()
        self.load_tool_patterns()
        self.learning_data = self.load_learning_data()

    def load_configuration(self):
        """Загрузка конфигурации движка"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Создание конфигурации по умолчанию
            self.config = self.create_default_config()
            self.save_configuration()

    def create_default_config(self) -> Dict:
        """Создание конфигурации по умолчанию"""
        return {
            "version": "1.0",
            "weights": {
                "file_type_match": 0.4,
                "semantic_match": 0.3,
                "complexity_match": 0.2,
                "learning_bonus": 0.1
            },
            "confidence_thresholds": {
                "high": 0.8,
                "medium": 0.6,
                "low": 0.4
            },
            "tool_availability": {
                "mcp__ast-grep-mcp__ast_grep": True,
                "mcp__serena__get_symbols_overview": True,
                "mcp__serena__find_symbol": True,
                "mcp__serena__find_referencing_symbols": True,
                "mcp__serena__replace_symbol_body": True,
                "mcp__serena__insert_after_symbol": True,
                "mcp__serena__search_for_pattern": True,
                "mcp__1c-framework-docs__search_docs": True,
                "mcp__universal-web-scraper__scrape_website": True,
                "mcp__docling__convert_document": True,
                "mcp__memory__create_entities": True,
                "mcp__sequential-thinking__sequentialthinking": True
            }
        }

    def load_tool_patterns(self):
        """Загрузка паттернов выбора инструментов из правил приоритизации"""
        self.tool_patterns = {
            # BSL анализ структуры - ОБЯЗАТЕЛЬНО AST-grep
            "bsl_structure_analysis": {
                "patterns": ["обзор структуры", "структура bsl", "список функций", "список процедур", "анализ модуля"],
                "file_types": [FileType.BSL],
                "primary_tool": "mcp__ast-grep-mcp__ast_grep",
                "fallback_tool": "mcp__serena__get_symbols_overview",
                "confidence_boost": 0.3,
                "parameters": {
                    "pattern": "Функция $NAME($$$ARGS)",
                    "bsl_type": "functions"
                }
            },

            # Поиск конкретной функции/процедуры
            "bsl_function_search": {
                "patterns": ["найти функцию", "найти процедуру", "где находится", "определение функции"],
                "file_types": [FileType.BSL],
                "primary_tool": "mcp__ast-grep-mcp__ast_grep",
                "fallback_tool": "mcp__serena__find_symbol",
                "confidence_boost": 0.25,
                "parameters": {
                    "bsl_type": "auto",
                    "include_body": True
                }
            },

            # Анализ зависимостей
            "dependency_analysis": {
                "patterns": ["где используется", "зависимости", "ссылки на функцию", "вызовы функции"],
                "file_types": [FileType.BSL],
                "primary_tool": "mcp__serena__find_referencing_symbols",
                "fallback_tool": "Grep",
                "confidence_boost": 0.2
            },

            # Замена кода
            "code_replacement": {
                "patterns": ["заменить функцию", "изменить процедуру", "рефакторинг", "обновить код"],
                "file_types": [FileType.BSL],
                "primary_tool": "mcp__serena__replace_symbol_body",
                "fallback_tool": "Edit",
                "confidence_boost": 0.2
            },

            # Поиск в документации
            "documentation_search": {
                "patterns": ["документация", "как сделать", "примеры", "фреймворк", "best practices"],
                "file_types": [],
                "primary_tool": "mcp__1c-framework-docs__search_docs",
                "fallback_tool": None,
                "confidence_boost": 0.25,
                "parameters": {
                    "search_type": "hybrid",
                    "limit": 5
                }
            },

            # Парсинг веб-сайтов
            "web_scraping": {
                "patterns": ["парсинг", "its.1c.ru", "веб-сайт", "документация с сайта", "извлечь данные"],
                "file_types": [FileType.WEB],
                "primary_tool": "mcp__universal-web-scraper__scrape_website",
                "fallback_tool": None,
                "confidence_boost": 0.3,
                "parameters": {
                    "adapter_type": "auto",
                    "include_links": True,
                    "save_to_memory": True
                }
            },

            # Конвертация документов
            "document_conversion": {
                "patterns": ["конвертировать pdf", "docx в markdown", "извлечь текст", "ocr"],
                "file_types": [FileType.DOCUMENT],
                "primary_tool": "mcp__docling__convert_document",
                "fallback_tool": None,
                "confidence_boost": 0.35,
                "parameters": {
                    "extract_images": True,
                    "ocr_enabled": True
                }
            },

            # Сложный анализ
            "complex_analysis": {
                "patterns": ["проанализировать", "сложная задача", "планирование", "стратегия", "многоступенчатый"],
                "file_types": [],
                "primary_tool": "mcp__sequential-thinking__sequentialthinking",
                "fallback_tool": None,
                "confidence_boost": 0.2,
                "parameters": {
                    "totalThoughts": 5,
                    "nextThoughtNeeded": True
                }
            },

            # Сохранение знаний
            "knowledge_storage": {
                "patterns": ["запомнить", "сохранить", "knowledge graph", "документировать", "база знаний"],
                "file_types": [],
                "primary_tool": "mcp__memory__create_entities",
                "fallback_tool": "Write",
                "confidence_boost": 0.15
            }
        }

    def analyze_request(self, user_request: str, file_paths: List[str] = None) -> TaskContext:
        """
        Анализ запроса пользователя для определения контекста

        Args:
            user_request: Текст запроса пользователя
            file_paths: Список путей к файлам (если есть)

        Returns:
            TaskContext: Контекст задачи с анализом
        """
        file_paths = file_paths or []

        # Определение типов файлов
        file_types = self._detect_file_types(file_paths, user_request)

        # Извлечение ключевых слов
        keywords = self._extract_keywords(user_request)

        # Определение сложности
        complexity = self._determine_complexity(user_request, keywords)

        # Определение намерения
        intent = self._determine_intent(user_request, keywords)

        # Определение предметной области
        domain = self._determine_domain(user_request, file_types)

        return TaskContext(
            user_request=user_request,
            file_paths=file_paths,
            file_types=file_types,
            complexity=complexity,
            keywords=keywords,
            intent=intent,
            domain=domain
        )

    def recommend_tools(self, context: TaskContext) -> List[ToolRecommendation]:
        """
        Рекомендация инструментов на основе контекста

        Args:
            context: Контекст задачи

        Returns:
            List[ToolRecommendation]: Отсортированный список рекомендаций
        """
        recommendations = []

        # Анализ по паттернам
        for pattern_name, pattern_config in self.tool_patterns.items():
            confidence = self._calculate_confidence(context, pattern_config)

            if confidence > self.config["confidence_thresholds"]["low"]:
                # Проверка доступности инструмента
                primary_tool = pattern_config["primary_tool"]
                if not self.config["tool_availability"].get(primary_tool, False):
                    continue

                # Создание параметров
                parameters = pattern_config.get("parameters", {})
                if context.file_paths:
                    parameters["path"] = context.file_paths[0]

                # Оценка времени выполнения
                estimated_time = self._estimate_execution_time(primary_tool, context.complexity)

                recommendation = ToolRecommendation(
                    tool_name=primary_tool,
                    category=self._get_tool_category(primary_tool),
                    confidence=confidence,
                    reason=f"Совпадение с паттерном '{pattern_name}'",
                    parameters=parameters,
                    fallback_tool=pattern_config.get("fallback_tool"),
                    estimated_time=estimated_time
                )

                recommendations.append(recommendation)

        # Сортировка по уверенности
        recommendations.sort(key=lambda x: x.confidence, reverse=True)

        # Обучение на основе выбора
        self._update_learning_data(context, recommendations)

        return recommendations[:5]  # Топ-5 рекомендаций

    def _detect_file_types(self, file_paths: List[str], user_request: str) -> List[FileType]:
        """Определение типов файлов"""
        file_types = []

        # Анализ расширений файлов
        for path in file_paths:
            path_lower = path.lower()
            if path_lower.endswith('.bsl'):
                file_types.append(FileType.BSL)
            elif path_lower.endswith(('.pdf', '.docx', '.doc', '.pptx')):
                file_types.append(FileType.DOCUMENT)
            elif path_lower.endswith(('.xml',)) and 'metadata' in path_lower:
                file_types.append(FileType.METADATA)
            elif path_lower.endswith(('.html', '.htm')):
                file_types.append(FileType.WEB)
            elif path_lower.endswith(('.json', '.yaml', '.yml', '.ini')):
                file_types.append(FileType.CONFIG)
            else:
                file_types.append(FileType.CODE)

        # Анализ содержимого запроса
        request_lower = user_request.lower()
        if any(word in request_lower for word in ['bsl', 'процедура', 'функция', '1с']):
            file_types.append(FileType.BSL)
        if any(word in request_lower for word in ['pdf', 'docx', 'документ']):
            file_types.append(FileType.DOCUMENT)
        if any(word in request_lower for word in ['сайт', 'веб', 'url', 'http']):
            file_types.append(FileType.WEB)

        return list(set(file_types))

    def _extract_keywords(self, text: str) -> List[str]:
        """Извлечение ключевых слов из текста"""
        # Важные ключевые слова для 1C и MCP
        important_keywords = [
            'функция', 'процедура', 'модуль', 'конфигурация', 'метаданные',
            'документ', 'справочник', 'регистр', 'отчет', 'обработка',
            'анализ', 'поиск', 'замена', 'создание', 'удаление',
            'структура', 'зависимости', 'рефакторинг', 'оптимизация',
            'документация', 'парсинг', 'конвертация', 'экспорт'
        ]

        text_lower = text.lower()
        found_keywords = [kw for kw in important_keywords if kw in text_lower]

        # Дополнительные ключевые слова через regex
        additional_patterns = [
            r'\b(найти|найди)\b',
            r'\b(создать|создай)\b',
            r'\b(заменить|замени)\b',
            r'\b(анализ|проанализ)\w*',
            r'\b(документ|докум)\w*'
        ]

        for pattern in additional_patterns:
            matches = re.findall(pattern, text_lower)
            found_keywords.extend(matches)

        return list(set(found_keywords))

    def _determine_complexity(self, request: str, keywords: List[str]) -> TaskComplexity:
        """Определение сложности задачи"""
        request_lower = request.lower()

        # Стратегические задачи
        strategic_indicators = ['планирование', 'стратегия', 'архитектура', 'модернизация', 'внедрение']
        if any(indicator in request_lower for indicator in strategic_indicators):
            return TaskComplexity.STRATEGIC

        # Сложные задачи
        complex_indicators = ['анализ', 'рефакторинг', 'оптимизация', 'зависимости', 'граф', 'многоступенчатый']
        if any(indicator in request_lower for indicator in complex_indicators):
            return TaskComplexity.COMPLEX

        # Средние задачи
        medium_indicators = ['заменить', 'изменить', 'обновить', 'добавить', 'создать функцию']
        if any(indicator in request_lower for indicator in medium_indicators):
            return TaskComplexity.MEDIUM

        # Простые задачи по умолчанию
        return TaskComplexity.SIMPLE

    def _determine_intent(self, request: str, keywords: List[str]) -> str:
        """Определение намерения пользователя"""
        request_lower = request.lower()

        intent_patterns = {
            'search': ['найти', 'поиск', 'где находится', 'искать'],
            'analyze': ['анализ', 'проанализ', 'изучить', 'исследовать'],
            'modify': ['заменить', 'изменить', 'обновить', 'исправить'],
            'create': ['создать', 'добавить', 'новый', 'сделать'],
            'document': ['документ', 'задокумент', 'описать', 'запомнить'],
            'convert': ['конверт', 'преобразовать', 'экспорт', 'импорт']
        }

        for intent, patterns in intent_patterns.items():
            if any(pattern in request_lower for pattern in patterns):
                return intent

        return 'unknown'

    def _determine_domain(self, request: str, file_types: List[FileType]) -> str:
        """Определение предметной области"""
        request_lower = request.lower()

        # Анализ типов файлов
        if FileType.BSL in file_types:
            return '1c'
        if FileType.DOCUMENT in file_types:
            return 'documents'
        if FileType.WEB in file_types:
            return 'web'

        # Анализ содержимого запроса
        if any(word in request_lower for word in ['1с', 'bsl', 'конфигурация', 'метаданные']):
            return '1c'
        if any(word in request_lower for word in ['документация', 'фреймворк', 'its.1c']):
            return 'documentation'
        if any(word in request_lower for word in ['сайт', 'веб', 'парсинг']):
            return 'web'

        return 'general'

    def _calculate_confidence(self, context: TaskContext, pattern_config: Dict) -> float:
        """Расчет уверенности для паттерна"""
        confidence = 0.0
        weights = self.config["weights"]

        # Совпадение по типам файлов
        if pattern_config["file_types"]:
            file_type_match = len(set(context.file_types) & set(pattern_config["file_types"])) / len(pattern_config["file_types"])
            confidence += file_type_match * weights["file_type_match"]
        else:
            confidence += 0.1  # Базовый бонус для универсальных инструментов

        # Совпадение по паттернам текста
        request_lower = context.user_request.lower()
        pattern_matches = sum(1 for pattern in pattern_config["patterns"] if pattern in request_lower)
        if pattern_matches > 0:
            semantic_match = min(pattern_matches / len(pattern_config["patterns"]), 1.0)
            confidence += semantic_match * weights["semantic_match"]

        # Бонус за сложность
        complexity_bonus = pattern_config.get("confidence_boost", 0.0)
        confidence += complexity_bonus * weights["complexity_match"]

        # Бонус от обучения
        learning_bonus = self._get_learning_bonus(context, pattern_config["primary_tool"])
        confidence += learning_bonus * weights["learning_bonus"]

        return min(confidence, 1.0)

    def _get_tool_category(self, tool_name: str) -> ToolCategory:
        """Определение категории инструмента"""
        if tool_name.startswith('mcp__'):
            if 'serena' in tool_name or 'ast-grep' in tool_name:
                return ToolCategory.MCP_SEMANTIC
            elif 'sequential-thinking' in tool_name:
                return ToolCategory.MCP_THINKING
            else:
                return ToolCategory.MCP_EXTERNAL
        return ToolCategory.STANDARD

    def _estimate_execution_time(self, tool_name: str, complexity: TaskComplexity) -> str:
        """Оценка времени выполнения"""
        base_times = {
            'mcp__ast-grep-mcp__ast_grep': '5-15 сек',
            'mcp__serena__get_symbols_overview': '10-30 сек',
            'mcp__serena__find_symbol': '5-20 сек',
            'mcp__serena__find_referencing_symbols': '15-45 сек',
            'mcp__universal-web-scraper__scrape_website': '30 сек - 3 мин',
            'mcp__docling__convert_document': '30 сек - 5 мин',
            'mcp__sequential-thinking__sequentialthinking': '2-10 мин'
        }

        base_time = base_times.get(tool_name, '10-30 сек')

        if complexity in [TaskComplexity.COMPLEX, TaskComplexity.STRATEGIC]:
            return f"{base_time} (увеличено из-за сложности)"

        return base_time

    def _get_learning_bonus(self, context: TaskContext, tool_name: str) -> float:
        """Получение бонуса от системы обучения"""
        # Простая система обучения на основе успешного использования
        request_hash = hashlib.md5(context.user_request.encode()).hexdigest()

        if request_hash in self.learning_data:
            successful_tools = self.learning_data[request_hash].get('successful_tools', [])
            if tool_name in successful_tools:
                return 0.1  # 10% бонус за успешное использование

        return 0.0

    def _update_learning_data(self, context: TaskContext, recommendations: List[ToolRecommendation]):
        """Обновление данных обучения"""
        request_hash = hashlib.md5(context.user_request.encode()).hexdigest()

        if request_hash not in self.learning_data:
            self.learning_data[request_hash] = {
                'request': context.user_request,
                'timestamp': datetime.now().isoformat(),
                'recommendations': [],
                'successful_tools': []
            }

        # Сохранение рекомендаций
        self.learning_data[request_hash]['recommendations'] = [
            {
                'tool': rec.tool_name,
                'confidence': rec.confidence,
                'reason': rec.reason
            }
            for rec in recommendations[:3]
        ]

        self.save_learning_data()

    def load_learning_data(self) -> Dict:
        """Загрузка данных обучения"""
        learning_file = Path(self.cache_path) / "learning_data.json"
        try:
            if learning_file.exists():
                with open(learning_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Ошибка загрузки данных обучения: {e}")

        return {}

    def save_learning_data(self):
        """Сохранение данных обучения"""
        learning_file = Path(self.cache_path) / "learning_data.json"
        try:
            with open(learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения данных обучения: {e}")

    def save_configuration(self):
        """Сохранение конфигурации"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения конфигурации: {e}")

    def generate_recommendation_report(self, context: TaskContext, recommendations: List[ToolRecommendation]) -> str:
        """Генерация отчета с рекомендациями"""
        report = f"""
# Dynamic Context Engine - Рекомендации по инструментам

## Анализ запроса
**Запрос:** {context.user_request}
**Файлы:** {', '.join(context.file_paths) if context.file_paths else 'Не указаны'}
**Типы файлов:** {', '.join([ft.value for ft in context.file_types])}
**Сложность:** {context.complexity.value}
**Намерение:** {context.intent}
**Предметная область:** {context.domain}
**Ключевые слова:** {', '.join(context.keywords)}

## Рекомендуемые инструменты

"""

        for i, rec in enumerate(recommendations, 1):
            confidence_level = "Высокая" if rec.confidence >= 0.8 else "Средняя" if rec.confidence >= 0.6 else "Низкая"

            report += f"""
### {i}. {rec.tool_name}
**Уверенность:** {rec.confidence:.2f} ({confidence_level})
**Причина:** {rec.reason}
**Категория:** {rec.category.value}
**Время выполнения:** {rec.estimated_time or 'Не оценено'}
**Fallback:** {rec.fallback_tool or 'Нет'}

**Параметры:**
```json
{json.dumps(rec.parameters, ensure_ascii=False, indent=2)}
```
"""

        report += f"""
## Статистика
**Всего проанализировано паттернов:** {len(self.tool_patterns)}
**Генерация отчета:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Версия движка:** 1.0
"""

        return report

def main():
    """Тестирование Dynamic Context Engine"""
    engine = DynamicContextEngine()

    # Тестовые примеры
    test_cases = [
        {
            "request": "Найди все функции в модуле ObjectModule.bsl",
            "files": ["src/DataProcessors/гкс_АРМПромежуточныйКомпозит/Ext/ObjectModule.bsl"]
        },
        {
            "request": "Где используется функция ЗаполнитьСписокПроизвольныйКомпозит?",
            "files": ["Forms/Форма/Ext/Form/Module.bsl"]
        },
        {
            "request": "Парсинг документации с сайта its.1c.ru",
            "files": []
        },
        {
            "request": "Конвертировать PDF техническое задание в Markdown",
            "files": ["docs/technical_specification.pdf"]
        },
        {
            "request": "Проанализировать архитектуру конфигурации и предложить улучшения",
            "files": ["src/projects/configuration/"]
        }
    ]

    print("🚀 Тестирование Dynamic Context Engine v1.0\n")

    for i, test_case in enumerate(test_cases, 1):
        print(f"{'='*60}")
        print(f"ТЕСТ {i}: {test_case['request']}")
        print(f"{'='*60}")

        # Анализ контекста
        context = engine.analyze_request(test_case['request'], test_case['files'])

        # Получение рекомендаций
        recommendations = engine.recommend_tools(context)

        # Генерация отчета
        report = engine.generate_recommendation_report(context, recommendations)

        # Сохранение отчета
        report_file = Path(engine.cache_path) / f"test_report_{i}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✅ Отчет сохранен: {report_file}")

        # Краткий вывод топ-3 рекомендаций
        print("\n🎯 ТОП-3 РЕКОМЕНДАЦИИ:")
        for j, rec in enumerate(recommendations[:3], 1):
            print(f"{j}. {rec.tool_name} (уверенность: {rec.confidence:.2f})")
            print(f"   Причина: {rec.reason}")

        print("\n")

    print("🎉 Все тесты завершены! Отчеты в папке cache/context-engine/")

if __name__ == "__main__":
    main()