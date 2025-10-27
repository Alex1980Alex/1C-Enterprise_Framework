#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Start Script for Dynamic Context Engine v1.0
Быстрый запуск системы интеллектуального выбора инструментов
"""

import sys
import json
import os
from pathlib import Path

# Добавляем путь к модулям
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Импорт с обработкой ошибок
try:
    from dynamic_context_engine import DynamicContextEngine, TaskContext
    ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Модуль dynamic_context_engine не найден: {e}")
    ENGINE_AVAILABLE = False

def quick_analyze_basic(user_request, file_paths=None):
    """Базовый анализ без полного движка"""

    print(f"🤖 Dynamic Context Engine v1.0 (Базовый режим)")
    print(f"📝 Запрос: {user_request}")
    print(f"📁 Файлы: {file_paths if file_paths else 'Не указаны'}")
    print("-" * 60)

    # Простой анализ на основе ключевых слов
    request_lower = user_request.lower()
    file_extensions = []

    if file_paths:
        file_extensions = [Path(fp).suffix.lower() for fp in file_paths]

    # Определение типа задачи
    task_type = "unknown"
    if any(word in request_lower for word in ['найти', 'найди', 'структура', 'функции', 'процедуры']):
        task_type = "search"
    elif any(word in request_lower for word in ['заменить', 'изменить', 'обновить']):
        task_type = "modify"
    elif any(word in request_lower for word in ['создать', 'добавить', 'новый']):
        task_type = "create"
    elif any(word in request_lower for word in ['парсинг', 'сайт', 'документация']):
        task_type = "web_parsing"
    elif any(word in request_lower for word in ['конвертировать', 'pdf', 'docx']):
        task_type = "document_conversion"

    # Базовые рекомендации
    recommendations = []

    if '.bsl' in file_extensions or any(word in request_lower for word in ['bsl', 'функция', 'процедура', '1с']):
        if task_type == "search":
            recommendations.append({
                'tool': 'mcp__ast-grep-mcp__ast_grep',
                'confidence': 0.9,
                'reason': 'BSL структурный анализ - ОБЯЗАТЕЛЬНО',
                'params': {
                    'pattern': 'Функция $NAME($$$ARGS)',
                    'bsl_type': 'functions',
                    'path': file_paths[0] if file_paths else 'src/'
                }
            })
        elif task_type == "modify":
            recommendations.append({
                'tool': 'mcp__serena__replace_symbol_body',
                'confidence': 0.85,
                'reason': 'Замена тела BSL функции/процедуры',
                'params': {
                    'name_path': 'ИмяФункции',
                    'relative_path': file_paths[0] if file_paths else 'Module.bsl'
                }
            })

    if task_type == "web_parsing":
        recommendations.append({
            'tool': 'mcp__universal-web-scraper__scrape_website',
            'confidence': 0.95,
            'reason': 'Парсинг веб-сайтов с интеллектуальными адаптерами',
            'params': {
                'url': 'https://its.1c.ru/db/metod8dev',
                'adapter_type': 'its_1c' if 'its.1c' in request_lower else 'auto',
                'save_to_memory': True
            }
        })

    if task_type == "document_conversion":
        recommendations.append({
            'tool': 'mcp__docling__convert_document',
            'confidence': 0.9,
            'reason': 'Конвертация документов в Markdown',
            'params': {
                'extract_images': True,
                'ocr_enabled': True
            }
        })

    # Документация
    if any(word in request_lower for word in ['документация', 'фреймворк', 'как сделать']):
        recommendations.append({
            'tool': 'mcp__1c-framework-docs__search_docs',
            'confidence': 0.8,
            'reason': 'Поиск в документации фреймворка',
            'params': {
                'search_type': 'hybrid',
                'limit': 5
            }
        })

    # Сложный анализ
    if any(word in request_lower for word in ['анализ', 'проанализ', 'сложн', 'планирование']):
        recommendations.append({
            'tool': 'mcp__sequential-thinking__sequentialthinking',
            'confidence': 0.75,
            'reason': 'Сложный многоступенчатый анализ',
            'params': {
                'totalThoughts': 5,
                'nextThoughtNeeded': True
            }
        })

    print(f"🎯 Базовый анализ:")
    print(f"   Тип файлов: {file_extensions}")
    print(f"   Тип задачи: {task_type}")
    print(f"   Предметная область: {'1c' if '.bsl' in file_extensions else 'general'}")
    print()

    print(f"🔧 Рекомендуемые инструменты:")

    if not recommendations:
        print("   ❌ Рекомендации не найдены")
        print("   💡 Попробуйте: mcp__serena__search_for_pattern для общего поиска")
        return

    for i, rec in enumerate(recommendations[:3], 1):
        confidence_emoji = "🟢" if rec['confidence'] >= 0.8 else "🟡" if rec['confidence'] >= 0.6 else "🔴"
        print(f"   {i}. {confidence_emoji} {rec['tool']}")
        print(f"      Уверенность: {rec['confidence']:.2f}")
        print(f"      Причина: {rec['reason']}")
        print()

    # Показать команду для топ рекомендации
    if recommendations:
        top_rec = recommendations[0]
        print(f"🚀 Рекомендуемая команда:")
        print(f"```javascript")
        print(f"{top_rec['tool']}({{")
        for key, value in top_rec['params'].items():
            if isinstance(value, str):
                print(f'  {key}: "{value}",')
            else:
                print(f'  {key}: {json.dumps(value)},')
        print(f"}})")
        print(f"```")

def quick_analyze_full(user_request, file_paths=None):
    """Полный анализ с движком"""

    print(f"🤖 Dynamic Context Engine v1.0 (Полный режим)")
    print(f"📝 Запрос: {user_request}")
    print(f"📁 Файлы: {file_paths if file_paths else 'Не указаны'}")
    print("-" * 60)

    # Инициализация движка
    engine = DynamicContextEngine()

    # Анализ контекста
    context = engine.analyze_request(user_request, file_paths or [])

    # Получение рекомендаций
    recommendations = engine.recommend_tools(context)

    print(f"🎯 Анализ контекста:")
    print(f"   Типы файлов: {[ft.value for ft in context.file_types]}")
    print(f"   Сложность: {context.complexity.value}")
    print(f"   Намерение: {context.intent}")
    print(f"   Область: {context.domain}")
    print()

    print(f"🔧 Рекомендуемые инструменты:")

    if not recommendations:
        print("   ❌ Рекомендации не найдены")
        return

    for i, rec in enumerate(recommendations[:3], 1):
        confidence_emoji = "🟢" if rec.confidence >= 0.8 else "🟡" if rec.confidence >= 0.6 else "🔴"
        print(f"   {i}. {confidence_emoji} {rec.tool_name}")
        print(f"      Уверенность: {rec.confidence:.2f}")
        print(f"      Время: {rec.estimated_time}")
        print(f"      Причина: {rec.reason}")
        print()

    # Показать команду для топ рекомендации
    if recommendations:
        top_rec = recommendations[0]
        print(f"🚀 Рекомендуемая команда:")
        print(f"```javascript")
        print(f"{top_rec.tool_name}({{")
        for key, value in top_rec.parameters.items():
            if isinstance(value, str):
                print(f'  {key}: "{value}",')
            else:
                print(f'  {key}: {json.dumps(value)},')
        print(f"}})")
        print(f"```")

def main():
    """Главная функция"""
    import argparse

    parser = argparse.ArgumentParser(description="Dynamic Context Engine Quick Start")
    parser.add_argument("request", help="Запрос пользователя")
    parser.add_argument("--files", nargs="*", help="Пути к файлам")
    parser.add_argument("--basic", action="store_true", help="Использовать базовый режим")

    args = parser.parse_args()

    if ENGINE_AVAILABLE and not args.basic:
        try:
            quick_analyze_full(args.request, args.files)
        except Exception as e:
            print(f"⚠️ Ошибка в полном режиме: {e}")
            print("🔄 Переключение на базовый режим...")
            quick_analyze_basic(args.request, args.files)
    else:
        quick_analyze_basic(args.request, args.files)

if __name__ == "__main__":
    main()