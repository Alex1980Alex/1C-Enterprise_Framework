# Serena MCP - Руководство по настройке проектов

> **Проблема:** Serena MCP не видит функции в BSL файлах проекта 251014_GKSTCPLK-1788
> **Причина:** Проект не зарегистрирован в Serena
> **Дата:** 2025-10-23

## 🔍 Диагностика

### Текущий статус:
```bash
Active project: 1C-Enterprise_Framework
Available projects:
  ✅ 250928_GKSTCPLK-1697
  ✅ 251001_GKSTCPLK-1716
  ✅ 251007_GKSTCPLK-1765
  ✅ 251008_GKSTCPLK-1763
  ❌ 251014_GKSTCPLK-1788  # <- НЕ ЗАРЕГИСТРИРОВАН!
  ✅ demo-accounting
  ✅ example-1c-project
```

### Симптомы:
- `mcp__serena__get_symbols_overview` возвращает только переменные
- `mcp__serena__find_symbol` не находит функции
- Language Server не индексирует файлы проекта

---

## ✅ Решение 1: Регистрация проекта в Serena

### 🚀 АВТОМАТИЧЕСКИЙ СПОСОБ (РЕКОМЕНДУЕТСЯ):

```bash
# Из корня фреймворка
bash scripts/serena-auto-init-project.sh "src/projects/configuration/251014_GKSTCPLK-1788" "251014_GKSTCPLK-1788"

# ИЛИ на Windows
scripts\serena-auto-init-project.bat "src\projects\configuration\251014_GKSTCPLK-1788" "251014_GKSTCPLK-1788"
```

Скрипт автоматически создаст:
- `.serena/project.yml` - конфигурация Serena
- `.serena/bsl-config.json` - настройки BSL Language Server
- `.serena/.gitignore` - игнорирование кэша

### 📝 РУЧНОЙ СПОСОБ:

<details>
<summary>Нажмите чтобы развернуть ручную инструкцию</summary>

### Шаг 1: Создать .serena директорию в проекте

```bash
cd "d:\1C-Enterprise_Framework\src\projects\configuration\251014_GKSTCPLK-1788"
mkdir .serena
```

### Шаг 2: Создать project.yml

```bash
cd .serena
cat > project.yml << 'EOF'
# Serena project configuration for 251014_GKSTCPLK-1788
language: bsl

ignore_all_files_in_gitignore: true
ignored_paths: []
read_only: false
excluded_tools: []
initial_prompt: ""
project_name: "251014_GKSTCPLK-1788"
EOF
```

### Шаг 3: Создать bsl-config.json

```bash
cat > bsl-config.json << 'EOF'
{
  "language": "bsl",
  "project_path": "d:\\1C-Enterprise_Framework\\src\\projects\\configuration\\251014_GKSTCPLK-1788",
  "source_paths": [
    "src"
  ],
  "lsp_enabled": true
}
EOF
```

</details>

### Шаг 4: Активировать проект через Serena

```javascript
// Использовать ПОЛНЫЙ ПУТЬ при первой активации
mcp__serena__activate_project({
  project: "d:/1C-Enterprise_Framework/src/projects/configuration/251014_GKSTCPLK-1788"
})

// После первой активации можно использовать короткое имя
mcp__serena__activate_project({
  project: "251014_GKSTCPLK-1788"
})
```

---

## ✅ Решение 2: Работа через корневой проект

### Использовать полные пути от корня:

```javascript
mcp__serena__get_symbols_overview({
  relative_path: "src/projects/configuration/251014_GKSTCPLK-1788/src/DataProcessors/гкс_АРМПромежуточныйКомпозит/Ext/ObjectModule.bsl"
})
```

### Преимущества:
- ✅ Не нужно регистрировать новый проект
- ✅ Все проекты доступны из одного места
- ✅ Проще управление

### Недостатки:
- ❌ Длинные пути
- ❌ Language Server может не индексировать глубоко вложенные файлы
- ❌ Медленнее работа

---

## ✅ Решение 3: Использовать AST-grep MCP (АЛЬТЕРНАТИВА)

AST-grep не требует Language Server и работает напрямую с синтаксическим деревом:

### Поиск процедур в BSL:

```javascript
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($ARGS)",
  path: "src/projects/configuration/251014_GKSTCPLK-1788",
  bsl_type: "procedures"
})
```

### Поиск экспортных функций:

```javascript
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($ARGS) Экспорт",
  path: "src/projects/configuration/251014_GKSTCPLK-1788",
  bsl_type: "functions",
  export_only: true
})
```

### Преимущества AST-grep:
- ✅ Не требует Language Server
- ✅ Работает с любыми BSL файлами
- ✅ Быстрый структурный поиск
- ✅ Поддержка паттернов с переменными ($NAME, $ARGS)

### Недостатки:
- ❌ Нет семантического анализа
- ❌ Не видит зависимости между символами
- ❌ Нет инструментов редактирования

---

## 🔧 Проверка работы

### Тест 1: Проверить доступные проекты

```javascript
mcp__serena__get_current_config()
```

Должен вернуть список с добавленным проектом.

### Тест 2: Получить обзор символов

```javascript
mcp__serena__get_symbols_overview({
  relative_path: "Ext/ObjectModule.bsl"
})
```

Должен вернуть список функций, а не только переменные.

### Тест 3: Найти конкретную функцию

```javascript
mcp__serena__find_symbol({
  name_path: "ТекстЗапросаДанныеДляДетальныхЗаписей",
  relative_path: "Ext/ObjectModule.bsl",
  include_body: true
})
```

Должен найти функцию и вернуть её тело.

---

## 📊 Рекомендации

### ⭐ **Для текущего фреймворка:**
Используй **Решение 2** (работа через корневой проект) - минимальные изменения, все работает сразу.

### ⭐ **Для активной разработки в 251014_GKSTCPLK-1788:**
Используй **Решение 1** (регистрация проекта) - удобнее для постоянной работы.

### ⭐ **Для быстрого поиска без Language Server:**
Используй **Решение 3** (AST-grep MCP) - работает всегда, независимо от настроек.

---

## 🚫 Известные ограничения BSL Language Server

### Проблемы с многострочными строками запросов:

BSL Language Server может НЕ распознавать функции, которые содержат многострочные строки с синтаксисом запросов (строки начинающиеся с `|`):

```bsl
Функция ТекстЗапроса()
    Возврат
    "ВЫБРАТЬ
    |   Поле1,
    |   Поле2
    |ИЗ
    |   Таблица";
КонецФункции
```

**Workaround:**
- Использовать AST-grep MCP для таких файлов
- ИЛИ использовать стандартные инструменты (Read, Edit, Grep)

---

## 📝 Обновление MCP Priority Rules

Добавлено правило в `.claude/mcp-priority-rules.md`:

**ЕСЛИ:** Serena MCP не видит символы в BSL файле
**ТО:** Проверить регистрацию проекта → Использовать AST-grep MCP → Fallback на стандартные инструменты

---

**Статус:** Готово к использованию
**Тестировано:** ✅
**Документировано:** ✅
**Версия:** 1.0
**Дата:** 2025-10-23
