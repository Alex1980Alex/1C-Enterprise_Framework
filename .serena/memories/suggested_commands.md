# Рекомендуемые команды для разработки

## Git команды
```bash
# Проверка статуса
git status

# Добавление файлов
git add .

# Коммит изменений
git commit -m "Описание изменений"

# Просмотр истории
git log --oneline
```

## MCP Server
```bash
# Запуск MCP сервера
python run_mcp_server.py

# Альтернативный запуск через bat файл (Windows)
run_mcp_server.bat
```

## Работа с Serena
```bash
# Активация проекта в Serena
# Выполняется автоматически при подключении
```

## Создание файлов 1С
```bash
# Создание нового общего модуля
echo "// Новый модуль" > src/CommonModules/НовыйМодуль.bsl

# Создание директории для справочника
mkdir src/Catalogs/НовыйСправочник
```

## Проверка проекта
```bash
# Проверка структуры файлов
find src -name "*.bsl" -type f

# Поиск по содержимому
grep -r "КлючевоеСлово" src/
```

## Python окружение (для MCP серверов)
```bash
# Создание виртуального окружения
python -m venv .venv

# Активация окружения (Windows)
.venv\Scripts\activate

# Активация окружения (Linux/Mac)
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```