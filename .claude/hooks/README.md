# Claude Code Hooks System

Система автоматического управления инфраструктурой через хуки Claude Code.

## Обзор

Хуки позволяют автоматизировать проверки и действия при работе с Claude Code. Все хуки находятся в `.claude/hooks/` и автоматически выполняются при соответствующих событиях.

## Структура

```
.claude/hooks/
├── pre-prompt.hook.sh          ← Исполняемый хук
├── pre-prompt/                 ← Документация pre-prompt хука
│   ├── README.md
│   └── ACTIVATION_GUIDE.md
├── post-prompt/                ← Будущий post-prompt хук (пока не активен)
├── archive/                    ← Архив старых версий
├── memory/                     ← Память системы
├── README.md                   ← Этот файл
└── STRUCTURE.md                ← Описание структуры
```

## Активные хуки

### Разделение ответственности

Система использует **два типа хуков** с четким разделением функций:

1. **Infrastructure Hooks** (`.claude/hooks/pre-prompt.hook.sh`)
   - Проверка базовой инфраструктуры (Docker, БД, сервисы)
   - Автозапуск Docker при необходимости
   - Один раз за сессию

2. **Memory AI Hooks** (`.claude/hooks/memory/*.bat`)
   - Анализ задач пользователя
   - Автосохранение результатов инструментов
   - Интеграция с Memory-AI MCP
   - Ротация логов

### pre-prompt.hook.sh (Infrastructure)

**Триггер:** Перед первым промптом в каждой сессии Claude Code

**Назначение:** Проверка базовой инфраструктуры проекта

**Проверяет:**
- Docker Desktop
- Qdrant (port 6333) - векторная БД
- Neo4j (port 7474) - граф БД
- Ollama (port 11434) - LLM сервер

**НЕ проверяет:**
- Memory AI MCP Server (проверяется отдельным memory хуком)

**Документация:**
- [Детальное описание](./pre-prompt/README.md)
- [Руководство по активации](./pre-prompt/ACTIVATION_GUIDE.md)
- [Быстрый старт](../../QUICK_START_HOOKS.md)

### memory/*.bat (Memory AI)

**Триггеры:** UserPromptSubmit, PostToolUse

**Назначение:** Автоматическая работа с памятью и контекстом

**Активные хуки:**
- `pre-prompt-check.bat` - проверка Memory MCP
- `post-user-prompt-analysis.bat` - анализ задачи (task-analysis.py)
- `auto-rotation-hook.bat` - ротация логов
- `post-tool-save.bat` - автосохранение результатов (auto-save.py)

**Документация:**
- [Полное описание](./memory/README.md)
- [Техническая документация](./memory/COMPLETE_DOCUMENTATION.md)

## Как работают хуки Claude Code

### Типы хуков

Claude Code поддерживает следующие типы хуков:

1. **pre-prompt** - перед обработкой промпта пользователя
2. **post-prompt** - после обработки промпта
3. **pre-tool-use** - перед использованием инструмента
4. **post-tool-use** - после использования инструмента

### Именование файлов

Хуки должны находиться **непосредственно в `.claude/hooks/`** (не в подпапках!) и иметь расширение:
- `.hook.sh` - для bash скриптов
- `.hook.bat` - для Windows batch скриптов

**Примеры:**
- `.claude/hooks/pre-prompt.hook.sh` ✅
- `.claude/hooks/pre-prompt/pre-prompt.hook.sh` ❌ (не будет работать!)

### Права на выполнение

Для Linux/Mac хуки должны иметь права на выполнение:
```bash
chmod +x .claude/hooks/*.hook.sh
```

Для Windows это не обязательно, так как bash автоматически запускается через Git Bash.

### Line endings

**Важно:** Bash скрипты должны иметь Unix line endings (LF), а не Windows (CRLF).

Проверка:
```bash
file .claude/hooks/pre-prompt.hook.sh
# Должно быть: "UTF-8 text executable"
# Не должно быть: "with CRLF line terminators"
```

Исправление:
```bash
dos2unix .claude/hooks/pre-prompt.hook.sh
```

## Интеграция со скриптами

Хуки используют инфраструктурные скрипты из `scripts/infrastructure/`:

| Скрипт | Назначение |
|--------|-----------|
| `start-docker-services.bat` | Запуск Docker и всех контейнеров |
| `stop-docker-services.bat` | Остановка контейнеров |
| `restart-docker-services.bat` | Перезапуск всех сервисов |
| `check-all-services.bat` | Детальная проверка статусов |
| `quick-status.bat` | Быстрая проверка |
| `validate-hooks-system.bat` | Валидация системы хуков |

**Использование:**
```bash
# Запустить инфраструктуру
scripts\infrastructure\start-docker-services.bat

# Проверить статус
scripts\infrastructure\check-all-services.bat

# Валидация перед перезапуском
scripts\infrastructure\validate-hooks-system.bat
```

## Управление хуками

### Отключить хук

Переименуйте файл, добавив `.disabled`:
```bash
mv .claude/hooks/pre-prompt.hook.sh .claude/hooks/pre-prompt.hook.sh.disabled
```

### Включить хук обратно

