# 🚀 Claude Code Hooks - Руководство по активации

## Быстрый старт

### 1. Проверка установки

Убедитесь что все файлы на месте:

```bash
# Хук
ls .claude/hooks/pre-prompt.hook.sh

# Скрипты
ls scripts/infrastructure/

# Должны быть:
# - start-docker-services.bat
# - stop-docker-services.bat
# - restart-docker-services.bat
# - check-all-services.bat
# - quick-status.bat
```

### 2. Активация хука (только для Linux/Mac)

Если вы используете Linux или Mac, дайте права на выполнение:

```bash
chmod +x .claude/hooks/pre-prompt.hook.sh
```

**Для Windows:** Права не требуются, так как Git для Windows включает bash.

### 3. Перезапуск Claude Code

**ВАЖНО:** Хуки загружаются при запуске Claude Code.

```bash
# Закройте текущую сессию
exit

# Запустите новую сессию Claude Code
claude
```

### 4. Первый запуск

При первом промпте вы увидите:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 AI Memory System Infrastructure Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Docker Desktop
✓ Qdrant (port 6333)
✓ Neo4j (port 7474)
✓ Ollama (port 11434)
✓ Memory AI MCP

Status: 5/5 services operational

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Сценарии использования

### Сценарий 1: Все работает ✅

```
✓ Docker Desktop
✓ Qdrant (port 6333)
✓ Neo4j (port 7474)
✓ Ollama (port 11434)
✓ Memory AI MCP

Status: 5/5 services operational
```

**Действие:** Ничего не требуется. Работайте как обычно!

---

### Сценарий 2: Docker не запущен ⚠️

```
✗ Docker Desktop
✗ Qdrant (port 6333)
✗ Neo4j (port 7474)
✓ Ollama (port 11434)
✓ Memory AI MCP

Status: 2/5 services operational

⚠ Docker is not running

Would you like to start Docker services? (y/n)
```

**Варианты:**

**A. Запустить автоматически (рекомендуется):**
```
y [Enter]
```

Система автоматически:
1. Запустит Docker Desktop
2. Подождет готовности (30 сек)
3. Запустит docker-compose
4. Проверит статус контейнеров

**B. Пропустить:**
```
n [Enter]
```

Вы увидите предупреждение:
```
Note: Some AI Memory features will be limited without Docker:
  • Semantic search (Qdrant) - unavailable
  • Graph analytics (Neo4j) - unavailable
  • Only LLM services will work
```

---

### Сценарий 3: Частичный сбой 🔶

```
✓ Docker Desktop
✗ Qdrant (port 6333)
✗ Neo4j (port 7474)
✓ Ollama (port 11434)
✓ Memory AI MCP

Status: 3/5 services operational

⚠ Some Docker services are not responding

Try running: scripts/infrastructure/start-docker-services.bat
```

**Действие:**
```bash
scripts\infrastructure\restart-docker-services.bat
```

---

## Ручное управление сервисами

### Запуск всех сервисов

```bash
scripts\infrastructure\start-docker-services.bat
```

**Что происходит:**
1. Проверка Docker Desktop
2. Автозапуск Docker если не работает
3. Ожидание готовности
4. Запуск docker-compose
5. Проверка статуса

**Время:** ~40-60 секунд

---

### Остановка сервисов

```bash
scripts\infrastructure\stop-docker-services.bat
```

**Использование:**
- Перед выключением компьютера
- Для освобождения ресурсов
- Перед обновлением Docker

---

### Перезапуск сервисов

```bash
scripts\infrastructure\restart-docker-services.bat
```

**Когда использовать:**
- После изменения конфигурации
- При зависании контейнеров
- После обновления образов

---

### Проверка статуса (детальная)

```bash
scripts\infrastructure\check-all-services.bat
```

**Вывод:**
```
========================================
AI Memory System - Health Check
========================================

[1/6] Docker Desktop...
[OK] Docker is available

[2/6] Qdrant Vector DB (port 6333)...
[OK] Qdrant is responding

[3/6] Neo4j Graph DB (port 7474)...
[OK] Neo4j is responding

[4/6] Ollama LLM Server (port 11434)...
[OK] Ollama is responding

[5/6] TimescaleDB (port 5432)...
[OK] TimescaleDB port is open

[6/6] Memory AI MCP Server...
[OK] Memory AI MCP is connected

========================================
Health Check Summary
========================================
Total services checked: 6
Services OK: 6
Services FAILED: 0

System Ready: 100%

[SUCCESS] All systems operational!
```

---

### Быстрая проверка

```bash
scripts\infrastructure\quick-status.bat
```

**Вывод:**
```
Checking services...
1c-qdrant: Up 5 minutes
1c-neo4j: Up 5 minutes
1c-timescaledb: Up 5 minutes
Docker: OK
Ollama: OK
Memory AI MCP: CONNECTED
```

---

## Конфигурация хуков

### Отключение автоматической проверки

**Вариант 1: Переименовать хук**
```bash
mv .claude/hooks/pre-prompt.hook.sh .claude/hooks/pre-prompt.hook.sh.disabled
```

**Вариант 2: Удалить хук**
```bash
rm .claude/hooks/pre-prompt.hook.sh
```

**Вариант 3: Создать флаг "уже проверено"**
```bash
touch /tmp/claude-code-infrastructure-checked
```

### Изменение частоты проверки

Отредактируйте `.claude/hooks/pre-prompt.hook.sh`:

