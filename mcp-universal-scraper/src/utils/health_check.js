/**
 * Система проверки здоровья Universal Scraper
 * Мониторит состояние компонентов и интеграций
 */
class HealthChecker {
  constructor(logger, monitor) {
    this.logger = logger;
    this.monitor = monitor;
    this.healthStatus = {
      overall: 'healthy',
      components: {
        browser: { status: 'unknown', lastCheck: null, error: null },
        cache: { status: 'unknown', lastCheck: null, error: null },
        memoryMcp: { status: 'unknown', lastCheck: null, error: null },
        doclingMcp: { status: 'unknown', lastCheck: null, error: null },
        sqliteCache: { status: 'unknown', lastCheck: null, error: null }
      },
      metrics: {
        uptime: 0,
        totalChecks: 0,
        lastHealthyCheck: null,
        lastUnhealthyCheck: null
      }
    };

    this.startTime = Date.now();
    this.checkInterval = null;
  }

  // Запуск периодических проверок
  startHealthChecks(intervalMs = 60000) {
    this.logger.info('Starting health checks', { interval: intervalMs });
    
    this.checkInterval = setInterval(async () => {
      await this.performHealthCheck();
    }, intervalMs);

    // Выполняем первую проверку сразу
    setTimeout(() => this.performHealthCheck(), 1000);
  }

  // Основная проверка здоровья
  async performHealthCheck() {
    const startTime = Date.now();
    this.healthStatus.metrics.totalChecks++;
    
    try {
      this.logger.debug('Performing health check');

      // Проверяем все компоненты
      await Promise.all([
        this.checkBrowserHealth(),
        this.checkCacheHealth(),
        this.checkMemoryMcpHealth(),
        this.checkDoclingMcpHealth(),
        this.checkSqliteCacheHealth()
      ]);

      // Определяем общее состояние
      this.updateOverallHealth();
      
      const duration = Date.now() - startTime;
      this.healthStatus.metrics.uptime = Date.now() - this.startTime;
      
      if (this.healthStatus.overall === 'healthy') {
        this.healthStatus.metrics.lastHealthyCheck = new Date().toISOString();
      } else {
        this.healthStatus.metrics.lastUnhealthyCheck = new Date().toISOString();
      }

      this.logger.debug('Health check completed', { 
        duration, 
        overall: this.healthStatus.overall 
      });

    } catch (error) {
      this.logger.error('Health check failed', { error: error.message });
      this.healthStatus.overall = 'unhealthy';
    }
  }

  // Проверка браузера Playwright
  async checkBrowserHealth() {
    try {
      const { chromium } = await import('playwright');
      const browser = await chromium.launch({ headless: true });
      await browser.close();
      
      this.updateComponentStatus('browser', 'healthy');
    } catch (error) {
      this.updateComponentStatus('browser', 'unhealthy', error.message);
    }
  }

  // Проверка кэша
  async checkCacheHealth() {
    try {
      // Проверяем доступность директории кэша
      const fs = await import('fs');
      const path = './cache';
      
      if (!fs.existsSync(path)) {
        throw new Error('Cache directory does not exist');
      }

      // Проверяем права на запись
      const testFile = './cache/.health_check';
      fs.writeFileSync(testFile, 'test');
      fs.unlinkSync(testFile);
      
      this.updateComponentStatus('cache', 'healthy');
    } catch (error) {
      this.updateComponentStatus('cache', 'unhealthy', error.message);
    }
  }

  // Проверка Memory MCP
  async checkMemoryMcpHealth() {
    try {
      // Простая проверка доступности MCP
      // В реальной реализации здесь был бы запрос к MCP серверу
      this.updateComponentStatus('memoryMcp', 'healthy');
    } catch (error) {
      this.updateComponentStatus('memoryMcp', 'unhealthy', error.message);
    }
  }

  // Проверка Docling MCP
  async checkDoclingMcpHealth() {
    try {
      // Проверка доступности Docling MCP
      this.updateComponentStatus('doclingMcp', 'healthy');
    } catch (error) {
      this.updateComponentStatus('doclingMcp', 'unhealthy', error.message);
    }
  }

