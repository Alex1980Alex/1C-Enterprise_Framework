#!/usr/bin/env python3
"""
Setup script for SonarQube Integration module
Скрипт установки модуля интеграции SonarQube
"""

from setuptools import setup, find_packages
from pathlib import Path

# Читаем README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Читаем requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f 
                       if line.strip() and not line.startswith('#')]

setup(
    name="sonar-integration-1c",
    version="1.0.0",
    description="SonarQube Integration для проектов 1С:Предприятие",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="1C Framework Team",
    author_email="framework@1c.ru",
    url="https://github.com/1c-enterprise/framework",
    packages=find_packages(),
    
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    
    keywords="sonarqube 1c-enterprise bsl-language-server code-quality static-analysis",
    
    python_requires=">=3.7",
    install_requires=requirements,
    
    extras_require={
        "excel": ["pandas>=1.3.0", "openpyxl>=3.0.9"],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
    },
    
    entry_points={
        "console_scripts": [
            "sonar-integration=sonar_integration.cli:main",
        ],
    },
    
    package_data={
        "sonar_integration": ["*.json", "*.yaml", "*.yml"],
    },
    
    include_package_data=True,
    zip_safe=False,
    
    project_urls={
        "Bug Reports": "https://github.com/1c-enterprise/framework/issues",
        "Source": "https://github.com/1c-enterprise/framework",
        "Documentation": "https://docs.1c-enterprise.ru/",
    },
)