# 🤖 Автоматизация и тестирование

## 🎯 Обзор инструментов автоматизации

Фреймворк предоставляет инструменты для автоматизации задач разработки, тестирования веб-интерфейса, управления проектами и CI/CD процессов.

---

## 🔧 Основные инструменты

### **1. Task Master v0.26.0 - Управление задачами**

**AI-помощник** для планирования разработки с 93 готовыми задачами и 535 подзадачами.

#### **Основные команды:**
```bash
cd claude-task-master

# Просмотр и управление задачами
npx task-master list                    # Все задачи
npx task-master next                    # Следующая рекомендуемая задача
npx task-master show 1                  # Детали задачи №1
npx task-master status                  # Статус проекта

# Фильтрация и поиск
npx task-master list --status pending   # Только ожидающие задачи
npx task-master list --tag development  # Задачи разработки
npx task-master search "BSL анализ"     # Поиск по тексту

# Управление тегами
npx task-master tags                    # Список всех тегов
npx task-master tags --show-metadata    # Теги с метаданными
```

#### **Создание и управление задачами:**
```bash
# Создание новых задач
npx task-master add-task \
  --title "Рефакторинг CommonModule" \
  --description "Улучшить структуру общего модуля" \
  --tag quality-control

# Парсинг задач из текстового описания
npx task-master parse-from-text "Создать отчёт по продажам с группировкой по менеджерам"

# Отметка выполнения
npx task-master mark-complete <task-id>
```

#### **Генерация тестов из задач:**
```bash
# Генерация тестового кода для задачи
npx task-master generate-test --id=1 --output-dir=tests/ --no-validate

# Генерация с исследованием
npx task-master generate-test --id=5 --output-dir=tests/ --research

# Пакетная генерация для нескольких задач
npx task-master generate-test --ids=2,3,4 --output-dir=tests/ --continue-on-error
```

#### **Интеграция с AI моделями:**
```bash
# Настройка моделей (Google AI уже настроена)
npx task-master models --list           # Список доступных моделей
npx task-master research "1С производительность" # Исследование с AI
```

---

### **2. Playwright Automation - Автотестирование веб-интерфейса**

**Автоматизация тестирования** веб-интерфейса 1С и API с созданием скриншотов и отчётов.

#### **Основы навигации и взаимодействия:**
```javascript
// Запуск браузера и навигация
mcp__playwright-automation__playwright_navigate({
  url: "http://localhost/infobase",
  browserType: "chromium",
  headless: false,
  width: 1920,
  height: 1080
})

// Базовые действия
mcp__playwright-automation__playwright_fill({
  selector: "#username",
  value: "Администратор"
})

mcp__playwright-automation__playwright_click({
  selector: "#login-button"
})

mcp__playwright-automation__playwright_press_key({
  key: "Enter"
})
```

#### **Функциональное тестирование:**
```javascript
// Тестирование создания документа
mcp__playwright-automation__playwright_click({
  selector: "[data-document='ЗаказПокупателя']"
})

mcp__playwright-automation__playwright_fill({
  selector: "#Покупатель_field",
  value: "ООО Тестовый клиент"
})

mcp__playwright-automation__playwright_fill({
  selector: "#Дата_field",
  value: "26.10.2025"
})

// Добавление строки в табличную часть
mcp__playwright-automation__playwright_click({
  selector: "#ДобавитьСтроку_button"
})

mcp__playwright-automation__playwright_fill({
  selector: "#Номенклатура_1",
  value: "Товар001"
})

// Сохранение документа
mcp__playwright-automation__playwright_press_key({
  key: "Ctrl+S"
})
```

#### **API тестирование:**
```javascript
// REST API тестирование
mcp__playwright-automation__playwright_post({
  url: "http://localhost/infobase/hs/api/v1/documents/ЗаказПокупателя",
  value: JSON.stringify({
    Покупатель: "Тестовый клиент",
    Дата: "2025-10-26",
    Товары: [
      {Номенклатура: "Товар001", Количество: 10, Цена: 1000}
    ]
  }),
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_TOKEN"
  }
})

// GET запросы
mcp__playwright-automation__playwright_get({
  url: "http://localhost/infobase/hs/api/v1/catalogs/Номенклатура"
})

// Ожидание ответа API
mcp__playwright-automation__playwright_expect_response({
  id: "order_creation",
  url: "*/api/v1/documents/ЗаказПокупателя"
})

mcp__playwright-automation__playwright_assert_response({
  id: "order_creation",
  value: "success"
})
```

