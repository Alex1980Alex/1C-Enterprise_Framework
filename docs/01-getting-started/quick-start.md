# Быстрый старт с 1C Enterprise Framework

> **Время чтения:** 10 минут • **Уровень:** Начинающий

## 🎯 Что вы получите

После прохождения этого руководства вы сможете:
- ✅ Анализировать качество BSL кода
- ✅ Использовать Task Master для управления задачами  
- ✅ Работать с MCP серверами для автоматизации
- ✅ Применять Git hooks для контроля качества

## 🚀 Шаг 1: Проверка окружения

```bash
# Проверка всех компонентов фреймворка
bash scripts/validate-project.sh
```

**Что проверяется:**
- Python 3.8+ и зависимости
- Node.js 16+ для Task Master
- Git hooks настройка
- BSL Language Server

## 🔧 Шаг 2: Первый анализ кода

### Быстрый анализ BSL файла
```bash
# Анализ конкретного файла
python -m sonar_integration analyze --src-dir "Module.bsl" --quick

# Анализ всего проекта
python -m sonar_integration analyze --src-dir src/ --output-dir reports/
```

### Генерация отчёта
```bash
# HTML отчёт с автоматическим открытием
python -m sonar_integration report reports/analysis.json --html && start reports/report.html
```

## 📋 Шаг 3: Работа с Task Master

```bash
cd claude-task-master

# Просмотр доступных задач
npx task-master list

# Получить следующую рекомендуемую задачу
npx task-master next

# Просмотр конкретной задачи
npx task-master show 1
```

## 🤖 Шаг 4: Использование MCP для BSL

### Анализ структуры BSL модуля
```javascript
// В Claude Desktop или через MCP команды
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($$$ARGS)",
  path: "src/CommonModules/UtilsModule.bsl",
  bsl_type: "functions"
})
```

### Поиск где используется функция
```javascript
mcp__serena__find_referencing_symbols({
  name_path: "ИмяФункции",
  relative_path: "CommonModules/Module.bsl"
})
```

## 🔄 Шаг 5: Git workflow с автоматическими проверками

```bash
# Создание новой ветки
git checkout -b feature/new-functionality

# Внесение изменений в код
# ... редактирование BSL файлов ...

# Коммит с автоматическими проверками
git add .
git commit -m "feat: добавлена новая функциональность

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Git hooks автоматически:
# - Запустят BSL анализ
# - Заблокируют коммит при BLOCKER ошибках
# - Покажут детальный отчёт
```

## 💡 Шаг 6: Полный цикл анализа (продвинутый)

```bash
# Автоматический pipeline: BSL + Serena + Reasoner + Memory
python scripts/mcp-integration/full-analysis-pipeline.py \
  --input "src/CommonModules/MyModule.bsl" \
  --output "reports/full-analysis" \
  --use-reasoner \
  --save-to-memory
```

## 🎓 Следующие шаги

### Для разработчиков
- 📖 [BSL разработка](../02-user-guides/developers/bsl-development.md)
- 🔍 [Контроль качества кода](../02-user-guides/developers/code-quality.md)
- 🔄 [Git workflow](../02-user-guides/developers/git-workflow.md)

### Для архитекторов  
- 🏗️ [Обзор архитектуры](../02-user-guides/architects/architecture-overview.md)
- 🔧 [Возможности фреймворка](../02-user-guides/architects/framework-capabilities.md)

### Для изучения MCP
- 🔌 [Базовое использование MCP](../04-examples/mcp-integration/basic-usage.md)
- 🚀 [Продвинутые сценарии](../04-examples/mcp-integration/advanced-scenarios.md)

## ❓ Часто задаваемые вопросы

### Q: Как исправить ошибки BSL анализа?
**A:** Используйте автоматические предложения из отчёта. Каждая ошибка содержит ссылку на правило и способы исправления.

### Q: Task Master показывает слишком много задач
**A:** Используйте фильтрацию: `npx task-master list --tag beginners` для начальных задач.

### Q: MCP серверы не работают
**A:** Проверьте конфигурацию Claude Desktop и установку зависимостей: [Настройка MCP](../03-technical-reference/configuration/mcp-setup.md)

## 🆘 Помощь и поддержка

- 🔧 [Устранение неполадок](../03-technical-reference/troubleshooting/common-issues.md)
- 📚 [Полная документация](../README.md)
- 💬 Создайте Issue в репозитории для вопросов

---

**⏱️ Время прохождения:** ~10 минут  
**🎯 Следующий шаг:** [Установка и настройка](installation.md)