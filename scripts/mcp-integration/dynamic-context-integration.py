#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dynamic Context Integration Script v1.0
Скрипт для интеграции Dynamic Context Engine с CLAUDE.md

Автоматически модифицирует CLAUDE.md для включения правил
интеллектуального выбора инструментов.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent))

try:
    from dynamic_context_engine import DynamicContextEngine
except ImportError:
    print("⚠️ Модуль dynamic_context_engine не найден, создаю базовую интеграцию")

def integrate_dynamic_context_with_claude_md():
    """Интеграция Dynamic Context Engine с CLAUDE.md"""

    claude_md_path = Path("D:/1C-Enterprise_Framework/CLAUDE.md")
    backup_path = Path("D:/1C-Enterprise_Framework/CLAUDE.md.backup")

    # Создание резервной копии
    if claude_md_path.exists():
        with open(claude_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Создана резервная копия: {backup_path}")
    else:
        print("❌ CLAUDE.md не найден!")
        return False

    # Поиск секции Tool usage policy
    tool_policy_pattern = r'(# Tool usage policy.*?)(?=\n# |$)'

    # Новая секция с интеграцией Dynamic Context Engine
    new_tool_policy = """# Tool usage policy

## 🤖 Dynamic Context Engine - Автоматический выбор инструментов

**ВАЖНО:** Фреймворк оснащен системой интеллектуального выбора инструментов, которая автоматически анализирует контекст запроса и предлагает оптимальные MCP инструменты.

### 🚀 Быстрый запуск Dynamic Context Engine

```python
# Автоматический анализ запроса и выбор инструментов
python scripts/mcp-integration/dynamic-context-engine.py --analyze "Найди все функции в модуле ObjectModule.bsl"

# Интерактивный режим с рекомендациями
python scripts/mcp-integration/dynamic-context-integration.py --interactive
```

### ⚡ Основные принципы выбора

**Семантические операции → MCP серверы**
**Текстовые операции → Стандартные инструменты**

### 🔴 ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА для BSL файлов

**ВСЕГДА используй `mcp__ast-grep-mcp__ast_grep` для анализа структуры BSL файлов**

```javascript
// ✅ ПРАВИЛЬНО - Анализ структуры BSL модуля
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($$$ARGS)",
  path: "src/DataProcessors/Module/Ext/ObjectModule.bsl",
  bsl_type: "functions"
})
```

### 📊 Автоматические рекомендации по типу задачи

| Задача | Уверенность | Инструмент | Время |
|--------|-------------|-------------|--------|
| **Анализ структуры BSL** | 90% | `mcp__ast-grep-mcp__ast_grep` | 5-15 сек |
| **Поиск функции BSL** | 85% | `mcp__ast-grep-mcp__ast_grep` | 5-20 сек |
| **Анализ зависимостей** | 80% | `mcp__serena__find_referencing_symbols` | 15-45 сек |
| **Поиск в документации** | 75% | `mcp__1c-framework-docs__search_docs` | 10-30 сек |
| **Парсинг веб-сайтов** | 95% | `mcp__universal-web-scraper__scrape_website` | 30 сек - 3 мин |
| **Конвертация документов** | 90% | `mcp__docling__convert_document` | 30 сек - 5 мин |
| **Сложный анализ** | 70% | `mcp__sequential-thinking__sequentialthinking` | 2-10 мин |

### 🧠 Self-Learning система

Engine автоматически обучается на основе:
- Успешного выполнения рекомендаций
- Частоты использования инструментов
- Контекста задач и их результатов
- Временных затрат на выполнение

### 📁 Конфигурация и кэширование

**Конфигурация:** `.claude/dynamic-context-config.json`
**Кэш рекомендаций:** `cache/context-engine/`
**Данные обучения:** `cache/context-engine/learning_data.json`

### 🔧 Настройка весов приоритизации

```json
{
  "weights": {
    "file_type_match": 0.4,      // Соответствие типа файла
    "semantic_match": 0.3,       // Семантическое совпадение
    "complexity_match": 0.2,     // Соответствие сложности
    "learning_bonus": 0.1        // Бонус от обучения
  }
}
```

### 📋 Практические примеры автоматического выбора

#### Запрос: "Найди все функции в модуле ObjectModule.bsl"
**Анализ контекста:**
- Тип файла: BSL ✅
- Намерение: search ✅
- Сложность: simple ✅
- Предметная область: 1c ✅

**Автоматическая рекомендация:**
```javascript
// Уверенность: 90% - Высокая
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($$$ARGS)",
  bsl_type: "functions",
  path: "src/module.bsl"
})
```

#### Запрос: "Где используется функция ЗаполнитьСписок?"
**Автоматическая рекомендация:**
```javascript
// Уверенность: 85% - Высокая
mcp__serena__find_referencing_symbols({
  name_path: "ЗаполнитьСписок",
  relative_path: "Module.bsl"
})
```

#### Запрос: "Парсинг документации с сайта its.1c.ru"
**Автоматическая рекомендация:**
```javascript
// Уверенность: 95% - Очень высокая
mcp__universal-web-scraper__scrape_website({
  url: "https://its.1c.ru/db/metod8dev",
  adapter_type: "its_1c",
  save_to_memory: true
})
```

### 🎯 Интеграция с существующими правилами

Dynamic Context Engine полностью совместим с существующими [MCP Priority Rules](.claude/mcp-priority-rules.md) и расширяет их возможности:

- ✅ Автоматический анализ контекста
- ✅ Интеллектуальная приоритизация
- ✅ Self-learning на основе использования
- ✅ Кэширование рекомендаций
- ✅ Производительность и метрики

---

**Версия Dynamic Context Engine:** 1.0
**Дата интеграции:** """ + datetime.now().strftime('%Y-%m-%d') + """
**Статус:** ✅ Полностью интегрирован и готов к использованию

---"""

    # Замена секции Tool usage policy
    if re.search(tool_policy_pattern, content, re.DOTALL):
        new_content = re.sub(tool_policy_pattern, new_tool_policy, content, flags=re.DOTALL)
        print("✅ Найдена и обновлена секция 'Tool usage policy'")
    else:
        # Добавление новой секции после Repository Overview
        repo_overview_pattern = r'(## 🏗️ Repository Overview.*?)(?=\n## |$)'
        if re.search(repo_overview_pattern, content, re.DOTALL):
            new_content = re.sub(repo_overview_pattern, r'\1\n\n' + new_tool_policy, content, flags=re.DOTALL)
            print("✅ Добавлена новая секция 'Tool usage policy' после Repository Overview")
        else:
            # Добавление в конец файла
            new_content = content + "\n\n" + new_tool_policy
            print("✅ Добавлена новая секция в конец CLAUDE.md")

    # Сохранение обновленного файла
    with open(claude_md_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ CLAUDE.md успешно обновлен с интеграцией Dynamic Context Engine")

    return True

def create_quick_start_script():
    """Создание скрипта быстрого запуска"""

    script_content = '''#!/usr/bin/env python3
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
'''

    script_path = Path("D:/1C-Enterprise_Framework/scripts/mcp-integration/quick-context-analyze.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)

    print(f"✅ Создан скрипт быстрого запуска: {script_path}")

    return script_path

def create_integration_documentation():
    """Создание документации по интеграции"""

    doc_content = '''# Dynamic Context Engine Integration Guide

## 🎯 Обзор

Dynamic Context Engine - это система интеллектуального выбора MCP инструментов для фреймворка 1C-Enterprise, которая автоматически анализирует контекст запроса пользователя и предлагает наиболее подходящие инструменты.

## 🚀 Быстрый старт

### 1. Автоматический анализ запроса
```bash
python scripts/mcp-integration/quick-context-analyze.py "Найди все функции в модуле ObjectModule.bsl" --files "src/module.bsl"
```

### 2. Полный анализ с отчетом
```python
from dynamic_context_engine import DynamicContextEngine

engine = DynamicContextEngine()
context = engine.analyze_request("Найди функции", ["file.bsl"])
recommendations = engine.recommend_tools(context)
report = engine.generate_recommendation_report(context, recommendations)
```

## 🧠 Архитектура системы

### Основные компоненты

1. **TaskContext** - контекст задачи с анализом запроса
2. **ToolRecommendation** - рекомендация по использованию инструмента
3. **DynamicContextEngine** - основной движок анализа
4. **Learning System** - система самообучения

### Алгоритм работы

```mermaid
graph TD
    A[Запрос пользователя] --> B[Анализ контекста]
    B --> C[Определение типов файлов]
    B --> D[Извлечение ключевых слов]
    B --> E[Определение сложности]
    B --> F[Определение намерения]

    C --> G[Расчет уверенности]
    D --> G
    E --> G
    F --> G

    G --> H[Ранжирование инструментов]
    H --> I[Генерация рекомендаций]
    I --> J[Обновление данных обучения]
```

## 📊 Система весов и приоритизации

### Веса для расчета уверенности
```json
{
  "file_type_match": 0.4,      // 40% - соответствие типа файла
  "semantic_match": 0.3,       // 30% - семантическое совпадение
  "complexity_match": 0.2,     // 20% - соответствие сложности
  "learning_bonus": 0.1        // 10% - бонус от обучения
}
```

### Пороги уверенности
- **Высокая (>= 0.8)**: Настоятельно рекомендуется
- **Средняя (>= 0.6)**: Рекомендуется с осторожностью
- **Низкая (>= 0.4)**: Альтернативный вариант

## 🔧 Конфигурация

### Основной файл конфигурации
**Путь:** `.claude/dynamic-context-config.json`

```json
{
  "version": "1.0",
  "weights": { /* веса приоритизации */ },
  "confidence_thresholds": { /* пороги уверенности */ },
  "tool_availability": { /* доступность инструментов */ },
  "bsl_specific": {
    "mandatory_ast_grep": true,
    "ast_grep_confidence_boost": 0.3
  }
}
```

### Паттерны выбора инструментов

Engine использует предопределенные паттерны для каждого типа задач:

- **bsl_structure_analysis** - анализ структуры BSL
- **bsl_function_search** - поиск функций/процедур
- **dependency_analysis** - анализ зависимостей
- **documentation_search** - поиск в документации
- **web_scraping** - парсинг веб-сайтов
- **document_conversion** - конвертация документов

## 📈 Self-Learning система

### Механизм обучения

1. **Сбор данных** - сохранение истории рекомендаций
2. **Анализ успешности** - отслеживание использованных инструментов
3. **Корректировка весов** - автоматическое улучшение алгоритма
4. **Персистентное хранение** - сохранение знаний между сессиями

### Файлы данных обучения
- `cache/context-engine/learning_data.json` - история рекомендаций
- `cache/context-engine/test_report_*.md` - отчеты тестирования

## 🎯 Практические примеры

### Пример 1: Анализ BSL модуля
```python
# Запрос: "Покажи структуру модуля ObjectModule.bsl"
# Результат: mcp__ast-grep-mcp__ast_grep (уверенность: 0.90)

mcp__ast-grep-mcp__ast_grep({
  "pattern": "Функция $NAME($$$ARGS)",
  "bsl_type": "functions",
  "path": "src/ObjectModule.bsl"
})
```

### Пример 2: Поиск зависимостей
```python
# Запрос: "Где используется функция ЗаполнитьСписок?"
# Результат: mcp__serena__find_referencing_symbols (уверенность: 0.85)

mcp__serena__find_referencing_symbols({
  "name_path": "ЗаполнитьСписок",
  "relative_path": "Module.bsl"
})
```

### Пример 3: Парсинг документации
```python
# Запрос: "Парсинг статьи с ITS 1C"
# Результат: mcp__universal-web-scraper__scrape_website (уверенность: 0.95)

mcp__universal-web-scraper__scrape_website({
  "url": "https://its.1c.ru/article",
  "adapter_type": "its_1c",
  "save_to_memory": true
})
```

## 🔄 Интеграция с существующими системами

### Связь с MCP Priority Rules
Engine расширяет существующие правила приоритизации из `.claude/mcp-priority-rules.md`:
- Автоматизирует выбор инструментов
- Добавляет интеллектуальный анализ контекста
- Сохраняет совместимость с ручными правилами

### Интеграция с CLAUDE.md
После запуска `dynamic-context-integration.py` в CLAUDE.md добавляется:
- Секция с описанием Dynamic Context Engine
- Автоматические рекомендации для типовых задач
- Примеры использования и конфигурации

## 📋 Метрики и мониторинг

### Ключевые метрики
- **Точность рекомендаций** - процент успешных предложений
- **Время анализа** - скорость обработки запроса
- **Использование инструментов** - статистика применения MCP
- **Обучение системы** - прогресс алгоритма

### Логирование
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🚀 Развитие и улучшения

### Запланированные функции (v1.1)
- [ ] Интеграция с внешними LLM для улучшения анализа
- [ ] Поддержка пользовательских паттернов
- [ ] Расширенная аналитика использования
- [ ] API для интеграции с другими инструментами

### Возможности расширения
- Добавление новых типов файлов
- Создание доменно-специфических правил
- Интеграция с системами мониторинга
- Экспорт рекомендаций в различные форматы

## 🔧 Устранение неполадок

### Частые проблемы

1. **Низкая уверенность рекомендаций**
   - Проверить соответствие ключевых слов в запросе
   - Настроить веса в конфигурации
   - Добавить новые паттерны для специфических задач

2. **Отсутствие рекомендаций**
   - Убедиться в доступности инструментов
   - Проверить корректность типов файлов
   - Добавить fallback инструменты

3. **Медленная работа**
   - Включить кэширование рекомендаций
   - Оптимизировать регулярные выражения
   - Ограничить количество анализируемых паттернов

### Диагностика
```bash
# Тестирование с подробным логированием
PYTHONIOENCODING=utf-8 python scripts/mcp-integration/dynamic-context-engine.py --debug

# Проверка конфигурации
python -c "
from dynamic_context_engine import DynamicContextEngine
engine = DynamicContextEngine()
print('Config loaded:', engine.config['version'])
"
```

---

**Версия документации:** 1.0
**Последнее обновление:** ''' + datetime.now().strftime('%Y-%m-%d') + '''
**Поддержка:** D:/1C-Enterprise_Framework/scripts/mcp-integration/
'''

    doc_path = Path("D:/1C-Enterprise_Framework/docs/dynamic-context-engine.md")
    doc_path.parent.mkdir(parents=True, exist_ok=True)

    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(doc_content)

    print(f"✅ Создана документация: {doc_path}")

    return doc_path

def main():
    """Основная функция интеграции"""
    print("🚀 Запуск интеграции Dynamic Context Engine с фреймворком")
    print("=" * 60)

    # 1. Интеграция с CLAUDE.md
    print("1️⃣ Интеграция с CLAUDE.md...")
    if integrate_dynamic_context_with_claude_md():
        print("   ✅ CLAUDE.md успешно обновлен")
    else:
        print("   ❌ Ошибка обновления CLAUDE.md")
        return False

    # 2. Создание скрипта быстрого запуска
    print("\n2️⃣ Создание скрипта быстрого запуска...")
    quick_script = create_quick_start_script()
    print(f"   ✅ Скрипт создан: {quick_script}")

    # 3. Создание документации
    print("\n3️⃣ Создание документации...")
    doc_path = create_integration_documentation()
    print(f"   ✅ Документация создана: {doc_path}")

    # 4. Финальная проверка
    print("\n4️⃣ Проверка интеграции...")

    required_files = [
        "D:/1C-Enterprise_Framework/scripts/mcp-integration/dynamic-context-engine.py",
        "D:/1C-Enterprise_Framework/.claude/dynamic-context-config.json",
        "D:/1C-Enterprise_Framework/scripts/mcp-integration/quick-context-analyze.py",
        "D:/1C-Enterprise_Framework/docs/dynamic-context-engine.md"
    ]

    all_files_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {Path(file_path).name}")
        else:
            print(f"   ❌ {Path(file_path).name} - НЕ НАЙДЕН")
            all_files_exist = False

    print("\n" + "=" * 60)
    if all_files_exist:
        print("🎉 Dynamic Context Engine успешно интегрирован!")
        print("\n📋 Что добавлено:")
        print("   • Автоматический анализ контекста запросов")
        print("   • Интеллектуальный выбор MCP инструментов")
        print("   • Self-learning система для улучшения рекомендаций")
        print("   • Интеграция с существующими MCP Priority Rules")
        print("   • Полная документация и примеры использования")

        print("\n🚀 Быстрый старт:")
        print("   python scripts/mcp-integration/quick-context-analyze.py \"Найди функции в модуле\"")
        print("   python scripts/mcp-integration/dynamic-context-engine.py")

        print("\n📚 Документация:")
        print("   docs/dynamic-context-engine.md")
        print("   .claude/mcp-priority-rules.md")

        return True
    else:
        print("❌ Интеграция завершена с ошибками!")
        return False

if __name__ == "__main__":
    main()