import { chromium } from 'playwright';
import { URL } from 'url';

/**
 * Рекурсивный скрапер для глубокого анализа сайтов
 * Поддерживает умное обхождение ссылок с учётом роботов и ограничений
 */
class RecursiveScraper {
  constructor(config, logger, monitor) {
    this.config = config;
    this.logger = logger;
    this.monitor = monitor;
    
    this.visitedUrls = new Set();
    this.pendingUrls = new Map(); // url -> {depth, priority}
    this.results = [];
    this.errors = [];
    
    this.maxDepth = config.maxDepth || 3;
    this.maxPages = config.maxPages || 100;
    this.delay = config.delay || 1000;
    this.concurrency = config.concurrency || 2;
    this.respectRobotsTxt = config.respectRobotsTxt !== false;
    
    this.robotsCache = new Map();
    this.activeScraping = new Set();
  }

  async scrapeRecursively(startUrl, adapter, options = {}) {
    this.logger.info('Starting recursive scraping', { 
      startUrl, 
      adapter,
      maxDepth: this.maxDepth,
      maxPages: this.maxPages 
    });

    const startTime = Date.now();
    
    try {
      // Инициализация
      this.visitedUrls.clear();
      this.pendingUrls.clear();
      this.results.length = 0;
      this.errors.length = 0;
      
      // Добавляем стартовый URL
      this.addUrlToPending(startUrl, 0, 10);
      
      // Проверяем robots.txt если нужно
      if (this.respectRobotsTxt) {
        await this.loadRobotsTxt(startUrl);
      }
      
      // Запускаем параллельный scraping
      await this.processUrlsConcurrently(adapter, options);
      
      const duration = Date.now() - startTime;
      
      this.logger.info('Recursive scraping completed', {
        startUrl,
        totalPages: this.results.length,
        totalErrors: this.errors.length,
        duration
      });

      return {
        success: true,
        results: this.results,
        errors: this.errors,
        summary: {
          startUrl,
          totalPages: this.results.length,
          totalErrors: this.errors.length,
          duration,
          visitedUrls: Array.from(this.visitedUrls),
          maxDepthReached: Math.max(...this.results.map(r => r.depth || 0))
        }
      };

    } catch (error) {
      this.logger.error('Recursive scraping failed', { 
        startUrl, 
        error: error.message 
      });
      
      return {
        success: false,
        error: error.message,
        results: this.results,
        errors: this.errors
      };
    }
  }

  async processUrlsConcurrently(adapter, options) {
    const workers = [];
    
    // Создаем воркеры для параллельной обработки
    for (let i = 0; i < this.concurrency; i++) {
      workers.push(this.worker(i, adapter, options));
    }
    
    // Ждём завершения всех воркеров
    await Promise.all(workers);
  }

  async worker(workerId, adapter, options) {
    this.logger.debug(`Worker ${workerId} started`);
    
    while (this.shouldContinueProcessing()) {
      const urlInfo = this.getNextUrl();
      
      if (!urlInfo) {
        // Ждём немного, возможно другие воркеры добавят новые URL
        await this.sleep(100);
        continue;
      }
      
      const { url, depth, priority } = urlInfo;
      
      try {
        await this.processUrl(url, depth, adapter, options);
        await this.sleep(this.delay); // Rate limiting
      } catch (error) {
        this.logger.error(`Worker ${workerId} failed to process URL`, {
          url,
          error: error.message
        });
        
        this.errors.push({
          url,
          depth,
          error: error.message,
          timestamp: new Date().toISOString()
        });
      }
    }
    
    this.logger.debug(`Worker ${workerId} finished`);
  }

  async processUrl(url, depth, adapter, options) {
    if (this.visitedUrls.has(url)) {
      return;
    }
    
    this.visitedUrls.add(url);
    this.activeScraping.add(url);
    
    this.logger.debug('Processing URL', { url, depth });
    
    try {
      // Проверяем robots.txt
      if (this.respectRobotsTxt && !await this.isAllowedByRobots(url)) {
        this.logger.warn('URL blocked by robots.txt', { url });
        return;
      }
      
      // Скрапим страницу
      const scrapingResult = await this.scrapePage(url, adapter, options);
      
      if (scrapingResult.success) {
        scrapingResult.depth = depth;
        scrapingResult.timestamp = new Date().toISOString();
        this.results.push(scrapingResult);
        
        // Извлекаем ссылки для дальнейшего обхода
        if (depth < this.maxDepth) {
          await this.extractAndQueueLinks(url, scrapingResult.content, depth + 1);
        }
      } else {
        this.errors.push({
          url,
          depth,
          error: scrapingResult.error,
          timestamp: new Date().toISOString()
        });
      }
      
    } finally {
      this.activeScraping.delete(url);
    }
  }

