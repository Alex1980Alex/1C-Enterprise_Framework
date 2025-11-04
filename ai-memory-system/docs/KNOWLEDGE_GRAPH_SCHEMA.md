# Knowledge Graph Schema для BSL Code

Схема графа знаний для хранения структуры и зависимостей 1C BSL кода в Neo4j.

## Обзор архитектуры

```
Project
  └─> Module
       ├─> Function
       ├─> Procedure
       └─> Variable
```

---

## Node Labels (Типы узлов)

### 1. Project
Корневой узел проекта

**Свойства:**
- `id` (string, unique): UUID проекта
- `name` (string): Название проекта
- `path` (string): Путь к корневой директории
- `created_at` (datetime): Дата создания
- `indexed_at` (datetime): Дата индексации
- `description` (string, optional): Описание проекта

**Индексы:**
```cypher
CREATE INDEX project_id_idx FOR (p:Project) ON (p.id);
CREATE INDEX project_name_idx FOR (p:Project) ON (p.name);
```

---

### 2. Module
BSL модуль (файл .bsl)

**Свойства:**
- `id` (string, unique): UUID модуля
- `name` (string): Имя модуля
- `file_path` (string): Относительный путь к файлу
- `module_type` (string): Тип модуля (ObjectModule, ManagerModule, CommonModule, FormModule)
- `functions_count` (int): Количество функций
- `procedures_count` (int): Количество процедур
- `variables_count` (int): Количество переменных
- `lines_count` (int): Количество строк кода
- `file_size` (int): Размер файла в байтах
- `content_hash` (string): SHA256 хэш содержимого
- `indexed_at` (datetime): Дата индексации
- `is_export` (boolean): Является ли модуль экспортным

**Индексы:**
```cypher
CREATE INDEX module_id_idx FOR (m:Module) ON (m.id);
CREATE INDEX module_type_idx FOR (m:Module) ON (m.module_type);
CREATE INDEX module_path_idx FOR (m:Module) ON (m.file_path);
CREATE FULLTEXT INDEX module_name_search FOR (m:Module) ON EACH [m.name];
```

---

### 3. Function
Функция BSL

**Свойства:**
- `id` (string, unique): UUID функции
- `name` (string): Имя функции
- `name_ru` (string, optional): Русское имя
- `signature` (string): Сигнатура функции
- `parameters` (list[string]): Список параметров
- `return_type` (string, optional): Тип возвращаемого значения
- `is_export` (boolean): Экспортная функция
- `line_start` (int): Начальная строка
- `line_end` (int): Конечная строка
- `complexity` (int, optional): Цикломатическая сложность
- `calls_count` (int): Количество вызовов других функций
- `description` (string, optional): Описание из комментариев

**Индексы:**
```cypher
CREATE INDEX function_id_idx FOR (f:Function) ON (f.id);
CREATE INDEX function_export_idx FOR (f:Function) ON (f.is_export);
CREATE FULLTEXT INDEX function_name_search FOR (f:Function) ON EACH [f.name];
```

---

### 4. Procedure
Процедура BSL

**Свойства:**
- `id` (string, unique): UUID процедуры
- `name` (string): Имя процедуры
- `name_ru` (string, optional): Русское имя
- `signature` (string): Сигнатура процедуры
- `parameters` (list[string]): Список параметров
- `is_export` (boolean): Экспортная процедура
- `line_start` (int): Начальная строка
- `line_end` (int): Конечная строка
- `complexity` (int, optional): Цикломатическая сложность
- `calls_count` (int): Количество вызовов
- `description` (string, optional): Описание

**Индексы:**
```cypher
CREATE INDEX procedure_id_idx FOR (p:Procedure) ON (p.id);
CREATE INDEX procedure_export_idx FOR (p:Procedure) ON (p.is_export);
CREATE FULLTEXT INDEX procedure_name_search FOR (p:Procedure) ON EACH [p.name];
```

---

### 5. Variable
Переменная BSL

