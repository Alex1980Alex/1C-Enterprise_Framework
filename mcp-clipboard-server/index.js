#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError
} from '@modelcontextprotocol/sdk/types.js';
import clipboardy from 'clipboardy';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class ClipboardServer {
  constructor() {
    this.server = new Server(
      {
        name: 'clipboard-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();

    // Error handling
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'clipboard_get_text',
            description: 'Получить текст из буфера обмена',
            inputSchema: {
              type: 'object',
              properties: {},
              required: [],
            },
          },
          {
            name: 'clipboard_set_text',
            description: 'Записать текст в буфер обмена',
            inputSchema: {
              type: 'object',
              properties: {
                text: {
                  type: 'string',
                  description: 'Текст для записи в буфер обмена',
                },
              },
              required: ['text'],
            },
          },
          {
            name: 'clipboard_get_image',
            description: 'Получить изображение из буфера обмена и сохранить во временный файл',
            inputSchema: {
              type: 'object',
              properties: {
                filename: {
                  type: 'string',
                  description: 'Имя файла для сохранения (необязательно)',
                },
              },
              required: [],
            },
          },
        ],
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      try {
        const { name, arguments: args } = request.params;

        switch (name) {
          case 'clipboard_get_text':
            return await this.getClipboardText();

          case 'clipboard_set_text':
            return await this.setClipboardText(args.text);

          case 'clipboard_get_image':
            return await this.getClipboardImage(args.filename);

          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        console.error('Tool error:', error);
        throw new McpError(
          ErrorCode.InternalError,
          `Tool execution failed: ${error.message}`
        );
      }
    });
  }

  async getClipboardText() {
    try {
      const text = await clipboardy.read();
      return {
        content: [
          {
            type: 'text',
            text: `Текст из буфера обмена:\n${text}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Не удалось прочитать текст из буфера обмена: ${error.message}`);
    }
  }

  async setClipboardText(text) {
    try {
      await clipboardy.write(text);
      return {
        content: [
          {
            type: 'text',
            text: `Текст успешно записан в буфер обмена: ${text.substring(0, 100)}${text.length > 100 ? '...' : ''}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Не удалось записать текст в буфер обмена: ${error.message}`);
    }
  }

  async getClipboardImage(filename) {
    try {
      // Используем PowerShell для получения изображения из буфера обмена
      const { spawn } = await import('child_process');
      const { promisify } = await import('util');

      const tempDir = process.env.TEMP || '/tmp';
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const imageFileName = filename || `clipboard_image_${timestamp}.png`;
      const imagePath = path.join(tempDir, imageFileName);

      return new Promise((resolve, reject) => {
        const ps = spawn('powershell', [
          '-Command',
          `
          Add-Type -AssemblyName System.Windows.Forms;
          Add-Type -AssemblyName System.Drawing;
          if ([System.Windows.Forms.Clipboard]::ContainsImage()) {
            $img = [System.Windows.Forms.Clipboard]::GetImage();
            $img.Save('${imagePath.replace(/\\/g, '\\\\')}', [System.Drawing.Imaging.ImageFormat]::Png);
            Write-Output 'SUCCESS: Image saved to ${imagePath}';
          } else {
            Write-Output 'ERROR: No image found in clipboard';
          }
          `
        ], { stdio: 'pipe' });

        let output = '';
        let errorOutput = '';

        ps.stdout.on('data', (data) => {
          output += data.toString();
        });

        ps.stderr.on('data', (data) => {
          errorOutput += data.toString();
        });

        ps.on('close', (code) => {
          if (code === 0 && output.includes('SUCCESS')) {
            // Возвращаем только текстовую информацию о пути к файлу
            resolve({
              content: [
                {
                  type: 'text',
                  text: `📸 Изображение успешно сохранено!\n\n📂 Путь к файлу:\n${imagePath}\n\n✅ Теперь вы можете использовать этот файл в Claude Code с помощью команды Read.`,
                },
              ],
            });
          } else if (output.includes('ERROR: No image found')) {
            resolve({
              content: [
                {
                  type: 'text',
                  text: `❌ В буфере обмена нет изображения.\n\n📝 Подсказка:\n1. Скопируйте изображение (Ctrl+C или через контекстное меню)\n2. Запустите команду /clipboard-image снова`,
                },
              ],
            });
          } else {
            reject(new Error(`Не удалось получить изображение из буфера обмена: ${errorOutput || output}`));
          }
        });
      });
    } catch (error) {
      throw new Error(`Ошибка при получении изображения: ${error.message}`);
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('MCP Clipboard Server running on stdio');
  }
}

const server = new ClipboardServer();
server.run().catch(console.error);