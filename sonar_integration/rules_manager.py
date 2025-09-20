"""
Rules Manager for BSL Language Server and SonarQube
Менеджер правил для BSL Language Server и SonarQube
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class BSLRule:
    """Представление правила BSL Language Server"""
    key: str
    name: str
    description: str
    severity: str
    category: str
    default_value: Optional[Any] = None
    enabled: bool = True


class RulesManager:
    """Управление правилами анализа кода BSL"""
    
    def __init__(self):
        self.rules_catalog_path = Path("sonar_integration/rules/bsl_rules_catalog.json")
        self.rules_cache: Dict[str, BSLRule] = {}
        self._load_rules_catalog()
    
    def _load_rules_catalog(self):
        """Загрузка каталога правил из JSON"""
        try:
            with open(self.rules_catalog_path, 'r', encoding='utf-8') as f:
                catalog = json.load(f)
                
            for severity, rules in catalog.get("rules", {}).items():
                for rule_data in rules:
                    rule = BSLRule(
                        key=rule_data["key"],
                        name=rule_data["name"],
                        description=rule_data["description"],
                        severity=severity.upper(),
                        category=self._get_rule_category(rule_data["key"]),
                        default_value=rule_data.get("defaultValue"),
                        enabled=True
                    )
                    self.rules_cache[rule.key] = rule
        except FileNotFoundError:
            print(f"Каталог правил не найден: {self.rules_catalog_path}")
        except Exception as e:
            print(f"Ошибка загрузки каталога правил: {e}")
    
    def _get_rule_category(self, rule_key: str) -> str:
        """Определение категории правила по ключу"""
        category_mapping = {
            "Cyclomatic": "performance",
            "LineLength": "style", 
            "MethodSize": "maintainability",
            "ExcessiveReturns": "maintainability",
            "HardcodedPassword": "security",
            "UndefinedVariable": "reliability",
            "DuplicateMethod": "reliability",
            "ExceptionHandling": "reliability",
            "OneSymbolVariable": "style",
            "BooleanLiteral": "style",
            "CommentedCode": "maintainability",
            "TodoComment": "maintainability"
        }
        
        for key_part, category in category_mapping.items():
            if key_part in rule_key:
                return category
        return "maintainability"
    
    def get_rule(self, rule_key: str) -> Optional[BSLRule]:
        """Получение правила по ключу"""
        return self.rules_cache.get(rule_key)
    
    def get_rules_by_severity(self, severity: str) -> List[BSLRule]:
        """Получение правил по уровню критичности"""
        return [rule for rule in self.rules_cache.values() 
                if rule.severity.upper() == severity.upper()]
    
    def get_rules_by_category(self, category: str) -> List[BSLRule]:
        """Получение правил по категории"""
        return [rule for rule in self.rules_cache.values() 
                if rule.category == category]
    
    def get_enabled_rules(self) -> List[BSLRule]:
        """Получение включенных правил"""
        return [rule for rule in self.rules_cache.values() if rule.enabled]
    
    def enable_rule(self, rule_key: str) -> bool:
        """Включение правила"""
        if rule_key in self.rules_cache:
            self.rules_cache[rule_key].enabled = True
            return True
        return False
    
    def disable_rule(self, rule_key: str) -> bool:
        """Отключение правила"""
        if rule_key in self.rules_cache:
            self.rules_cache[rule_key].enabled = False
            return True
        return False
    
    def create_rules_profile(self, profile_name: str, 
                           severity_levels: List[str] = None,
                           categories: List[str] = None,
                           custom_rules: Dict[str, Any] = None) -> Dict[str, Any]:
        """Создание профиля правил"""
        
        if severity_levels is None:
            severity_levels = ["BLOCKER", "CRITICAL", "MAJOR"]
        
        profile = {
            "name": profile_name,
            "description": f"Профиль правил BSL: {profile_name}",
            "language": "ru",
            "rules": {}
        }
        
        # Добавляем правила по уровням критичности
        for severity in severity_levels:
            rules = self.get_rules_by_severity(severity)
            for rule in rules:
                if rule.enabled:
                    profile["rules"][rule.key] = {
                        "severity": rule.severity,
                        "enabled": True
                    }
                    if rule.default_value is not None:
                        profile["rules"][rule.key]["value"] = rule.default_value
        
        # Фильтрация по категориям
        if categories:
            filtered_rules = {}
            for rule_key, rule_config in profile["rules"].items():
                rule = self.get_rule(rule_key)
                if rule and rule.category in categories:
                    filtered_rules[rule_key] = rule_config
            profile["rules"] = filtered_rules
        
        # Применяем пользовательские настройки
        if custom_rules:
            for rule_key, rule_config in custom_rules.items():
                if rule_key in profile["rules"]:
                    profile["rules"][rule_key].update(rule_config)
                else:
                    profile["rules"][rule_key] = rule_config
        
        return profile
    
    def export_sonar_rules(self, rules_profile: Dict[str, Any]) -> str:
        """Экспорт правил в формат SonarQube properties"""
        lines = [
            f"# SonarQube Rules Profile: {rules_profile['name']}",
            f"# Description: {rules_profile['description']}",
            ""
        ]
        
        for rule_key, rule_config in rules_profile["rules"].items():
            if rule_config.get("enabled", True):
                if "value" in rule_config:
                    lines.append(f"sonar.bsl.{rule_key}={rule_config['value']}")
                else:
                    lines.append(f"sonar.bsl.{rule_key}=true")
        
        return "\n".join(lines)
    
    def export_bsl_config(self, rules_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Экспорт правил в формат BSL Language Server"""
        bsl_config = {
            "diagnostics": {
                "parameters": {}
            }
        }
        
        for rule_key, rule_config in rules_profile["rules"].items():
            if rule_config.get("enabled", True):
                if "value" in rule_config:
                    if isinstance(rule_config["value"], dict):
                        bsl_config["diagnostics"]["parameters"][rule_key] = rule_config["value"]
                    else:
                        # Простое значение - создаем структуру по типу правила
                        if "max" in rule_key.lower():
                            param_name = "max" + rule_key.split("max")[-1] if "max" in rule_key else "maxValue"
                            bsl_config["diagnostics"]["parameters"][rule_key] = {
                                param_name: rule_config["value"]
                            }
                        else:
                            bsl_config["diagnostics"]["parameters"][rule_key] = rule_config["value"]
                else:
                    bsl_config["diagnostics"]["parameters"][rule_key] = True
        
        return bsl_config
    
    def validate_rule_config(self, rule_key: str, config: Dict[str, Any]) -> bool:
        """Валидация конфигурации правила"""
        rule = self.get_rule(rule_key)
        if not rule:
            return False
        
        # Базовая валидация для числовых параметров
        if rule.default_value is not None and isinstance(rule.default_value, (int, float)):
            if "value" in config:
                try:
                    float(config["value"])
                    return True
                except (ValueError, TypeError):
                    return False
        
        return True
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """Получение сводки по правилам"""
        summary = {
            "total_rules": len(self.rules_cache),
            "enabled_rules": len(self.get_enabled_rules()),
            "by_severity": {},
            "by_category": {}
        }
        
        # Группировка по критичности
        for severity in ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]:
            rules = self.get_rules_by_severity(severity)
            summary["by_severity"][severity] = {
                "total": len(rules),
                "enabled": len([r for r in rules if r.enabled])
            }
        
        # Группировка по категориям
        categories = set(rule.category for rule in self.rules_cache.values())
        for category in categories:
            rules = self.get_rules_by_category(category)
            summary["by_category"][category] = {
                "total": len(rules),
                "enabled": len([r for r in rules if r.enabled])
            }
        
        return summary