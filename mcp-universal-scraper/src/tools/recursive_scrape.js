import RecursiveScraper from './recursive_scraper.js';

/**
 * MCP Tool для рекурсивного скрапинга сайтов
 */
class RecursiveScrapeConfig {
  static getToolDefinition() {
    return {
      name: 'recursive_scrape_website',
      description: 'Выполняет рекурсивное сканирование сайта с глубоким анализом структуры и извлечением контента с множества страниц',
      inputSchema: {
        type: 'object',
        properties: {
          url: {
            type: 'string',
            description: 'Стартовый URL для рекурсивного сканирования'
          },
          adapter: {
            type: 'string',
            enum: ['documentation', 'news', 'its_1c', 'ecommerce', 'generic'],
            description: 'Тип адаптера для оптимального извлечения контента',
            default: 'generic'
          },
          maxDepth: {
            type: 'integer',
            minimum: 1,
            maximum: 5,
            description: 'Максимальная глубина рекурсии (по умолчанию: 3)',
            default: 3
          },
          maxPages: {
            type: 'integer',
            minimum: 1,
            maximum: 500,
            description: 'Максимальное количество страниц для обработки (по умолчанию: 100)',
            default: 100
          },
          delay: {
            type: 'integer',
            minimum: 100,
            maximum: 10000,
            description: 'Задержка между запросами в миллисекундах (по умолчанию: 1000)',
            default: 1000
          },
          concurrency: {
            type: 'integer',
            minimum: 1,
            maximum: 10,
            description: 'Количество параллельных потоков (по умолчанию: 2)',
            default: 2
          },
          respectRobotsTxt: {
            type: 'boolean',
            description: 'Учитывать ограничения robots.txt (по умолчанию: true)',
            default: true
          },
          saveToCache: {
            type: 'boolean',
            description: 'Сохранять результаты в кэш (по умолчанию: true)',
            default: true
          },
          saveToMemory: {
            type: 'boolean',
            description: 'Сохранять результаты в Memory MCP (по умолчанию: true)',
            default: true
          },
          includeImages: {
            type: 'boolean',
            description: 'Извлекать информацию об изображениях (по умолчанию: false)',
            default: false
          },
          followExternalLinks: {
            type: 'boolean',
            description: 'Следовать по внешним ссылкам (по умолчанию: false)',
            default: false
          },
          filterPatterns: {
            type: 'array',
            items: { type: 'string' },
            description: 'Паттерны URL для исключения из сканирования',
            default: []
          },
          priorityPatterns: {
            type: 'array',
            items: { type: 'string' },
            description: 'Паттерны URL с высоким приоритетом',
            default: []
          }
        },
        required: ['url']
      }
    };
  }

  constructor(logger, monitor, memoryMcp, sqliteCache) {
    this.logger = logger;
    this.monitor = monitor;
    this.memoryMcp = memoryMcp;
    this.sqliteCache = sqliteCache;
  }

