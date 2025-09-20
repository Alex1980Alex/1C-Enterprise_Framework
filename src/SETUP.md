# 🛠️ Руководство по настройке проектов

Пошаговое руководство по работе с проектами 1С в рамках фреймворка.

## 📋 Предварительные требования

1. **Serena MCP Server** - установлен и настроен
2. **BSL Language Server** - автоматически загружается Serena
3. **1С:Предприятие 8.3.26** - для разработки конфигураций

## 🚀 Создание нового проекта

### 1. Структура проекта

```bash
cd d:\1C-Enterprise_Framework\src\projects
mkdir your-project-name
cd your-project-name
```

### 2. Создание конфигурации Serena

Скопируйте шаблон из `templates/basic-config/.serena/project.yml`:

```yaml
project_name: "your-project-name"
language: "bsl"
ignored_paths:
  - "out/"
  - "DT-INF/"
  - "*.cf"
  - "*.dt"
read_only: false
encoding: "utf-8"
```

### 3. Регистрация в Serena

```bash
# Активировать проект
serena activate-project your-project-name

# Или по полному пути
serena activate-project "d:\1C-Enterprise_Framework\src\projects\your-project-name"
```

## 📁 Типовая структура проекта 1С

```
your-project/
├── .serena/
│   └── project.yml
├── src/
│   ├── Catalogs/           # Справочники
│   ├── Documents/          # Документы
│   ├── CommonModules/      # Общие модули
│   ├── DataProcessors/     # Обработки
│   ├── Reports/            # Отчеты
│   ├── InformationRegisters/ # Регистры сведений
│   └── AccumulationRegisters/ # Регистры накопления
├── docs/                   # Документация
└── README.md
```

## 🔄 Работа с MCP сервером

### Запуск сервера

```bash
cd d:\1C-Enterprise_Framework\serena
uv run serena-mcp-server
```

### Команды Serena

```bash
# Просмотр проектов
serena list-projects

# Активация проекта
serena activate-project project-name

# Проверка статуса
serena status
```

## 📚 Использование библиотек

Из каталога `libraries/` можно подключать:

- `common-utils/` - общие утилиты
- `integration-lib/` - библиотеки интеграции

Скопируйте нужные модули в свой проект или настройте как внешние зависимости.

## 🎯 Лучшие практики

1. **Именование проектов** - используйте kebab-case
2. **Кодировка** - всегда UTF-8
3. **Структура** - следуйте типовой организации каталогов
4. **Документация** - создавайте README.md для каждого проекта
5. **Git** - используйте .gitignore для исключения служебных файлов 1С