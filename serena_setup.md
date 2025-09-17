# Установка Serena в Claude Code

## Установка завершена

Serena успешно установлена в директории `D:\1C-Enterprise_Framework\serena`.

## Добавление Serena в Claude Code

Для добавления Serena в Claude Code выполните следующую команду в терминале Claude Code:

### Вариант 1: Использование локальной установки
```bash
claude mcp add serena -- uv run --directory D:/1C-Enterprise_Framework/serena serena start-mcp-server --context ide-assistant --project D:/1C-Enterprise_Framework
```

### Вариант 2: Использование uvx (рекомендуется)
```bash
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project D:/1C-Enterprise_Framework
```

## Проверка установки

После добавления Serena, попросите Claude прочитать инструкции Serena:
- Введите команду: `/mcp__serena__initial_instructions`
- Или просто попросите: "read Serena's initial instructions"

## Основные возможности Serena

1. **Семантический поиск кода** - поиск по символам, функциям, классам
2. **Редактирование на основе LSP** - точное редактирование кода с учетом контекста
3. **Управление проектами** - активация и индексация проектов
4. **Память проекта** - сохранение знаний о проекте между сессиями

## Примечание для работы с 1С

Serena не имеет встроенной поддержки языка 1С (BSL), но вы можете:
1. Использовать общие инструменты поиска и редактирования файлов
2. Работать с файлами `.bsl` как с текстовыми файлами
3. Использовать регулярные выражения для поиска по коду 1С

## Полезные команды Serena

- Активация проекта: используйте инструмент `activate_project`
- Индексация проекта: используйте инструмент `index_project`
- Поиск файлов: используйте инструмент `find_files`
- Поиск по содержимому: используйте инструмент `regex_search`