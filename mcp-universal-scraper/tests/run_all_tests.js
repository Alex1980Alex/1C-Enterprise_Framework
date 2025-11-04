import AdapterTester from './test_adapters.js';
import IntegrationTester from './test_integration.js';
import fs from 'fs';
import path from 'path';

/**
 * Главный скрипт для запуска всех тестов Universal Scraper
 */
class MasterTestSuite {
  constructor() {
    this.startTime = Date.now();
    this.results = {
      integration: null,
      adapters: null,
      performance: null
    };
  }

  async runAllTests() {
    console.log('🧪 ЗАПУСК ПОЛНОГО ТЕСТИРОВАНИЯ UNIVERSAL SCRAPER');
    console.log('='.repeat(80));
    console.log(`📅 Время запуска: ${new Date().toLocaleString()}`);
    console.log(`🖥️  Платформа: ${process.platform} ${process.arch}`);
    console.log(`📦 Node.js: ${process.version}`);
    console.log('='.repeat(80));

    try {
      // 1. Интеграционные тесты
      console.log('\n🔗 ФАЗА 1: ИНТЕГРАЦИОННЫЕ ТЕСТЫ');
      console.log('─'.repeat(50));
      const integrationTester = new IntegrationTester();
      this.results.integration = await integrationTester.runIntegrationTests();

      // 2. Тесты адаптеров
      console.log('\n🔧 ФАЗА 2: ТЕСТИРОВАНИЕ АДАПТЕРОВ');
      console.log('─'.repeat(50));
      const adapterTester = new AdapterTester();
      this.results.adapters = await adapterTester.runAllTests();

      // 3. Тесты производительности (опционально)
      if (process.argv.includes('--performance')) {
        console.log('\n⚡ ФАЗА 3: ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ');
        console.log('─'.repeat(50));
        this.results.performance = await this.runPerformanceTests(adapterTester);
      }

      // Генерация сводного отчёта
      await this.generateMasterReport();
      
      // Финальная сводка
      this.printFinalSummary();

    } catch (error) {
      console.error('\n💥 КРИТИЧЕСКАЯ ОШИБКА ТЕСТИРОВАНИЯ:', error.message);
      console.error(error.stack);
      process.exit(1);
    }
  }

  async runPerformanceTests(adapterTester) {
    const performanceResults = {};
    
    const testCases = [
      { adapter: 'generic', url: 'https://example.com' },
      { adapter: 'documentation', url: 'https://docs.github.com/en' },
      { adapter: 'news', url: 'https://habr.com/ru/news/' }
    ];

    for (const testCase of testCases) {
      try {
        console.log(`\n⚡ Тест производительности: ${testCase.adapter}`);
        const result = await adapterTester.performanceTest(
          testCase.adapter, 
          testCase.url, 
          3 // iterations
        );
        
        if (result) {
          performanceResults[testCase.adapter] = result;
        }
      } catch (error) {
        console.error(`❌ Ошибка производительности ${testCase.adapter}: ${error.message}`);
        performanceResults[testCase.adapter] = { error: error.message };
      }
    }

    return performanceResults;
  }

