/**
 * Bulk scraping tool for processing multiple URLs
 */
import { chromium } from 'playwright';

export function createBulkScrapeTool() {
  return {
    async execute(args) {
      const { 
        urls, 
        concurrent_limit = 3, 
        delay_between_requests = 2 
      } = args;

      if (!Array.isArray(urls) || urls.length === 0) {
        return {
          content: [{
            type: 'text',
            text: 'Error: urls must be a non-empty array'
          }],
          isError: true
        };
      }

      console.error(`Starting bulk scrape of ${urls.length} URLs with concurrency ${concurrent_limit}`);

      const results = [];
      const errors = [];
      let processed = 0;

      // Process URLs in batches
      for (let i = 0; i < urls.length; i += concurrent_limit) {
        const batch = urls.slice(i, i + concurrent_limit);
        
        const batchPromises = batch.map(async (url, index) => {
          try {
            // Add delay between requests
            if (delay_between_requests > 0 && index > 0) {
              await this.sleep(delay_between_requests * 1000);
            }
            
            const result = await this.scrapeSingleUrl(url);
            processed++;
            console.error(`Processed ${processed}/${urls.length}: ${url}`);
            return result;
            
          } catch (error) {
            processed++;
            console.error(`Error ${processed}/${urls.length}: ${url} - ${error.message}`);
            errors.push({
              url,
              error: error.message,
              timestamp: new Date().toISOString()
            });
            return null;
          }
        });

        const batchResults = await Promise.all(batchPromises);
        results.push(...batchResults.filter(result => result !== null));

        // Delay between batches
        if (i + concurrent_limit < urls.length && delay_between_requests > 0) {
          await this.sleep(delay_between_requests * 1000);
        }
      }

      const summary = {
        total_urls: urls.length,
        successful: results.length,
        failed: errors.length,
        success_rate: `${((results.length / urls.length) * 100).toFixed(1)}%`,
        processed_at: new Date().toISOString()
      };

      return {
        content: [{
          type: 'text',
          text: `Bulk Scraping Results\n\n` +
                `Summary: ${summary.successful}/${summary.total_urls} URLs successful (${summary.success_rate})\n\n` +
                `Results:\n${JSON.stringify({ summary, results, errors }, null, 2)}`
        }]
      };
    },

    async scrapeSingleUrl(url) {
      const browser = await chromium.launch({ headless: true });
      const page = await browser.newPage();

      try {
        await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });

        const content = await page.evaluate(() => {
          // Remove unwanted elements
          const unwantedSelectors = [
            'script', 'style', 'nav', 'header', 'footer',
            '.advertisement', '.ads', '.sidebar'
          ];
          
          unwantedSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => el.remove());
          });

          // Find main content
          const mainContent = document.querySelector('main, .content, article, .main') || document.body;
          
          return {
            title: document.title,
            text: mainContent.textContent.trim(),
            html: mainContent.innerHTML,
            url: window.location.href
          };
        });

        await browser.close();

        return {
          url: content.url,
          title: content.title,
          content: content.text.substring(0, 5000), // Limit content length
          word_count: content.text.split(/\s+/).length,
          scraped_at: new Date().toISOString()
        };

      } catch (error) {
        await browser.close();
        throw error;
      }
    },

    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }
  };
}