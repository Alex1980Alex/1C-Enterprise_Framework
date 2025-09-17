# Команды для разработки в проекте 1C-Enterprise Framework

## Команды Serena (если подключен к Claude Code)

### Активация Serena в Claude Code
```bash
# Вариант 1: Локальная установка
claude mcp add serena -- uv run --directory D:/1C-Enterprise_Framework/serena serena start-mcp-server --context ide-assistant --project D:/1C-Enterprise_Framework

# Вариант 2: Через uvx (рекомендуется)
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project D:/1C-Enterprise_Framework
```

## Работа с файлами 1С

### Создание новых модулей
```bash
# Создать новый общий модуль
echo "// Модуль" > src/CommonModules/НовыйМодуль.bsl

# Создать структуру каталога
mkdir src/Catalogs/НовыйСправочник
```

## Системные команды (Windows)

### Навигация
```bash
# Список файлов
dir
# или
ls (если доступен PowerShell)

# Переход в директорию
cd src\CommonModules

# Текущая директория
cd
```

### Поиск
```bash
# Поиск файлов по имени
dir /s /b *.bsl

# Поиск текста в файлах (PowerShell)
Select-String -Path "*.bsl" -Pattern "текст"

# Поиск через findstr
findstr /s /i "текст" *.bsl
```

### Git команды
```bash
# Статус репозитория
git status

# Добавить файлы
git add .

# Коммит
git commit -m "Описание изменений"

# История
git log --oneline
```

## Полезные инструменты Serena

Поскольку Serena не поддерживает BSL напрямую, используйте:
- `list_dir` - просмотр структуры проекта
- `find_file` - поиск файлов по маске
- `search_for_pattern` - поиск по содержимому с regex
- Общие инструменты редактирования текстовых файлов

## Рекомендации
- VS Code с расширением "Language 1C (BSL)" для подсветки синтаксиса
- Использовать UTF-8 кодировку для файлов .bsl