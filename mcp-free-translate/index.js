#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import translate from '@vitalets/google-translate-api';
import { fixLayout, convertLayout, detectLayout } from './keyboard-layouts.js';

const server = new Server(
  {
    name: 'free-translate',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'translate',
        description: 'Translate text using free Google Translate API',
        inputSchema: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'Text to translate',
            },
            to: {
              type: 'string',
              description: 'Target language code (e.g., "ru", "en", "es")',
              default: 'en',
            },
            from: {
              type: 'string',
              description: 'Source language code (auto-detected if not specified)',
              default: 'auto',
            },
          },
          required: ['text'],
        },
      },
      {
        name: 'translate_to_russian',
        description: 'Quick translate to Russian',
        inputSchema: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'Text to translate to Russian',
            },
          },
          required: ['text'],
        },
      },
      {
        name: 'translate_to_english',
        description: 'Quick translate to English',
        inputSchema: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'Text to translate to English',
            },
          },
          required: ['text'],
        },
      },
      {
        name: 'fix_keyboard_layout',
        description: 'Fix text typed in wrong keyboard layout (e.g., "lf" -> "да", "ghbdtn" -> "привет")',
        inputSchema: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'Text to fix (typed in wrong layout)',
            },
            target_layout: {
              type: 'string',
              description: 'Target layout: "en", "ru", or "auto" (default)',
              default: 'auto',
              enum: ['auto', 'en', 'ru'],
            },
          },
          required: ['text'],
        },
      },
      {
        name: 'convert_keyboard_layout',
        description: 'Convert text from one keyboard layout to another',
        inputSchema: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'Text to convert',
            },
            from_layout: {
              type: 'string',
              description: 'Source layout',
              enum: ['en', 'ru'],
            },
            to_layout: {
              type: 'string',
              description: 'Target layout',
              enum: ['en', 'ru'],
            },
          },
          required: ['text', 'from_layout', 'to_layout'],
        },
      },
      {
        name: 'detect_keyboard_layout',
        description: 'Detect keyboard layout of the text',
        inputSchema: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'Text to analyze',
            },
          },
          required: ['text'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'translate': {
        const { text, to = 'en', from = 'auto' } = args;

        const result = await translate(text, { to, from });

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                original: text,
                translated: result.text,
                from: result.from.language.iso,
                to: to,
                confidence: result.from.language.confidence,
              }, null, 2),
            },
          ],
        };
      }

      case 'translate_to_russian': {
        const { text } = args;

        const result = await translate(text, { to: 'ru' });

        return {
          content: [
            {
              type: 'text',
              text: `Перевод: ${result.text}`,
            },
          ],
        };
      }

      case 'translate_to_english': {
        const { text } = args;

        const result = await translate(text, { to: 'en' });

        return {
          content: [
            {
              type: 'text',
              text: `Translation: ${result.text}`,
            },
          ],
        };
      }

      case 'fix_keyboard_layout': {
        const { text, target_layout = 'auto' } = args;

        const result = fixLayout(text, target_layout);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                original: text,
                corrected: result.corrected,
                from_layout: result.from,
                to_layout: result.to,
                confidence: result.confidence,
                message: result.message || 'Layout fixed successfully',
              }, null, 2),
            },
          ],
        };
      }

      case 'convert_keyboard_layout': {
        const { text, from_layout, to_layout } = args;

        const converted = convertLayout(text, from_layout, to_layout);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                original: text,
                converted: converted,
                from_layout: from_layout,
                to_layout: to_layout,
              }, null, 2),
            },
          ],
        };
      }

      case 'detect_keyboard_layout': {
        const { text } = args;

        const detected = detectLayout(text);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                text: text,
                detected_layout: detected,
              }, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Translation error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Free Translate MCP server running on stdio');
}

main().catch((error) => {
  console.error('Server failed to start:', error);
  process.exit(1);
});