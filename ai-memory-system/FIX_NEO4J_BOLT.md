# Исправление Neo4j Bolt Interface

## Диагноз

**Проблема**: Neo4j Bolt интерфейс (порт 7687) не отвечает.

**Статус**:
- ✓ HTTP интерфейс (7474) работает
- ✗ Bolt интерфейс (7687) НЕ работает

**Влияние**: Без Bolt невозможно подключение из Python/MCP сервера к Neo4j.

---

## Решение 1: Использовать Docker (Рекомендуется) ⭐

Это самый простой и надежный способ получить рабочий Neo4j с Bolt.

### Шаг 1: Проверьте Docker

```bash
docker --version
```

Если Docker не установлен: https://www.docker.com/products/docker-desktop

### Шаг 2: Запустите Neo4j

Запустите файл:
```
D:\1C-Enterprise_Framework\ai-memory-system\start_neo4j_docker.bat
```

Или выполните вручную:
```bash
docker run -d ^
  --name neo4j-mcp ^
  -p 7474:7474 -p 7687:7687 ^
  -e NEO4J_AUTH=neo4j/mcp12345 ^
  -e NEO4J_server_bolt_enabled=true ^
  -e NEO4J_server_bolt_listen__address=:7687 ^
  -v neo4j-mcp-data:/data ^
  neo4j:latest
```

### Шаг 3: Подождите 30 секунд

Neo4j требует время на запуск.

### Шаг 4: Проверьте доступность

```bash
# Проверка HTTP
curl http://localhost:7474

# Проверка Bolt (должна появиться ошибка подключения, но порт должен отвечать)
timeout 5 bash -c "echo > /dev/tcp/localhost/7687"
```

### Шаг 5: Установите пароль

```powershell
# PowerShell
$env:NEO4J_PASSWORD="mcp12345"

# Или в конфигурации Claude Code
# %APPDATA%\Claude\claude_desktop_config.json
# "NEO4J_PASSWORD": "mcp12345"
```

### Шаг 6: Перезапустите Claude Code

1. Закройте все окна Claude Code
2. Запустите заново

### Шаг 7: Проверьте подключение

```bash
cd D:\1C-Enterprise_Framework\ai-memory-system
python test_neo4j_password.py
```

**Пароль**: `mcp12345`

---

## Решение 2: Исправить существующий Neo4j Desktop

Если у вас уже установлен Neo4j Desktop и вы хотите его исправить.

### Шаг 1: Откройте Neo4j Desktop

1. Запустите Neo4j Desktop
2. Выберите вашу базу данных
3. **Остановите** её (кнопка Stop)

### Шаг 2: Откройте настройки

1. Нажмите на **три точки** (⋮) справа от базы
2. Выберите **Settings** или **Manage**
3. Найдите **Configuration files**

### Шаг 3: Проверьте neo4j.conf

Откройте файл `neo4j.conf` и найдите секцию Bolt:

```conf
# Bolt connector
server.bolt.enabled=true
server.bolt.listen_address=:7687
```

Убедитесь, что:
- `server.bolt.enabled=true` (НЕ закомментирована)
- `server.bolt.listen_address=:7687` (правильный порт)

### Шаг 4: Сохраните и перезапустите

1. Сохраните `neo4j.conf`
2. **Запустите** базу данных заново
3. Подождите 20-30 секунд

### Шаг 5: Проверьте Bolt

```bash
timeout 5 bash -c "echo > /dev/tcp/localhost/7687"
```

Если команда завершается без ошибки - Bolt работает!

### Шаг 6: Найдите пароль

В Neo4j Desktop:
1. **Settings** → **Database**
2. Там должен быть пароль или возможность его изменить

Или сбросьте пароль:
1. Остановите базу
2. В Settings найдите кнопку **Reset Password**
3. Установите новый: например, `mcp12345`
4. Запустите базу

---

## Решение 3: Переустановить Neo4j Desktop

Если ничего не помогает.

### Шаг 1: Удалите старый Neo4j

1. Удалите Neo4j Desktop через "Программы и компоненты"
2. Удалите данные:
   ```
   %LOCALAPPDATA%\Neo4j
   %APPDATA%\Neo4j
   ```

