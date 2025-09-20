# MCP Servers Configuration Documentation

## Установленные MCP серверы

### 1. Task Master AI
**Статус:** ✅ Установлен и настроен
**Команда:** `task-master-ai`
**Описание:** Управление задачами и проектами с AI-поддержкой
**Конфигурация:**
```json
"task-master-ai": {
    "type": "stdio",
    "command": "task-master-ai",
    "args": []
}
```

### 2. Serena Framework
**Статус:** ✅ Установлен и настроен
**Команда:** `/mnt/d/1C-Enterprise_Cursor_Framework/serena-unified/run_mcp_server.sh`
**Описание:** Фреймворк для работы с 1C проектами
**Конфигурация:**
```json
"serena-framework": {
    "type": "stdio",
    "command": "/mnt/d/1C-Enterprise_Cursor_Framework/serena-unified/run_mcp_server.sh",
    "args": [],
    "env": {
        "PYTHONPATH": "/mnt/d/1C-Enterprise_Cursor_Framework/serena-unified/src"
    }
}
```

### 3. GitHub MCP
**Статус:** ✅ Установлен и настроен
**Команда:** `@modelcontextprotocol/server-github`
**Описание:** Интеграция с GitHub API для управления репозиториями
**Конфигурация:**
```json
"github": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
    }
}
```

### 4. Brave Search MCP
**Статус:** ✅ Установлен и настроен
**Команда:** `@modelcontextprotocol/server-brave-search`
**Описание:** Поиск в интернете через Brave Search API
**Конфигурация:**
```json
"brave-search": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
    "env": {
        "BRAVE_API_KEY": "your_api_key_here"
    }
}
```

### 5. Rust Filesystem MCP
**Статус:** ✅ Установлен и настроен
**Команда:** `/home/lex/.local/bin/rust-mcp-filesystem`
**Описание:** Быстрый доступ к файловой системе через Rust
**Конфигурация:**
```json
"rust-filesystem": {
    "type": "stdio",
    "command": "/home/lex/.local/bin/rust-mcp-filesystem",
    "args": [
        "--allow-write",
        "/mnt/d/1C-Enterprise_Cursor_Framework"
    ]
}
```

### 6. Sequential Thinking MCP
**Статус:** ✅ Установлен (10.09.2025)
**Команда:** `@modelcontextprotocol/server-sequential-thinking`
**Описание:** Последовательный анализ и декомпозиция сложных задач
**Конфигурация:**
```json
"sequential-thinking": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
}
```

### 7. PostgreSQL MCP (Enhanced)
**Статус:** ✅ Установлен (10.09.2025)
**Команда:** `enhanced-postgres-mcp-server`
**Описание:** Расширенный сервер для работы с PostgreSQL базами данных
**Конфигурация:**
```json
"postgres": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "enhanced-postgres-mcp-server"],
    "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:password@localhost:5432/database"
    }
}
```
**Примечание:** Необходимо настроить строку подключения к вашей PostgreSQL базе данных

### 8. MySQL MCP
**Статус:** ✅ Установлен (10.09.2025)
**Команда:** `@benborla29/mcp-server-mysql`
**Описание:** MCP сервер для работы с MySQL базами данных с поддержкой чтения и записи
**Конфигурация:**
```json
"mysql": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@benborla29/mcp-server-mysql"],
    "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "root",
        "MYSQL_PASS": "password",
        "MYSQL_DB": "database",
        "ALLOW_WRITE": "false"
    }
}
```
**Параметры:**
- `MYSQL_HOST`: Адрес MySQL сервера
- `MYSQL_PORT`: Порт подключения (по умолчанию 3306)
- `MYSQL_USER`: Имя пользователя БД
- `MYSQL_PASS`: Пароль пользователя
- `MYSQL_DB`: Имя базы данных
- `ALLOW_WRITE`: Разрешить операции записи (true/false)

## Проверка работоспособности

### Тестовый чек-лист

#### Sequential Thinking MCP
- [ ] Запуск сервера без ошибок
- [ ] Доступность команд анализа
- [ ] Корректная декомпозиция задач
- [ ] Сохранение контекста между вызовами

