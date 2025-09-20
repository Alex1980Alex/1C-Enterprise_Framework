# 📚 Документация 1C-Enterprise Cursor Framework

## 🎯 Навигация по документации

Добро пожаловать в центральную документацию фреймворка! Используйте эту карту для быстрого поиска нужной информации.

---

## 🚀 Быстрый старт

### 🏃‍♂️ **Новичок во фреймворке?**
1. **[QUICK_START_ULTIMATE_2025.md](./QUICK_START_ULTIMATE_2025.md)** - Активация за 5 минут
2. **[Framework documentation cursor.md](./Framework%20documentation%20cursor.md)** - Руководство для Cursor IDE  
3. **[Framework documentation claude.md](./Framework%20documentation%20claude.md)** - Руководство для Claude Code

### ⚡ **Нужна конкретная информация?**
- **Системы хуков**: [API Documentation/ultimate-hooks-system.md](./API%20Documentation/ultimate-hooks-system.md)
- **MCP команды**: [API Documentation/mcp-commands-reference.md](./API%20Documentation/mcp-commands-reference.md)
- **BSL интеграция**: [API Documentation/bsl-language-server-integration.md](./API%20Documentation/bsl-language-server-integration.md)

---

## 📖 Структура документации

### 📁 **1. Пользовательские руководства** (для разработчиков)

| Документ | Аудитория | Содержание | Размер |
|----------|-----------|------------|--------|
| **[QUICK_START_ULTIMATE_2025.md](./QUICK_START_ULTIMATE_2025.md)** | Все пользователи | 🚀 Быстрая активация ULTIMATE системы | 459 строк |
| **[Framework documentation cursor.md](./Framework%20documentation%20cursor.md)** | Cursor IDE | 💻 Полное руководство по Cursor IDE | 645 строк |
| **[Framework documentation claude.md](./Framework%20documentation%20claude.md)** | Claude Code | 🤖 Полное руководство по Claude Code | 485 строк |
| **[АВТОМАТИЧЕСКИЕ_ХУКИ_SERENA.md](./АВТОМАТИЧЕСКИЕ_ХУКИ_SERENA.md)** | Администраторы | 🔧 Обзор системы автоматизации | 155 строк |

### 📁 **2. Архитектурные руководства** (`Guides/`)

| Документ | Назначение | Детализация |
|----------|------------|-------------|
| **[Guides/architecture-overview.md](./Guides/architecture-overview.md)** | 🏗️ Архитектура фреймворка | Схемы, компоненты, принципы |

### 📁 **3. Техническая документация** (`API Documentation/`)

| Категория | Документы | Описание |
|-----------|-----------|----------|
| **🎮 Центральный индекс** | **[README.md](./API%20Documentation/README.md)** | Навигация по всем API |
| **🚀 ULTIMATE система** | **[ultimate-hooks-system.md](./API%20Documentation/ultimate-hooks-system.md)** | 22 хука, 39 инструментов (981 строка) |
| **🔗 MCP интеграция** | **[mcp-commands-reference.md](./API%20Documentation/mcp-commands-reference.md)** | 35 MCP команд серии serena__* |
| **🤖 Claude Code API** | **[claude-code-api-reference.md](./API%20Documentation/claude-code-api-reference.md)** | CLI, slash команды, hooks, SDK |
| **⚡ Базовые хуки** | **[claude-code-hooks-api.md](./API%20Documentation/claude-code-hooks-api.md)** | Система автоматического соблюдения правил |
| **📊 BSL анализ** | **[bsl-language-server-integration.md](./API%20Documentation/bsl-language-server-integration.md)** | 793 правила качества кода |
| **🔄 Git автоматизация** | **[git-automation-tools.md](./API%20Documentation/git-automation-tools.md)** | Полная автоматизация версионного контроля |
| **💻 Cursor интеграция** | **[cursor-ide-integration.md](./API%20Documentation/cursor-ide-integration.md)** | 17 модулей управления AI |

---

## 🎯 Сценарии использования

### 🚀 **Я хочу начать использовать фреймворк**
```
1. QUICK_START_ULTIMATE_2025.md     - активация за 5 минут
2. Framework documentation *.md     - выбрать под вашу IDE
3. API Documentation/README.md      - обзор всех возможностей
```

### 🔧 **Настраиваю автоматизацию разработки**
```
1. ultimate-hooks-system.md         - понять ULTIMATE систему 
2. claude-code-hooks-api.md         - базовые хуки
3. АВТОМАТИЧЕСКИЕ_ХУКИ_SERENA.md   - обзор автоматизации
```

### 🤖 **Интегрирую с AI и внешними системами**
```  
1. mcp-commands-reference.md        - все 39 команд MCP
2. claude-code-api-reference.md     - API Claude Code
3. cursor-ide-integration.md        - интеграция Cursor IDE
```

