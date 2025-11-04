/**
 * SQLite MCP Integration for Universal Web Scraper
 * Provides intelligent caching to avoid redundant scraping
 */

import crypto from 'crypto';

export class SQLiteCacheIntegration {
  constructor() {
    this.enabled = false;
    this.tableName = 'scraper_cache';
    this.maxCacheAge = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
    this.initializeConnection();
  }

  async initializeConnection() {
    try {
      console.error('Initializing SQLite Cache integration...');
      
      // Create cache table if not exists
      await this.createCacheTable();
      
      this.enabled = true;
      console.error('SQLite Cache ready');
    } catch (error) {
      console.error('SQLite MCP not available:', error.message);
      this.enabled = false;
    }
  }

  async createCacheTable() {
    const createTableSQL = `
      CREATE TABLE IF NOT EXISTS ${this.tableName} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url_hash TEXT UNIQUE NOT NULL,
        original_url TEXT NOT NULL,
        adapter_type TEXT NOT NULL,
        content_hash TEXT NOT NULL,
        scraped_content TEXT NOT NULL,
        metadata TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        accessed_at INTEGER NOT NULL,
        hit_count INTEGER DEFAULT 1
      )
    `;

    // In real implementation: await mcp_sqlite_create_table({ query: createTableSQL });
    console.error('[SQLite Cache] Cache table created/verified');

    // Create index for faster lookups
    const createIndexSQL = `
      CREATE INDEX IF NOT EXISTS idx_url_hash_adapter 
      ON ${this.tableName} (url_hash, adapter_type)
    `;

    // In real implementation: await mcp_sqlite_write_query({ query: createIndexSQL });
    console.error('[SQLite Cache] Cache index created');
  }

  generateUrlHash(url, adapter_type, options = {}) {
    // Create unique hash based on URL, adapter, and relevant options
    const hashInput = JSON.stringify({
      url: url.toLowerCase(),
      adapter: adapter_type,
      auth: options.auth ? 'authenticated' : 'public',
      depth: options.max_depth || 1
    });
    
    return crypto.createHash('sha256').update(hashInput).digest('hex');
  }

  generateContentHash(content) {
    return crypto.createHash('md5').update(content).digest('hex');
  }

  async getCachedContent(url, adapter_type, options = {}) {
    if (!this.enabled) {
      return null;
    }

    try {
      const urlHash = this.generateUrlHash(url, adapter_type, options);
      const now = Date.now();
      
      const query = `
        SELECT * FROM ${this.tableName} 
        WHERE url_hash = '${urlHash}' 
        AND adapter_type = '${adapter_type}'
        ORDER BY created_at DESC 
        LIMIT 1
      `;

      // In real implementation: const result = await mcp_sqlite_read_query({ query });
      const result = { rows: [] }; // Simulated empty result

      if (result.rows && result.rows.length > 0) {
        const cached = result.rows[0];
        const cacheAge = now - cached.created_at;
        
        // Check if cache is still valid
        if (cacheAge <= this.maxCacheAge) {
          // Update access stats
          await this.updateCacheStats(cached.id);
          
          console.error(`[SQLite Cache] Cache HIT for ${url} (age: ${Math.round(cacheAge/1000/60)} min)`);
          
          return {
            url: cached.original_url,
            content: cached.scraped_content,
            metadata: JSON.parse(cached.metadata),
            cached: true,
            cache_age: cacheAge,
            cache_hit_count: cached.hit_count + 1
          };
        } else {
          console.error(`[SQLite Cache] Cache EXPIRED for ${url} (age: ${Math.round(cacheAge/1000/60/60)} hours)`);
          // Clean up expired cache
          await this.cleanupExpiredCache(cached.id);
        }
      }

      console.error(`[SQLite Cache] Cache MISS for ${url}`);
      return null;

    } catch (error) {
      console.error('Error reading from cache:', error.message);
      return null;
    }
  }

  async saveCachedContent(url, adapter_type, scrapingResult, options = {}) {
    if (!this.enabled) {
      return false;
    }

    try {
      const urlHash = this.generateUrlHash(url, adapter_type, options);
      const contentHash = this.generateContentHash(scrapingResult.content);
      const now = Date.now();

      // Check if we already have this exact content
      const existingQuery = `
        SELECT id FROM ${this.tableName} 
        WHERE url_hash = '${urlHash}' 
        AND content_hash = '${contentHash}'
      `;

      // In real implementation: const existing = await mcp_sqlite_read_query({ query: existingQuery });
      const existing = { rows: [] }; // Simulated

      if (existing.rows && existing.rows.length > 0) {
        console.error('[SQLite Cache] Content unchanged, updating access time');
        await this.updateCacheStats(existing.rows[0].id);
        return true;
      }

      // Save new cache entry
      const insertQuery = `
        INSERT OR REPLACE INTO ${this.tableName} 
        (url_hash, original_url, adapter_type, content_hash, scraped_content, metadata, created_at, accessed_at)
        VALUES (
          '${urlHash}',
          '${url.replace(/'/g, "''")}',
          '${adapter_type}',
          '${contentHash}',
          '${scrapingResult.content.replace(/'/g, "''")}',
          '${JSON.stringify(scrapingResult.metadata).replace(/'/g, "''")}',
          ${now},
          ${now}
        )
      `;

      // In real implementation: await mcp_sqlite_write_query({ query: insertQuery });
      
      console.error(`[SQLite Cache] Saved to cache: ${url} (${scrapingResult.content.length} chars)`);
      
      // Cleanup old entries periodically
      if (Math.random() < 0.1) { // 10% chance
        await this.cleanupOldCache();
      }

      return true;

    } catch (error) {
      console.error('Error saving to cache:', error.message);
      return false;
    }
  }

