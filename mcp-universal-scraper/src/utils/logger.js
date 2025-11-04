import fs from 'fs';
import path from 'path';
import { createWriteStream } from 'fs';

/**
 * Система логирования для Universal Scraper
 * Поддерживает файловое и консольное логирование с ротацией
 */
class Logger {
  constructor(config = {}) {
    this.config = {
      level: config.level || 'info',
      file: config.file || './logs/scraper.log',
      maxFileSize: this.parseSize(config.maxFileSize || '10MB'),
      maxFiles: config.maxFiles || 5,
      console: config.console !== false,
      timestamp: config.timestamp !== false,
      ...config
    };

    this.levels = {
      error: 0,
      warn: 1,
      info: 2,
      debug: 3,
      trace: 4
    };

    this.currentLogLevel = this.levels[this.config.level] || 2;
    this.logStream = null;
    this.initializeFileLogging();
  }

  parseSize(sizeStr) {
    const units = { 'B': 1, 'KB': 1024, 'MB': 1024*1024, 'GB': 1024*1024*1024 };
    const match = sizeStr.match(/^(\d+(?:\.\d+)?)\s*(B|KB|MB|GB)$/i);
    if (!match) return 10 * 1024 * 1024; // Default 10MB
    return Math.floor(parseFloat(match[1]) * units[match[2].toUpperCase()]);
  }

  initializeFileLogging() {
    if (!this.config.file) return;

    try {
      const logDir = path.dirname(this.config.file);
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
      }

      this.checkLogRotation();
      this.logStream = createWriteStream(this.config.file, { flags: 'a' });
    } catch (error) {
      console.error('Failed to initialize file logging:', error.message);
    }
  }

  checkLogRotation() {
    if (!fs.existsSync(this.config.file)) return;

    const stats = fs.statSync(this.config.file);
    if (stats.size >= this.config.maxFileSize) {
      this.rotateLogFiles();
    }
  }

  rotateLogFiles() {
    try {
      // Закрываем текущий поток
      if (this.logStream) {
        this.logStream.end();
      }

      const logBaseName = this.config.file;
      const logDir = path.dirname(logBaseName);
      const logName = path.basename(logBaseName, path.extname(logBaseName));
      const logExt = path.extname(logBaseName);

      // Сдвигаем существующие файлы
      for (let i = this.config.maxFiles - 1; i >= 1; i--) {
        const oldFile = path.join(logDir, `${logName}.${i}${logExt}`);
        const newFile = path.join(logDir, `${logName}.${i + 1}${logExt}`);
        
        if (fs.existsSync(oldFile)) {
          if (i === this.config.maxFiles - 1) {
            fs.unlinkSync(oldFile); // Удаляем самый старый
          } else {
            fs.renameSync(oldFile, newFile);
          }
        }
      }

      // Переименовываем текущий файл
      const firstRotated = path.join(logDir, `${logName}.1${logExt}`);
      if (fs.existsSync(logBaseName)) {
        fs.renameSync(logBaseName, firstRotated);
      }

      // Создаем новый поток
      this.logStream = createWriteStream(logBaseName, { flags: 'a' });
    } catch (error) {
      console.error('Log rotation failed:', error.message);
    }
  }

  formatMessage(level, message, meta = {}) {
    const timestamp = this.config.timestamp ? new Date().toISOString() : '';
    const metaStr = Object.keys(meta).length > 0 ? ` ${JSON.stringify(meta)}` : '';
    
    return `${timestamp} [${level.toUpperCase()}] ${message}${metaStr}`;
  }

  log(level, message, meta = {}) {
    if (this.levels[level] > this.currentLogLevel) return;

    const formattedMessage = this.formatMessage(level, message, meta);

    // Консольное логирование
    if (this.config.console) {
      const consoleMethod = level === 'error' ? 'error' : 
                           level === 'warn' ? 'warn' : 'log';
      console[consoleMethod](formattedMessage);
    }

    // Файловое логирование
    if (this.logStream) {
      this.checkLogRotation();
      this.logStream.write(formattedMessage + '\n');
    }
  }

  error(message, meta = {}) {
    this.log('error', message, meta);
  }

  warn(message, meta = {}) {
    this.log('warn', message, meta);
  }

  info(message, meta = {}) {
    this.log('info', message, meta);
  }

  debug(message, meta = {}) {
    this.log('debug', message, meta);
  }

  trace(message, meta = {}) {
    this.log('trace', message, meta);
  }

  // Специальные методы для скрапинга
  scrapingStarted(url, adapter, meta = {}) {
    this.info('Scraping started', { url, adapter, ...meta });
  }

  scrapingCompleted(url, adapter, duration, meta = {}) {
    this.info('Scraping completed', { url, adapter, duration, ...meta });
  }

  scrapingFailed(url, adapter, error, meta = {}) {
    this.error('Scraping failed', { url, adapter, error: error.message, ...meta });
  }

  cacheHit(url, adapter, meta = {}) {
    this.debug('Cache hit', { url, adapter, ...meta });
  }

  cacheMiss(url, adapter, meta = {}) {
    this.debug('Cache miss', { url, adapter, ...meta });
  }

  // Статистика производительности
  performanceMetric(metric, value, unit, meta = {}) {
    this.info('Performance metric', { metric, value, unit, ...meta });
  }

  close() {
    if (this.logStream) {
      this.logStream.end();
    }
  }
}

export default Logger;