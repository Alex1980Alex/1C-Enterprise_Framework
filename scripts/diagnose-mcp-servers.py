#!/usr/bin/env python3
"""Диагностика MCP серверов"""

import subprocess
import sys
import os
import time
import json

def test_server(name, command, args, cwd, env):
    """Тестирует запуск MCP сервера"""
    print(f"\n{'='*60}")
    print(f"Тестирование: {name}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print(f"Args: {args}")
    print(f"CWD: {cwd}")
    print(f"Env keys: {list(env.keys())}")

    try:
        # Объединяем переменные окружения
        full_env = os.environ.copy()
        full_env.update(env)

        # Запускаем процесс
        proc = subprocess.Popen(
            [command] + args,
            cwd=cwd,
            env=full_env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        # Даем серверу время на инициализацию
        time.sleep(2)

        # Отправляем инициализирующее сообщение MCP
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        try:
            proc.stdin.write(json.dumps(init_message) + "\n")
            proc.stdin.flush()

            # Ждем ответ
            time.sleep(1)

            # Проверяем статус процесса
            poll = proc.poll()
            if poll is None:
                print("✅ Сервер успешно запустился и ожидает команд")
                proc.terminate()
                proc.wait(timeout=5)
                return True
            else:
                print(f"❌ Сервер завершился с кодом: {poll}")
                stderr = proc.stderr.read()
                if stderr:
                    print(f"STDERR:\n{stderr}")
                return False

        except Exception as e:
            print(f"⚠️ Ошибка при отправке инициализирующего сообщения: {e}")
            proc.terminate()
            proc.wait(timeout=5)
            return False

    except FileNotFoundError:
        print(f"❌ Команда не найдена: {command}")
        return False
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
        return False

# Конфигурация серверов для тестирования
servers = [
    {
        "name": "1c-enterprise-database",
        "command": "C:\\Users\\AlexT\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
        "args": ["-m", "py_server", "stdio"],
        "cwd": "D:/1C-Enterprise_Framework/mcp-1c-integration/src",
        "env": {
            "PYTHONPATH": "D:/1C-Enterprise_Framework/mcp-1c-integration/src",
            "PYTHONIOENCODING": "utf-8",
            "MCP_ONEC_URL": "http://localhost/251017_GKSTCPLK-1794",
            "MCP_ONEC_USERNAME": "a.terletskiy@sodrugestvo.ru",
            "MCP_ONEC_PASSWORD": "1234",
            "MCP_ONEC_SERVICE_ROOT": "mcp",
            "MCP_LOG_LEVEL": "INFO"
        }
    },
    {
        "name": "docling",
        "command": "C:\\Users\\AlexT\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
        "args": ["server_enhanced.py"],
        "cwd": "D:/1C-Enterprise_Framework/mcp-docling-server",
        "env": {
            "PYTHONPATH": "D:/1C-Enterprise_Framework/mcp-docling-server",
            "PYTHONIOENCODING": "utf-8",
            "DOCLING_CACHE_DIR": "D:/1C-Enterprise_Framework/cache/docling",
            "DOCLING_LOG_LEVEL": "INFO"
        }
    },
    {
        "name": "1c-docs",
        "command": "C:\\Users\\AlexT\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
        "args": ["mcp_server.py"],
        "cwd": "D:/1C-Enterprise_Framework/scripts/docs-mcp",
        "env": {
            "PYTHONPATH": "D:/1C-Enterprise_Framework/scripts/docs-mcp",
            "PYTHONIOENCODING": "utf-8",
            "DOCS_ROOT": "D:/1C-Enterprise_Framework/Документация по фреймворку"
        }
    }
]

if __name__ == "__main__":
    print("Начало диагностики MCP серверов")
    print(f"Python версия: {sys.version}")

    results = {}
    for server in servers:
        results[server["name"]] = test_server(
            server["name"],
            server["command"],
            server["args"],
            server["cwd"],
            server["env"]
        )

    print(f"\n{'='*60}")
    print("РЕЗУЛЬТАТЫ")
    print(f"{'='*60}")
    for name, success in results.items():
        status = "✅ OK" if success else "❌ FAILED"
        print(f"{name}: {status}")
