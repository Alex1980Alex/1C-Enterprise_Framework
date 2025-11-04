# Инструкция по установке Docker Desktop

## Статус: ЗАГРУЗКА В ПРОЦЕССЕ ⏳

Установщик Docker Desktop загружается автоматически (~550MB)

**Текущий прогресс**: Проверяется...
**Путь к файлу**: `%TEMP%\DockerDesktopInstaller.exe`

---

## После завершения загрузки

### Шаг 1: Проверить загруженный файл

```bash
# Проверить наличие файла
dir %TEMP%\DockerDesktopInstaller.exe

# Проверить размер (должен быть ~550MB)
```

### Шаг 2: Запустить установщик

**Вариант А: Из командной строки**
```bash
%TEMP%\DockerDesktopInstaller.exe install
```

**Вариант Б: Двойной клик**
1. Откройте `%TEMP%` в проводнике:
   - Win+R → `%TEMP%` → Enter
2. Найдите `DockerDesktopInstaller.exe`
3. Двойной клик → согласитесь с UAC

### Шаг 3: Процесс установки

1. **Welcome Screen**
   - Click "OK"

2. **Configuration**
   - [x] Use WSL 2 instead of Hyper-V (recommended)
   - [ ] Add shortcut to desktop
   - Click "OK"

3. **Installation**
   - Подождите 5-10 минут
   - Установка компонентов

4. **Installation Successful**
   - Click "Close"
   - **ВАЖНО**: Перезагрузите компьютер

### Шаг 4: После перезагрузки

1. **Запустите Docker Desktop**
   - Найдите в Start Menu
   - Или из трея (правый нижний угол)

2. **Service Agreement**
   - Прочитайте и согласитесь
   - Click "Accept"

3. **Docker Tutorial** (опционально)
   - Можете пропустить: "Skip tutorial"

4. **Дождитесь запуска**
   - Иконка Docker в трее станет зеленой
   - Статус: "Docker Desktop is running"

### Шаг 5: Проверка установки

```bash
# В новой командной строке (важно - новой!)
docker --version
# Должно вывести: Docker version 24.x.x, build ...

docker ps
# Должно вывести пустой список контейнеров (это ОК)

docker info
# Должно показать подробную информацию о Docker
```

---

## Требования к системе ✅

- [x] Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041+)
- [x] WSL 2 (будет установлен автоматически, если отсутствует)
- [x] 4GB RAM (у вас 32GB ✅)
- [x] Virtualization enabled in BIOS ✅

---

## Возможные проблемы

### WSL 2 не установлен

Если Docker просит установить WSL 2:

```bash
# Запустите PowerShell от администратора
wsl --install
wsl --set-default-version 2

# Перезагрузите компьютер
```

### Hyper-V конфликты

Если появляется ошибка про Hyper-V:

1. Откройте "Turn Windows features on or off"
2. Включите:
   - [x] Virtual Machine Platform
   - [x] Windows Subsystem for Linux
3. Перезагрузите

### Docker не запускается

```bash
# Полная переустановка
1. Settings → Reset → Uninstall
2. Удалите: %LOCALAPPDATA%\Docker
3. Перезагрузка
4. Установите снова
```

---

## Размер на диске

- Установка Docker Desktop: ~3GB
- Образы контейнеров (наш проект): ~5GB
- **Итого**: ~8GB

---

## Настройки после установки (опционально)

### 1. Resources

Docker Desktop → Settings → Resources:

```
CPUs: 8 (из 16 доступных)
Memory: 8 GB (из 32 GB)
Swap: 2 GB
Disk image size: 100 GB
```

### 2. Docker Engine

Оставить по умолчанию, или добавить:

```json
{
  "experimental": false,
  "features": {
    "buildkit": true
  }
}
```

---

## После успешной установки

Вернитесь к Claude Code и напишите:
```
"Docker установлен"
```

Я продолжу с запуском сервисов и установкой Ollama!

---

**Время установки**: ~15-20 минут (включая перезагрузку)
**Текущий этап**: Загрузка установщика (в процессе)