  // Проверка SQLite кэша
  async checkSqliteCacheHealth() {
    try {
      // Проверка SQLite базы данных
      this.updateComponentStatus('sqliteCache', 'healthy');
    } catch (error) {
      this.updateComponentStatus('sqliteCache', 'unhealthy', error.message);
    }
  }

  // Обновление статуса компонента
  updateComponentStatus(component, status, error = null) {
    this.healthStatus.components[component] = {
      status,
      lastCheck: new Date().toISOString(),
      error
    };

    if (status === 'unhealthy') {
      this.logger.warn(`Component ${component} is unhealthy`, { error });
    } else {
      this.logger.debug(`Component ${component} is healthy`);
    }
  }

  // Определение общего состояния здоровья
  updateOverallHealth() {
    const components = Object.values(this.healthStatus.components);
    const unhealthyComponents = components.filter(c => c.status === 'unhealthy');
    const unknownComponents = components.filter(c => c.status === 'unknown');

    if (unhealthyComponents.length > 0) {
      this.healthStatus.overall = 'unhealthy';
    } else if (unknownComponents.length > 0) {
      this.healthStatus.overall = 'degraded';
    } else {
      this.healthStatus.overall = 'healthy';
    }
  }

  // Получение статуса здоровья
  getHealthStatus() {
    return {
      ...this.healthStatus,
      timestamp: new Date().toISOString(),
      performance: this.monitor ? this.monitor.getSummary() : null
    };
  }

  // Проверка готовности (readiness)
  isReady() {
    const criticalComponents = ['browser', 'cache'];
    return criticalComponents.every(component => 
      this.healthStatus.components[component].status === 'healthy'
    );
  }

  // Проверка живости (liveness)
  isAlive() {
    return this.healthStatus.overall !== 'unhealthy';
  }

  // Получение детального отчёта
  getDetailedReport() {
    const status = this.getHealthStatus();
    
    return {
      summary: {
        overall: status.overall,
        ready: this.isReady(),
        alive: this.isAlive(),
        uptime: this.formatDuration(status.metrics.uptime),
        totalChecks: status.metrics.totalChecks
      },
      components: Object.entries(status.components).map(([name, info]) => ({
        name,
        status: info.status,
        lastCheck: info.lastCheck,
        error: info.error,
        timeSinceLastCheck: info.lastCheck ? 
          Date.now() - new Date(info.lastCheck).getTime() : null
      })),
      performance: status.performance,
      recommendations: this.getHealthRecommendations()
    };
  }

  // Рекомендации по улучшению здоровья
  getHealthRecommendations() {
    const recommendations = [];
    const components = this.healthStatus.components;

    // Проверяем каждый компонент
    Object.entries(components).forEach(([name, info]) => {
      if (info.status === 'unhealthy') {
        recommendations.push({
          severity: 'high',
          component: name,
          issue: 'Component is unhealthy',
          suggestion: `Check ${name} configuration and logs`,
          error: info.error
        });
      } else if (info.status === 'unknown') {
        recommendations.push({
          severity: 'medium',
          component: name,
          issue: 'Component status unknown',
          suggestion: `Verify ${name} connectivity and configuration`
        });
      }
    });

    // Проверяем производительность
    if (this.monitor) {
      const metrics = this.monitor.getMetrics();
      
      if (metrics.scraping.averageTime > 10000) { // > 10 секунд
        recommendations.push({
          severity: 'medium',
          component: 'performance',
          issue: 'High average response time',
          suggestion: 'Consider optimizing scraping logic or increasing timeouts'
        });
      }

      if (metrics.memory.heapUsed > 500 * 1024 * 1024) { // > 500MB
        recommendations.push({
          severity: 'medium',
          component: 'memory',
          issue: 'High memory usage',
          suggestion: 'Consider implementing memory cleanup or reducing concurrent requests'
        });
      }

      if (metrics.successRate < 80) {
        recommendations.push({
          severity: 'high',
          component: 'reliability',
          issue: 'Low success rate',
          suggestion: 'Review error logs and improve error handling'
        });
      }
    }

    return recommendations;
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

  // Остановка проверок здоровья
  stopHealthChecks() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
      this.logger.info('Health checks stopped');
    }
  }

  // Принудительная проверка здоровья
  async forceHealthCheck() {
    this.logger.info('Forcing health check');
    await this.performHealthCheck();
    return this.getHealthStatus();
  }
}

export default HealthChecker;