**Свойства:**
- `id` (string, unique): UUID переменной
- `name` (string): Имя переменной
- `scope` (string): Область видимости (module, function, procedure)
- `is_export` (boolean): Экспортная переменная
- `line_number` (int): Номер строки объявления
- `initial_value` (string, optional): Начальное значение

**Индексы:**
```cypher
CREATE INDEX variable_id_idx FOR (v:Variable) ON (v.id);
CREATE INDEX variable_scope_idx FOR (v:Variable) ON (v.scope);
```

---

### 6. Query
SQL/BSL запрос

**Свойства:**
- `id` (string, unique): UUID запроса
- `query_text` (string): Текст запроса
- `query_type` (string): Тип (SELECT, UPDATE, etc.)
- `line_start` (int): Начальная строка
- `line_end` (int): Конечная строка
- `tables_used` (list[string]): Используемые таблицы

**Индексы:**
```cypher
CREATE INDEX query_id_idx FOR (q:Query) ON (q.id);
CREATE INDEX query_type_idx FOR (q:Query) ON (q.query_type);
```

---

## Relationship Types (Типы связей)

### 1. CONTAINS
Проект содержит модули, модуль содержит функции/процедуры/переменные

**Варианты:**
- `(Project)-[:CONTAINS]->(Module)`
- `(Module)-[:CONTAINS]->(Function)`
- `(Module)-[:CONTAINS]->(Procedure)`
- `(Module)-[:CONTAINS]->(Variable)`

**Свойства:**
- `created_at` (datetime): Дата создания связи

---

### 2. CALLS
Функция/процедура вызывает другую функцию/процедуру

**Варианты:**
- `(Function)-[:CALLS]->(Function)`
- `(Function)-[:CALLS]->(Procedure)`
- `(Procedure)-[:CALLS]->(Function)`
- `(Procedure)-[:CALLS]->(Procedure)`

**Свойства:**
- `call_count` (int): Количество вызовов
- `line_numbers` (list[int]): Номера строк вызовов
- `is_conditional` (boolean): Условный вызов

---

### 3. USES
Использование переменной в функции/процедуре

**Варианты:**
- `(Function)-[:USES]->(Variable)`
- `(Procedure)-[:USES]->(Variable)`

**Свойства:**
- `usage_type` (string): read, write, read_write
- `line_numbers` (list[int]): Номера строк использования

---

### 4. DEPENDS_ON
Модульная зависимость

**Варианты:**
- `(Module)-[:DEPENDS_ON]->(Module)`

**Свойства:**
- `dependency_type` (string): import, reference, inheritance
- `strength` (float): Сила зависимости (0.0-1.0)

---

### 5. EXECUTES
Выполнение запроса

**Варианты:**
- `(Function)-[:EXECUTES]->(Query)`
- `(Procedure)-[:EXECUTES]->(Query)`

**Свойства:**
- `line_number` (int): Номер строки выполнения
- `is_dynamic` (boolean): Динамический запрос

---

### 6. SIMILAR_TO
Семантическая похожесть

**Варианты:**
- `(Function)-[:SIMILAR_TO]->(Function)`
- `(Module)-[:SIMILAR_TO]->(Module)`

**Свойства:**
- `similarity_score` (float): Score похожести (0.0-1.0)
- `similarity_type` (string): semantic, structural, naming

---

## Cypher Examples

### Создание проекта и модуля
```cypher
// Создание проекта
CREATE (p:Project {
  id: 'proj-001',
  name: '1C Framework',
  path: '/src',
  created_at: datetime(),
  indexed_at: datetime()
})

// Создание модуля
CREATE (m:Module {
  id: 'mod-001',
  name: 'УправлениеДокументами',
  file_path: 'src/CommonModules/УправлениеДокументами.bsl',
  module_type: 'CommonModule',
  functions_count: 5,
  procedures_count: 3,
  indexed_at: datetime()
})

// Связь проект-модуль
CREATE (p)-[:CONTAINS {created_at: datetime()}]->(m)
```

---

