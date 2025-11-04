#!/usr/bin/env node

/**
 * Universal Web Scraper MCP Server
 * Provides intelligent web scraping capabilities through MCP protocol
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';

// Import scraping tools
import { createScrapeTool } from './tools/scrape.js';
import { createAnalyzeTool } from './tools/analyze.js';
import { createBulkScrapeTool } from './tools/bulk_scrape.js';
import { createGetAdaptersTool } from './tools/get_adapters.js';

class UniversalScraperServer {
  constructor() {
    this.server = new Server(
      {
        name: 'universal-web-scraper',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  setupToolHandlers() {
    // Register available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'scrape_website',
            description: 'Scrape content from any website with intelligent adapter detection',
            inputSchema: {
              type: 'object',
              properties: {
                url: {
                  type: 'string',
                  description: 'URL to scrape'
                },
                adapter_type: {
                  type: 'string',
                  description: 'Force specific adapter (documentation, news, its_1c, generic)',
                  enum: ['documentation', 'news', 'its_1c', 'generic']
                },
                max_depth: {
                  type: 'number',
                  description: 'Maximum depth for recursive scraping (default: 1)',
                  default: 1
                },
                include_links: {
                  type: 'boolean',
                  description: 'Include found links in result (default: true)',
                  default: true
                },
                include_images: {
                  type: 'boolean',
                  description: 'Include found images in result (default: true)',
                  default: true
                },
                output_format: {
                  type: 'string',
                  description: 'Output format (markdown, html, text)',
                  enum: ['markdown', 'html', 'text'],
                  default: 'markdown'
                },
                save_to_memory: {
                  type: 'boolean',
                  description: 'Save results to Memory MCP (default: false)',
                  default: false
                },
                auth: {
                  type: 'object',
                  description: 'Authentication credentials if required',
                  properties: {
                    username: { type: 'string' },
                    password: { type: 'string' }
                  }
                }
              },
              required: ['url']
            }
          },
          {
            name: 'analyze_website_structure',
            description: 'Analyze website structure and suggest optimal scraping strategy',
            inputSchema: {
              type: 'object',
              properties: {
                url: {
                  type: 'string',
                  description: 'URL to analyze'
                },
                deep_analysis: {
                  type: 'boolean',
                  description: 'Perform deep structure analysis (default: false)',
                  default: false
                }
              },
              required: ['url']
            }
          },
          {
            name: 'bulk_scrape_websites',
            description: 'Scrape multiple websites in parallel with rate limiting',
            inputSchema: {
              type: 'object',
              properties: {
                urls: {
                  type: 'array',
                  items: { type: 'string' },
                  description: 'List of URLs to scrape'
                },
                concurrent_limit: {
                  type: 'number',
                  description: 'Maximum concurrent requests (default: 3)',
                  default: 3
                },
                delay_between_requests: {
                  type: 'number',
                  description: 'Delay between requests in seconds (default: 2)',
                  default: 2
                }
              },
              required: ['urls']
            }
          },
          {
            name: 'get_supported_adapters',
            description: 'Get list of supported website adapters and their capabilities',
            inputSchema: {
              type: 'object',
              properties: {}
            }
          }
        ]
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'scrape_website':
            return await createScrapeTool().execute(args);
          
          case 'analyze_website_structure':
            return await createAnalyzeTool().execute(args);
          
          case 'bulk_scrape_websites':
            return await createBulkScrapeTool().execute(args);
          
          case 'get_supported_adapters':
            return await createGetAdaptersTool().execute(args);
          
          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        if (error instanceof McpError) {
          throw error;
        }
        
        throw new McpError(
          ErrorCode.InternalError,
          `Error executing tool ${name}: ${error.message}`
        );
      }
    });
  }

  setupErrorHandling() {
    this.server.onerror = (error) => {
      console.error('[MCP Error]', error);
    };

    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Universal Web Scraper MCP Server running on stdio');
  }
}

// Start the server
const server = new UniversalScraperServer();
server.run().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});