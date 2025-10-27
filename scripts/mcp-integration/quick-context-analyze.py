#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Start Script for Dynamic Context Engine
Быстрый запуск системы интеллектуального выбора инструментов
"""

import sys
import json
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent))

from dynamic_context_engine import DynamicContextEngine, TaskContext

def quick_analyze(user_request, file_paths=None):
    """Быстрый анализ запроса"""

    print(f"🤖 Dynamic Context Engine v1.0")
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

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Dynamic Context Engine Quick Start")
    parser.add_argument("request", help="Запрос пользователя")
    parser.add_argument("--files", nargs="*", help="Пути к файлам")

    args = parser.parse_args()

    quick_analyze(args.request, args.files)
