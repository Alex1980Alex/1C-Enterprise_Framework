"""
Report Generator for SonarQube Analysis Results
Генератор отчетов для результатов анализа SonarQube
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class AnalysisResult:
    """Результат анализа кода"""
    file_path: str
    rule_key: str
    rule_name: str
    severity: str
    line: int
    message: str
    category: str


class ReportGenerator:
    """Генератор отчетов анализа кода"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def parse_sonar_json_report(self, json_file: str) -> List[AnalysisResult]:
        """Парсинг JSON отчета SonarQube"""
        results = []
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for issue in data.get("issues", []):
                result = AnalysisResult(
                    file_path=issue.get("component", ""),
                    rule_key=issue.get("rule", ""),
                    rule_name=issue.get("message", ""),
                    severity=issue.get("severity", "INFO"),
                    line=issue.get("line", 0),
                    message=issue.get("message", ""),
                    category=self._get_category_by_rule(issue.get("rule", ""))
                )
                results.append(result)
                
        except Exception as e:
            print(f"Ошибка парсинга JSON отчета: {e}")
            
        return results
    
    def parse_bsl_json_report(self, json_file: str) -> List[AnalysisResult]:
        """Парсинг JSON отчета BSL Language Server"""
        results = []
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for file_analysis in data:
                file_path = file_analysis.get("filePath", "")
                
                for issue in file_analysis.get("diagnostics", []):
                    result = AnalysisResult(
                        file_path=file_path,
                        rule_key=issue.get("code", ""),
                        rule_name=issue.get("description", ""),
                        severity=issue.get("severity", "INFO"),
                        line=issue.get("range", {}).get("start", {}).get("line", 0),
                        message=issue.get("message", ""),
                        category=self._get_category_by_rule(issue.get("code", ""))
                    )
                    results.append(result)
                    
        except Exception as e:
            print(f"Ошибка парсинга BSL JSON отчета: {e}")
            
        return results
    
    def _get_category_by_rule(self, rule_key: str) -> str:
        """Определение категории по ключу правила"""
        category_mapping = {
            "Cyclomatic": "Производительность",
            "LineLength": "Стиль кода",
            "MethodSize": "Сопровождаемость", 
            "ExcessiveReturns": "Сопровождаемость",
            "HardcodedPassword": "Безопасность",
            "UndefinedVariable": "Надежность",
            "DuplicateMethod": "Надежность",
            "ExceptionHandling": "Надежность",
            "OneSymbolVariable": "Стиль кода",
            "BooleanLiteral": "Стиль кода",
            "CommentedCode": "Сопровождаемость",
            "TodoComment": "Сопровождаемость"
        }
        
        for key_part, category in category_mapping.items():
            if key_part in rule_key:
                return category
        return "Общие"
    
    def generate_summary_report(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Генерация сводного отчета"""
        summary = {
            "analysis_date": datetime.now().isoformat(),
            "total_issues": len(results),
            "by_severity": {},
            "by_category": {},
            "by_file": {},
            "top_issues": {}
        }
        
        # Группировка по критичности
        for result in results:
            severity = result.severity
            if severity not in summary["by_severity"]:
                summary["by_severity"][severity] = 0
            summary["by_severity"][severity] += 1
        
        # Группировка по категориям
        for result in results:
            category = result.category
            if category not in summary["by_category"]:
                summary["by_category"][category] = 0
            summary["by_category"][category] += 1
        
        # Группировка по файлам
        for result in results:
            file_path = result.file_path
            if file_path not in summary["by_file"]:
                summary["by_file"][file_path] = 0
            summary["by_file"][file_path] += 1
        
        # Топ проблемных правил
        rule_counts = {}
        for result in results:
            rule = result.rule_key
            if rule not in rule_counts:
                rule_counts[rule] = 0
            rule_counts[rule] += 1
        
        summary["top_issues"] = dict(sorted(rule_counts.items(), 
                                          key=lambda x: x[1], reverse=True)[:10])
        
        return summary
    
    def export_to_excel(self, results: List[AnalysisResult], filename: str = None) -> str:
        """Экспорт результатов в Excel"""
        if filename is None:
            filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        output_path = self.output_dir / filename
        
        try:
            import pandas as pd
            
            # Подготовка данных
            data = []
            for result in results:
                data.append({
                    "Файл": result.file_path,
                    "Правило": result.rule_key,
                    "Название": result.rule_name,
                    "Критичность": result.severity,
                    "Строка": result.line,
                    "Сообщение": result.message,
                    "Категория": result.category
                })
            
            df = pd.DataFrame(data)
            
            # Создание Excel файла с несколькими листами
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Основной лист с данными
                df.to_excel(writer, sheet_name='Детали', index=False)
                
                # Сводка по критичности
                severity_summary = df.groupby('Критичность').size().reset_index(name='Количество')
                severity_summary.to_excel(writer, sheet_name='По критичности', index=False)
                
                # Сводка по категориям
                category_summary = df.groupby('Категория').size().reset_index(name='Количество')
                category_summary.to_excel(writer, sheet_name='По категориям', index=False)
                
                # Топ файлов с проблемами
                file_summary = df.groupby('Файл').size().reset_index(name='Количество')
                file_summary = file_summary.sort_values('Количество', ascending=False).head(20)
                file_summary.to_excel(writer, sheet_name='Топ файлов', index=False)
            
            return str(output_path)
            
        except ImportError:
            print("Для экспорта в Excel требуется установить pandas и openpyxl")
            return self.export_to_csv(results, filename.replace('.xlsx', '.csv'))
        except Exception as e:
            print(f"Ошибка экспорта в Excel: {e}")
            return ""
    
    def export_to_csv(self, results: List[AnalysisResult], filename: str = None) -> str:
        """Экспорт результатов в CSV"""
        if filename is None:
            filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output_path = self.output_dir / filename
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['Файл', 'Правило', 'Название', 'Критичность', 'Строка', 'Сообщение', 'Категория']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for result in results:
                    writer.writerow({
                        'Файл': result.file_path,
                        'Правило': result.rule_key,
                        'Название': result.rule_name,
                        'Критичность': result.severity,
                        'Строка': result.line,
                        'Сообщение': result.message,
                        'Категория': result.category
                    })
            
            return str(output_path)
            
        except Exception as e:
            print(f"Ошибка экспорта в CSV: {e}")
            return ""
    
    def export_to_html(self, results: List[AnalysisResult], filename: str = None) -> str:
        """Экспорт результатов в HTML отчет"""
        if filename is None:
            filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        output_path = self.output_dir / filename
        summary = self.generate_summary_report(results)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет анализа кода 1С</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .severity-BLOCKER {{ background-color: #ffebee; }}
        .severity-CRITICAL {{ background-color: #fff3e0; }}
        .severity-MAJOR {{ background-color: #fff8e1; }}
        .severity-MINOR {{ background-color: #f3e5f5; }}
        .severity-INFO {{ background-color: #e8f5e8; }}
        .summary-card {{ 
            display: inline-block; 
            margin: 10px; 
            padding: 15px; 
            border: 1px solid #ddd; 
            border-radius: 5px; 
            min-width: 150px;
        }}
    </style>
</head>
<body>
    <h1>Отчет анализа кода 1С:Предприятие</h1>
    <p>Дата анализа: {summary['analysis_date']}</p>
    
    <h2>Сводка</h2>
    <div class="summary-card">
        <h3>Всего проблем</h3>
        <p style="font-size: 24px; margin: 0;">{summary['total_issues']}</p>
    </div>
    
    <h3>По критичности</h3>
    <table>
        <tr><th>Критичность</th><th>Количество</th></tr>
"""
        
        for severity, count in summary['by_severity'].items():
            html_content += f"<tr class='severity-{severity}'><td>{severity}</td><td>{count}</td></tr>"
        
        html_content += """
    </table>
    
    <h3>По категориям</h3>
    <table>
        <tr><th>Категория</th><th>Количество</th></tr>
"""
        
        for category, count in summary['by_category'].items():
            html_content += f"<tr><td>{category}</td><td>{count}</td></tr>"
        
        html_content += """
    </table>
    
    <h2>Детализация проблем</h2>
    <table>
        <tr>
            <th>Файл</th>
            <th>Правило</th>
            <th>Критичность</th>
            <th>Строка</th>
            <th>Сообщение</th>
            <th>Категория</th>
        </tr>
"""
        
        for result in results[:1000]:  # Ограничиваем для производительности
            html_content += f"""
        <tr class="severity-{result.severity}">
            <td>{result.file_path}</td>
            <td>{result.rule_key}</td>
            <td>{result.severity}</td>
            <td>{result.line}</td>
            <td>{result.message}</td>
            <td>{result.category}</td>
        </tr>
"""
        
        html_content += """
    </table>
</body>
</html>
"""
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return str(output_path)
        except Exception as e:
            print(f"Ошибка экспорта в HTML: {e}")
            return ""
    
    def generate_trend_report(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Генерация отчета по трендам"""
        trend_report = {
            "period": f"{historical_data[0]['date']} - {historical_data[-1]['date']}",
            "total_issues_trend": [],
            "severity_trends": {},
            "category_trends": {},
            "improvement_metrics": {}
        }
        
        # Тренды по общему количеству проблем
        for data_point in historical_data:
            trend_report["total_issues_trend"].append({
                "date": data_point["date"],
                "count": data_point["total_issues"]
            })
        
        # Расчет метрик улучшения
        if len(historical_data) >= 2:
            first = historical_data[0]
            last = historical_data[-1]
            
            trend_report["improvement_metrics"] = {
                "total_change": last["total_issues"] - first["total_issues"],
                "total_change_percent": ((last["total_issues"] - first["total_issues"]) / first["total_issues"] * 100) if first["total_issues"] > 0 else 0,
                "blocker_change": last.get("blocker_issues", 0) - first.get("blocker_issues", 0),
                "critical_change": last.get("critical_issues", 0) - first.get("critical_issues", 0)
            }
        
        return trend_report