### Создание функции с вызовом
```cypher
// Функция 1
CREATE (f1:Function {
  id: 'func-001',
  name: 'ПолучитьДанные',
  signature: 'Функция ПолучитьДанные(Параметр1)',
  parameters: ['Параметр1'],
  is_export: true,
  line_start: 10,
  line_end: 25
})

// Функция 2
CREATE (f2:Function {
  id: 'func-002',
  name: 'ВыполнитьЗапрос',
  signature: 'Функция ВыполнитьЗапрос(ТекстЗапроса)',
  parameters: ['ТекстЗапроса'],
  is_export: false,
  line_start: 30,
  line_end: 45
})

// Связь вызова
CREATE (f1)-[:CALLS {
  call_count: 1,
  line_numbers: [15],
  is_conditional: false
}]->(f2)
```

---

### Поиск зависимостей модуля
```cypher
// Найти все модули, от которых зависит данный модуль
MATCH (m:Module {name: 'УправлениеДокументами'})-[:DEPENDS_ON]->(dep:Module)
RETURN m.name, dep.name, dep.module_type

// Найти все функции, вызываемые функцией
MATCH (f:Function {name: 'ПолучитьДанные'})-[:CALLS*1..3]->(called:Function)
RETURN f.name, called.name, length(path) AS depth
```

---

### Анализ использования переменных
```cypher
// Найти все переменные, используемые функцией
MATCH (f:Function {name: 'ПолучитьДанные'})-[u:USES]->(v:Variable)
RETURN f.name, v.name, u.usage_type, u.line_numbers
```

---

## Аналитические запросы

### 1. Top-10 самых вызываемых функций
```cypher
MATCH (f:Function)<-[c:CALLS]-()
WITH f, count(c) AS call_count
ORDER BY call_count DESC
LIMIT 10
RETURN f.name, f.module, call_count
```

---

### 2. Circular dependencies (циклические зависимости)
```cypher
MATCH path = (m:Module)-[:DEPENDS_ON*2..5]->(m)
RETURN m.name, length(path) AS cycle_depth
ORDER BY cycle_depth
```

---

### 3. Orphan functions (неиспользуемые функции)
```cypher
MATCH (f:Function)
WHERE NOT (f)<-[:CALLS]-()
  AND f.is_export = false
RETURN f.name, f.module
```

---

### 4. Complexity hotspots
```cypher
MATCH (f:Function)
WHERE f.complexity > 10
RETURN f.name, f.complexity, f.module
ORDER BY f.complexity DESC
```

---

## Performance Constraints

### Рекомендуемые ограничения

```cypher
// Ограничение на уникальность ID
CREATE CONSTRAINT project_id_unique FOR (p:Project) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT module_id_unique FOR (m:Module) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT function_id_unique FOR (f:Function) REQUIRE f.id IS UNIQUE;
CREATE CONSTRAINT procedure_id_unique FOR (p:Procedure) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT variable_id_unique FOR (v:Variable) REQUIRE v.id IS UNIQUE;
CREATE CONSTRAINT query_id_unique FOR (q:Query) REQUIRE q.id IS UNIQUE;

// Ограничение на обязательные свойства
CREATE CONSTRAINT module_name_exists FOR (m:Module) REQUIRE m.name IS NOT NULL;
CREATE CONSTRAINT function_name_exists FOR (f:Function) REQUIRE f.name IS NOT NULL;
```

---

## Метаданные схемы

**Версия:** 1.0
**Дата создания:** 2025-11-02
**Автор:** AI Memory System
**Проект:** 1C-Enterprise Framework

**Изменения:**
- v1.0 (2025-11-02): Начальная версия схемы

---

## Следующие шаги

1. ✅ Создание схемы (данный документ)
2. ⏳ Реализация создания constraints и indexes
3. ⏳ Разработка BSL parser для извлечения зависимостей
4. ⏳ Загрузка данных из существующего индекса
5. ⏳ Интеграция с semantic search
6. ⏳ Визуализация графа
