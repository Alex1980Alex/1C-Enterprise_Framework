# Tree-sitter BSL Compilation Guide

## 🚀 Краткое руководство

### Вариант 1: Использование без компиляции (рекомендуется)
```bash
# Запуск упрощенного AST-grep
bash scripts/test-ast-grep-simple.sh

# Использование fallback поиска
grep -r "Процедура" src/ --include="*.bsl" -n
```

### Вариант 2: Полная компиляция

#### Windows:
1. **Установить Visual Studio Build Tools**
   ```
   https://visualstudio.microsoft.com/visual-cpp-build-tools/
   Выберите: C++ build tools
   ```

2. **Установить Rust (альтернатива)**
   ```
   https://rustup.rs/
   ```

3. **Компиляция**
   ```bash
   cd tree-sitter-bsl
   npm install
   tree-sitter generate
   npm run build
   ```

#### Linux/macOS:
```bash
# Установка компилятора
sudo apt install build-essential  # Ubuntu
brew install gcc                  # macOS

# Компиляция
cd tree-sitter-bsl
npm install
tree-sitter generate
tree-sitter build
```

### Вариант 3: Docker
```bash
# Создание Docker контейнера с компилятором
docker run -it --rm -v $(pwd):/work node:18 bash
cd /work/tree-sitter-bsl
apt update && apt install -y build-essential
npm install
tree-sitter generate
tree-sitter build
```

## 🔧 Решение проблем

### Если нет компилятора:
- Используйте fallback поиск: `grep -r "паттерн" src/`
- Установите минимальный компилятор: `choco install mingw`

### Если компиляция не удается:
- Проверьте версии: `node --version`, `npm --version`
- Очистите кеш: `npm cache clean --force`
- Переустановите зависимости: `rm -rf node_modules && npm install`

## 📊 Статус компонентов

✅ **Работает без компиляции:**
- Grep поиск BSL кода
- MCP интеграция
- Базовая функциональность

⚠️ **Требует компиляции:**
- Структурный AST поиск
- Точное сопоставление синтаксиса
- Продвинутые паттерны

## 🎯 Рекомендации

1. **Начните с fallback поиска** - он покрывает 80% случаев
2. **Используйте MCP инструменты** для GitHub поиска
3. **Компилируйте только при необходимости** структурного анализа