  async execute(args) {
    const requestId = `recursive_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    try {
      this.logger.scrapingStarted(args.url, `recursive_${args.adapter}`, { requestId, ...args });
      
      if (this.monitor) {
        this.monitor.startRequest(requestId, args.url, `recursive_${args.adapter}`);
      }

      // Валидация URL
      if (!this.isValidUrl(args.url)) {
        throw new Error('Invalid URL provided');
      }

      // Создаём конфигурацию для рекурсивного скрапера
      const config = {
        maxDepth: args.maxDepth || 3,
        maxPages: args.maxPages || 100,
        delay: args.delay || 1000,
        concurrency: args.concurrency || 2,
        respectRobotsTxt: args.respectRobotsTxt !== false,
        includeImages: args.includeImages || false,
        followExternalLinks: args.followExternalLinks || false,
        filterPatterns: args.filterPatterns || [],
        priorityPatterns: args.priorityPatterns || []
      };

      // Создаём и запускаем рекурсивный скрапер
      const scraper = new RecursiveScraper(config, this.logger, this.monitor);
      const startTime = Date.now();
      
      const result = await scraper.scrapeRecursively(args.url, args.adapter || 'generic', {
        includeImages: config.includeImages,
        followExternalLinks: config.followExternalLinks
      });

      const duration = Date.now() - startTime;

      if (!result.success) {
        throw new Error(result.error || 'Recursive scraping failed');
      }

      // Обрабатываем результаты
      const processedResult = await this.processScrapingResults(result, args, requestId);

      // Сохраняем в кэш если требуется
      if (args.saveToCache && this.sqliteCache) {
        await this.saveToCache(args.url, args.adapter, processedResult, args);
      }

      // Сохраняем в Memory MCP если требуется
      if (args.saveToMemory && this.memoryMcp) {
        await this.saveToMemoryMcp(processedResult, args);
      }

      this.logger.scrapingCompleted(args.url, `recursive_${args.adapter}`, duration, {
        requestId,
        pagesScraped: result.results.length,
        errorsCount: result.errors.length,
        maxDepthReached: result.summary.maxDepthReached
      });

      if (this.monitor) {
        this.monitor.endRequest(requestId, true);
      }

      return {
        success: true,
        data: processedResult,
        metadata: {
          requestId,
          url: args.url,
          adapter: args.adapter,
          duration,
          summary: result.summary,
          config: {
            maxDepth: config.maxDepth,
            maxPages: config.maxPages,
            concurrency: config.concurrency
          }
        }
      };

    } catch (error) {
      this.logger.scrapingFailed(args.url, `recursive_${args.adapter}`, error, { requestId });
      
      if (this.monitor) {
        this.monitor.endRequest(requestId, false, error);
      }

      return {
        success: false,
        error: error.message,
        requestId,
        url: args.url,
        adapter: args.adapter
      };
    }
  }

  async processScrapingResults(rawResult, args, requestId) {
    const processedResults = {
      summary: rawResult.summary,
      pages: [],
      sitemap: this.generateSitemap(rawResult.results),
      contentAnalysis: this.analyzeContent(rawResult.results),
      errors: rawResult.errors,
      statistics: this.generateStatistics(rawResult.results, rawResult.errors)
    };

    // Обрабатываем каждую страницу
    for (const page of rawResult.results) {
      const processedPage = {
        url: page.url,
        depth: page.depth,
        title: page.metadata?.title || 'Untitled',
        content: {
          text: this.cleanText(page.content?.text || ''),
          wordCount: this.countWords(page.content?.text || ''),
          links: page.content?.links || [],
          images: args.includeImages ? (page.content?.images || []) : [],
          metadata: page.content?.metadata || {}
        },
        responseInfo: {
          status: page.metadata?.responseStatus || 'ok',
          finalUrl: page.metadata?.finalUrl || page.url,
          timestamp: page.timestamp
        },
        analysis: {
          contentType: this.detectContentType(page.content?.text || ''),
          language: this.detectLanguage(page.content?.text || ''),
          readabilityScore: this.calculateReadability(page.content?.text || '')
        }
      };

      processedResults.pages.push(processedPage);
    }

    return processedResults;
  }

  generateSitemap(results) {
    const sitemap = {
      totalPages: results.length,
      structure: {},
      byDepth: {}
    };

    for (const page of results) {
      const urlObj = new URL(page.url);
      const pathParts = urlObj.pathname.split('/').filter(p => p);
      
      // Строим структуру дерева
      let current = sitemap.structure;
      for (const part of pathParts) {
        if (!current[part]) {
          current[part] = { _pages: [], _children: {} };
        }
        current = current[part]._children;
      }
      
      // Добавляем страницу
      const leafKey = pathParts[pathParts.length - 1] || 'root';
      if (!sitemap.structure[leafKey]) {
        sitemap.structure[leafKey] = { _pages: [], _children: {} };
      }
      sitemap.structure[leafKey]._pages.push({
        url: page.url,
        title: page.metadata?.title,
        depth: page.depth
      });

      // Группируем по глубине
      const depth = page.depth || 0;
      if (!sitemap.byDepth[depth]) {
        sitemap.byDepth[depth] = [];
      }
      sitemap.byDepth[depth].push(page.url);
    }

    return sitemap;
  }

  analyzeContent(results) {
    const analysis = {
      totalWords: 0,
      averageWordsPerPage: 0,
      languageDistribution: {},
      contentTypes: {},
      topKeywords: [],
      duplicateContent: []
    };

    const allText = [];
    const wordCounts = [];

    for (const page of results) {
      const text = page.content?.text || '';
      const wordCount = this.countWords(text);
      
      analysis.totalWords += wordCount;
      wordCounts.push(wordCount);
      allText.push(text);

      // Анализ языка
      const language = this.detectLanguage(text);
      analysis.languageDistribution[language] = (analysis.languageDistribution[language] || 0) + 1;

      // Анализ типа контента
      const contentType = this.detectContentType(text);
      analysis.contentTypes[contentType] = (analysis.contentTypes[contentType] || 0) + 1;
    }

    analysis.averageWordsPerPage = wordCounts.length > 0 ? 
      Math.round(analysis.totalWords / wordCounts.length) : 0;

    // Поиск ключевых слов
    analysis.topKeywords = this.extractKeywords(allText.join(' '), 20);

    // Поиск дублирующегося контента
    analysis.duplicateContent = this.findDuplicateContent(results);

    return analysis;
  }

  generateStatistics(results, errors) {
    const stats = {
      totalPages: results.length,
      totalErrors: errors.length,
      successRate: results.length > 0 ? 
        (results.length / (results.length + errors.length)) * 100 : 0,
      depthDistribution: {},
      errorsByType: {},
      averagePageSize: 0,
      totalContentSize: 0
    };

    // Статистика по глубине
    for (const page of results) {
      const depth = page.depth || 0;
      stats.depthDistribution[depth] = (stats.depthDistribution[depth] || 0) + 1;
      
      const contentSize = (page.content?.text || '').length;
      stats.totalContentSize += contentSize;
    }

    stats.averagePageSize = results.length > 0 ? 
      Math.round(stats.totalContentSize / results.length) : 0;

    // Статистика ошибок
    for (const error of errors) {
      const errorType = this.categorizeError(error.error);
      stats.errorsByType[errorType] = (stats.errorsByType[errorType] || 0) + 1;
    }

    return stats;
  }

  // Утилитарные методы
  isValidUrl(url) {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  cleanText(text) {
    return text
      .replace(/\s+/g, ' ')
      .replace(/\n+/g, '\n')
      .trim();
  }

  countWords(text) {
    return text.split(/\s+/).filter(word => word.length > 0).length;
  }

  detectContentType(text) {
    if (text.includes('class ') || text.includes('function ') || text.includes('var ')) {
      return 'code';
    }
    if (text.includes('<!DOCTYPE') || text.includes('<html')) {
      return 'html';
    }
    if (text.length > 1000 && text.split('.').length > 10) {
      return 'article';
    }
    if (text.length < 200) {
      return 'snippet';
    }
    return 'text';
  }

  detectLanguage(text) {
    // Простое определение языка по ключевым словам
    const russianWords = ['и', 'в', 'на', 'с', 'по', 'для', 'не', 'что', 'это', 'как'];
    const englishWords = ['the', 'and', 'of', 'to', 'a', 'in', 'that', 'have', 'it', 'for'];
    
    const words = text.toLowerCase().split(/\s+/);
    const russianCount = words.filter(word => russianWords.includes(word)).length;
    const englishCount = words.filter(word => englishWords.includes(word)).length;
    
    if (russianCount > englishCount) return 'ru';
    if (englishCount > russianCount) return 'en';
    return 'unknown';
  }

  calculateReadability(text) {
    // Упрощённый индекс читаемости
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const words = text.split(/\s+/).filter(w => w.length > 0);
    const avgWordsPerSentence = sentences.length > 0 ? words.length / sentences.length : 0;
    
    if (avgWordsPerSentence < 10) return 'easy';
    if (avgWordsPerSentence < 20) return 'medium';
    return 'hard';
  }

  extractKeywords(text, limit = 20) {
    const words = text.toLowerCase()
      .replace(/[^\w\sа-яё]/gi, '')
      .split(/\s+/)
      .filter(word => word.length > 3);
    
    const frequency = {};
    for (const word of words) {
      frequency[word] = (frequency[word] || 0) + 1;
    }
    
    return Object.entries(frequency)
      .sort(([,a], [,b]) => b - a)
      .slice(0, limit)
      .map(([word, count]) => ({ word, count }));
  }

  findDuplicateContent(results) {
    const duplicates = [];
    const textHashes = new Map();
    
    for (const page of results) {
      const text = page.content?.text || '';
      if (text.length < 100) continue; // Игнорируем короткий контент
      
      const hash = this.simpleHash(text);
      if (textHashes.has(hash)) {
        duplicates.push({
          url1: textHashes.get(hash),
          url2: page.url,
          similarity: 'exact'
        });
      } else {
        textHashes.set(hash, page.url);
      }
    }
    
    return duplicates;
  }

  simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash;
  }

  categorizeError(errorMessage) {
    if (errorMessage.includes('timeout')) return 'timeout';
    if (errorMessage.includes('network')) return 'network';
    if (errorMessage.includes('404')) return 'not_found';
    if (errorMessage.includes('403') || errorMessage.includes('401')) return 'access_denied';
    if (errorMessage.includes('robots')) return 'robots_blocked';
    return 'other';
  }

  async saveToCache(url, adapter, result, options) {
    try {
      await this.sqliteCache.saveScrapingResult(
        url, 
        `recursive_${adapter}`, 
        result, 
        options
      );
    } catch (error) {
      this.logger.warn('Failed to save recursive scraping to cache', { 
        url, 
        error: error.message 
      });
    }
  }

  async saveToMemoryMcp(result, options) {
    try {
      await this.memoryMcp.saveRecursiveScrapingResult(result, options);
    } catch (error) {
      this.logger.warn('Failed to save recursive scraping to Memory MCP', { 
        error: error.message 
      });
    }
  }
}

export default RecursiveScrapeConfig;