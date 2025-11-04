import os from 'os';
import { performance } from 'perf_hooks';

/**
 * Система мониторинга производительности и метрик для Universal Scraper
 */
class PerformanceMonitor {
  constructor(logger) {
    this.logger = logger;
    this.metrics = {
      scraping: {
        totalRequests: 0,
        successfulRequests: 0,
        failedRequests: 0,
        cacheHits: 0,
        cacheMisses: 0,
        totalTime: 0,
        averageTime: 0,
        minTime: Infinity,
        maxTime: 0
      },
      adapters: {},
      domains: {},
      memory: {
        heapUsed: 0,
        heapTotal: 0,
        external: 0,
        rss: 0
      },
      system: {
        cpuUsage: 0,
        loadAverage: []
      }
    };

    this.startTime = Date.now();
    this.activeRequests = new Map();
    
    // Периодический сбор системных метрик
    this.metricsInterval = setInterval(() => {
      this.collectSystemMetrics();
    }, 30000); // Каждые 30 секунд
  }

  // Начало мониторинга запроса
  startRequest(requestId, url, adapter) {
    const startTime = performance.now();
    this.activeRequests.set(requestId, {
      url,
      adapter,
      startTime,
      memoryBefore: process.memoryUsage()
    });

    this.logger.trace('Request monitoring started', { 
      requestId, 
      url, 
      adapter,
      memoryBefore: this.formatMemory(process.memoryUsage())
    });

    return requestId;
  }

  // Завершение мониторинга запроса
  endRequest(requestId, success = true, error = null) {
    const request = this.activeRequests.get(requestId);
    if (!request) {
      this.logger.warn('Request not found for monitoring', { requestId });
      return;
    }

    const endTime = performance.now();
    const duration = endTime - request.startTime;
    const memoryAfter = process.memoryUsage();
    const memoryDelta = {
      heapUsed: memoryAfter.heapUsed - request.memoryBefore.heapUsed,
      heapTotal: memoryAfter.heapTotal - request.memoryBefore.heapTotal,
      external: memoryAfter.external - request.memoryBefore.external,
      rss: memoryAfter.rss - request.memoryBefore.rss
    };

    // Обновляем общие метрики
    this.updateScrapingMetrics(duration, success);
    
    // Обновляем метрики адаптера
    this.updateAdapterMetrics(request.adapter, duration, success);
    
    // Обновляем метрики домена
    const domain = this.extractDomain(request.url);
    this.updateDomainMetrics(domain, duration, success);

    this.logger.debug('Request monitoring completed', {
      requestId,
      url: request.url,
      adapter: request.adapter,
      duration: Math.round(duration),
      success,
      error: error?.message,
      memoryDelta: this.formatMemory(memoryDelta)
    });

    this.activeRequests.delete(requestId);
  }

  updateScrapingMetrics(duration, success) {
    const metrics = this.metrics.scraping;
    
    metrics.totalRequests++;
    if (success) {
      metrics.successfulRequests++;
    } else {
      metrics.failedRequests++;
    }
    
    metrics.totalTime += duration;
    metrics.averageTime = metrics.totalTime / metrics.totalRequests;
    metrics.minTime = Math.min(metrics.minTime, duration);
    metrics.maxTime = Math.max(metrics.maxTime, duration);
  }

  updateAdapterMetrics(adapter, duration, success) {
    if (!this.metrics.adapters[adapter]) {
      this.metrics.adapters[adapter] = {
        totalRequests: 0,
        successfulRequests: 0,
        failedRequests: 0,
        totalTime: 0,
        averageTime: 0,
        minTime: Infinity,
        maxTime: 0
      };
    }

    const adapterMetrics = this.metrics.adapters[adapter];
    adapterMetrics.totalRequests++;
    if (success) {
      adapterMetrics.successfulRequests++;
    } else {
      adapterMetrics.failedRequests++;
    }
    
    adapterMetrics.totalTime += duration;
    adapterMetrics.averageTime = adapterMetrics.totalTime / adapterMetrics.totalRequests;
    adapterMetrics.minTime = Math.min(adapterMetrics.minTime, duration);
    adapterMetrics.maxTime = Math.max(adapterMetrics.maxTime, duration);
  }

  updateDomainMetrics(domain, duration, success) {
    if (!this.metrics.domains[domain]) {
      this.metrics.domains[domain] = {
        totalRequests: 0,
        successfulRequests: 0,
        failedRequests: 0,
        totalTime: 0,
        averageTime: 0
      };
    }

    const domainMetrics = this.metrics.domains[domain];
    domainMetrics.totalRequests++;
    if (success) {
      domainMetrics.successfulRequests++;
    } else {
      domainMetrics.failedRequests++;
    }
    
    domainMetrics.totalTime += duration;
    domainMetrics.averageTime = domainMetrics.totalTime / domainMetrics.totalRequests;
  }

  // Кэш метрики
  recordCacheHit(url, adapter) {
    this.metrics.scraping.cacheHits++;
    this.logger.debug('Cache hit recorded', { url, adapter });
  }

  recordCacheMiss(url, adapter) {
    this.metrics.scraping.cacheMisses++;
    this.logger.debug('Cache miss recorded', { url, adapter });
  }

  // Сбор системных метрик
  collectSystemMetrics() {
    // Память процесса
    this.metrics.memory = process.memoryUsage();
    
    // Системные метрики
    this.metrics.system.loadAverage = os.loadavg();
    
    // CPU Usage (простая реализация)
    const startUsage = process.cpuUsage();
    setTimeout(() => {
      const endUsage = process.cpuUsage(startUsage);
      this.metrics.system.cpuUsage = (endUsage.user + endUsage.system) / 1000000; // в секундах
    }, 100);

    this.logger.performanceMetric('memory_heap_used', this.metrics.memory.heapUsed, 'bytes');
    this.logger.performanceMetric('memory_rss', this.metrics.memory.rss, 'bytes');
    this.logger.performanceMetric('system_load_1m', this.metrics.system.loadAverage[0], 'ratio');
  }

