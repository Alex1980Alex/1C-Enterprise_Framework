/**
 * Main scraping tool for Universal Web Scraper
 * Integrates with existing MCP servers (Playwright, Memory, Docling)
 */

import { chromium } from 'playwright';
import * as cheerio from 'cheerio';
import TurndownService from 'turndown';
import urlParse from 'url-parse';

export function createScrapeTool() {
  const turndownService = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced'
  });

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
        auth
      } = args;

      try {
        console.error(`Starting scrape of: ${url}`);
        
        // 1. Launch browser
        const browser = await chromium.launch({ headless: true });
        const context = await browser.newContext({
          userAgent: 'Universal Web Scraper 1.0 (MCP Integration)'
        });
        const page = await context.newPage();

        // 2. Navigate to URL
        await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });

        // 3. Handle authentication if provided
        if (auth && auth.username && auth.password) {
          await this.handleAuthentication(page, auth);
        }

        // 4. Detect site type and select adapter
        const siteType = adapter_type || await this.detectSiteType(page, url);
        console.error(`Detected site type: ${siteType}`);

        // 5. Extract content using appropriate adapter
        const adapter = this.getAdapter(siteType);
        const rawContent = await adapter.extract(page, url);

        // 6. Process content based on output format
        let processedContent;
        switch (output_format) {
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

        // 7. Extract additional data
        const links = include_links ? await this.extractLinks(page, url) : [];
        const images = include_images ? await this.extractImages(page, url) : [];

        // 8. Close browser
        await browser.close();

        // 9. Prepare result
        const result = {
          url,
          title: rawContent.title,
          content: processedContent,
          adapter_used: siteType,
          metadata: {
            scraped_at: new Date().toISOString(),
            content_length: processedContent.length,
            links_found: links.length,
            images_found: images.length
          },
          links: links.slice(0, 50), // Limit to first 50 links
          images: images.slice(0, 20) // Limit to first 20 images
        };

        // 10. Save to Memory MCP if requested
        if (save_to_memory) {
          await this.saveToMemory(result);
        }

        return {
          content: [{
            type: 'text',
            text: `Successfully scraped: ${url}\n\n` +
                  `Title: ${result.title}\n` +
                  `Adapter: ${result.adapter_used}\n` +
                  `Content length: ${result.metadata.content_length} characters\n` +
                  `Links found: ${result.metadata.links_found}\n` +
                  `Images found: ${result.metadata.images_found}\n\n` +
                  `Content:\n${result.content}`
          }]
        };

      } catch (error) {
        console.error(`Scraping error for ${url}:`, error);
        
        return {
          content: [{
            type: 'text',
            text: `Error scraping ${url}: ${error.message}`
          }],
          isError: true
        };
      }
    },

    async handleAuthentication(page, auth) {
      // Basic authentication handling
      // Look for common login form patterns
      try {
        const usernameSelector = 'input[name*="user"], input[name*="login"], input[name*="email"], #username, #login';
        const passwordSelector = 'input[name*="pass"], input[name*="password"], #password';
        const submitSelector = 'input[type="submit"], button[type="submit"], button:has-text("Войти"), button:has-text("Login")';

        await page.fill(usernameSelector, auth.username);
        await page.fill(passwordSelector, auth.password);
        await page.click(submitSelector);
        
        // Wait for navigation after login
        await page.waitForLoadState('networkidle', { timeout: 10000 });
        
        console.error('Authentication completed');
      } catch (error) {
        console.error('Authentication failed:', error.message);
      }
    },

    async detectSiteType(page, url) {
      try {
        const domain = urlParse(url).hostname;
        
        // Check for known domains
        if (domain.includes('its.1c.ru')) return 'its_1c';
        if (domain.includes('docs.') || domain.includes('documentation')) return 'documentation';
        if (domain.includes('news') || domain.includes('habr') || domain.includes('medium')) return 'news';
        
        // Analyze page structure
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
              // Try multiple selectors for documentation sites
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
              // Специфичные селекторы для its.1c.ru
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
              // Remove navigation, sidebar, footer
              const elementsToRemove = [
                'nav', 'header', 'footer', 
                '.nav', '.navigation', '.sidebar', 
                '.menu', '.ads', '.advertisement'
              ];
              
              elementsToRemove.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => el.remove());
              });
              
              // Find main content
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
                text: text.substring(0, 100) // Limit text length
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
                alt: alt.substring(0, 100) // Limit alt text length
              });
            } catch (error) {
              // Invalid URL, skip
            }
          }
        });
        
        return images;
      }, baseUrl);
    },

    async saveToMemory(result) {
      // Integration with Memory MCP would go here
      // For now, just log that we would save to memory
      console.error(`Would save to Memory MCP: ${result.title} (${result.metadata.content_length} chars)`);
    }
  };
}