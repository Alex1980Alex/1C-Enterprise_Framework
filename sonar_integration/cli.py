#!/usr/bin/env python3
"""
Command Line Interface for SonarQube Integration
Интерфейс командной строки для интеграции SonarQube
"""

import argparse
import json
import sys
from pathlib import Path

from .config_manager import ConfigManager
from .rules_manager import RulesManager
from .report_generator import ReportGenerator
from .ci_integration import CIIntegration


def init_project(args):
    """Инициализация проекта с SonarQube"""
    config_manager = ConfigManager(args.project_root)
    
    custom_rules = {}
    if args.max_complexity:
        custom_rules["CyclomaticComplexity.maxComplexity"] = args.max_complexity
    if args.max_line_length:
        custom_rules["LineLength.maxLineLength"] = args.max_line_length
    if args.max_method_size:
        custom_rules["MethodSize.maxMethodSize"] = args.max_method_size
    
    success = config_manager.sync_configs(
        args.project_key,
        args.project_name,
        custom_rules
    )
    
    if success:
        print(f"✅ Проект '{args.project_name}' успешно инициализирован!")
        print(f"📁 Созданы файлы:")
        print(f"   - sonar-project.properties")
        print(f"   - .bsl-language-server.json")
    else:
        print("❌ Ошибка инициализации проекта")
        sys.exit(1)


def list_rules(args):
    """Список доступных правил"""
    rules_manager = RulesManager()
    
    if args.severity:
        rules = rules_manager.get_rules_by_severity(args.severity)
        print(f"\n📋 Правила уровня {args.severity}:")
    elif args.category:
        rules = rules_manager.get_rules_by_category(args.category)
        print(f"\n📋 Правила категории '{args.category}':")
    else:
        rules = list(rules_manager.rules_cache.values())
        print(f"\n📋 Все доступные правила ({len(rules)}):")
    
    for rule in rules:
        status = "✅" if rule.enabled else "❌"
        print(f"{status} {rule.key:<30} | {rule.severity:<8} | {rule.name}")
        if args.verbose:
            print(f"    {rule.description}")
            if rule.default_value:
                print(f"    Значение по умолчанию: {rule.default_value}")
            print()


def create_profile(args):
    """Создание профиля правил"""
    rules_manager = RulesManager()
    
    severity_levels = args.severity.split(',') if args.severity else None
    categories = args.category.split(',') if args.category else None
    
    profile = rules_manager.create_rules_profile(
        args.name,
        severity_levels,
        categories
    )
    
    output_file = args.output or f"{args.name.lower().replace(' ', '_')}_profile.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Профиль '{args.name}' создан: {output_file}")
        print(f"📊 Включено правил: {len(profile['rules'])}")
        
    except Exception as e:
        print(f"❌ Ошибка создания профиля: {e}")
        sys.exit(1)


def analyze(args):
    """Запуск анализа кода"""
    ci = CIIntegration(args.project_root)
    
    print("🔍 Запуск анализа BSL Language Server...")
    result = ci.run_local_analysis(args.src_dir, args.output_dir)
    
    if result["success"]:
        print(f"✅ Анализ завершен успешно!")
        if "total_issues" in result:
            print(f"📊 Найдено проблем: {result['total_issues']}")
            print(f"📁 Проанализировано файлов: {result['analyzed_files']}")
        print(f"📁 Отчеты сохранены в: {result['reports_dir']}")
    else:
        print(f"❌ Ошибка анализа: {result.get('error', 'Неизвестная ошибка')}")
        if result.get("stderr"):
            print(f"Stderr: {result['stderr']}")
        sys.exit(1)


def generate_report(args):
    """Генерация отчета"""
    report_gen = ReportGenerator(args.output_dir)
    
    if not Path(args.input_file).exists():
        print(f"❌ Файл не найден: {args.input_file}")
        sys.exit(1)
    
    print(f"📊 Обработка отчета: {args.input_file}")
    
    if args.format == "sonar":
        results = report_gen.parse_sonar_json_report(args.input_file)
    else:
        results = report_gen.parse_bsl_json_report(args.input_file)
    
    if not results:
        print("⚠️ Проблемы в коде не найдены или ошибка парсинга")
        return
    
    print(f"📋 Найдено проблем: {len(results)}")
    
    # Генерируем отчеты в разных форматах
    if args.excel:
        excel_file = report_gen.export_to_excel(results)
        if excel_file:
            print(f"📊 Excel отчет: {excel_file}")
    
    if args.csv:
        csv_file = report_gen.export_to_csv(results)
        if csv_file:
            print(f"📄 CSV отчет: {csv_file}")
    
    if args.html:
        html_file = report_gen.export_to_html(results)
        if html_file:
            print(f"🌐 HTML отчет: {html_file}")
    
    # Выводим сводку
    summary = report_gen.generate_summary_report(results)
    print(f"\n📈 Сводка по критичности:")
    for severity, count in summary["by_severity"].items():
        print(f"   {severity}: {count}")