  async generateMasterReport() {
    const report = {
      timestamp: new Date().toISOString(),
      testSuite: 'Universal Scraper MCP',
      version: '1.0.0',
      duration: Date.now() - this.startTime,
      environment: {
        nodeVersion: process.version,
        platform: process.platform,
        arch: process.arch,
        cwd: process.cwd()
      },
      summary: {
        totalTestSuites: 0,
        totalTests: 0,
        totalPassed: 0,
        totalFailed: 0,
        overallSuccessRate: 0,
        criticalIssues: 0
      },
      results: this.results,
      recommendations: [],
      healthScore: 0
    };

    // Подсчёт общих метрик
    this.calculateSummaryMetrics(report);
    
    // Анализ результатов и генерация рекомендаций
    this.analyzeResults(report);
    
    // Расчёт общего показателя здоровья
    this.calculateHealthScore(report);

    // Сохранение отчёта
    const reportPath = path.join(process.cwd(), 'tests', 'master_report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    // Генерация HTML отчёта
    await this.generateHtmlReport(report);

    console.log(`\n💾 Мастер-отчёт сохранён: ${reportPath}`);
    
    return report;
  }

  calculateSummaryMetrics(report) {
    let totalTests = 0;
    let totalPassed = 0;
    let totalFailed = 0;
    let testSuites = 0;

    // Интеграционные тесты
    if (this.results.integration) {
      testSuites++;
      for (const results of Object.values(this.results.integration)) {
        totalTests += results.passed + results.failed;
        totalPassed += results.passed;
        totalFailed += results.failed;
      }
    }

    // Тесты адаптеров
    if (this.results.adapters) {
      testSuites++;
      for (const results of Object.values(this.results.adapters)) {
        totalTests += results.passed + results.failed;
        totalPassed += results.passed;
        totalFailed += results.failed;
      }
    }

    report.summary.totalTestSuites = testSuites;
    report.summary.totalTests = totalTests;
    report.summary.totalPassed = totalPassed;
    report.summary.totalFailed = totalFailed;
    report.summary.overallSuccessRate = totalTests > 0 ? 
      ((totalPassed / totalTests) * 100).toFixed(1) : '0.0';
  }

  analyzeResults(report) {
    const recommendations = [];

    // Анализ интеграционных тестов
    if (this.results.integration) {
      for (const [component, results] of Object.entries(this.results.integration)) {
        if (results.failed > 0) {
          recommendations.push({
            type: 'critical',
            category: 'integration',
            component,
            issue: `Интеграционные тесты провалены для ${component}`,
            impact: 'high',
            suggestion: `Немедленно исправить интеграцию с ${component}`,
            errors: results.errors
          });
          report.summary.criticalIssues++;
        }
      }
    }

    // Анализ адаптеров
    if (this.results.adapters) {
      for (const [adapter, results] of Object.entries(this.results.adapters)) {
        const total = results.passed + results.failed;
        const successRate = total > 0 ? (results.passed / total) * 100 : 0;
        
        if (successRate < 50) {
          recommendations.push({
            type: 'critical',
            category: 'adapter',
            component: adapter,
            issue: `Очень низкая успешность адаптера ${adapter} (${successRate.toFixed(1)}%)`,
            impact: 'high',
            suggestion: `Полностью переработать логику адаптера ${adapter}`
          });
          report.summary.criticalIssues++;
        } else if (successRate < 80) {
          recommendations.push({
            type: 'warning',
            category: 'adapter',
            component: adapter,
            issue: `Низкая успешность адаптера ${adapter} (${successRate.toFixed(1)}%)`,
            impact: 'medium',
            suggestion: `Улучшить селекторы и обработку ошибок для ${adapter}`
          });
        }
      }
    }

    // Анализ производительности
    if (this.results.performance) {
      for (const [adapter, perf] of Object.entries(this.results.performance)) {
        if (perf.error) {
          recommendations.push({
            type: 'warning',
            category: 'performance',
            component: adapter,
            issue: `Ошибка теста производительности для ${adapter}`,
            impact: 'medium',
            suggestion: `Проверить стабильность адаптера ${adapter}`
          });
        } else if (perf.avgTime > 10000) { // > 10 секунд
          recommendations.push({
            type: 'warning',
            category: 'performance',
            component: adapter,
            issue: `Медленная работа адаптера ${adapter} (${perf.avgTime.toFixed(0)}мс)`,
            impact: 'medium',
            suggestion: `Оптимизировать производительность ${adapter}`
          });
        }
      }
    }

    report.recommendations = recommendations;
  }

  calculateHealthScore(report) {
    let score = 100;
    
    // Снижаем за критические проблемы
    score -= report.summary.criticalIssues * 20;
    
    // Снижаем за общую успешность
    const successRate = parseFloat(report.summary.overallSuccessRate);
    if (successRate < 90) {
      score -= (90 - successRate) * 2;
    }
    
    // Снижаем за количество предупреждений
    const warnings = report.recommendations.filter(r => r.type === 'warning').length;
    score -= warnings * 5;
    
    report.healthScore = Math.max(0, Math.min(100, score));
  }

  async generateHtmlReport(report) {
    const html = `
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Universal Scraper - Отчёт тестирования</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }
        .header h1 { margin: 0; font-size: 2.5em; }
        .header .subtitle { font-size: 1.2em; opacity: 0.9; margin-top: 10px; }
        .content { padding: 30px; }
        .metric-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric-card { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 20px; text-align: center; }
        .metric-value { font-size: 2.5em; font-weight: bold; margin: 10px 0; }
        .metric-label { color: #6c757d; font-size: 0.9em; }
        .success { color: #28a745; }
        .warning { color: #ffc107; }
        .danger { color: #dc3545; }
        .health-score { font-size: 3em; font-weight: bold; margin: 20px 0; }
        .health-excellent { color: #28a745; }
        .health-good { color: #17a2b8; }
        .health-warning { color: #ffc107; }
        .health-poor { color: #dc3545; }
        .section { margin: 30px 0; }
        .section h2 { color: #495057; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; }
        .recommendations { margin: 20px 0; }
        .recommendation { border-left: 4px solid #dee2e6; padding: 15px; margin: 10px 0; background: #f8f9fa; }
        .recommendation.critical { border-color: #dc3545; background: #f8d7da; }
        .recommendation.warning { border-color: #ffc107; background: #fff3cd; }
        .details { margin: 20px 0; }
        .details-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        .details-table th, .details-table td { border: 1px solid #dee2e6; padding: 12px; text-align: left; }
        .details-table th { background: #e9ecef; font-weight: 600; }
        .footer { background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px; color: #6c757d; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Universal Scraper</h1>
            <div class="subtitle">Отчёт комплексного тестирования MCP сервера</div>
            <div>📅 ${new Date(report.timestamp).toLocaleString('ru-RU')}</div>
        </div>
        
        <div class="content">
            <div class="section">
                <div class="metric-cards">
                    <div class="metric-card">
                        <div class="metric-value success">${report.summary.totalPassed}</div>
                        <div class="metric-label">Успешных тестов</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value danger">${report.summary.totalFailed}</div>
                        <div class="metric-label">Провалено тестов</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${report.summary.overallSuccessRate}%</div>
                        <div class="metric-label">Общая успешность</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value ${this.getHealthClass(report.healthScore)}">${report.healthScore}</div>
                        <div class="metric-label">Показатель здоровья</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>📊 Детальная статистика</h2>
                <table class="details-table">
                    <thead>
                        <tr>
                            <th>Компонент</th>
                            <th>Успешно</th>
                            <th>Ошибок</th>
                            <th>Успешность</th>
                            <th>Статус</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.generateDetailsRows(report)}
                    </tbody>
                </table>
            </div>

            ${report.recommendations.length > 0 ? `
            <div class="section">
                <h2>💡 Рекомендации</h2>
                <div class="recommendations">
                    ${report.recommendations.map(rec => `
                        <div class="recommendation ${rec.type}">
                            <strong>${rec.component || rec.category}:</strong> ${rec.issue}<br>
                            <em>Рекомендация:</em> ${rec.suggestion}
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}

            <div class="section">
                <h2>🔧 Информация о системе</h2>
                <p><strong>Node.js:</strong> ${report.environment.nodeVersion}</p>
                <p><strong>Платформа:</strong> ${report.environment.platform} ${report.environment.arch}</p>
                <p><strong>Время выполнения:</strong> ${(report.duration / 1000).toFixed(1)} секунд</p>
                <p><strong>Тестовых наборов:</strong> ${report.summary.totalTestSuites}</p>
            </div>
        </div>
        
        <div class="footer">
            <p>🤖 Автоматически сгенерировано Universal Scraper Test Suite</p>
            <p>Claude Code Framework - ${new Date().getFullYear()}</p>
        </div>
    </div>
</body>
</html>`;

    const htmlPath = path.join(process.cwd(), 'tests', 'master_report.html');
    fs.writeFileSync(htmlPath, html);
    console.log(`📄 HTML отчёт сохранён: ${htmlPath}`);
  }

  getHealthClass(score) {
    if (score >= 90) return 'health-excellent';
    if (score >= 70) return 'health-good';
    if (score >= 50) return 'health-warning';
    return 'health-poor';
  }

  generateDetailsRows(report) {
    const rows = [];
    
    // Интеграционные тесты
    if (report.results.integration) {
      for (const [component, results] of Object.entries(report.results.integration)) {
        const total = results.passed + results.failed;
        const successRate = total > 0 ? ((results.passed / total) * 100).toFixed(1) : '0.0';
        const status = results.failed === 0 ? '✅' : '❌';
        
        rows.push(`
          <tr>
            <td>🔗 ${component}</td>
            <td>${results.passed}</td>
            <td>${results.failed}</td>
            <td>${successRate}%</td>
            <td>${status}</td>
          </tr>
        `);
      }
    }

    // Тесты адаптеров
    if (report.results.adapters) {
      for (const [adapter, results] of Object.entries(report.results.adapters)) {
        const total = results.passed + results.failed;
        const successRate = total > 0 ? ((results.passed / total) * 100).toFixed(1) : '0.0';
        const status = results.failed === 0 ? '✅' : '❌';
        
        rows.push(`
          <tr>
            <td>🔧 ${adapter}</td>
            <td>${results.passed}</td>
            <td>${results.failed}</td>
            <td>${successRate}%</td>
            <td>${status}</td>
          </tr>
        `);
      }
    }

    return rows.join('');
  }

  printFinalSummary() {
    const totalTime = Date.now() - this.startTime;
    
    console.log('\n' + '='.repeat(80));
    console.log('🎯 ФИНАЛЬНАЯ СВОДКА ТЕСТИРОВАНИЯ');
    console.log('='.repeat(80));
    
    // Подсчёт общих метрик
    let totalTests = 0;
    let totalPassed = 0;
    let totalFailed = 0;
    
    if (this.results.integration) {
      for (const results of Object.values(this.results.integration)) {
        totalTests += results.passed + results.failed;
        totalPassed += results.passed;
        totalFailed += results.failed;
      }
    }
    
    if (this.results.adapters) {
      for (const results of Object.values(this.results.adapters)) {
        totalTests += results.passed + results.failed;
        totalPassed += results.passed;
        totalFailed += results.failed;
      }
    }
    
    const overallSuccessRate = totalTests > 0 ? ((totalPassed / totalTests) * 100).toFixed(1) : '0.0';
    
    console.log(`📊 СТАТИСТИКА:`);
    console.log(`   🧪 Всего тестов: ${totalTests}`);
    console.log(`   ✅ Успешных: ${totalPassed}`);
    console.log(`   ❌ Провалено: ${totalFailed}`);
    console.log(`   📈 Общая успешность: ${overallSuccessRate}%`);
    console.log(`   ⏱️  Общее время: ${(totalTime / 1000).toFixed(1)}с`);
    
    // Определение статуса
    let status = '🎉 ОТЛИЧНО';
    let statusColor = '\x1b[32m'; // Зелёный
    
    if (parseFloat(overallSuccessRate) < 90) {
      status = '⚠️  ТРЕБУЕТ ВНИМАНИЯ';
      statusColor = '\x1b[33m'; // Жёлтый
    }
    
    if (parseFloat(overallSuccessRate) < 70 || totalFailed > 5) {
      status = '🚨 КРИТИЧНО';
      statusColor = '\x1b[31m'; // Красный
    }
    
    console.log(`\n${statusColor}🎯 ИТОГОВЫЙ СТАТУС: ${status}\x1b[0m`);
    
    console.log('\n📁 ОТЧЁТЫ:');
    console.log(`   📄 JSON: tests/master_report.json`);
    console.log(`   🌐 HTML: tests/master_report.html`);
    
    console.log('\n' + '='.repeat(80));
    
    // Рекомендации по запуску
    if (parseFloat(overallSuccessRate) >= 90) {
      console.log('🚀 Система готова к production использованию!');
    } else if (parseFloat(overallSuccessRate) >= 70) {
      console.log('⚠️  Рекомендуется исправить выявленные проблемы перед production');
    } else {
      console.log('🚨 Система НЕ готова к production - требуются критические исправления');
    }
  }
}

// Запуск если вызывается напрямую
if (import.meta.url === `file://${process.argv[1]}`) {
  const masterSuite = new MasterTestSuite();
  
  try {
    await masterSuite.runAllTests();
    
    // Определяем код выхода
    let totalFailed = 0;
    if (masterSuite.results.integration) {
      for (const results of Object.values(masterSuite.results.integration)) {
        totalFailed += results.failed;
      }
    }
    if (masterSuite.results.adapters) {
      for (const results of Object.values(masterSuite.results.adapters)) {
        totalFailed += results.failed;
      }
    }
    
    process.exit(totalFailed === 0 ? 0 : 1);
    
  } catch (error) {
    console.error('💥 Критическая ошибка:', error.message);
    process.exit(1);
  }
}

export default MasterTestSuite;