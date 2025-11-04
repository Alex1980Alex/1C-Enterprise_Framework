import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

/**
 * Комплексные тесты для всех адаптеров Universal Scraper
 */
class AdapterTester {
  constructor() {
    this.testResults = {
      documentation: { passed: 0, failed: 0, errors: [] },
      news: { passed: 0, failed: 0, errors: [] },
      its_1c: { passed: 0, failed: 0, errors: [] },
      ecommerce: { passed: 0, failed: 0, errors: [] },
      generic: { passed: 0, failed: 0, errors: [] }
    };
    
    this.testUrls = {
      documentation: [
        'https://docs.github.com/en',
        'https://developer.mozilla.org/en-US/',
        'https://nodejs.org/en/docs/'
      ],
      news: [
        'https://habr.com/ru/news/',
        'https://tass.ru/',
        'https://www.rbc.ru/'
      ],
      its_1c: [
        'https://its.1c.ru/db/metod8dev',
        'https://its.1c.ru/db/content'
      ],
      ecommerce: [
        'https://www.ozon.ru/product/',
        'https://market.yandex.ru/product/',
        'https://www.wildberries.ru/catalog/'
      ],
      generic: [
        'https://example.com',
        'https://httpbin.org/html',
        'https://jsonplaceholder.typicode.com'
      ]
    };
  }

  async runAllTests() {
    console.log('🧪 Запуск тестирования всех адаптеров...\n');
    
    const startTime = Date.now();
    
    for (const [adapter, urls] of Object.entries(this.testUrls)) {
      console.log(`\n📋 Тестирование адаптера: ${adapter}`);
      console.log('─'.repeat(50));
      
      await this.testAdapter(adapter, urls);
    }
    
    const totalTime = Date.now() - startTime;
    this.printSummary(totalTime);
    
    return this.testResults;
  }

  async testAdapter(adapter, urls) {
    const config = await this.loadAdapterConfig(adapter);
    
    for (const url of urls) {
      try {
        console.log(`  🔗 Тестирование: ${url}`);
        
        const result = await this.testSingleUrl(url, adapter, config);
        
        if (result.success) {
          this.testResults[adapter].passed++;
          console.log(`    ✅ Успешно: ${result.extractedData.title || 'Без заголовка'}`);
          console.log(`    📊 Контент: ${result.extractedData.contentLength} символов`);
          console.log(`    🔗 Ссылки: ${result.extractedData.linksCount}`);
        } else {
          this.testResults[adapter].failed++;
          this.testResults[adapter].errors.push({
            url,
            error: result.error,
            timestamp: new Date().toISOString()
          });
          console.log(`    ❌ Ошибка: ${result.error}`);
        }
        
        // Задержка между запросами
        await this.sleep(1000);
        
      } catch (error) {
        this.testResults[adapter].failed++;
        this.testResults[adapter].errors.push({
          url,
          error: error.message,
          timestamp: new Date().toISOString()
        });
        console.log(`    💥 Исключение: ${error.message}`);
      }
    }
  }

  async testSingleUrl(url, adapter, config) {
    const browser = await chromium.launch({ 
      headless: true,
      timeout: 30000 
    });
    
    const page = await browser.newPage();
    
    try {
      // Настраиваем User-Agent
      await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
      
      // Загружаем страницу
      await page.goto(url, { 
        waitUntil: 'domcontentloaded',
        timeout: 20000 
      });
      
      // Ждём дополнительную загрузку
      await page.waitForTimeout(2000);
      
      // Извлекаем данные согласно конфигурации адаптера
      const extractedData = await page.evaluate((adapterConfig) => {
        const data = {
          title: '',
          content: '',
          contentLength: 0,
          links: [],
          linksCount: 0,
          images: [],
          imagesCount: 0,
          metadata: {}
        };
        
        // Извлекаем заголовок
        const titleSelectors = adapterConfig.selectors?.title || ['h1', 'title'];
        for (const selector of titleSelectors) {
          const element = document.querySelector(selector);
          if (element && element.textContent?.trim()) {
            data.title = element.textContent.trim();
            break;
          }
        }
        
        // Извлекаем основной контент
        const contentSelectors = adapterConfig.selectors?.content || ['main', '.content', 'article'];
        for (const selector of contentSelectors) {
          const element = document.querySelector(selector);
          if (element) {
            data.content = element.innerText || element.textContent || '';
            if (data.content.length > 100) { // Минимальная длина контента
              break;
            }
          }
        }
        
        data.contentLength = data.content.length;
        
        // Извлекаем ссылки
        const links = document.querySelectorAll('a[href]');
        data.links = Array.from(links).slice(0, 50).map(link => ({
          href: link.href,
          text: link.textContent?.trim() || '',
          title: link.title || ''
        }));
        data.linksCount = data.links.length;
        
        // Извлекаем изображения
        const images = document.querySelectorAll('img[src]');
        data.images = Array.from(images).slice(0, 20).map(img => ({
          src: img.src,
          alt: img.alt || '',
          title: img.title || ''
        }));
        data.imagesCount = data.images.length;
        
        // Метаданные
        const metaDescription = document.querySelector('meta[name="description"]');
        if (metaDescription) {
          data.metadata.description = metaDescription.getAttribute('content') || '';
        }
        
        const metaKeywords = document.querySelector('meta[name="keywords"]');
        if (metaKeywords) {
          data.metadata.keywords = metaKeywords.getAttribute('content') || '';
        }
        
        return data;
      }, config);
      
      // Валидация результатов
      const validation = this.validateExtractedData(extractedData, adapter);
      
      return {
        success: validation.isValid,
        extractedData,
        validation,
        error: validation.isValid ? null : validation.errors.join(', ')
      };
      
    } catch (error) {
      return {
        success: false,
        error: error.message,
        extractedData: null
      };
    } finally {
      await browser.close();
    }
  }