  async scrapePage(url, adapter, options) {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    try {
      // Загружаем страницу
      await page.goto(url, { 
        waitUntil: 'domcontentloaded',
        timeout: 30000 
      });
      
      // Ждём загрузки контента
      await page.waitForTimeout(1000);
      
      // Извлекаем контент в зависимости от адаптера
      const content = await this.extractContent(page, adapter);
      
      return {
        success: true,
        url,
        content,
        metadata: {
          title: await page.title(),
          responseStatus: page.url() !== url ? 'redirected' : 'ok',
          finalUrl: page.url()
        }
      };
      
    } catch (error) {
      return {
        success: false,
        url,
        error: error.message
      };
    } finally {
      await browser.close();
    }
  }

  async extractContent(page, adapter) {
    // Загружаем конфигурацию адаптера
    const adapterConfig = await this.loadAdapterConfig(adapter);
    
    return await page.evaluate((config) => {
      const content = {
        text: '',
        links: [],
        images: [],
        metadata: {}
      };
      
      // Извлекаем основной текст
      const contentSelectors = config.selectors.content || ['main', '.content', 'article'];
      for (const selector of contentSelectors) {
        const element = document.querySelector(selector);
        if (element) {
          content.text = element.innerText || element.textContent || '';
          break;
        }
      }
      
      // Извлекаем ссылки
      const links = document.querySelectorAll('a[href]');
      content.links = Array.from(links).map(link => ({
        href: link.href,
        text: link.textContent?.trim() || '',
        title: link.title || ''
      }));
      
      // Извлекаем изображения
      const images = document.querySelectorAll('img[src]');
      content.images = Array.from(images).map(img => ({
        src: img.src,
        alt: img.alt || '',
        title: img.title || ''
      }));
      
      // Извлекаем метаданные
      const titleElement = document.querySelector('h1') || document.querySelector('title');
      if (titleElement) {
        content.metadata.title = titleElement.textContent?.trim() || '';
      }
      
      const metaDescription = document.querySelector('meta[name="description"]');
      if (metaDescription) {
        content.metadata.description = metaDescription.getAttribute('content') || '';
      }
      
      return content;
    }, adapterConfig);
  }

  async extractAndQueueLinks(baseUrl, content, nextDepth) {
    if (!content.links || !Array.isArray(content.links)) {
      return;
    }
    
    const baseUrlObj = new URL(baseUrl);
    const domain = baseUrlObj.hostname;
    
    for (const link of content.links) {
      try {
        const linkUrl = new URL(link.href, baseUrl);
        
        // Фильтруем ссылки
        if (!this.shouldFollowLink(linkUrl, domain)) {
          continue;
        }
        
        const normalizedUrl = this.normalizeUrl(linkUrl.href);
        
        if (!this.visitedUrls.has(normalizedUrl) && !this.pendingUrls.has(normalizedUrl)) {
          // Определяем приоритет ссылки
          const priority = this.calculateLinkPriority(link, linkUrl, baseUrlObj);
          this.addUrlToPending(normalizedUrl, nextDepth, priority);
        }
        
      } catch (error) {
        // Игнорируем некорректные URL
        this.logger.debug('Invalid URL found', { href: link.href, error: error.message });
      }
    }
  }

  shouldFollowLink(linkUrl, baseDomain) {
    // Проверяем протокол
    if (!['http:', 'https:'].includes(linkUrl.protocol)) {
      return false;
    }
    
    // Проверяем домен (остаёмся в рамках того же домена)
    if (linkUrl.hostname !== baseDomain) {
      return false;
    }
    
    // Исключаем файлы
    const excludeExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.exe'];
    const pathname = linkUrl.pathname.toLowerCase();
    if (excludeExtensions.some(ext => pathname.endsWith(ext))) {
      return false;
    }
    
    // Исключаем служебные страницы
    const excludePatterns = ['/admin', '/login', '/logout', '/signup', '/register', '/api/'];
    if (excludePatterns.some(pattern => pathname.includes(pattern))) {
      return false;
    }
    
    return true;
  }

  calculateLinkPriority(link, linkUrl, baseUrl) {
    let priority = 5; // базовый приоритет
    
    // Увеличиваем приоритет для важных разделов
    const highPriorityPatterns = ['/docs', '/documentation', '/help', '/support', '/api'];
    if (highPriorityPatterns.some(pattern => linkUrl.pathname.includes(pattern))) {
      priority += 3;
    }
    
    // Уменьшаем приоритет для вспомогательных страниц
    const lowPriorityPatterns = ['/contact', '/about', '/privacy', '/terms'];
    if (lowPriorityPatterns.some(pattern => linkUrl.pathname.includes(pattern))) {
      priority -= 2;
    }
    
    // Увеличиваем приоритет для коротких путей
    const pathDepth = linkUrl.pathname.split('/').filter(p => p).length;
    if (pathDepth <= 2) {
      priority += 1;
    }
    
    return Math.max(1, Math.min(10, priority));
  }

