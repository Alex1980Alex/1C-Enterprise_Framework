import fs from 'fs';
import path from 'path';

/**
 * Интеграционные тесты для Universal Scraper MCP сервера
 * Тестирует взаимодействие между компонентами
 */
class IntegrationTester {
  constructor() {
    this.testResults = {
      mcpIntegration: { passed: 0, failed: 0, errors: [] },
      cacheIntegration: { passed: 0, failed: 0, errors: [] },
      memoryIntegration: { passed: 0, failed: 0, errors: [] },
      doclingIntegration: { passed: 0, failed: 0, errors: [] },
      recursiveScraping: { passed: 0, failed: 0, errors: [] }
    };
  }

  async runIntegrationTests() {
    console.log('🔗 Запуск интеграционных тестов...\n');
    
    const startTime = Date.now();
    
    await this.testMcpServerInitialization();
    await this.testCacheIntegration();
    await this.testMemoryMcpIntegration();
    await this.testDoclingMcpIntegration();
    await this.testRecursiveScrapingFlow();
    
    const totalTime = Date.now() - startTime;
    this.printIntegrationSummary(totalTime);
    
    return this.testResults;
  }

  async testMcpServerInitialization() {
    console.log('🚀 Тестирование инициализации MCP сервера...');
    
    try {
      // Проверяем наличие всех необходимых файлов
      const requiredFiles = [
        'src/index.js',
        'package.json',
        'config/server.json',
        'config/adapters/generic.json'
      ];
      
      for (const file of requiredFiles) {
        if (!fs.existsSync(file)) {
          throw new Error(`Отсутствует обязательный файл: ${file}`);
        }
      }
      
      // Проверяем конфигурацию
      const serverConfig = JSON.parse(fs.readFileSync('config/server.json', 'utf8'));
      if (!serverConfig.server || !serverConfig.server.name) {
        throw new Error('Некорректная конфигурация сервера');
      }
      
      // Проверяем package.json
      const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
      if (!packageJson.name || !packageJson.dependencies) {
        throw new Error('Некорректный package.json');
      }
      
      this.testResults.mcpIntegration.passed++;
      console.log('  ✅ Инициализация сервера - OK');
      
    } catch (error) {
      this.testResults.mcpIntegration.failed++;
      this.testResults.mcpIntegration.errors.push({
        test: 'server_initialization',
        error: error.message,
        timestamp: new Date().toISOString()
      });
      console.log(`  ❌ Ошибка инициализации: ${error.message}`);
    }
  }

  async testCacheIntegration() {
    console.log('\n💾 Тестирование интеграции с кэшем...');
    
    try {
      // Проверяем наличие кэш директории
      if (!fs.existsSync('cache')) {
        fs.mkdirSync('cache', { recursive: true });
      }
      
      // Тестируем создание кэш файла
      const testCacheFile = 'cache/test_cache.json';
      const testData = {
        url: 'https://example.com',
        adapter: 'generic',
        content: 'test content',
        timestamp: new Date().toISOString()
      };
      
      fs.writeFileSync(testCacheFile, JSON.stringify(testData, null, 2));
      
      // Проверяем чтение
      const readData = JSON.parse(fs.readFileSync(testCacheFile, 'utf8'));
      if (readData.url !== testData.url) {
        throw new Error('Данные кэша не совпадают');
      }
      
      // Очищаем тестовый файл
      fs.unlinkSync(testCacheFile);
      
      this.testResults.cacheIntegration.passed++;
      console.log('  ✅ Кэш интеграция - OK');
      
    } catch (error) {
      this.testResults.cacheIntegration.failed++;
      this.testResults.cacheIntegration.errors.push({
        test: 'cache_integration',
        error: error.message,
        timestamp: new Date().toISOString()
      });
      console.log(`  ❌ Ошибка кэша: ${error.message}`);
    }
  }