```bash
# Текущее значение: 1 час (3600 секунд)
(sleep 3600 && rm -f "$STATUS_FILE") &

# Изменить на 30 минут:
(sleep 1800 && rm -f "$STATUS_FILE") &

# Изменить на 2 часа:
(sleep 7200 && rm -f "$STATUS_FILE") &
```

### Отключение интерактивного запроса

Отредактируйте `.claude/hooks/pre-prompt.hook.sh`, найдите:

```bash
if [ $DOCKER_OK -eq 0 ]; then
    echo -e "${YELLOW}⚠${NC} Docker is not running"
    echo ""
    echo "Would you like to start Docker services? (y/n)"
    read -r -n 1 -t 10 response
    # ...
fi
```

**Вариант A: Автозапуск без вопроса**
```bash
if [ $DOCKER_OK -eq 0 ]; then
    echo "Starting Docker services automatically..."
    cmd.exe /c "D:\1C-Enterprise_Framework\scripts\infrastructure\start-docker-services.bat"
fi
```

**Вариант B: Только предупреждение**
```bash
if [ $DOCKER_OK -eq 0 ]; then
    echo -e "${YELLOW}⚠${NC} Docker is not running"
    echo "Run: scripts/infrastructure/start-docker-services.bat"
fi
```

---

## Устранение проблем

### Проблема: Хук не срабатывает

**Решения:**

1. **Проверьте права (Linux/Mac):**
   ```bash
   chmod +x .claude/hooks/pre-prompt.hook.sh
   ```

2. **Проверьте наличие bash:**
   ```bash
   which bash
   # Должно вывести путь, например: /usr/bin/bash
   ```

3. **Проверьте синтаксис:**
   ```bash
   bash -n .claude/hooks/pre-prompt.hook.sh
   # Не должно быть ошибок
   ```

4. **Запустите вручную для теста:**
   ```bash
   bash .claude/hooks/pre-prompt.hook.sh
   ```

---

### Проблема: Docker не запускается автоматически

**Решения:**

1. **Проверьте путь к Docker Desktop:**

   Откройте `scripts\infrastructure\start-docker-services.bat`, найдите:
   ```batch
   if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe"
   ```

   Если у вас другой путь, измените его.

2. **Запустите Docker Desktop вручную:**
   ```
   start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
   ```

3. **Проверьте права администратора:**

   Запустите CMD от имени администратора и выполните скрипт.

---

### Проблема: Сервисы не отвечают после запуска

**Решения:**

1. **Подождите дольше:**

   Некоторые сервисы (особенно Neo4j) могут запускаться до 60 секунд.

2. **Проверьте логи:**
   ```bash
   docker-compose -f ai-memory-system/docker/docker-compose.yml logs
   ```

3. **Перезапустите контейнеры:**
   ```bash
   scripts\infrastructure\restart-docker-services.bat
   ```

4. **Проверьте docker-compose.yml:**
   ```bash
   cd ai-memory-system
   docker-compose -f docker/docker-compose.yml config
   ```

---

### Проблема: Флаг проверки не сбрасывается

**Решения:**

1. **Удалите флаг вручную:**
   ```bash
   rm /tmp/claude-code-infrastructure-checked
   ```

2. **Проверьте фоновый процесс:**
   ```bash
   ps aux | grep sleep
   # Если есть зависший процесс, убейте его
   ```

---

## Продвинутое использование

### Создание своих хуков

**Доступные типы хуков:**

1. **pre-prompt** - Перед каждым промптом
2. **post-prompt** - После каждого промпта
3. **session-start** - При запуске сессии
4. **session-end** - При завершении сессии
5. **tool-call** - При вызове инструмента

**Пример нового хука:**

```bash
# .claude/hooks/session-start.hook.sh
#!/bin/bash

echo "🎉 Welcome to AI Memory System!"
echo "Session started at: $(date)"

# Загрузить конфигурацию проекта
source .env
```

### Интеграция с CI/CD

Используйте скрипты для автоматизации:

```yaml
# .github/workflows/test.yml
- name: Start infrastructure
  run: scripts/infrastructure/start-docker-services.bat

- name: Check health
  run: scripts/infrastructure/check-all-services.bat

- name: Run tests
  run: pytest tests/

- name: Stop infrastructure
  run: scripts/infrastructure/stop-docker-services.bat
```

---

## Часто задаваемые вопросы

### В: Будет ли хук запускаться при каждом сообщении?

**О:** Нет, только один раз за сессию (или раз в час). Создается флаг `/tmp/claude-code-infrastructure-checked`.

---

### В: Можно ли отключить автозапрос Docker?

**О:** Да, см. раздел "Конфигурация хуков" → "Отключение интерактивного запроса".

---

### В: Как часто проверяется статус?

**О:** По умолчанию один раз при первом промпте, затем раз в час. Настраивается в `.claude/hooks/pre-prompt.hook.sh`.

---

### В: Влияют ли хуки на производительность?

**О:** Минимально. Проверка занимает 1-3 секунды и выполняется только раз за сессию.

---

### В: Что если я хочу всегда проверять статус?

**О:** Удалите строки с созданием флага в `pre-prompt.hook.sh`:
```bash
# Закомментируйте или удалите:
# touch "$STATUS_FILE"
# (sleep 3600 && rm -f "$STATUS_FILE") &
```

---

## Поддержка

**Проблемы или вопросы?**

1. Проверьте логи: `docker-compose logs`
2. Запустите проверку: `scripts/infrastructure/check-all-services.bat`
3. Прочитайте README: `.claude/hooks/README.md`

---

**Версия:** 1.0
**Дата:** 2025-11-04
**Автор:** Claude Code Assistant