  normalizeUrl(url) {
    const urlObj = new URL(url);
    // Убираем фрагменты и некоторые параметры
    urlObj.hash = '';
    urlObj.searchParams.delete('utm_source');
    urlObj.searchParams.delete('utm_medium');
    urlObj.searchParams.delete('utm_campaign');
    return urlObj.href;
  }

  addUrlToPending(url, depth, priority) {
    if (this.pendingUrls.size >= this.maxPages * 2) {
      return; // Ограничиваем размер очереди
    }
    
    this.pendingUrls.set(url, { depth, priority });
  }

  getNextUrl() {
    if (this.pendingUrls.size === 0) {
      return null;
    }
    
    // Находим URL с наивысшим приоритетом
    let bestUrl = null;
    let bestPriority = -1;
    
    for (const [url, info] of this.pendingUrls) {
      if (info.priority > bestPriority) {
        bestUrl = url;
        bestPriority = info.priority;
      }
    }
    
    if (bestUrl) {
      const info = this.pendingUrls.get(bestUrl);
      this.pendingUrls.delete(bestUrl);
      return { url: bestUrl, ...info };
    }
    
    return null;
  }

  shouldContinueProcessing() {
    return (
      this.results.length < this.maxPages &&
      (this.pendingUrls.size > 0 || this.activeScraping.size > 0)
    );
  }

  async loadRobotsTxt(url) {
    const urlObj = new URL(url);
    const robotsUrl = `${urlObj.protocol}//${urlObj.host}/robots.txt`;
    
    if (this.robotsCache.has(urlObj.host)) {
      return;
    }
    
    try {
      const response = await fetch(robotsUrl);
      if (response.ok) {
        const robotsText = await response.text();
        this.parseRobotsTxt(urlObj.host, robotsText);
      } else {
        // Если robots.txt не найден, разрешаем всё
        this.robotsCache.set(urlObj.host, { allowAll: true });
      }
    } catch (error) {
      this.logger.warn('Failed to load robots.txt', { robotsUrl, error: error.message });
      this.robotsCache.set(urlObj.host, { allowAll: true });
    }
  }

  parseRobotsTxt(host, robotsText) {
    const rules = {
      allowAll: false,
      disallowed: [],
      crawlDelay: 0
    };
    
    const lines = robotsText.split('\n');
    let currentUserAgent = null;
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('#') || !trimmed) continue;
      
      const [key, value] = trimmed.split(':').map(s => s.trim());
      
      if (key.toLowerCase() === 'user-agent') {
        currentUserAgent = value.toLowerCase();
      } else if (currentUserAgent === '*' || currentUserAgent === 'claudecode') {
        if (key.toLowerCase() === 'disallow') {
          if (value === '/') {
            rules.allowAll = false;
            rules.disallowed = ['/'];
          } else if (value) {
            rules.disallowed.push(value);
          }
        } else if (key.toLowerCase() === 'crawl-delay') {
          rules.crawlDelay = parseInt(value) || 0;
        }
      }
    }
    
    this.robotsCache.set(host, rules);
    
    if (rules.crawlDelay > 0) {
      this.delay = Math.max(this.delay, rules.crawlDelay * 1000);
    }
  }

  async isAllowedByRobots(url) {
    const urlObj = new URL(url);
    const rules = this.robotsCache.get(urlObj.host);
    
    if (!rules || rules.allowAll) {
      return true;
    }
    
    return !rules.disallowed.some(pattern => {
      if (pattern === '/') return true;
      return urlObj.pathname.startsWith(pattern);
    });
  }

  async loadAdapterConfig(adapter) {
    try {
      const fs = await import('fs');
      const configPath = `./config/adapters/${adapter}.json`;
      
      if (fs.existsSync(configPath)) {
        const configText = fs.readFileSync(configPath, 'utf8');
        return JSON.parse(configText);
      }
    } catch (error) {
      this.logger.warn('Failed to load adapter config', { adapter, error: error.message });
    }
    
    // Возвращаем базовую конфигурацию
    return {
      selectors: {
        content: ['main', '.content', 'article', '#content'],
        title: ['h1', 'title', '.title'],
        links: ['a[href]']
      }
    };
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Получение статистики процесса
  getProgress() {
    return {
      visited: this.visitedUrls.size,
      pending: this.pendingUrls.size,
      results: this.results.length,
      errors: this.errors.length,
      active: this.activeScraping.size,
      maxPages: this.maxPages,
      maxDepth: this.maxDepth,
      progress: Math.min(100, (this.results.length / this.maxPages) * 100)
    };
  }
}

export default RecursiveScraper;