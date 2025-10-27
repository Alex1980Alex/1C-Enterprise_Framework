# 🚀 Полная автоматизация AST-grep MCP Server для Claude Code

## 🎯 Цель: Запустил Claude Code → Всё работает автоматически!

### ⚡ Быстрая настройка (1 клик):

```bash
# Запустите этот файл ОДИН РАЗ:
enable-full-automation.bat
```

**Всё! Больше никаких действий не требуется.**

---

## 🔧 Что происходит автоматически:

### При загрузке Windows:
✅ **MCP Server запускается в фоне**
✅ **BSL поддержка активируется**
✅ **Готовность к работе с Claude Code**

### При запуске Claude Code:
✅ **Автоматическое подключение к MCP**
✅ **BSL язык поддерживается сразу**
✅ **Структурный поиск доступен**

---

## 💻 Использование в Claude Code:

```python
# Найти все функции 1С в проекте
find_code(
    project_folder="D:/My1CProject",
    pattern="Функция $NAME",
    language="bsl"
)

# Найти экспортные процедуры
find_code(
    project_folder="D:/My1CProject",
    pattern="Процедура $NAME($$$) Экспорт",
    language="bsl"
)

# Найти обработчики форм
find_code_by_rule(
    project_folder="D:/My1CProject",
    yaml="""
id: form-handlers
language: bsl
rule:
  any:
    - pattern: "Процедура ПриСозданииНаСервере($$$)"
    - pattern: "Процедура ПередЗаписью($$$)"
"""
)
```

---

## 🔍 Проверка работы:

### Если что-то не работает:
```bash
# Проверить статус MCP Server
check-mcp-status.bat
```

### Ожидаемый результат:
```
✅ AST-grep MCP Server запущен и работает
🎯 Статус: ГОТОВ К РАБОТЕ
📡 Claude Code может использовать BSL поиск
```

---

## 🛠️ Управление автозапуском:

### Отключить автозапуск:
```
Удалите файл: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\AST-grep MCP Server.lnk
```

### Включить обратно:
```bash
# Запустите снова
enable-full-automation.bat
```

---

## 🎉 Результат:

**Теперь вы просто запускаете Claude Code и сразу используете мощный структурный поиск BSL кода!**

Никаких дополнительных команд, настроек или ожидания - всё работает автоматически в фоне.