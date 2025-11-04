/**
 * Enhanced scraping tool with MCP integrations
 * Includes Memory MCP, Docling MCP, and SQLite Cache
 */

import { chromium } from 'playwright';
import * as cheerio from 'cheerio';
import TurndownService from 'turndown';
import urlParse from 'url-parse';
import { MemoryMCPIntegration } from '../integrations/memory_mcp.js';
import { DoclingMCPIntegration } from '../integrations/docling_mcp.js';
import { SQLiteCacheIntegration } from '../integrations/sqlite_cache.js';

export function createEnhancedScrapeTool() {
  const turndownService = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced'
  });

  // Initialize integrations
  const memoryMCP = new MemoryMCPIntegration();
  const doclingMCP = new DoclingMCPIntegration();
  const sqliteCache = new SQLiteCacheIntegration();

  return {
    async execute(args) {
      const {
        url,
        adapter_type,
        max_depth = 1,
        include_links = true,
        include_images = true,
        output_format = 'markdown',
        save_to_memory = false,
        use_cache = true,
        auth
      } = args;

      try {
        console.error(`Starting enhanced scrape of: ${url}`);
        
        // 1. Check if it's a document that needs Docling
        if (doclingMCP.isDocumentUrl(url)) {
          console.error('Document detected, using Docling MCP...');
          return await this.handleDocumentScraping(url, args);
        }

        // 2. Check cache first
        const detectedAdapter = adapter_type || await this.quickDetectSiteType(url);
        
        if (use_cache && sqliteCache.enabled) {
          const cachedResult = await sqliteCache.getCachedContent(url, detectedAdapter, args);
          if (cachedResult) {
            return await this.formatCachedResult(cachedResult, save_to_memory);
          }
        }

        // 3. Perform fresh scraping
        const scrapingResult = await this.performFreshScraping(url, detectedAdapter, args);

        // 4. Save to cache
        if (use_cache && sqliteCache.enabled && scrapingResult.success) {
          await sqliteCache.saveCachedContent(url, detectedAdapter, scrapingResult, args);
        }

        // 5. Save to Memory MCP if requested
        if (save_to_memory && memoryMCP.enabled && scrapingResult.success) {
          await memoryMCP.saveScrapedContent({
            ...scrapingResult,
            adapter_used: detectedAdapter
          });
        }

        // 6. Format and return result
        return await this.formatFinalResult(scrapingResult, detectedAdapter);

      } catch (error) {
        console.error(`Enhanced scraping error for ${url}:`, error);
        
        return {
          content: [{
            type: 'text',
            text: `Error in enhanced scraping ${url}: ${error.message}`
          }],
          isError: true
        };
      }
    },

    async handleDocumentScraping(url, args) {
      try {
        const conversionResult = await doclingMCP.convertDocument(url, {
          extract_images: args.include_images,
          ocr_enabled: true
        });

        if (args.save_to_memory && memoryMCP.enabled) {
          await memoryMCP.saveScrapedContent({
            ...conversionResult,
            adapter_used: 'docling_mcp'
          });
        }

        return {
          content: [{
            type: 'text',
            text: `Successfully converted document: ${url}\\n\\n` +
                  `Title: ${conversionResult.title}\\n` +
                  `Format: ${conversionResult.metadata.original_format}\\n` +
                  `Pages: ${conversionResult.metadata.pages_processed}\\n` +
                  `Images: ${conversionResult.metadata.images_extracted}\\n` +
                  `Tables: ${conversionResult.metadata.tables_extracted}\\n\\n` +
                  `Content:\\n${conversionResult.content}`
          }]
        };

      } catch (error) {
        return {
          content: [{
            type: 'text',
            text: `Error converting document ${url}: ${error.message}`
          }],
          isError: true
        };
      }
    },

    async formatCachedResult(cachedResult, saveToMemory) {
      let statusText = `Retrieved from cache: ${cachedResult.url}\\n\\n` +
                      `Cache age: ${Math.round(cachedResult.cache_age / 1000 / 60)} minutes\\n` +
                      `Hit count: ${cachedResult.cache_hit_count}\\n` +
                      `Content length: ${cachedResult.content.length} characters\\n\\n` +
                      `Content:\\n${cachedResult.content}`;

      if (saveToMemory && memoryMCP.enabled) {
        await memoryMCP.saveScrapedContent({
          ...cachedResult,
          adapter_used: 'cached_content'
        });
        statusText += '\\n\\n✅ Saved to Memory MCP';
      }

      return {
        content: [{
          type: 'text',
          text: statusText
        }]
      };
    },

    async performFreshScraping(url, adapter_type, args) {
      // This is the original scraping logic
      const browser = await chromium.launch({ headless: true });
      const context = await browser.newContext({
        userAgent: 'Universal Web Scraper 1.0 (Enhanced MCP Integration)'
      });
      const page = await context.newPage();

      try {
        await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });

        if (args.auth && args.auth.username && args.auth.password) {
          await this.handleAuthentication(page, args.auth);
        }

        const siteType = adapter_type || await this.detectSiteType(page, url);
        const adapter = this.getAdapter(siteType);
        const rawContent = await adapter.extract(page, url);

        let processedContent;
        switch (args.output_format) {
          case 'markdown':
            processedContent = turndownService.turndown(rawContent.html);
            break;
          case 'html':
            processedContent = rawContent.html;
            break;
          case 'text':
            processedContent = rawContent.text;
            break;
          default:
            processedContent = turndownService.turndown(rawContent.html);
        }

        const links = args.include_links ? await this.extractLinks(page, url) : [];
        const images = args.include_images ? await this.extractImages(page, url) : [];

        return {
          url,
          title: rawContent.title,
          content: processedContent,
          metadata: {
            scraped_at: new Date().toISOString(),
            content_length: processedContent.length,
            links_found: links.length,
            images_found: images.length,
            cache_enabled: true
          },
          links: links.slice(0, 50),
          images: images.slice(0, 20),
          success: true
        };

      } finally {
        await browser.close();
      }
    },

    async formatFinalResult(scrapingResult, adapterUsed) {
      let statusText = `Successfully scraped: ${scrapingResult.url}\\n\\n` +
                      `Title: ${scrapingResult.title}\\n` +
                      `Adapter: ${adapterUsed}\\n` +
                      `Content length: ${scrapingResult.metadata.content_length} characters\\n` +
                      `Links found: ${scrapingResult.metadata.links_found}\\n` +
                      `Images found: ${scrapingResult.metadata.images_found}\\n`;

      // Add integration status
      const integrations = [];
      if (sqliteCache.enabled) integrations.push('SQLite Cache');
      if (memoryMCP.enabled) integrations.push('Memory MCP');
      if (doclingMCP.enabled) integrations.push('Docling MCP');
      
      if (integrations.length > 0) {
        statusText += `Integrations: ${integrations.join(', ')}\\n`;
      }

      statusText += `\\nContent:\\n${scrapingResult.content}`;

      return {
        content: [{
          type: 'text',
          text: statusText
        }]
      };
    },

    async quickDetectSiteType(url) {
      // Quick detection without loading the page
      const domain = urlParse(url).hostname;
      
      if (domain.includes('its.1c.ru')) return 'its_1c';
      if (domain.includes('docs.') || domain.includes('documentation')) return 'documentation';
      if (domain.includes('news') || domain.includes('habr') || domain.includes('medium')) return 'news';
      
      return 'generic';
    },

    // Include all the original helper methods
    async handleAuthentication(page, auth) {
      try {
        const usernameSelector = 'input[name*="user"], input[name*="login"], input[name*="email"], #username, #login';
        const passwordSelector = 'input[name*="pass"], input[name*="password"], #password';
        const submitSelector = 'input[type="submit"], button[type="submit"], button:has-text("Войти"), button:has-text("Login")';

        await page.fill(usernameSelector, auth.username);
        await page.fill(passwordSelector, auth.password);
        await page.click(submitSelector);
        await page.waitForLoadState('networkidle', { timeout: 10000 });
        
        console.error('Authentication completed');
      } catch (error) {
        console.error('Authentication failed:', error.message);
      }
    },

    async detectSiteType(page, url) {
      try {
        const domain = urlParse(url).hostname;
        
        if (domain.includes('its.1c.ru')) return 'its_1c';
        if (domain.includes('docs.') || domain.includes('documentation')) return 'documentation';
        if (domain.includes('news') || domain.includes('habr') || domain.includes('medium')) return 'news';
        
        const indicators = await page.evaluate(() => {
          const classes = document.documentElement.className;
          const bodyClasses = document.body ? document.body.className : '';
          const hasDocNav = !!document.querySelector('.doc-nav, .toc, .documentation, .api-docs');
          const hasArticles = !!document.querySelector('article, .post, .news-item');
          const hasProducts = !!document.querySelector('.product, .item, .catalog');
          
          return {
            classes: classes + ' ' + bodyClasses,
            hasDocNav,
            hasArticles,
            hasProducts
          };
        });

        if (indicators.hasDocNav) return 'documentation';
        if (indicators.hasArticles) return 'news';
        if (indicators.hasProducts) return 'ecommerce';
        
        return 'generic';
      } catch (error) {
        console.error('Site type detection failed:', error);
        return 'generic';
      }
    },

    getAdapter(siteType) {
      const adapters = {
        documentation: {
          async extract(page, url) {
            const content = await page.evaluate(() => {
              const selectors = [
                'main .content',
                '.documentation',
                '.doc-content',
                '.article-body',
                '.content',
                '#content'
              ];
              
              let element;
              for (const selector of selectors) {
                element = document.querySelector(selector);
                if (element) break;
              }
              
              if (!element) {
                element = document.querySelector('main') || document.body;
              }
              
              return {
                title: document.title,
                html: element.innerHTML,
                text: element.textContent
              };
            });
            
            return content;
          }
        },

        news: {
          async extract(page, url) {
            const content = await page.evaluate(() => {
              const selectors = [
                'article',
                '.post-content',
                '.article-body',
                '.news-content',
                '.content'
              ];
              
              let element;
              for (const selector of selectors) {
                element = document.querySelector(selector);
                if (element) break;
              }
              
              if (!element) {
                element = document.querySelector('main') || document.body;
              }
              
              return {
                title: document.title,
                html: element.innerHTML,
                text: element.textContent
              };
            });
            
            return content;
          }
        },

        its_1c: {
          async extract(page, url) {
            const content = await page.evaluate(() => {
              const contentElement = document.querySelector('.content-area, .doc-content, main') || document.body;
              
              return {
                title: document.title,
                html: contentElement.innerHTML,
                text: contentElement.textContent
              };
            });
            
            return content;
          }
        },

        generic: {
          async extract(page, url) {
            const content = await page.evaluate(() => {
              const elementsToRemove = [
                'nav', 'header', 'footer', 
                '.nav', '.navigation', '.sidebar', 
                '.menu', '.ads', '.advertisement'
              ];
              
              elementsToRemove.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => el.remove());
              });
              
              const mainElement = document.querySelector('main, #main, .main, .content, article') || document.body;
              
              return {
                title: document.title,
                html: mainElement.innerHTML,
                text: mainElement.textContent
              };
            });
            
            return content;
          }
        }
      };

      return adapters[siteType] || adapters.generic;
    },

    async extractLinks(page, baseUrl) {
      return await page.evaluate((baseUrl) => {
        const links = [];
        const linkElements = document.querySelectorAll('a[href]');
        
        linkElements.forEach(link => {
          const href = link.getAttribute('href');
          const text = link.textContent.trim();
          
          if (href && text) {
            try {
              const absoluteUrl = new URL(href, baseUrl).toString();
              links.push({
                url: absoluteUrl,
                text: text.substring(0, 100)
              });
            } catch (error) {
              // Invalid URL, skip
            }
          }
        });
        
        return links;
      }, baseUrl);
    },

    async extractImages(page, baseUrl) {
      return await page.evaluate((baseUrl) => {
        const images = [];
        const imgElements = document.querySelectorAll('img[src]');
        
        imgElements.forEach(img => {
          const src = img.getAttribute('src');
          const alt = img.getAttribute('alt') || '';
          
          if (src) {
            try {
              const absoluteUrl = new URL(src, baseUrl).toString();
              images.push({
                url: absoluteUrl,
                alt: alt.substring(0, 100)
              });
            } catch (error) {
              // Invalid URL, skip
            }
          }
        });
        
        return images;
      }, baseUrl);
    }
  };
}