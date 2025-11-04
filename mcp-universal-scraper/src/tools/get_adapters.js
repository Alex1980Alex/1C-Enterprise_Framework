/**
 * Tool для получения списка поддерживаемых адаптеров
 */
export function createGetAdaptersTool() {
  return {
    async execute(args) {
      const adapters = {
        documentation: {
          name: 'Documentation',
          description: 'Специализированный адаптер для документационных сайтов, API docs, wikis',
          patterns: ['docs.', 'documentation.', 'wiki.', 'help.', 'support.'],
          examples: ['docs.github.com', 'developer.mozilla.org', 'nodejs.org/docs'],
          features: ['Navigation extraction', 'Table of contents', 'Code blocks', 'API references']
        },
        news: {
          name: 'News & Blogs',
          description: 'Адаптер для новостных сайтов и блогов',
          patterns: ['news.', 'blog.', 'press.', 'media.'],
          examples: ['habr.com', 'tass.ru', 'rbc.ru'],
          features: ['Article metadata', 'Author extraction', 'Publication date', 'Categories/tags']
        },
        its_1c: {
          name: '1C ITS Portal',
          description: 'Специализированный адаптер для портала its.1c.ru',
          patterns: ['its.1c.ru'],
          examples: ['its.1c.ru/docs/', 'its.1c.ru/articles/'],
          features: ['1C documentation', 'Code examples', 'File attachments', 'Question/Answer format']
        },
        ecommerce: {
          name: 'E-commerce',
          description: 'Адаптер для интернет-магазинов и каталогов товаров',
          patterns: ['shop.', 'store.', 'market.', 'catalog.'],
          examples: ['ozon.ru', 'market.yandex.ru', 'wildberries.ru'],
          features: ['Product details', 'Prices', 'Specifications', 'Reviews', 'Images']
        },
        generic: {
          name: 'Generic',
          description: 'Универсальный адаптер для любых веб-сайтов',
          patterns: ['*'],
          examples: ['example.com', 'любой сайт'],
          features: ['Basic content extraction', 'Fallback option', 'Clean text output']
        }
      };

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              adapters,
              total: Object.keys(adapters).length,
              usage: 'Используйте adapter_type в scrape_website для принудительного выбора адаптера'
            }, null, 2)
          }
        ]
      };
    }
  };
}