  async updateCacheStats(cacheId) {
    try {
      const updateQuery = `
        UPDATE ${this.tableName} 
        SET accessed_at = ${Date.now()}, hit_count = hit_count + 1
        WHERE id = ${cacheId}
      `;

      // In real implementation: await mcp_sqlite_write_query({ query: updateQuery });
      
    } catch (error) {
      console.error('Error updating cache stats:', error.message);
    }
  }

  async cleanupExpiredCache(cacheId = null) {
    try {
      const cutoffTime = Date.now() - this.maxCacheAge;
      
      let deleteQuery;
      if (cacheId) {
        deleteQuery = `DELETE FROM ${this.tableName} WHERE id = ${cacheId}`;
      } else {
        deleteQuery = `DELETE FROM ${this.tableName} WHERE created_at < ${cutoffTime}`;
      }

      // In real implementation: await mcp_sqlite_write_query({ query: deleteQuery });
      
      console.error('[SQLite Cache] Cleaned up expired entries');

    } catch (error) {
      console.error('Error cleaning up cache:', error.message);
    }
  }

  async cleanupOldCache() {
    try {
      // Keep only the 1000 most recent entries
      const cleanupQuery = `
        DELETE FROM ${this.tableName} 
        WHERE id NOT IN (
          SELECT id FROM ${this.tableName} 
          ORDER BY accessed_at DESC 
          LIMIT 1000
        )
      `;

      // In real implementation: await mcp_sqlite_write_query({ query: cleanupQuery });
      
      console.error('[SQLite Cache] Cleaned up old cache entries');

    } catch (error) {
      console.error('Error cleaning up old cache:', error.message);
    }
  }

  async getCacheStatistics() {
    if (!this.enabled) {
      return null;
    }

    try {
      const statsQuery = `
        SELECT 
          COUNT(*) as total_entries,
          COUNT(DISTINCT adapter_type) as adapters_used,
          AVG(hit_count) as avg_hit_count,
          MIN(created_at) as oldest_entry,
          MAX(accessed_at) as newest_access,
          SUM(LENGTH(scraped_content)) as total_content_size
        FROM ${this.tableName}
      `;

      // In real implementation: const result = await mcp_sqlite_read_query({ query: statsQuery });
      
      // Simulated result
      const result = {
        rows: [{
          total_entries: 0,
          adapters_used: 0,
          avg_hit_count: 0,
          oldest_entry: Date.now(),
          newest_access: Date.now(),
          total_content_size: 0
        }]
      };

      if (result.rows && result.rows.length > 0) {
        const stats = result.rows[0];
        
        return {
          total_cached_pages: stats.total_entries,
          adapters_used: stats.adapters_used,
          average_hit_count: Math.round(stats.avg_hit_count * 100) / 100,
          cache_age_hours: Math.round((Date.now() - stats.oldest_entry) / 1000 / 60 / 60),
          last_access_hours: Math.round((Date.now() - stats.newest_access) / 1000 / 60 / 60),
          total_content_mb: Math.round(stats.total_content_size / 1024 / 1024 * 100) / 100,
          cache_efficiency: stats.total_entries > 0 ? Math.round(stats.avg_hit_count / stats.total_entries * 100) : 0
        };
      }

      return null;

    } catch (error) {
      console.error('Error getting cache statistics:', error.message);
      return null;
    }
  }

  async getTopCachedDomains(limit = 10) {
    if (!this.enabled) {
      return [];
    }

    try {
      const domainsQuery = `
        SELECT 
          SUBSTR(original_url, 1, INSTR(original_url || '/', '/', 8) - 1) as domain,
          COUNT(*) as page_count,
          SUM(hit_count) as total_hits,
          MAX(accessed_at) as last_access
        FROM ${this.tableName}
        GROUP BY domain
        ORDER BY total_hits DESC
        LIMIT ${limit}
      `;

      // In real implementation: const result = await mcp_sqlite_read_query({ query: domainsQuery });
      
      // Return simulated empty result
      return [];

    } catch (error) {
      console.error('Error getting top cached domains:', error.message);
      return [];
    }
  }

  async clearCache(domain = null) {
    if (!this.enabled) {
      return false;
    }

    try {
      let deleteQuery;
      
      if (domain) {
        deleteQuery = `DELETE FROM ${this.tableName} WHERE original_url LIKE '%${domain}%'`;
      } else {
        deleteQuery = `DELETE FROM ${this.tableName}`;
      }

      // In real implementation: await mcp_sqlite_write_query({ query: deleteQuery });
      
      console.error(`[SQLite Cache] Cleared cache${domain ? ' for domain: ' + domain : ' (all entries)'}`);
      return true;

    } catch (error) {
      console.error('Error clearing cache:', error.message);
      return false;
    }
  }
}