### 📊 **Настраиваю контроль качества кода**
```
1. bsl-language-server-integration.md  - 793 правила BSL LS
2. git-automation-tools.md             - автоматические Git проверки  
3. architecture-overview.md            - принципы архитектуры
```

---

## ⚠️ Известные проблемы документации

### 🚨 **ВНИМАНИЕ: Дублирование информации**

Некоторые темы описаны в нескольких местах. При противоречиях используйте этот **приоритет источников**:

1. **Автоматические хуки**:
   - 🥇 **ultimate-hooks-system.md** - полная техническая документация
   - 🥈 **claude-code-hooks-api.md** - базовые возможности  
   - 🥉 **АВТОМАТИЧЕСКИЕ_ХУКИ_SERENA.md** - краткий обзор

2. **MCP команды**:  
   - 🥇 **mcp-commands-reference.md** - полный справочник
   - 🥈 Упоминания в других файлах - для контекста

3. **Ролевая модель Claude**:
   - 🥇 **Framework documentation claude.md** - детальное описание
   - 🥈 **architecture-overview.md** - архитектурная схема

### 🔄 **Статус реализации возможностей**

| Система | Статус | Источник истины |
|---------|--------|-----------------|
| **ULTIMATE хуки (22 шт)** | ⚠️ Концептуально | `ultimate-hooks-system.md` |
| **Serena MCP (35 команд)** | ⚠️ Внешние скрипты | `mcp-commands-reference.md` |  
| **BSL Language Server** | ⚠️ Внешний инструмент | `bsl-language-server-integration.md` |
| **Git автоматизация** | ⚠️ Внешние скрипты | `git-automation-tools.md` |
| **JetBrains интеграция** | ❌ Планируется | `ultimate-hooks-system.md` (раздел ограничения) |

---

## 🛠️ Планы улучшения документации

### 📋 **Приоритет 1: Критические исправления**
- [ ] Устранить противоречия в описании возможностей
- [ ] Консолидировать дублирующуюся информацию  
- [ ] Привести к единому виду количество команд и функций

### 📋 **Приоритет 2: Структурная оптимизация**
- [ ] Разбить перегруженные документы (981+ строк)
- [ ] Объединить микро-документы (<200 строк)
- [ ] Создать тематические группировки в API Documentation

### 📋 **Приоритет 3: Улучшение навигации**
- [ ] Добавить breadcrumbs в каждый документ
- [ ] Создать интерактивную карту возможностей
- [ ] Разработать поисковый индекс

---

## 📊 Статистика документации

```
📈 Общая статистика:
├── Всего файлов: 13
├── Строк документации: ~4,500
├── Языки: Русский (приоритет), English (частично) 
├── Последнее обновление: 2025-09-03
└── Статус: Производственная готовность ✅

🎯 Качество по категориям:
├── Содержание: 8/10 (детально и актуально)
├── Структура: 6/10 (требует оптимизации)  
├── Навигация: 7/10 (после этого README улучшилась)
├── Дублирование: 4/10 (критический уровень)
└── Связность: 5/10 (есть противоречия)
```

---

## 🔗 Внешние ресурсы

### 🌐 **Связанные проекты**
- [BSL Language Server GitHub](https://github.com/1c-syntax/bsl-language-server) - Статический анализатор 1С кода
- [Cursor IDE Documentation](https://cursor.sh/docs) - Официальная документация Cursor
- [Model Context Protocol](https://modelcontextprotocol.io/) - Спецификация MCP

### 📚 **Официальная документация 1С**
- [1С:Предприятие 8.3.26](https://its.1c.ru/db/v8326doc) - Полная документация платформы
- [BSP 3.1](https://its.1c.ru/db/bsp311doc) - Библиотека стандартных подсистем

---

## 🆘 Поддержка и обратная связь

### 📞 **Нужна помощь?**
1. **Проблемы с документацией**: [GitHub Issues](https://github.com/Alex1980Alex/1C-Enterprise-Cursor-Framework/issues)
2. **Вопросы по использованию**: См. раздел "Устранение неполадок" в соответствующих руководствах
3. **Предложения по улучшению**: Создайте Issue с тегом `documentation`

### 🤝 **Как улучшить документацию**
1. Сообщите о найденных ошибках через GitHub Issues
2. Предложите исправления через Pull Requests  
3. Поделитесь опытом использования для обновления примеров

---

**📅 Версия документации:** 1.0  
**🗓️ Последнее обновление:** 03.09.2025  
**👤 Ответственный:** Команда 1C-Enterprise Cursor Framework  
**⭐ Статус:** ⚠️ Документация готова, реализация концептуальная  

*Эта документация постоянно развивается. Следите за обновлениями и делитесь обратной связью!*