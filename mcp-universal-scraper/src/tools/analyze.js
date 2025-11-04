/**
 * Website structure analysis tool
 */
import { chromium } from 'playwright';

export function createAnalyzeTool() {
  return {
    async execute(args) {
      const { url, deep_analysis = false } = args;

      try {
        console.error(`Analyzing website structure: ${url}`);
        
        const browser = await chromium.launch({ headless: true });
        const page = await browser.newPage();
        
        await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
        
        const analysis = await page.evaluate((deepAnalysis) => {
          const result = {
            domain: window.location.hostname,
            protocol: window.location.protocol,
            title: document.title,
            description: '',
            structure: {
              hasNavigation: false,
              hasHeader: false,
              hasFooter: false,
              hasSidebar: false,
              hasMainContent: false,
              hasArticles: false,
              hasForms: false
            },
            content: {
              totalElements: document.querySelectorAll('*').length,
              textLength: document.body.textContent.length,
              linkCount: document.querySelectorAll('a[href]').length,
              imageCount: document.querySelectorAll('img[src]').length,
              formCount: document.querySelectorAll('form').length
            },
            technology: {
              frameworks: [],
              hasJavaScript: !!document.querySelector('script'),
              hasCSS: !!document.querySelector('link[rel="stylesheet"], style'),
              viewport: document.querySelector('meta[name="viewport"]')?.getAttribute('content') || 'not-set'
            },
            seo: {
              metaDescription: '',
              metaKeywords: '',
              ogTitle: '',
              ogDescription: '',
              hasH1: !!document.querySelector('h1'),
              headingStructure: {}
            }
          };

          // Meta description
          const metaDesc = document.querySelector('meta[name="description"]');
          if (metaDesc) result.seo.metaDescription = metaDesc.getAttribute('content');
          
          // Meta keywords
          const metaKeywords = document.querySelector('meta[name="keywords"]');
          if (metaKeywords) result.seo.metaKeywords = metaKeywords.getAttribute('content');

          // Open Graph
          const ogTitle = document.querySelector('meta[property="og:title"]');
          if (ogTitle) result.seo.ogTitle = ogTitle.getAttribute('content');
          
          const ogDesc = document.querySelector('meta[property="og:description"]');
          if (ogDesc) result.seo.ogDescription = ogDesc.getAttribute('content');

          // Structure analysis
          result.structure.hasNavigation = !!document.querySelector('nav, .nav, .navigation, #navigation');
          result.structure.hasHeader = !!document.querySelector('header, .header, #header');
          result.structure.hasFooter = !!document.querySelector('footer, .footer, #footer');
          result.structure.hasSidebar = !!document.querySelector('.sidebar, .side-bar, aside, #sidebar');
          result.structure.hasMainContent = !!document.querySelector('main, .main, #main, .content, #content');
          result.structure.hasArticles = !!document.querySelector('article, .article, .post');
          result.structure.hasForms = result.content.formCount > 0;

          // Heading structure
          for (let i = 1; i <= 6; i++) {
            const headings = document.querySelectorAll(`h${i}`);
            if (headings.length > 0) {
              result.seo.headingStructure[`h${i}`] = headings.length;
            }
          }

          // Framework detection
          if (window.React) result.technology.frameworks.push('React');
          if (window.Vue) result.technology.frameworks.push('Vue.js');
          if (window.angular) result.technology.frameworks.push('Angular');
          if (window.jQuery || window.$) result.technology.frameworks.push('jQuery');

          // Deep analysis
          if (deepAnalysis) {
            result.deepAnalysis = {
              selectors: {
                navigation: this.findBestSelectors(['nav', '.nav', '.navigation', '#navigation']),
                content: this.findBestSelectors(['main', '.main', '.content', 'article', '.post']),
                title: this.findBestSelectors(['h1', '.title', '.page-title', '.post-title']),
                sidebar: this.findBestSelectors(['.sidebar', 'aside', '.side-nav'])
              },
              recommendations: []
            };

            // Add recommendations
            if (!result.seo.metaDescription) {
              result.deepAnalysis.recommendations.push('Добавить meta description для SEO');
            }
            if (!result.structure.hasMainContent) {
              result.deepAnalysis.recommendations.push('Рекомендуется использовать семантический тег <main>');
            }
            if (Object.keys(result.seo.headingStructure).length === 0) {
              result.deepAnalysis.recommendations.push('Добавить заголовки (h1-h6) для структуры контента');
            }
          }

          return result;
        }, deep_analysis);

        await browser.close();

        // Determine suggested scraping strategy
        const strategy = this.suggestScrapingStrategy(analysis);

        const result = {
          url,
          analysis,
          strategy,
          analyzed_at: new Date().toISOString()
        };

        return {
          content: [{
            type: 'text',
            text: JSON.stringify(result, null, 2)
          }]
        };

      } catch (error) {
        console.error(`Analysis error for ${url}:`, error);
        
        return {
          content: [{
            type: 'text',
            text: `Error analyzing ${url}: ${error.message}`
          }],
          isError: true
        };
      }
    },

    suggestScrapingStrategy(analysis) {
      const strategy = {
        recommendedAdapter: 'generic',
        confidence: 0.5,
        selectors: {
          title: ['h1', 'title'],
          content: ['main', '.content', 'article'],
          navigation: ['nav', '.nav']
        },
        crawling: {
          recommended: false,
          maxDepth: 1,
          respectRobots: true
        },
        notes: []
      };

      // Determine best adapter
      if (analysis.domain.includes('docs') || analysis.structure.hasNavigation) {
        strategy.recommendedAdapter = 'documentation';
        strategy.confidence = 0.8;
        strategy.crawling.recommended = true;
        strategy.crawling.maxDepth = 3;
        strategy.notes.push('Detected documentation site - recommend recursive crawling');
      } else if (analysis.structure.hasArticles) {
        strategy.recommendedAdapter = 'news';
        strategy.confidence = 0.7;
        strategy.notes.push('Detected blog/news structure');
      } else if (analysis.domain.includes('its.1c.ru')) {
        strategy.recommendedAdapter = 'its_1c';
        strategy.confidence = 0.9;
        strategy.notes.push('Detected 1C ITS portal');
      }

      // Suggest selectors based on analysis
      if (analysis.structure.hasMainContent) {
        strategy.selectors.content.unshift('main');
      }
      if (analysis.seo.hasH1) {
        strategy.selectors.title.unshift('h1');
      }

      // Performance recommendations
      if (analysis.content.totalElements > 1000) {
        strategy.notes.push('Large page detected - consider selective element extraction');
      }
      if (analysis.content.linkCount > 100) {
        strategy.notes.push('Many links found - good candidate for crawling');
        strategy.crawling.recommended = true;
      }

      return strategy;
    }
  };
}