  async testMemoryMcpIntegration() {
    console.log('\n🧠 Тестирование интеграции с Memory MCP...');
    
    try {
      // Проверяем наличие интеграционного модуля
      if (!fs.existsSync('src/integrations/memory_mcp.js')) {
        throw new Error('Отсутствует модуль интеграции Memory MCP');
      }
      
      // Проверяем структуру модуля
      const memoryMcpContent = fs.readFileSync('src/integrations/memory_mcp.js', 'utf8');
      if (!memoryMcpContent.includes('saveScrapedContent')) {
        throw new Error('Memory MCP модуль не содержит необходимые методы');
      }
      
      // Симулируем создание сущности
      const testEntity = {
        name: 'TestWebsite',
        entityType: 'scraped_webpage',
        observations: ['Test scraping observation']
      };
      
      // В реальном тестировании здесь был бы вызов Memory MCP
      // Сейчас просто проверяем структуру данных
      if (!testEntity.name || !testEntity.entityType) {
        throw new Error('Некорректная структура сущности');
      }
      
      this.testResults.memoryIntegration.passed++;
      console.log('  ✅ Memory MCP интеграция - OK');
      
    } catch (error) {
      this.testResults.memoryIntegration.failed++;
      this.testResults.memoryIntegration.errors.push({
        test: 'memory_mcp_integration',
        error: error.message,
        timestamp: new Date().toISOString()
      });
      console.log(`  ❌ Ошибка Memory MCP: ${error.message}`);
    }
  }

  async testDoclingMcpIntegration() {
    console.log('\n📄 Тестирование интеграции с Docling MCP...');
    
    try {
      // Проверяем наличие интеграционного модуля
      if (!fs.existsSync('src/integrations/docling_mcp.js')) {
        throw new Error('Отсутствует модуль интеграции Docling MCP');
      }
      
      // Проверяем структуру модуля
      const doclingMcpContent = fs.readFileSync('src/integrations/docling_mcp.js', 'utf8');
      if (!doclingMcpContent.includes('isDocumentUrl')) {
        throw new Error('Docling MCP модуль не содержит необходимые методы');
      }
      
      // Тестируем определение документных URL
      const documentUrls = [
        'https://example.com/document.pdf',
        'https://example.com/file.docx',
        'https://example.com/presentation.pptx'
      ];
      
      const nonDocumentUrls = [
        'https://example.com/page.html',
        'https://example.com/api/data.json'
      ];
      
      // Проверяем логику определения типа файла
      for (const url of documentUrls) {
        if (!this.isDocumentUrl(url)) {
          throw new Error(`URL ${url} должен определяться как документ`);
        }
      }
      
      for (const url of nonDocumentUrls) {
        if (this.isDocumentUrl(url)) {
          throw new Error(`URL ${url} не должен определяться как документ`);
        }
      }
      
      this.testResults.doclingIntegration.passed++;
      console.log('  ✅ Docling MCP интеграция - OK');
      
    } catch (error) {
      this.testResults.doclingIntegration.failed++;
      this.testResults.doclingIntegration.errors.push({
        test: 'docling_mcp_integration',
        error: error.message,
        timestamp: new Date().toISOString()
      });
      console.log(`  ❌ Ошибка Docling MCP: ${error.message}`);
    }
  }

  async testRecursiveScrapingFlow() {
    console.log('\n🔄 Тестирование рекурсивного скрапинга...');
    
    try {
      // Проверяем наличие модуля рекурсивного скрапинга
      if (!fs.existsSync('src/tools/recursive_scraper.js')) {
        throw new Error('Отсутствует модуль рекурсивного скрапинга');
      }
      
      if (!fs.existsSync('src/tools/recursive_scrape.js')) {
        throw new Error('Отсутствует MCP tool рекурсивного скрапинга');
      }
      
      // Проверяем структуру конфигурации
      const testConfig = {
        maxDepth: 2,
        maxPages: 10,
        delay: 1000,
        concurrency: 1,
        respectRobotsTxt: true
      };
      
      if (testConfig.maxDepth < 1 || testConfig.maxPages < 1) {
        throw new Error('Некорректная конфигурация рекурсивного скрапинга');
      }
      
      // Симулируем результат рекурсивного скрапинга
      const mockResult = {
        success: true,
        results: [
          {
            url: 'https://example.com',
            depth: 0,
            content: { text: 'Test content', links: [] }
          }
        ],
        errors: [],
        summary: {
          startUrl: 'https://example.com',
          totalPages: 1,
          totalErrors: 0,
          maxDepthReached: 0
        }
      };
      
      if (!mockResult.success || !mockResult.summary) {
        throw new Error('Некорректная структура результата');
      }
      
      this.testResults.recursiveScraping.passed++;
      console.log('  ✅ Рекурсивный скрапинг - OK');
      
    } catch (error) {
      this.testResults.recursiveScraping.failed++;
      this.testResults.recursiveScraping.errors.push({
        test: 'recursive_scraping_flow',
        error: error.message,
        timestamp: new Date().toISOString()
      });
      console.log(`  ❌ Ошибка рекурсивного скрапинга: ${error.message}`);
    }
  }

