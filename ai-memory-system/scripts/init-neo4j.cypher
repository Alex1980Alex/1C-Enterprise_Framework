// Initialize Neo4j Knowledge Graph for 1C-Enterprise Framework

// Create constraints for unique nodes
CREATE CONSTRAINT module_name IF NOT EXISTS FOR (m:Module) REQUIRE m.name IS UNIQUE;
CREATE CONSTRAINT config_name IF NOT EXISTS FOR (c:Configuration) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT developer_email IF NOT EXISTS FOR (d:Developer) REQUIRE d.email IS UNIQUE;
CREATE CONSTRAINT issue_id IF NOT EXISTS FOR (i:Issue) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT procedure_full_name IF NOT EXISTS FOR (p:Procedure) REQUIRE p.full_name IS UNIQUE;
CREATE CONSTRAINT function_full_name IF NOT EXISTS FOR (f:Function) REQUIRE f.full_name IS UNIQUE;

// Create indexes for common queries
CREATE INDEX module_type IF NOT EXISTS FOR (m:Module) ON (m.type);
CREATE INDEX module_path IF NOT EXISTS FOR (m:Module) ON (m.path);
CREATE INDEX config_version IF NOT EXISTS FOR (c:Configuration) ON (c.version);
CREATE INDEX developer_name IF NOT EXISTS FOR (d:Developer) ON (d.name);
CREATE INDEX issue_status IF NOT EXISTS FOR (i:Issue) ON (i.status);
CREATE INDEX issue_priority IF NOT EXISTS FOR (i:Issue) ON (i.priority);

// Create sample developer nodes
CREATE (d1:Developer {
    name: 'Terletskiy Alexander',
    email: 'a.terletskiy@sodrugestvo.ru',
    role: 'Senior 1C Developer',
    expertise: ['BSL', 'Architecture', 'Performance', 'Framework Design'],
    created_at: datetime()
});

// Create sample configuration node
CREATE (cfg:Configuration {
    name: '1C-Enterprise-Framework',
    version: '8.3.26.1521',
    platform: '1C:Enterprise',
    description: 'AI-powered development framework',
    created_at: datetime(),
    last_modified: datetime()
});

// Create sample common modules
CREATE (m1:Module {
    name: 'гкс_РаботаСДанными',
    type: 'CommonModule',
    path: 'CommonModules/гкс_РаботаСДанными.bsl',
    description: 'Общие функции работы с данными',
    lines_of_code: 450,
    complexity: 15,
    last_modified: datetime(),
    created_at: datetime()
});

CREATE (m2:Module {
    name: 'гкс_Интеграция',
    type: 'CommonModule',
    path: 'CommonModules/гкс_Интеграция.bsl',
    description: 'Функции интеграции с внешними системами',
    lines_of_code: 320,
    complexity: 12,
    last_modified: datetime(),
    created_at: datetime()
});

CREATE (m3:Module {
    name: 'гкс_Валидация',
    type: 'CommonModule',
    path: 'CommonModules/гкс_Валидация.bsl',
    description: 'Валидация данных',
    lines_of_code: 280,
    complexity: 8,
    last_modified: datetime(),
    created_at: datetime()
});

// Create relationships
MATCH (d:Developer {email: 'a.terletskiy@sodrugestvo.ru'})
MATCH (cfg:Configuration {name: '1C-Enterprise-Framework'})
CREATE (d)-[:AUTHORED {date: datetime()}]->(cfg);

MATCH (d:Developer {email: 'a.terletskiy@sodrugestvo.ru'})
MATCH (m:Module)
WHERE m.name IN ['гкс_РаботаСДанными', 'гкс_Интеграция', 'гкс_Валидация']
CREATE (d)-[:AUTHORED {date: datetime()}]->(m);

