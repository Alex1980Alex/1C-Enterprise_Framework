"""
CI/CD Integration for SonarQube Analysis
Интеграция с системами CI/CD для анализа SonarQube
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class CIIntegration:
    """Интеграция с системами непрерывной интеграции"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        
    def generate_github_workflow(self, project_key: str, 
                                sonar_token_secret: str = "SONAR_TOKEN") -> str:
        """Генерация GitHub Actions workflow для SonarQube"""
        
        workflow_content = f"""
name: SonarQube Analysis for 1C:Enterprise

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  sonarqube:
    name: SonarQube Analysis
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      with:
        fetch-depth: 0
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install BSL Language Server
      run: |
        npm install -g @1c-syntax/bsl-language-server
    
    - name: Run BSL Analysis
      run: |
        bsl-language-server --analyze --srcDir src/ --reportDir reports/ --reporter json
    
    - name: SonarQube Scan
      uses: sonarqube-quality-gate-action@master
      env:
        SONAR_TOKEN: ${{{{ secrets.{sonar_token_secret} }}}}
        SONAR_HOST_URL: ${{{{ secrets.SONAR_HOST_URL }}}}
      with:
        projectBaseDir: .
    
    - name: Upload Analysis Results
      uses: actions/upload-artifact@v3
      with:
        name: sonar-analysis-results
        path: |
          reports/
          .scannerwork/
"""
        
        return workflow_content
    
    def generate_gitlab_ci(self, project_key: str) -> str:
        """Генерация GitLab CI конфигурации для SonarQube"""
        
        gitlab_ci_content = f"""
stages:
  - analysis
  - quality-gate

variables:
  SONAR_USER_HOME: "${{CI_PROJECT_DIR}}/.sonar"
  GIT_DEPTH: "0"

cache:
  key: "${{CI_JOB_NAME}}"
  paths:
    - .sonar/cache

bsl-analysis:
  stage: analysis
  image: node:18-alpine
  before_script:
    - npm install -g @1c-syntax/bsl-language-server
  script:
    - mkdir -p reports
    - bsl-language-server --analyze --srcDir src/ --reportDir reports/ --reporter json
  artifacts:
    reports:
      junit: reports/bsl-junit.xml
    paths:
      - reports/
    expire_in: 1 week

sonarqube-check:
  stage: analysis
  image: 
    name: sonarsource/sonar-scanner-cli:latest
    entrypoint: [""]
  variables:
    SONAR_USER_HOME: "${{CI_PROJECT_DIR}}/.sonar"
  cache:
    key: "${{CI_JOB_NAME}}"
    paths:
      - .sonar/cache
  script: 
    - sonar-scanner
  only:
    - main
    - develop
    - merge_requests

quality-gate:
  stage: quality-gate
  image: sonarsource/sonar-scanner-cli:latest
  script:
    - sonar-scanner -Dsonar.qualitygate.wait=true
  only:
    - main
    - develop
"""
        
        return gitlab_ci_content
    
    def generate_jenkins_pipeline(self, project_key: str) -> str:
        """Генерация Jenkins Pipeline для SonarQube"""
        
        jenkins_content = f"""
pipeline {{
    agent any
    
    tools {{
        nodejs 'NodeJS-18'
    }}
    
    environment {{
        SONAR_SCANNER_HOME = tool 'SonarQubeScanner'
        SONAR_TOKEN = credentials('sonar-token')
    }}
    
    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
            }}
        }}
        
        stage('Install Dependencies') {{
            steps {{
                sh 'npm install -g @1c-syntax/bsl-language-server'
            }}
        }}
        
        stage('BSL Analysis') {{
            steps {{
                sh '''
                    mkdir -p reports
                    bsl-language-server --analyze --srcDir src/ --reportDir reports/ --reporter json
                '''
            }}
        }}
        
        stage('SonarQube Analysis') {{
            steps {{
                withSonarQubeEnv('SonarQube') {{
                    sh '${{SONAR_SCANNER_HOME}}/bin/sonar-scanner'
                }}
            }}
        }}
        
        stage('Quality Gate') {{
            steps {{
                timeout(time: 10, unit: 'MINUTES') {{
                    waitForQualityGate abortPipeline: true
                }}
            }}
        }}
    }}
    
    post {{
        always {{
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: '*.html',
                reportName: 'BSL Analysis Report'
            ])
        }}
        
        failure {{
            emailext (
                subject: "SonarQube Analysis Failed: ${{env.JOB_NAME}} - ${{env.BUILD_NUMBER}}",
                body: "Build failed. Check console output at ${{env.BUILD_URL}}",
                to: "${{env.CHANGE_AUTHOR_EMAIL}}"
            )
        }}
    }}
}}
"""
        
        return jenkins_content
    
    def generate_azure_pipeline(self, project_key: str) -> str:
        """Генерация Azure DevOps Pipeline для SonarQube"""
        
        azure_content = f"""
trigger:
  branches:
    include:
    - main
    - develop

pr:
  branches:
    include:
    - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  SONAR_TOKEN: $(SONAR_TOKEN)
  SONAR_HOST_URL: $(SONAR_HOST_URL)

stages:
- stage: Analysis
  displayName: 'Code Analysis'
  jobs:
  - job: SonarQube
    displayName: 'SonarQube Analysis'
    steps:
    
    - task: NodeTool@0
      displayName: 'Use Node.js 18'
      inputs:
        versionSpec: '18'
    
    - script: |
        npm install -g @1c-syntax/bsl-language-server
      displayName: 'Install BSL Language Server'
    
    - script: |
        mkdir -p reports
        bsl-language-server --analyze --srcDir src/ --reportDir reports/ --reporter json
      displayName: 'Run BSL Analysis'
    
    - task: SonarQubePrepare@5
      displayName: 'Prepare SonarQube analysis'
      inputs:
        SonarQube: 'SonarQube'
        scannerMode: 'CLI'
        configMode: 'file'
    
    - task: SonarQubeAnalyze@5
      displayName: 'Run SonarQube analysis'
    
    - task: SonarQubePublish@5
      displayName: 'Publish SonarQube results'
      inputs:
        pollingTimeoutSec: '300'
    
    - task: PublishTestResults@2
      displayName: 'Publish BSL test results'
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: 'reports/bsl-junit.xml'
        failTaskOnFailedTests: false
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish analysis artifacts'
      inputs:
        pathToPublish: 'reports'
        artifactName: 'analysis-reports'
"""
        
        return azure_content
    
    def setup_pre_commit_hook(self) -> bool:
        """Настройка pre-commit хука для анализа BSL"""
        
        hook_content = """#!/bin/sh
# Pre-commit hook for BSL Language Server analysis

echo "Running BSL Language Server analysis..."

# Проверяем наличие BSL LS
if ! command -v bsl-language-server &> /dev/null; then
    echo "BSL Language Server not found. Install with: npm install -g @1c-syntax/bsl-language-server"
    exit 1
fi

# Получаем список измененных .bsl файлов
CHANGED_BSL_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\\.bsl$')

if [ -z "$CHANGED_BSL_FILES" ]; then
    echo "No BSL files changed, skipping analysis"
    exit 0
fi

# Создаем временную папку для анализа
TEMP_DIR=$(mktemp -d)
mkdir -p "$TEMP_DIR/src"

# Копируем измененные файлы
for file in $CHANGED_BSL_FILES; do
    cp "$file" "$TEMP_DIR/src/"
done

# Запускаем анализ
cd "$TEMP_DIR"
bsl-language-server --analyze --srcDir src/ --reportDir reports/ --reporter json

# Проверяем результаты
if [ -f "reports/bsl-analysis.json" ]; then
    ISSUES_COUNT=$(jq '[.[].diagnostics | length] | add' reports/bsl-analysis.json 2>/dev/null || echo "0")
    
    if [ "$ISSUES_COUNT" -gt 0 ]; then
        echo "Found $ISSUES_COUNT BSL issues in changed files:"
        jq -r '.[] | select(.diagnostics | length > 0) | .filePath as $file | .diagnostics[] | "\\($file):\\(.range.start.line): \\(.message)"' reports/bsl-analysis.json
        
        echo ""
        echo "Please fix the issues before committing or use --no-verify to skip this check"
        
        # Очистка
        rm -rf "$TEMP_DIR"
        exit 1
    fi
fi

# Очистка
rm -rf "$TEMP_DIR"
echo "BSL analysis passed!"
exit 0
"""
        
        try:
            hooks_dir = self.project_root / ".git" / "hooks"
            hook_file = hooks_dir / "pre-commit"
            
            with open(hook_file, 'w') as f:
                f.write(hook_content)
            
            # Делаем файл исполняемым
            os.chmod(hook_file, 0o755)
            
            return True
        except Exception as e:
            print(f"Ошибка настройки pre-commit хука: {e}")
            return False
    
    def run_local_analysis(self, src_dir: str = "src", 
                          output_dir: str = "reports") -> Dict[str, Any]:
        """Локальный запуск анализа BSL"""
        
        try:
            # Создаем директорию для отчетов
            reports_path = Path(output_dir)
            reports_path.mkdir(exist_ok=True)
            
            # Команда для запуска BSL Language Server
            cmd = [
                "bsl-language-server",
                "--analyze",
                "--srcDir", src_dir,
                "--reportDir", output_dir,
                "--reporter", "json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            analysis_result = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "reports_dir": str(reports_path)
            }
            
            # Попытка прочитать результаты анализа
            json_report = reports_path / "bsl-analysis.json"
            if json_report.exists():
                with open(json_report, 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)
                    
                total_issues = sum(len(file_data.get("diagnostics", [])) 
                                 for file_data in analysis_data)
                analysis_result["total_issues"] = total_issues
                analysis_result["analyzed_files"] = len(analysis_data)
            
            return analysis_result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    def create_ci_config_files(self, ci_type: str, project_key: str) -> bool:
        """Создание конфигурационных файлов для CI/CD"""
        
        try:
            if ci_type.lower() == "github":
                workflow_dir = self.project_root / ".github" / "workflows"
                workflow_dir.mkdir(parents=True, exist_ok=True)
                
                workflow_file = workflow_dir / "sonarqube.yml"
                with open(workflow_file, 'w') as f:
                    f.write(self.generate_github_workflow(project_key))
                    
            elif ci_type.lower() == "gitlab":
                gitlab_file = self.project_root / ".gitlab-ci.yml"
                with open(gitlab_file, 'w') as f:
                    f.write(self.generate_gitlab_ci(project_key))
                    
            elif ci_type.lower() == "jenkins":
                jenkins_file = self.project_root / "Jenkinsfile"
                with open(jenkins_file, 'w') as f:
                    f.write(self.generate_jenkins_pipeline(project_key))
                    
            elif ci_type.lower() == "azure":
                azure_file = self.project_root / "azure-pipelines.yml"
                with open(azure_file, 'w') as f:
                    f.write(self.generate_azure_pipeline(project_key))
            else:
                print(f"Неподдерживаемый тип CI/CD: {ci_type}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Ошибка создания конфигурации CI/CD: {e}")
            return False