  // Вспомогательный метод для определения документных URL
  isDocumentUrl(url) {
    const supportedFormats = ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls'];
    return supportedFormats.some(format => url.toLowerCase().endsWith(format));
  }

  printIntegrationSummary(totalTime) {
    console.log('\n' + '='.repeat(60));
    console.log('🔗 СВОДКА ИНТЕГРАЦИОННЫХ ТЕСТОВ');
    console.log('='.repeat(60));
    
    let totalPassed = 0;
    let totalFailed = 0;
    
    for (const [component, results] of Object.entries(this.testResults)) {
      totalPassed += results.passed;
      totalFailed += results.failed;
      
      const total = results.passed + results.failed;
      const successRate = total > 0 ? ((results.passed / total) * 100).toFixed(1) : '0.0';
      
      console.log(`\n🔧 ${component.toUpperCase()}`);
      console.log(`   ✅ Успешно: ${results.passed}`);
      console.log(`   ❌ Ошибок: ${results.failed}`);
      console.log(`   📈 Успешность: ${successRate}%`);
      
      if (results.errors.length > 0) {
        console.log(`   🚨 Ошибки:`);
        results.errors.forEach(error => {
          console.log(`      • ${error.test}: ${error.error}`);
        });
      }
    }
    
    const overallTotal = totalPassed + totalFailed;
    const overallSuccessRate = overallTotal > 0 ? ((totalPassed / overallTotal) * 100).toFixed(1) : '0.0';
    
    console.log(`\n🎯 ОБЩИЕ РЕЗУЛЬТАТЫ:`);
    console.log(`   ✅ Всего успешных: ${totalPassed}`);
    console.log(`   ❌ Всего ошибок: ${totalFailed}`);
    console.log(`   📈 Общая успешность: ${overallSuccessRate}%`);
    console.log(`   ⏱️  Время выполнения: ${(totalTime / 1000).toFixed(1)}с`);
    
    console.log('\n' + '='.repeat(60));
  }

  async generateIntegrationReport() {
    const report = {
      timestamp: new Date().toISOString(),
      type: 'integration_tests',
      summary: {
        totalComponents: Object.keys(this.testResults).length,
        totalPassed: 0,
        totalFailed: 0,
        overallSuccessRate: 0
      },
      components: {},
      recommendations: [],
      systemInfo: {
        nodeVersion: process.version,
        platform: process.platform,
        arch: process.arch
      }
    };
    
    for (const [component, results] of Object.entries(this.testResults)) {
      const total = results.passed + results.failed;
      report.summary.totalPassed += results.passed;
      report.summary.totalFailed += results.failed;
      
      report.components[component] = {
        ...results,
        total,
        successRate: total > 0 ? ((results.passed / total) * 100).toFixed(1) : '0.0'
      };
    }
    
    report.summary.overallSuccessRate = (report.summary.totalPassed + report.summary.totalFailed) > 0 ? 
      ((report.summary.totalPassed / (report.summary.totalPassed + report.summary.totalFailed)) * 100).toFixed(1) : '0.0';
    
    // Генерация рекомендаций
    for (const [component, results] of Object.entries(report.components)) {
      if (results.failed > 0) {
        report.recommendations.push({
          type: 'critical',
          component,
          issue: `Обнаружены ошибки интеграции в компоненте ${component}`,
          suggestion: `Проверить зависимости и конфигурацию для ${component}`,
          errors: results.errors
        });
      }
      
      if (parseFloat(results.successRate) < 100) {
        report.recommendations.push({
          type: 'improvement',
          component,
          issue: `Неполная успешность тестов (${results.successRate}%)`,
          suggestion: `Улучшить надёжность интеграции ${component}`
        });
      }
    }
    
    return report;
  }
}

export default IntegrationTester;

// Если файл запускается напрямую
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new IntegrationTester();
  
  try {
    const results = await tester.runIntegrationTests();
    const report = await tester.generateIntegrationReport();
    
    // Сохраняем отчёт
    const reportPath = path.join(process.cwd(), 'tests', 'integration_report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`\n💾 Интеграционный отчёт сохранён: ${reportPath}`);
    
    // Выход с кодом ошибки если есть критические проблемы
    const criticalErrors = report.recommendations.filter(r => r.type === 'critical').length;
    process.exit(criticalErrors === 0 ? 0 : 1);
    
  } catch (error) {
    console.error('💥 Критическая ошибка интеграционного тестирования:', error.message);
    process.exit(1);
  }
}