#### **Создание документации и отчётов:**
```javascript
// Скриншоты для документации
mcp__playwright-automation__playwright_screenshot({
  name: "main-interface",
  fullPage: true,
  savePng: true,
  downloadsDir: "reports/screenshots/"
})

// PDF документация
mcp__playwright-automation__playwright_save_as_pdf({
  filename: "user-guide.pdf",
  outputPath: "reports/documentation/",
  format: "A4",
  printBackground: true,
  margin: {
    top: "1cm",
    bottom: "1cm",
    left: "1cm", 
    right: "1cm"
  }
})

// Получение содержимого страницы
mcp__playwright-automation__playwright_get_visible_text()
mcp__playwright-automation__playwright_get_visible_html({
  removeScripts: true,
  cleanHtml: true,
  maxLength: 50000
})
```

#### **Генерация тестового кода:**
```javascript
// Запись действий пользователя в код
mcp__playwright-automation__start_codegen_session({
  options: {
    outputPath: "tests/generated/",
    testNamePrefix: "1C_AutoTest",
    includeComments: true
  }
})

// Завершение записи и генерация кода
mcp__playwright-automation__end_codegen_session({
  sessionId: "session_id"
})
```

---

### **3. Git hooks и версионный контроль**

**Автоматическая проверка** качества кода при коммитах с блокировкой некачественных изменений.

#### **Настроенные Git hooks:**
- **pre-commit** - анализ BSL качества измененных файлов
- **commit-msg** - проверка формата сообщений коммитов
- **pre-push** - полная проверка перед отправкой в удалённый репозиторий

#### **Автоматические проверки:**
```bash
# При коммите автоматически выполняется:
git add Module.bsl
git commit -m "feat: улучшение функции обработки данных"

# Hook автоматически запускает:
# 1. python -m sonar_integration analyze --src-dir "Module.bsl" --quick
# 2. Проверка на BLOCKER и CRITICAL ошибки
# 3. Блокировка коммита при наличии критичных проблем
```

#### **Настройка хуков:**
```bash
# Активация хуков (если не активированы автоматически)
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/commit-msg

# Обход хуков при необходимости (не рекомендуется)
git commit --no-verify -m "WIP: временный коммит"
```

---

### **4. CI/CD Pipeline - GitHub Actions**

**Автоматизация** проверок качества, тестирования и деплоя через GitHub Actions.

#### **Настроенные workflows:**
1. **Quality Check** (`.github/workflows/bsl-quality-check.yml`)
   - Анализ BSL качества при каждом PR
   - Автоматические комментарии с результатами
   - Блокировка PR при критичных ошибках

2. **Daily Reports** (`.github/workflows/daily-quality-report.yml`)
   - Ежедневные отчёты качества кода
   - Создание GitHub Issues с результатами
   - Отслеживание динамики метрик

#### **Функции CI/CD:**
- **Автоматический анализ** всех .bsl файлов в PR
- **Комментарии в PR** с детальными результатами анализа
- **Загрузка артефактов** - отчёты доступны для скачивания
- **Блокировка merge** при наличии BLOCKER ошибок
- **Уведомления** в Slack/Teams при проблемах (настраивается)

#### **Ручной запуск анализа:**
```bash
# Через GitHub CLI
gh workflow run "BSL Quality Check" --ref main

# Через веб-интерфейс GitHub
# Actions → BSL Quality Check → Run workflow
```

---

### **5. Sequential Thinking MCP - Автоматизация планирования**

**Структурированное мышление** для автоматизации планирования сложных задач.

#### **Автоматическое планирование:**
```javascript
// Декомпозиция сложной задачи
mcp__sequential-thinking__sequentialthinking({
  thought: "Планирую автоматизацию тестирования документооборота заказов",
  thoughtNumber: 1,
  totalThoughts: 12,
  nextThoughtNeeded: true
})

// Анализ зависимостей
mcp__sequential-thinking__sequentialthinking({
  thought: "Определяю последовательность тестов: создание → заполнение → проведение → отчёты",
  thoughtNumber: 5,
  totalThoughts: 12,
  nextThoughtNeeded: true
})

// Планирование ресурсов
mcp__sequential-thinking__sequentialthinking({
  thought: "Оцениваю необходимые ресурсы: тестовые данные, окружения, время выполнения",
  thoughtNumber: 8,
  totalThoughts: 12,
  nextThoughtNeeded: true
})
```

---

## 📋 Практические сценарии

### **🔄 Полный цикл автоматизированной разработки:**