```bash
mv .claude/hooks/pre-prompt.hook.sh.disabled .claude/hooks/pre-prompt.hook.sh
```

### Принудительная проверка

Удалите временный флаг:
```bash
rm /tmp/claude-code-infrastructure-checked
```

### Ручной запуск для тестирования

```bash
bash .claude/hooks/pre-prompt.hook.sh
```

## Создание своего хука

### Шаг 1: Создайте файл

```bash
touch .claude/hooks/my-custom.hook.sh
chmod +x .claude/hooks/my-custom.hook.sh
```

### Шаг 2: Добавьте shebang

```bash
#!/bin/bash
```

### Шаг 3: Напишите логику

```bash
#!/bin/bash

echo "My custom hook is running!"

# Ваш код здесь
```

### Шаг 4: Протестируйте

```bash
bash .claude/hooks/my-custom.hook.sh
```

### Шаг 5: Создайте документацию

```
.claude/hooks/my-custom/
├── README.md
└── examples/
```

## Требования

### Обязательные

- ✅ Claude Code CLI установлен
- ✅ Bash (Git Bash для Windows)
- ✅ Права на выполнение для `.sh` файлов

### Опциональные

- Docker Desktop (для инфраструктурных хуков)
- docker-compose (для управления контейнерами)

## Устранение проблем

### Хук не выполняется

**Проблема:** Хук создан, но не срабатывает при промпте

**Решение:**
1. Проверьте расположение (должен быть в `.claude/hooks/`, не в подпапке)
2. Проверьте имя файла (должно быть `*.hook.sh` или `*.hook.bat`)
3. Проверьте права: `chmod +x .claude/hooks/*.hook.sh`
4. Перезапустите Claude Code: `exit` → `claude`

### Ошибка синтаксиса bash

**Проблема:** `bash: syntax error near unexpected token`

**Решение:**
1. Проверьте line endings: `file .claude/hooks/pre-prompt.hook.sh`
2. Конвертируйте в LF: `dos2unix .claude/hooks/pre-prompt.hook.sh`
3. Проверьте синтаксис: `bash -n .claude/hooks/pre-prompt.hook.sh`

### Docker не запускается

**Проблема:** Хук предлагает запустить Docker, но ничего не происходит

**Решение:**
1. Проверьте путь к Docker Desktop в скрипте
2. Запустите Docker Desktop вручную один раз
3. Проверьте права администратора
4. Запустите скрипт вручную: `scripts\infrastructure\start-docker-services.bat`

### Timeout при проверке сервисов

**Проблема:** Хук висит и не отвечает

**Решение:**
1. Увеличьте timeout в команде `curl`: `timeout 5 curl ...`
2. Проверьте доступность портов: `netstat -an | findstr "6333 7474 11434"`
3. Перезапустите проблемные сервисы

## Валидация системы

Перед использованием рекомендуется запустить полную проверку:

```bash
scripts\infrastructure\validate-hooks-system.bat
```

Это проверит:
- ✅ Наличие всех необходимых файлов
- ✅ Доступность bash
- ✅ Синтаксис bash скриптов
- ✅ Наличие docker-compose.yml
- ✅ Доступность Docker Desktop
- ✅ Доступность Claude CLI

## Производительность

| Операция | Время |
|----------|-------|
| Проверка (все работает) | ~2 сек |
| Проверка (Docker выключен) | ~3 сек |
| Автозапуск Docker | ~60 сек |
| Overhead на сессию | минимальный |

## Безопасность

- Хуки выполняются с правами текущего пользователя
- Не используют sudo/администратора без явного запроса
- Все пароли берутся из `.env` файлов
- Временные файлы создаются в `/tmp/`
- Логи не содержат чувствительной информации

## Расширение системы

### Планируемые хуки

- **post-prompt** - сбор статистики использования
- **pre-tool-use** - валидация параметров инструментов
- **session-end** - корректное завершение сервисов
- **error-handler** - автоматическое восстановление после ошибок

### Интеграция

Система хуков готова для интеграции с:
- CI/CD пайплайнами
- Системами мониторинга (Prometheus, Grafana)
- Системами логирования (ELK, Loki)
- Системами уведомлений (Slack, Telegram)

## Дополнительные ресурсы

### Документация

- [QUICK_START_HOOKS.md](../../QUICK_START_HOOKS.md) - быстрый старт
- [.claude/HOOKS_SYSTEM_COMPLETE.md](../.claude/HOOKS_SYSTEM_COMPLETE.md) - полный отчет
- [pre-prompt/README.md](./pre-prompt/README.md) - детали pre-prompt хука
- [pre-prompt/ACTIVATION_GUIDE.md](./pre-prompt/ACTIVATION_GUIDE.md) - руководство активации

### Внешние ссылки

- [Claude Code Documentation](https://docs.claude.ai/code)
- [Git Bash для Windows](https://git-scm.com/download/win)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)

---

**Версия:** 1.1
**Дата обновления:** 2025-11-04
**Статус:** ✅ Production Ready
**Лицензия:** MIT

**Изменения:**
- Реорганизована структура документации
- Добавлены подпапки для каждого типа хуков
- Улучшена навигация
- Добавлены примеры создания собственных хуков