#### PostgreSQL MCP
- [ ] Подключение к базе данных
- [ ] Выполнение SELECT запросов
- [ ] Выполнение INSERT/UPDATE/DELETE операций
- [ ] Работа с транзакциями
- [ ] Обработка ошибок подключения

#### MySQL MCP
- [ ] Подключение к MySQL серверу
- [ ] Выполнение SELECT запросов
- [ ] Проверка схемы базы данных
- [ ] Выполнение INSERT/UPDATE/DELETE (если ALLOW_WRITE=true)
- [ ] Работа с несколькими базами данных
- [ ] Обработка ошибок подключения

## Команды для проверки

### Проверка установки пакетов
```bash
# Проверка глобально установленных пакетов
npm list -g @modelcontextprotocol/server-sequential-thinking
npm list -g enhanced-postgres-mcp-server
npm list -g @benborla29/mcp-server-mysql

# Проверка версий
npx @modelcontextprotocol/server-sequential-thinking --version
npx enhanced-postgres-mcp-server --version
npx @benborla29/mcp-server-mysql --version
```

### Тестирование Sequential Thinking
```bash
# В Claude Code после перезапуска
# Используйте команды sequential thinking для анализа
```

### Тестирование PostgreSQL
```bash
# Проверка подключения (требуется настроенная БД)
psql -U user -h localhost -d database -c "SELECT version();"
```

## Настройка PostgreSQL

### Установка PostgreSQL (если не установлен)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Создание пользователя и базы данных
sudo -u postgres createuser --interactive
sudo -u postgres createdb mydatabase
```

### Настройка строки подключения PostgreSQL
Измените в `.mcp.json`:
```json
"POSTGRES_CONNECTION_STRING": "postgresql://your_user:your_password@localhost:5432/your_database"
```

## Настройка MySQL

### Установка MySQL (если не установлен)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install mysql-server mysql-client

# Создание пользователя и базы данных
sudo mysql
CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'mypassword';
CREATE DATABASE mydatabase;
GRANT ALL PRIVILEGES ON mydatabase.* TO 'myuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Настройка параметров подключения MySQL
Измените в `.mcp.json`:
```json
"env": {
    "MYSQL_HOST": "localhost",
    "MYSQL_PORT": "3306",
    "MYSQL_USER": "myuser",
    "MYSQL_PASS": "mypassword",
    "MYSQL_DB": "mydatabase",
    "ALLOW_WRITE": "true"  // Установите true для разрешения записи
}
```

## Возможные проблемы и решения

### Sequential Thinking MCP
**Проблема:** Сервер не запускается
**Решение:** Проверьте версию Node.js (требуется >= 18.0.0)

### PostgreSQL MCP
**Проблема:** Ошибка подключения к БД
**Решение:** 
1. Проверьте, что PostgreSQL запущен: `sudo systemctl status postgresql`
2. Проверьте правильность строки подключения
3. Убедитесь, что пользователь имеет права доступа к БД

### MySQL MCP
**Проблема:** Ошибка подключения к MySQL
**Решение:**
1. Проверьте, что MySQL запущен: `sudo systemctl status mysql`
2. Проверьте параметры подключения (хост, порт, пользователь, пароль)
3. Убедитесь, что база данных существует
4. Проверьте права пользователя: `SHOW GRANTS FOR 'user'@'localhost';`

**Проблема:** Ошибка при операциях записи
**Решение:**
1. Установите `"ALLOW_WRITE": "true"` в конфигурации
2. Убедитесь, что пользователь имеет права на запись в БД

## Дополнительные ресурсы

- [Sequential Thinking MCP Documentation](https://github.com/modelcontextprotocol/server-sequential-thinking)
- [Enhanced PostgreSQL MCP Documentation](https://www.npmjs.com/package/enhanced-postgres-mcp-server)
- [MySQL MCP Server Documentation](https://github.com/benborla/mcp-server-mysql)
- [MCP Protocol Specification](https://github.com/modelcontextprotocol/specification)

---

**Последнее обновление:** 10.09.2025
**Автор:** Claude Code Assistant