### Шаг 2: Скачайте Neo4j Desktop

https://neo4j.com/download/

### Шаг 3: Установите и создайте базу

1. Установите Neo4j Desktop
2. Создайте **новую** базу данных
3. При создании установите пароль: `mcp12345`
4. Запустите базу

### Шаг 4: Проверьте

```bash
# HTTP
curl http://localhost:7474

# Bolt
timeout 5 bash -c "echo > /dev/tcp/localhost/7687"

# Python connection
cd D:\1C-Enterprise_Framework\ai-memory-system
python test_neo4j_password.py
```

---

## Решение 4: Запустить MCP сервер БЕЗ Neo4j

Если вам срочно нужен MCP сервер, а Neo4j можно настроить позже.

### Преимущества

- ✅ Работает сразу
- ✅ 4 из 5 инструментов доступны
- ✅ Не нужен пароль Neo4j

### Недостатки

- ❌ Инструмент `analyze_graph` не работает

### Инструкция

См. файл `ALTERNATIVE_NEO4J_SETUP.md` → **Решение 1**

Кратко:
1. Откройте `%APPDATA%\Claude\claude_desktop_config.json`
2. Удалите строку `"NEO4J_PASSWORD": "your_password"`
3. Перезапустите Claude Code

---

## Проверка после исправления

### Тест 1: Проверка портов

```bash
# HTTP (должен ответить)
curl http://localhost:7474

# Bolt (не должно быть ошибки "Connection refused")
timeout 5 bash -c "echo > /dev/tcp/localhost/7687"
```

### Тест 2: Python подключение

```bash
cd D:\1C-Enterprise_Framework\ai-memory-system
python test_neo4j_password.py
```

Должно показать: **SUCCESS! Working password: mcp12345**

### Тест 3: MCP сервер

```bash
cd D:\1C-Enterprise_Framework\ai-memory-system
set NEO4J_PASSWORD=mcp12345
python mcp_server\server_fastmcp.py
```

Должно показать:
```
INFO:__main__:=== Starting AI Memory MCP Server (FastMCP) ===
INFO:__main__:✓ Neo4j Service connected
INFO:__main__:✓ LLM Service
INFO:__main__:✓ Qdrant Vector Store
```

---

## Рекомендуемый порядок действий

1. **Попробуйте Решение 1** (Docker) - самый простой и быстрый
   - Требует Docker Desktop
   - Гарантированно работает
   - Известный пароль: `mcp12345`

2. Если Docker недоступен → **Решение 2** (исправить существующий)
   - Проверьте `neo4j.conf`
   - Включите Bolt connector
   - Найдите/сбросьте пароль

3. Если ничего не помогло → **Решение 4** (без Neo4j)
   - Работает сразу
   - 4 из 5 инструментов доступны
   - Neo4j можно добавить позже

---

## Частые ошибки

### "Connection refused" на порту 7687

**Причина**: Bolt connector не включен или Neo4j не запущен.

**Решение**:
- Проверьте `server.bolt.enabled=true` в `neo4j.conf`
- Перезапустите Neo4j

### "ServiceUnavailable"

**Причина**: Neo4j запущен, но Bolt не отвечает.

**Решение**:
- Проверьте логи Neo4j
- Убедитесь что порт 7687 не занят другим процессом

### "Authentication failed"

**Причина**: Неверный пароль.

**Решение**:
- Сбросьте пароль через Neo4j Desktop
- Или используйте Docker с известным паролем

---

## Поддержка

После исправления у вас должно быть:

- ✅ Neo4j HTTP (7474) - работает
- ✅ Neo4j Bolt (7687) - работает
- ✅ Известный пароль
- ✅ MCP сервер подключается к Neo4j

**Файлы для справки**:
- `start_neo4j_docker.bat` - запуск через Docker
- `test_neo4j_password.py` - проверка пароля
- `CHECK_NEO4J_PASSWORD.md` - способы найти пароль
- `ALTERNATIVE_NEO4J_SETUP.md` - работа без Neo4j
