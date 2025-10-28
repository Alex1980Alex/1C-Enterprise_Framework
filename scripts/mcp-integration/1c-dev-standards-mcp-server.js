#!/usr/bin/env node

/**
 * 1C Development Standards MCP Server
 * Запускает Python MCP сервер для документации по стандартам разработки 1C
 */

const { spawn } = require('child_process');
const path = require('path');

// Настройка путей
const PYTHON_PATH = 'C:\\Users\\AlexT\\AppData\\Local\\Programs\\Python\\Python313\\python.exe';
const DOCS_MCP_PATH = path.join(__dirname, '..', 'docs-mcp', 'mcp_server.py');
const DOCS_ROOT = 'D:/1C-Enterprise_Framework/Документация разработчика';

// Настройка переменных окружения
const env = {
    ...process.env,
    PYTHONIOENCODING: 'utf-8',
    DOCS_ROOT: DOCS_ROOT,
    PYTHONPATH: path.join(__dirname, '..', 'docs-mcp'),
};

// Запуск Python MCP сервера
const pythonProcess = spawn(PYTHON_PATH, [DOCS_MCP_PATH], {
    env: env,
    stdio: 'inherit',
    shell: false,
});

// Обработка ошибок
pythonProcess.on('error', (error) => {
    console.error('[1c-dev-standards] Ошибка запуска Python процесса:', error);
    process.exit(1);
});

pythonProcess.on('exit', (code) => {
    if (code !== 0) {
        console.error(`[1c-dev-standards] Python процесс завершился с кодом ${code}`);
        process.exit(code);
    }
});

// Обработка сигналов завершения
process.on('SIGINT', () => {
    pythonProcess.kill('SIGINT');
});

process.on('SIGTERM', () => {
    pythonProcess.kill('SIGTERM');
});