  // Получение метрик
  getMetrics() {
    const uptime = Date.now() - this.startTime;
    const cacheHitRate = this.metrics.scraping.totalRequests > 0 ? 
      (this.metrics.scraping.cacheHits / this.metrics.scraping.totalRequests) * 100 : 0;
    const successRate = this.metrics.scraping.totalRequests > 0 ?
      (this.metrics.scraping.successfulRequests / this.metrics.scraping.totalRequests) * 100 : 0;

    return {
      ...this.metrics,
      uptime,
      cacheHitRate,
      successRate,
      activeRequests: this.activeRequests.size,
      timestamp: new Date().toISOString()
    };
  }

  // Получение краткого отчёта
  getSummary() {
    const metrics = this.getMetrics();
    
    return {
      uptime: this.formatDuration(metrics.uptime),
      totalRequests: metrics.scraping.totalRequests,
      successRate: `${metrics.successRate.toFixed(2)}%`,
      cacheHitRate: `${metrics.cacheHitRate.toFixed(2)}%`,
      averageResponseTime: `${metrics.scraping.averageTime.toFixed(2)}ms`,
      activeRequests: metrics.activeRequests,
      memoryUsage: this.formatMemory(metrics.memory),
      topAdapters: this.getTopAdapters(3),
      topDomains: this.getTopDomains(3)
    };
  }

  getTopAdapters(count = 5) {
    return Object.entries(this.metrics.adapters)
      .sort(([,a], [,b]) => b.totalRequests - a.totalRequests)
      .slice(0, count)
      .map(([name, metrics]) => ({
        name,
        requests: metrics.totalRequests,
        successRate: `${((metrics.successfulRequests / metrics.totalRequests) * 100).toFixed(2)}%`,
        avgTime: `${metrics.averageTime.toFixed(2)}ms`
      }));
  }

  getTopDomains(count = 5) {
    return Object.entries(this.metrics.domains)
      .sort(([,a], [,b]) => b.totalRequests - a.totalRequests)
      .slice(0, count)
      .map(([name, metrics]) => ({
        name,
        requests: metrics.totalRequests,
        successRate: `${((metrics.successfulRequests / metrics.totalRequests) * 100).toFixed(2)}%`,
        avgTime: `${metrics.averageTime.toFixed(2)}ms`
      }));
  }

  // Утилиты
  extractDomain(url) {
    try {
      return new URL(url).hostname;
    } catch {
      return 'unknown';
    }
  }

  formatMemory(memory) {
    return {
      heapUsed: `${(memory.heapUsed / 1024 / 1024).toFixed(2)} MB`,
      heapTotal: `${(memory.heapTotal / 1024 / 1024).toFixed(2)} MB`,
      external: `${(memory.external / 1024 / 1024).toFixed(2)} MB`,
      rss: `${(memory.rss / 1024 / 1024).toFixed(2)} MB`
    };
  }

  formatDuration(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ${hours % 24}h ${minutes % 60}m`;
    if (hours > 0) return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  }

  // Экспорт метрик
  exportMetrics(format = 'json') {
    const metrics = this.getMetrics();
    
    switch (format) {
      case 'json':
        return JSON.stringify(metrics, null, 2);
      case 'csv':
        return this.exportToCsv(metrics);
      case 'prometheus':
        return this.exportToPrometheus(metrics);
      default:
        return metrics;
    }
  }

  exportToCsv(metrics) {
    const rows = [
      'timestamp,total_requests,successful_requests,failed_requests,cache_hits,cache_misses,avg_time,memory_heap_used,memory_rss'
    ];
    
    rows.push([
      metrics.timestamp,
      metrics.scraping.totalRequests,
      metrics.scraping.successfulRequests,
      metrics.scraping.failedRequests,
      metrics.scraping.cacheHits,
      metrics.scraping.cacheMisses,
      metrics.scraping.averageTime.toFixed(2),
      metrics.memory.heapUsed,
      metrics.memory.rss
    ].join(','));
    
    return rows.join('\n');
  }

  exportToPrometheus(metrics) {
    const lines = [];
    
    // Основные метрики скрапинга
    lines.push(`# HELP scraper_requests_total Total number of scraping requests`);
    lines.push(`# TYPE scraper_requests_total counter`);
    lines.push(`scraper_requests_total ${metrics.scraping.totalRequests}`);
    
    lines.push(`# HELP scraper_requests_successful_total Number of successful requests`);
    lines.push(`# TYPE scraper_requests_successful_total counter`);
    lines.push(`scraper_requests_successful_total ${metrics.scraping.successfulRequests}`);
    
    lines.push(`# HELP scraper_cache_hits_total Number of cache hits`);
    lines.push(`# TYPE scraper_cache_hits_total counter`);
    lines.push(`scraper_cache_hits_total ${metrics.scraping.cacheHits}`);
    
    lines.push(`# HELP scraper_memory_heap_used_bytes Memory heap used in bytes`);
    lines.push(`# TYPE scraper_memory_heap_used_bytes gauge`);
    lines.push(`scraper_memory_heap_used_bytes ${metrics.memory.heapUsed}`);
    
    return lines.join('\n');
  }

  // Очистка и завершение
  cleanup() {
    if (this.metricsInterval) {
      clearInterval(this.metricsInterval);
    }
  }
}

export default PerformanceMonitor;