  validateExtractedData(data, adapter) {
    const validation = {
      isValid: true,
      errors: [],
      warnings: []
    };
    
    // Общие проверки
    if (!data.title || data.title.length < 3) {
      validation.errors.push('Заголовок не найден или слишком короткий');
      validation.isValid = false;
    }
    
    if (data.contentLength < 50) {
      validation.errors.push('Контент слишком короткий или не найден');
      validation.isValid = false;
    }
    
    if (data.linksCount === 0) {
      validation.warnings.push('Ссылки не найдены');
    }
    
    // Специфичные проверки для каждого адаптера
    switch (adapter) {
      case 'documentation':
        if (data.linksCount < 5) {
          validation.warnings.push('Мало ссылок для документационного сайта');
        }
        if (!data.content.includes('API') && !data.content.includes('documentation')) {
          validation.warnings.push('Не обнаружены признаки документации');
        }
        break;
        
      case 'news':
        if (data.contentLength < 200) {
          validation.warnings.push('Контент короток для новостной статьи');
        }
        if (!data.metadata.description) {
          validation.warnings.push('Отсутствует описание статьи');
        }
        break;
        
      case 'its_1c':
        if (!data.content.includes('1С') && !data.title.includes('1С')) {
          validation.warnings.push('Не обнаружены признаки 1С контента');
        }
        break;
        
      case 'ecommerce':
        if (data.imagesCount === 0) {
          validation.warnings.push('Изображения товаров не найдены');
        }
        if (!data.content.includes('цена') && !data.content.includes('price')) {
          validation.warnings.push('Информация о цене не найдена');
        }
        break;
        
      case 'generic':
        // Для generic адаптера требования минимальны
        break;
    }
    
    return validation;
  }

  async loadAdapterConfig(adapter) {
    try {
      const configPath = path.join(process.cwd(), 'config', 'adapters', `${adapter}.json`);
      
      if (fs.existsSync(configPath)) {
        const configText = fs.readFileSync(configPath, 'utf8');
        return JSON.parse(configText);
      }
    } catch (error) {
      console.warn(`⚠️  Не удалось загрузить конфигурацию для ${adapter}: ${error.message}`);
    }
    
    // Возвращаем базовую конфигурацию
    return {
      selectors: {
        title: ['h1', 'title', '.title'],
        content: ['main', '.content', 'article', '#content'],
        links: ['a[href]'],
        images: ['img[src]']
      }
    };
  }

