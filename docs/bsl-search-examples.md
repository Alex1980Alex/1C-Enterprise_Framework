# Руководство по поиску BSL кода с помощью AST-grep

## ✅ Настроенная конфигурация

### MCP Server настроен:
- **mcp_settings.json**: AST-grep MCP сервер добавлен
- **Claude permissions**: добавлено разрешение `mcp__ast-grep__ast_grep`
- **BSL поддержка**: добавлены языки "bsl" и "1c" с fallback на JavaScript парсер

## 🔍 Рабочие примеры поиска BSL кода

### 1. Поиск процедур
```bash
# Используем grep для простого текстового поиска
grep -n "Процедура.*Экспорт" "src/projects/configuration/demo-accounting/src/CommonModules/*/Ext/Module.bsl"

# Или через AST-grep с JavaScript синтаксисом (простые паттерны)
ast-grep -p "Процедура" -l javascript --globs "*.bsl" "src/projects/configuration/demo-accounting/src/"
```

### 2. Поиск функций
```bash
# Простой текстовый поиск функций
grep -n "Функция.*Экспорт" "src/projects/configuration/demo-accounting/src/CommonModules/*/Ext/Module.bsl"

# Или через BSL Language Server
python -m sonar_integration analyze --src-dir "src/projects/configuration/demo-accounting/src/" --search-pattern "Функция"
```

### 3. Через MCP (когда сервер подключится)
```javascript
// Пример использования через Claude Code когда MCP сервер заработает
{
  "pattern": "Процедура",
  "language": "bsl", 
  "path": "src/projects/configuration/demo-accounting/src/",
  "glob": "*.bsl",
  "context": 2,
  "head_limit": 10
}
```

## ⚠️ Текущие ограничения

1. **AST-grep не поддерживает BSL синтаксис нативно**
   - Используется JavaScript парсер как fallback
   - Сложные BSL конструкции могут не распознаваться

2. **MCP сервер требует перезапуска Claude Code**
   - Изменения в конфигурации требуют перезапуска
   - Сервер может не появиться в списке сразу

## 💡 Рекомендуемые альтернативы

### Для поиска кода 1С используйте:

1. **BSL Language Server** (рекомендуется):
```bash
python -m sonar_integration analyze --search-pattern "ИмяПроцедуры"
```

2. **Ripgrep** (быстро и надежно):
```bash
rg "Процедура.*Экспорт" --type-add 'bsl:*.bsl' --type bsl
```

3. **GitHub Code Search** (для внешних репозиториев):
```bash
# Через MCP
mcp__github__search_code("1С:Предприятие language:bsl ИмяПроцедуры")
```

## 🎯 Следующие шаги для полной настройки

1. **Создание Tree-sitter грамматики для BSL**
2. **Интеграция с ast-grep как полноценный язык**  
3. **Тестирование сложных поисковых паттернов**
4. **Настройка автоматического запуска MCP сервера**

---

**Статус**: ⚠️ Частично работает  
**Рекомендация**: Используйте BSL Language Server для полноценного поиска кода 1С