```bash
# 1. Получение задачи из Task Master
cd claude-task-master
npx task-master next

# 2. Автоматическая генерация тестов для задачи
npx task-master generate-test --id=<task-id> --output-dir=tests/ --research

# 3. Разработка функциональности
# (ваш код)

# 4. Автоматическая проверка качества при коммите
git add .
git commit -m "feat: реализация новой функциональности"
# Git hook автоматически проверит качество кода

# 5. Автоматическое тестирование
```
```javascript
// Playwright тесты запускаются автоматически
mcp__playwright-automation__playwright_navigate({
  url: "http://localhost/test-infobase"
})
// ... тестовые сценарии
```

### **🧪 Комплексное тестирование конфигурации:**

```javascript
// 1. Тестирование авторизации
mcp__playwright-automation__playwright_navigate({
  url: "http://localhost/infobase"
})

mcp__playwright-automation__playwright_fill({
  selector: "#username",
  value: "Тестировщик"
})

mcp__playwright-automation__playwright_click({
  selector: "#login"
})

// 2. Тестирование основных функций
mcp__playwright-automation__playwright_click({
  selector: "[data-path='Документы.ЗаказПокупателя']"
})

// 3. API тестирование
mcp__playwright-automation__playwright_post({
  url: "http://localhost/infobase/hs/api/v1/test-endpoint",
  value: JSON.stringify({test: "data"})
})

// 4. Создание отчёта
mcp__playwright-automation__playwright_screenshot({
  name: "comprehensive-test-results",
  fullPage: true
})

mcp__playwright-automation__playwright_save_as_pdf({
  filename: "test-report.pdf",
  outputPath: "reports/"
})
```

### **📊 Автоматизация отчётности:**

```bash
# 1. Ежедневный анализ качества (через cron или GitHub Actions)
python -m sonar_integration analyze --src-dir . --output-dir daily-reports/

# 2. Генерация сводного отчёта
python -m sonar_integration report daily-reports/analysis.json --html --excel

# 3. Автоматическая отправка отчётов
# (через настроенные GitHub Actions или скрипты)
```

### **🔧 Автоматизация рефакторинга:**

```javascript
// 1. Автоматический поиск кандидатов для рефакторинга
mcp__ast-grep-mcp__ast_grep({
  pattern: "Функция $NAME($$$ARGS) $$$BODY КонецФункции",
  path: "src/",
  head_limit: 50
})

// 2. Планирование рефакторинга через Sequential Thinking
mcp__sequential-thinking__sequentialthinking({
  thought: "Анализирую найденные функции для определения приоритетов рефакторинга",
  thoughtNumber: 1,
  totalThoughts: 8,
  nextThoughtNeeded: true
})

// 3. Автоматический рефакторинг простых случаев
mcp__ast-grep-mcp__ast_grep({
  pattern: "Процедура $NAME() // TODO: упростить",
  replacement: "Процедура $NAME() // Упрощено автоматически",
  mode: "replace",
  dry_run: false
})
```

---

## 🔗 Интеграция и настройка

### **Task Master интеграция:**
- Автоматическое создание задач из результатов анализа кода
- Генерация тестов на основе описания задач
- Интеграция с AI моделями для исследований

### **Playwright интеграция:**
- Автоматический запуск тестов при изменении кода
- Генерация скриншотов для документации
- API тестирование с валидацией результатов

### **CI/CD интеграция:**
- GitHub Actions для автоматических проверок
- Автоматические комментарии в PR
- Блокировка некачественного кода

### **Git hooks интеграция:**
- Проверка качества при каждом коммите
- Автоматическое форматирование кода
- Блокировка коммитов с критичными ошибками

---

## ⚙️ Настройка и конфигурация

### **Task Master настройка:**
```bash
# В claude-task-master/.taskmaster/config.json
{
  "defaultModel": "google-ai",
  "outputFormat": "markdown",
  "autoValidate": true
}
```

### **Playwright настройка:**
```javascript
// Переменные окружения
PLAYWRIGHT_BROWSER_TYPE=chromium
PLAYWRIGHT_HEADLESS=false
PLAYWRIGHT_TIMEOUT=30000
```

### **Git hooks настройка:**
```bash
# В .git/hooks/pre-commit
#!/bin/bash
python -m sonar_integration analyze --src-dir . --quick --severity BLOCKER,CRITICAL
if [ $? -ne 0 ]; then
    echo "❌ Обнаружены критичные ошибки BSL"
    exit 1
fi
```

---

*Руководство обновлено: 26.10.2025*  
*Поддерживаемые браузеры: Chromium, Firefox, WebKit*  
*Интеграции: GitHub Actions, Git hooks, Task Master AI v0.26.0*