MATCH (cfg:Configuration {name: '1C-Enterprise-Framework'})
MATCH (m:Module)
WHERE m.name IN ['гкс_РаботаСДанными', 'гкс_Интеграция', 'гкс_Валидация']
CREATE (cfg)-[:CONTAINS]->(m);

// Create module dependencies
MATCH (m1:Module {name: 'гкс_Интеграция'})
MATCH (m2:Module {name: 'гкс_РаботаСДанными'})
CREATE (m1)-[:DEPENDS_ON {type: 'function_call', critical: true}]->(m2);

MATCH (m1:Module {name: 'гкс_Валидация'})
MATCH (m2:Module {name: 'гкс_РаботаСДанными'})
CREATE (m1)-[:DEPENDS_ON {type: 'function_call', critical: false}]->(m2);

// Create sample issue
CREATE (issue:Issue {
    id: 'INIT-001',
    title: 'AI Memory System Implementation',
    description: 'Implement enterprise-grade AI memory system for 1C Framework',
    status: 'In Progress',
    priority: 'High',
    created_at: datetime(),
    updated_at: datetime()
});

MATCH (d:Developer {email: 'a.terletskiy@sodrugestvo.ru'})
MATCH (i:Issue {id: 'INIT-001'})
CREATE (d)-[:ASSIGNED_TO]->(i);

MATCH (i:Issue {id: 'INIT-001'})
MATCH (cfg:Configuration {name: '1C-Enterprise-Framework'})
CREATE (i)-[:RELATED_TO]->(cfg);

// Create sample procedures
CREATE (p1:Procedure {
    full_name: 'гкс_РаботаСДанными.ПолучитьДанныеДокумента',
    name: 'ПолучитьДанныеДокумента',
    module: 'гкс_РаботаСДанными',
    parameters: ['Ссылка'],
    return_type: 'Структура',
    lines: 25,
    description: 'Получить данные документа по ссылке',
    created_at: datetime()
});

CREATE (p2:Procedure {
    full_name: 'гкс_Интеграция.ОтправитьДанные',
    name: 'ОтправитьДанные',
    module: 'гкс_Интеграция',
    parameters: ['Данные', 'Адрес'],
    return_type: 'Булево',
    lines: 45,
    description: 'Отправить данные во внешнюю систему',
    created_at: datetime()
});

// Link procedures to modules
MATCH (m:Module {name: 'гкс_РаботаСДанными'})
MATCH (p:Procedure {full_name: 'гкс_РаботаСДанными.ПолучитьДанныеДокумента'})
CREATE (m)-[:CONTAINS]->(p);

MATCH (m:Module {name: 'гкс_Интеграция'})
MATCH (p:Procedure {full_name: 'гкс_Интеграция.ОтправитьДанные'})
CREATE (m)-[:CONTAINS]->(p);

// Create procedure call relationships
MATCH (p1:Procedure {full_name: 'гкс_Интеграция.ОтправитьДанные'})
MATCH (p2:Procedure {full_name: 'гкс_РаботаСДанными.ПолучитьДанныеДокумента'})
CREATE (p1)-[:CALLS {frequency: 'high'}]->(p2);

// Create full-text indexes for search
CALL db.index.fulltext.createNodeIndex('module_search', ['Module'], ['name', 'description']) IF NOT EXISTS;
CALL db.index.fulltext.createNodeIndex('procedure_search', ['Procedure', 'Function'], ['name', 'description']) IF NOT EXISTS;
CALL db.index.fulltext.createNodeIndex('issue_search', ['Issue'], ['title', 'description']) IF NOT EXISTS;

// Return summary
MATCH (d:Developer) WITH count(d) as developers
MATCH (m:Module) WITH developers, count(m) as modules
MATCH (p:Procedure) WITH developers, modules, count(p) as procedures
MATCH (i:Issue) WITH developers, modules, procedures, count(i) as issues
MATCH (cfg:Configuration) WITH developers, modules, procedures, issues, count(cfg) as configs
RETURN developers, modules, procedures, issues, configs;