  printSummary(totalTime) {
    console.log('\n' + '='.repeat(60));
    console.log('📊 СВОДКА РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ');
    console.log('='.repeat(60));
    
    let totalPassed = 0;
    let totalFailed = 0;
    
    for (const [adapter, results] of Object.entries(this.testResults)) {
      totalPassed += results.passed;
      totalFailed += results.failed;
      
      const total = results.passed + results.failed;
      const successRate = total > 0 ? ((results.passed / total) * 100).toFixed(1) : '0.0';
      
      console.log(`\n🔧 ${adapter.toUpperCase()}`);
      console.log(`   ✅ Успешно: ${results.passed}`);
      console.log(`   ❌ Ошибок: ${results.failed}`);
      console.log(`   📈 Успешность: ${successRate}%`);
      
      if (results.errors.length > 0) {
        console.log(`   🚨 Последние ошибки:`);
        results.errors.slice(-2).forEach(error => {
          console.log(`      • ${error.url}: ${error.error}`);
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

  async generateDetailedReport() {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalTests: 0,
        totalPassed: 0,
        totalFailed: 0,
        overallSuccessRate: 0
      },
      adapters: {},
      recommendations: []
    };
    
    for (const [adapter, results] of Object.entries(this.testResults)) {
      const total = results.passed + results.failed;
      report.summary.totalTests += total;
      report.summary.totalPassed += results.passed;
      report.summary.totalFailed += results.failed;
      
      report.adapters[adapter] = {
        ...results,
        total,
        successRate: total > 0 ? ((results.passed / total) * 100).toFixed(1) : '0.0'
      };
    }
    
    report.summary.overallSuccessRate = report.summary.totalTests > 0 ? 
      ((report.summary.totalPassed / report.summary.totalTests) * 100).toFixed(1) : '0.0';
    
    // Генерация рекомендаций
    for (const [adapter, results] of Object.entries(report.adapters)) {
      if (parseFloat(results.successRate) < 80) {
        report.recommendations.push({
          type: 'improvement',
          adapter,
          issue: `Низкая успешность тестов (${results.successRate}%)`,
          suggestion: `Проверить селекторы и логику извлечения для адаптера ${adapter}`
        });
      }
      
      if (results.errors.length > 0) {
        const errorTypes = results.errors.reduce((acc, error) => {
          const type = this.categorizeError(error.error);
          acc[type] = (acc[type] || 0) + 1;
          return acc;
        }, {});
        
        report.recommendations.push({
          type: 'error_analysis',
          adapter,
          issue: `Обнаружены ошибки: ${Object.keys(errorTypes).join(', ')}`,
          suggestion: `Улучшить обработку ошибок для типов: ${Object.keys(errorTypes).join(', ')}`
        });
      }
    }
    
    return report;
  }

  categorizeError(errorMessage) {
    if (errorMessage.includes('timeout')) return 'timeout';
    if (errorMessage.includes('network')) return 'network';
    if (errorMessage.includes('404')) return 'not_found';
    if (errorMessage.includes('403') || errorMessage.includes('401')) return 'access_denied';
    if (errorMessage.includes('navigation')) return 'navigation';
    return 'other';
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Метод для тестирования производительности
  async performanceTest(adapter, url, iterations = 5) {
    console.log(`\n⚡ Тест производительности: ${adapter} на ${url}`);
    
    const times = [];
    
    for (let i = 0; i < iterations; i++) {
      const startTime = Date.now();
      
      try {
        const config = await this.loadAdapterConfig(adapter);
        const result = await this.testSingleUrl(url, adapter, config);
        const endTime = Date.now();
        
        if (result.success) {
          times.push(endTime - startTime);
          console.log(`  Итерация ${i + 1}: ${endTime - startTime}мс ✅`);
        } else {
          console.log(`  Итерация ${i + 1}: Ошибка - ${result.error} ❌`);
        }
      } catch (error) {
        console.log(`  Итерация ${i + 1}: Исключение - ${error.message} 💥`);
      }
      
      await this.sleep(500);
    }
    
    if (times.length > 0) {
      const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
      const minTime = Math.min(...times);
      const maxTime = Math.max(...times);
      
      console.log(`  📊 Статистика:`);
      console.log(`     Среднее время: ${avgTime.toFixed(0)}мс`);
      console.log(`     Минимальное: ${minTime}мс`);
      console.log(`     Максимальное: ${maxTime}мс`);
      console.log(`     Успешных тестов: ${times.length}/${iterations}`);
      
      return {
        avgTime,
        minTime,
        maxTime,
        successCount: times.length,
        totalIterations: iterations,
        successRate: (times.length / iterations) * 100
      };
    }
    
    return null;
  }
}

// Экспорт для использования в других модулях
export default AdapterTester;

// Если файл запускается напрямую
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new AdapterTester();
  
  try {
    const results = await tester.runAllTests();
    const report = await tester.generateDetailedReport();
    
    // Сохраняем детальный отчёт
    const reportPath = path.join(process.cwd(), 'tests', 'test_report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`\n💾 Детальный отчёт сохранён: ${reportPath}`);
    
    // Выход с кодом ошибки если есть проблемы
    const overallSuccess = parseFloat(report.summary.overallSuccessRate);
    process.exit(overallSuccess >= 80 ? 0 : 1);
    
  } catch (error) {
    console.error('💥 Критическая ошибка тестирования:', error.message);
    process.exit(1);
  }
}