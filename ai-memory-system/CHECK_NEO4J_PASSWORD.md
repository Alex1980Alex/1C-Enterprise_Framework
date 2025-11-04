# Как проверить пароль Neo4j

## Способ 1: Через Neo4j Browser (Рекомендуется)

1. Откройте браузер и перейдите по адресу:
   ```
   http://localhost:7474
   ```

2. Вы увидите форму входа с полями:
   - **Connect URL**: `bolt://localhost:7687` (уже заполнено)
   - **Username**: `neo4j`
   - **Password**: (нужно узнать)

3. Попробуйте следующие стандартные пароли по порядку:
   - `neo4j` (стандартный пароль по умолчанию)
   - `password`
   - `admin`
   - `12345678`

4. **Если вход успешен** - вы увидите рабочую область Neo4j Browser
   - Запомните пароль, который сработал!

5. **Установите этот пароль в переменную окружения**:

   **PowerShell**:
   ```powershell
   $env:NEO4J_PASSWORD="найденный_пароль"
   ```

   **CMD**:
   ```cmd
   set NEO4J_PASSWORD=найденный_пароль
   ```

## Способ 2: Проверка через Python

Создайте файл `test_pass.py`:

```python
from neo4j import GraphDatabase

# Попробуйте разные пароли
passwords = ["neo4j", "password", "admin", "12345678"]

for pwd in passwords:
    try:
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", pwd)
        )
        with driver.session() as session:
            session.run("RETURN 1").single()
        driver.close()

        print(f"SUCCESS! Password is: {pwd}")
        print(f"\nSet it with:")
        print(f'$env:NEO4J_PASSWORD="{pwd}"')
        break
    except:
        print(f"'{pwd}' - not working")
```

Запустите:
```bash
python test_pass.py
```

## Способ 3: Посмотреть в логах (если Neo4j только установлен)

Если Neo4j был только что установлен, пароль по умолчанию:
- **Username**: `neo4j`
- **Password**: `neo4j`

При первом входе Neo4j попросит сменить пароль.

## Способ 4: Сброс пароля (если забыли)

1. **Остановите Neo4j**:
   ```bash
   # Windows (Если установлен как служба)
   net stop neo4j

   # Или через Neo4j Desktop - кнопка Stop
   ```

2. **Удалите файл auth**:
   ```bash
   # Путь зависит от установки, обычно:
   # Neo4j Desktop
   C:\Users\<username>\AppData\Local\Neo4j\Relate\Data\dbmss\dbms-<id>\data\dbms\auth

   # Или стандартная установка
   C:\Program Files\Neo4j\<version>\data\dbms\auth
   ```

3. **Запустите Neo4j снова**:
   - Пароль сбросится на `neo4j/neo4j`
   - При первом входе попросит установить новый

## После того, как нашли пароль

### 1. Установите переменную окружения

**Для текущей сессии PowerShell**:
```powershell
$env:NEO4J_PASSWORD="ваш_пароль"
```

**Для постоянной установки (Windows)**:
```powershell
[System.Environment]::SetEnvironmentVariable('NEO4J_PASSWORD', 'ваш_пароль', 'User')
```

### 2. Или создайте файл .env

В папке `ai-memory-system` создайте файл `.env`:
```bash
NEO4J_PASSWORD=ваш_пароль
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
```

### 3. Проверьте, что MCP сервер работает

```bash
cd D:\1C-Enterprise_Framework\ai-memory-system
python mcp_server\server_fastmcp.py
```

Должны увидеть:
```
INFO:__main__:=== Starting AI Memory MCP Server (FastMCP) ===
INFO:__main__:=== Инициализация сервисов ===
INFO:__main__:✓ LLM Service
INFO:__main__:✓ Qdrant Vector Store
INFO:__main__:✓ Neo4j Service
```

Если видите `✓ Neo4j Service` - значит пароль правильный!

## Проверка текущего пароля в переменных окружения

**PowerShell**:
```powershell
echo $env:NEO4J_PASSWORD
```

**CMD**:
```cmd
echo %NEO4J_PASSWORD%
```

Если пусто - переменная не установлена.

## Troubleshooting

### Neo4j не запущен

```bash
# Проверка
curl http://localhost:7474

# Если ошибка - Neo4j не запущен
# Запустите через Neo4j Desktop или как службу Windows
```

### Ошибка "ServiceUnavailable"

- Neo4j запущен, но не отвечает на bolt://localhost:7687
- Проверьте порт в конфигурации Neo4j
- Убедитесь, что bolt connector включен

### Ошибка "Authentication failed"

- Неверный пароль
- Попробуйте другие пароли из списка
- Или сбросьте пароль (способ 4)

## Частые пароли Neo4j

1. `neo4j` - стандартный по умолчанию
2. `password` - часто используется
3. `admin` - альтернативный вариант
4. `your_password` - заглушка в коде (не работает!)

## Контакты для помощи

Если ничего не помогло:
1. Проверьте логи Neo4j в папке `logs/`
2. Посмотрите конфигурацию в `conf/neo4j.conf`
3. Обратитесь к документации Neo4j
