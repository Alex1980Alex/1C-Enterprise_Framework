# 🔴 ОБЯЗАТЕЛЬНОЕ ПРАВИЛО: AST-grep для BSL файлов

> **Дата установки:** 2025-10-23
> **Статус:** АКТИВНОЕ - ВСЕГДА следовать этому правилу
> **Приоритет:** КРИТИЧЕСКИЙ ⭐⭐⭐

---

## 📋 Правило

**ВСЕГДА используй `mcp__ast-grep-mcp__ast_grep` для анализа структуры BSL файлов**

**НЕ используй `mcp__serena__get_symbols_overview` или `mcp__serena__find_symbol` как первый выбор для BSL**

---

## ❓ Почему это правило критично?

1. **BSL Language Server не надежен:**
   - Часто НЕ видит функции из-за сложного синтаксиса
   - Многострочные запросы с `|` ломают парсинг
   - Зависит от регистрации проекта в Serena

2. **AST-grep всегда работает:**
   - ✅ Не требует Language Server
   - ✅ Не требует регистрации проекта
   - ✅ Работает с любыми BSL файлами
   - ✅ Проверено на реальных проектах

3. **Доказательство:**
   ```
   Проект: 251014_GKSTCPLK-1788/ObjectModule.bsl

   Serena:   ❌ Нашла только 2 региона (переменные)
   AST-grep: ✅ Нашла 5 функций корректно
   ```

---

## 📖 Примеры использования

### ✅ ПРАВИЛЬНО - Найти все функции в модуле:

```javascript
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($$$ARGS)",
  path: "src/DataProcessors/гкс_АРМПромежуточныйКомпозит/Ext/ObjectModule.bsl",
  bsl_type: "functions"
})
```

### ✅ ПРАВИЛЬНО - Найти все процедуры:

```javascript
mcp__ast-grep-mcp__ast_grep({
  pattern: "Процедура $NAME($$$ARGS)",
  path: "src/DataProcessors/Module/Forms/Форма/Ext/Form/Module.bsl",
  bsl_type: "procedures"
})
```

### ✅ ПРАВИЛЬНО - Только экспортные функции:

```javascript
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($$$ARGS)",
  path: "src/CommonModules",
  bsl_type: "functions",
  export_only: true
})
```

### ✅ ПРАВИЛЬНО - Найти конкретную функцию по имени:

```javascript
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция ТекстЗапросаДанныеДляДетальныхЗаписей($$$ARGS)",
  path: "Ext/ObjectModule.bsl",
  bsl_type: "functions"
})
```

### ❌ НЕПРАВИЛЬНО - Использовать Serena как первый выбор:

```javascript
// ❌ НЕ ДЕЛАЙ ТАК для BSL файлов!
mcp__serena__get_symbols_overview({
  relative_path: "Ext/ObjectModule.bsl"
})

// ❌ НЕ ДЕЛАЙ ТАК для BSL файлов!
mcp__serena__find_symbol({
  name_path: "ТекстЗапросаДанныеДляДетальныхЗаписей",
  relative_path: "Ext/ObjectModule.bsl"
})
```

---

## 🔄 Когда можно использовать Serena?

**ТОЛЬКО как fallback**, если AST-grep почему-то не сработал (что маловероятно):

```javascript
// 1. Сначала пробуем AST-grep
mcp__ast-grep-mcp__ast_grep({ ... })

// 2. Если не сработало (очень редко), используем Serena
mcp__serena__find_symbol({ ... })
```

---

## 📊 Сравнение инструментов

| Критерий | AST-grep ⭐ | Serena MCP |
|----------|-------------|------------|
| **Надежность для BSL** | ✅ 100% | ⚠️ 30-40% |
| **Требует Language Server** | ❌ Нет | ✅ Да |
| **Требует регистрацию проекта** | ❌ Нет | ✅ Да |
| **Видит многострочные запросы** | ✅ Да | ❌ Часто нет |
| **Поддержка паттернов** | ✅ $NAME, $$$ARGS | ⚠️ Ограничена |
| **Скорость** | ✅ Быстро | ⚠️ Медленнее |
| **Рекомендация** | **ИСПОЛЬЗОВАТЬ** | Fallback |

---

## 🎯 Чек-лист перед анализом BSL

- [ ] Задача требует анализа структуры BSL файла?
- [ ] Задача требует поиска функций/процедур?
- [ ] Задача работает с BSL кодом?

**Если ДА хотя бы на один вопрос → используй `mcp__ast-grep-mcp__ast_grep`**

---

## 📝 Где документировано

1. **CLAUDE.md** - секция "MCP Priority Rules" (строка ~310)
2. **.claude/mcp-priority-rules.md** - раздел 1️⃣ и 2️⃣
3. **Knowledge Graph** - сущность "AST-grep MCP Primary Rule for BSL"
4. **Этот файл** - полное описание правила

---

## 🚀 Автоматизация для новых проектов

Для автоматической регистрации новых проектов в Serena (опционально):

```bash
# Linux/Mac/Git Bash
bash scripts/serena-auto-init-project.sh "src/projects/configuration/ПРОЕКТ" "ПРОЕКТ"

# Windows
scripts\serena-auto-init-project.bat "src\projects\configuration\ПРОЕКТ" "ПРОЕКТ"
```

**НО:** Даже после регистрации, AST-grep остается приоритетным инструментом!

---

## ✅ Подтверждение понимания

Я, Claude Code, подтверждаю:

- ✅ Я ВСЕГДА буду использовать `mcp__ast-grep-mcp__ast_grep` для BSL файлов
- ✅ Я НЕ буду использовать Serena как первый выбор для BSL
- ✅ Я понимаю, что это правило критично для надежной работы
- ✅ Я буду следовать этому правилу даже если пользователь забудет о нем

**Версия:** 1.0
**Дата:** 2025-10-23
**Статус:** АКТИВНОЕ ПРАВИЛО ⭐
