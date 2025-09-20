# 📁 Каталог проектов 1С:Предприятие

Данный каталог содержит исходные коды проектов разработанных на платформе **1С:Предприятие 8.3.26** с поддержкой **Serena MCP Server**.

## 🏗️ Структура каталога

```
src/
├── 📁 projects/                    # Основные проекты
│   ├── 📁 erp-system/             # Пример: ERP система
│   ├── 📁 crm-module/             # Пример: CRM модуль
│   └── 📁 accounting-base/        # Пример: Учетная база
│
├── 📁 extensions/                 # Расширения конфигураций
│   ├── 📁 integration-extension/  # Пример: Расширение интеграции
│   └── 📁 custom-reports/         # Пример: Дополнительные отчеты
│
├── 📁 libraries/                  # Библиотеки и общие модули
│   ├── 📁 common-utils/           # Общие утилиты
│   └── 📁 integration-lib/        # Библиотека интеграции
│
├── 📁 templates/                  # Шаблоны проектов
│   ├── 📁 basic-config/           # Базовая конфигурация
│   └── 📁 bsp-template/           # Шаблон на основе БСП
│
├── 🔧 bsl_language_server.py      # BSL Language Server для Serena
├── 🔧 ls_config.py               # Конфигурация языков Serena
└── 📋 README.md                  # Этот файл
```

## 🚀 Быстрый старт

### 1. Создание нового проекта
```bash
# Перейти в каталог проектов
cd src/projects

# Создать новый проект
mkdir my-new-project
cd my-new-project

# Инициализировать Serena проект
serena add-project .
```

### 2. Активация проекта в Serena
```bash
# Активировать проект
serena activate-project my-new-project

# Или по пути
serena activate-project "d:\1C-Enterprise_Framework\src\projects\my-new-project"
```

### 3. Запуск MCP сервера
```bash
# Запустить MCP сервер
cd d:\1C-Enterprise_Framework\serena
uv run serena-mcp-server
```

## 📋 Типовая структура проекта 1С

Каждый проект должен содержать:

```
project-name/
├── 📁 .serena/                    # Конфигурация Serena
│   └── project.yml               # Настройки проекта
│
├── 📁 src/                       # Исходные коды конфигурации
│   ├── 📁 Catalogs/              # Справочники
│   ├── 📁 Documents/             # Документы
│   ├── 📁 CommonModules/         # Общие модули
│   ├── 📁 DataProcessors/        # Обработки
│   ├── 📁 Reports/               # Отчеты
│   ├── 📁 InformationRegisters/  # Регистры сведений
│   ├── 📁 AccumulationRegisters/ # Регистры накопления
│   └── 📁 Configuration/         # Корень конфигурации
│
├── 📁 docs/                      # Документация проекта
├── 📁 tests/                     # Тесты (если используются)
├── .gitignore                    # Git исключения
└── README.md                     # Описание проекта
```

## 🔧 Конфигурация Serena

Для каждого проекта создайте `.serena/project.yml`:

```yaml
project_name: "название-проекта"
language: "bsl"
ignored_paths:
  - "out/"
  - "DT-INF/"
  - "*.cf"
  - "*.dt"
encoding: "utf-8"
```

## 📚 Документация

- [Руководство по разработке 1С](../Документация разработчика/)
- [API Documentation](../Документация по фреймворку/API Documentation/)
- [Cursor Rules](../cursor-rules/)

## 🤝 Поддержка

При возникновении вопросов обращайтесь к документации фреймворка или используйте MCP команды Serena.