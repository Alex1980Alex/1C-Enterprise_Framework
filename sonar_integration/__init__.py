"""
SonarQube Integration Module for 1C:Enterprise Framework
Модуль интеграции SonarQube для фреймворка 1С:Предприятие

Обеспечивает:
- Автоматическое создание конфигураций SonarQube
- Синхронизацию правил BSL Language Server
- Генерацию отчетов анализа кода
- Интеграцию с CI/CD пайплайнами
"""

__version__ = "1.0.0"
__author__ = "1C Framework Team"

from .config_manager import ConfigManager
from .rules_manager import RulesManager
from .report_generator import ReportGenerator
from .ci_integration import CIIntegration

__all__ = [
    'ConfigManager',
    'RulesManager', 
    'ReportGenerator',
    'CIIntegration'
]