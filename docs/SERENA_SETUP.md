# Настройка Serena MCP для Claude Desktop

## Проблема
Оригинальный Serena требует Python 3.11/3.12, но у вас установлен Python 3.13.

## Решение
Создан упрощенный MCP сервер `simple_serena_mcp.py` с базовой функциональностью Serena.

## Возможности сервера

1. **read_file** - Чтение файлов (UTF-8 и CP1251)
2. **list_directory** - Просмотр содержимого директорий
3. **search_files** - Поиск по файлам с поддержкой фильтров по типам
4. **write_file** - Запись файлов
5. **execute_command** - Выполнение системных команд

## Настройка Claude Desktop

1. Откройте файл конфигурации Claude Desktop:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Добавьте следующую конфигурацию:

```json
{
  "mcpServers": {
    "serena": {
      "command": "python",
      "args": [
        "D:\\1C-Enterprise_Framework\\simple_serena_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "D:\\1C-Enterprise_Framework"
      }
    }
  }
}
```

3. Перезапустите Claude Desktop

## Проверка работы

Сервер работает корректно - отвечает на запросы инициализации.

## Использование в Claude

После настройки в Claude Desktop вы сможете использовать команды:

- Читать файлы: "Прочитай файл config.py"
- Искать в проекте: "Найди все функции с именем 'get_data'"
- Выполнять команды: "Запусти тесты проекта"
- Работать с директориями: "Покажи содержимое папки src/"

## Файлы проекта

- `simple_serena_mcp.py` - Основной MCP сервер
- `claude_serena_config.json` - Пример конфигурации
- `SERENA_SETUP.md` - Данная инструкция