def setup_ci(args):
    """Настройка CI/CD"""
    ci = CIIntegration(args.project_root)
    
    success = ci.create_ci_config_files(args.type, args.project_key)
    
    if success:
        print(f"✅ Конфигурация {args.type} создана!")
        
        if args.pre_commit:
            if ci.setup_pre_commit_hook():
                print("✅ Pre-commit хук настроен")
            else:
                print("⚠️ Ошибка настройки pre-commit хука")
    else:
        print(f"❌ Ошибка создания конфигурации {args.type}")
        sys.exit(1)


def main():
    """Главная функция CLI"""
    parser = argparse.ArgumentParser(
        description="SonarQube Integration для 1С:Предприятие",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--project-root", 
        default=".",
        help="Корневая папка проекта (по умолчанию: текущая)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")
    
    # Команда init
    init_parser = subparsers.add_parser("init", help="Инициализация проекта")
    init_parser.add_argument("project_key", help="Ключ проекта SonarQube")
    init_parser.add_argument("project_name", help="Название проекта")
    init_parser.add_argument("--max-complexity", type=int, help="Максимальная цикломатическая сложность")
    init_parser.add_argument("--max-line-length", type=int, help="Максимальная длина строки")
    init_parser.add_argument("--max-method-size", type=int, help="Максимальный размер метода")
    init_parser.set_defaults(func=init_project)
    
    # Команда rules
    rules_parser = subparsers.add_parser("rules", help="Управление правилами")
    rules_parser.add_argument("--severity", help="Фильтр по критичности")
    rules_parser.add_argument("--category", help="Фильтр по категории")
    rules_parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод")
    rules_parser.set_defaults(func=list_rules)
    
    # Команда profile
    profile_parser = subparsers.add_parser("profile", help="Создание профиля правил")
    profile_parser.add_argument("name", help="Название профиля")
    profile_parser.add_argument("--severity", help="Уровни критичности (через запятую)")
    profile_parser.add_argument("--category", help="Категории (через запятую)")
    profile_parser.add_argument("--output", "-o", help="Файл для сохранения")
    profile_parser.set_defaults(func=create_profile)
    
    # Команда analyze
    analyze_parser = subparsers.add_parser("analyze", help="Анализ кода")
    analyze_parser.add_argument("--src-dir", default="src", help="Папка с исходниками")
    analyze_parser.add_argument("--output-dir", default="reports", help="Папка для отчетов")
    analyze_parser.set_defaults(func=analyze)
    
    # Команда report
    report_parser = subparsers.add_parser("report", help="Генерация отчета")
    report_parser.add_argument("input_file", help="Файл с результатами анализа")
    report_parser.add_argument("--format", choices=["sonar", "bsl"], default="bsl", help="Формат входного файла")
    report_parser.add_argument("--output-dir", default="reports", help="Папка для отчетов")
    report_parser.add_argument("--excel", action="store_true", help="Генерировать Excel отчет")
    report_parser.add_argument("--csv", action="store_true", help="Генерировать CSV отчет")
    report_parser.add_argument("--html", action="store_true", help="Генерировать HTML отчет")
    report_parser.set_defaults(func=generate_report)
    
    # Команда ci
    ci_parser = subparsers.add_parser("ci", help="Настройка CI/CD")
    ci_parser.add_argument("type", choices=["github", "gitlab", "jenkins", "azure"], help="Тип CI/CD системы")
    ci_parser.add_argument("project_key", help="Ключ проекта SonarQube")
    ci_parser.add_argument("--pre-commit", action="store_true", help="Настроить pre-commit хук")
    ci_parser.set_defaults(func=setup_ci)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()