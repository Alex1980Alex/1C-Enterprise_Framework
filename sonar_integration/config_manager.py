"""
Configuration Manager for SonarQube Integration
Менеджер конфигураций для интеграции SonarQube
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Управление конфигурациями SonarQube и BSL Language Server"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.sonar_config_path = self.project_root / "sonar-project.properties"
        self.bsl_config_path = self.project_root / ".bsl-language-server.json"
        self.rules_catalog_path = Path("sonar_integration/rules/bsl_rules_catalog.json")
        
    def load_bsl_rules_catalog(self) -> Dict[str, Any]:
        """Загрузка каталога правил BSL"""
        try:
            with open(self.rules_catalog_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def generate_sonar_config(self, project_key: str, project_name: str, 
                            custom_rules: Optional[Dict] = None) -> str:
        """Генерация конфигурации sonar-project.properties"""
        
        config_lines = [
            "# SonarQube Configuration for 1C:Enterprise Project",
            "# Автоматически сгенерировано sonar_integration",
            "",
            f"sonar.projectKey={project_key}",
            f"sonar.projectName={project_name}",
            "sonar.projectVersion=1.0",
            "sonar.language=ru",
            "",
            "# === Пути к исходникам ===",
            "sonar.sources=src/",
            "sonar.tests=tests/",
            "sonar.inclusions=**/*.bsl,**/*.os,**/*.sdbl",
            "sonar.exclusions=**/node_modules/**,**/bin/**,**/obj/**",
            "",
            "# === BSL Language Server Settings ===",
        ]
        
        # Добавляем стандартные правила
        default_rules = {
            "CyclomaticComplexity.maxComplexity": 20,
            "LineLength.maxLineLength": 120,
            "MethodSize.maxMethodSize": 50,
            "ExcessiveReturns.maxEnableReturns": 3,
            "QuantityOptionalArguments.maxOptionalArgumentsCount": 3,
            "HardcodedPasswordInMethod.passwordFieldNames": "Пароль|Password|Пароль1|Пароль2",
            "OneSymbolVariable": "false",
            "BooleanLiteral": "false"
        }
        
        # Объединяем с пользовательскими правилами
        if custom_rules:
            default_rules.update(custom_rules)
            
        for rule, value in default_rules.items():
            config_lines.append(f"sonar.bsl.{rule}={value}")
        
        config_lines.extend([
            "",
            "# === Настройки качества кода ===",
            "sonar.qualitygate.wait=true",
            "sonar.coverage.exclusions=**/*.bsl",
            "sonar.cpd.exclusions=**/*.bsl",
            "sonar.verbose=false"
        ])
        
        return "\n".join(config_lines)
    
    def generate_bsl_config(self, custom_params: Optional[Dict] = None) -> Dict[str, Any]:
        """Генерация конфигурации .bsl-language-server.json"""
        
        config = {
            "$schema": "https://1c-syntax.github.io/bsl-language-server/configuration/schema.json",
            "language": "ru",
            "diagnosticLanguage": "ru",
            "traceLevel": "off",
            "diagnostics": {
                "computeTrigger": "onType",
                "parameters": {
                    "CyclomaticComplexity": {"maxComplexity": 20},
                    "LineLength": {"maxLineLength": 120},
                    "MethodSize": {"maxMethodSize": 50},
                    "ExcessiveReturns": {"maxEnableReturns": 3},
                    "QuantityOptionalArguments": {"maxOptionalArgumentsCount": 3},
                    "HardcodedPasswordInMethod": {
                        "passwordFieldNames": "Пароль|Password|Пароль1|Пароль2|IMAP|SMTP"
                    },
                    "OneSymbolVariable": False,
                    "BooleanLiteral": False,
                    "CommentedCode": True,
                    "TodoComment": True,
                    "UndefinedVariable": True,
                    "DuplicateMethod": True,
                    "ExceptionHandling": True
                },
                "subsystemsFilter": {
                    "include": ["Основная", "БизнесПроцессы"],
                    "exclude": ["ТестовыеДанные", "Устаревшие"]
                }
            },
            "codeActions": {
                "quickFix": True
            }
        }
        
        # Применяем пользовательские параметры
        if custom_params:
            if "parameters" in custom_params:
                config["diagnostics"]["parameters"].update(custom_params["parameters"])
            if "subsystemsFilter" in custom_params:
                config["diagnostics"]["subsystemsFilter"].update(custom_params["subsystemsFilter"])
        
        return config
    
    def save_sonar_config(self, content: str) -> bool:
        """Сохранение конфигурации SonarQube"""
        try:
            with open(self.sonar_config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Ошибка сохранения sonar-project.properties: {e}")
            return False
    
    def save_bsl_config(self, config: Dict[str, Any]) -> bool:
        """Сохранение конфигурации BSL Language Server"""
        try:
            with open(self.bsl_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения .bsl-language-server.json: {e}")
            return False
    
    def sync_configs(self, project_key: str, project_name: str, 
                    custom_rules: Optional[Dict] = None,
                    custom_bsl_params: Optional[Dict] = None) -> bool:
        """Синхронизация всех конфигураций"""
        try:
            # Генерируем и сохраняем конфигурацию SonarQube
            sonar_content = self.generate_sonar_config(project_key, project_name, custom_rules)
            sonar_saved = self.save_sonar_config(sonar_content)
            
            # Генерируем и сохраняем конфигурацию BSL LS
            bsl_config = self.generate_bsl_config(custom_bsl_params)
            bsl_saved = self.save_bsl_config(bsl_config)
            
            return sonar_saved and bsl_saved
        except Exception as e:
            print(f"Ошибка синхронизации конфигураций: {e}")
            return False