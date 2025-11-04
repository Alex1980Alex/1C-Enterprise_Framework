#!/usr/bin/env python3
"""
Safe Neo4j Initialization Script
Handles Neo4j 5.x syntax correctly
"""
import sys
from neo4j import GraphDatabase

# Connection settings
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4j_secure_2025"

def execute_cypher(driver, query, description):
    """Execute a single Cypher query"""
    try:
        with driver.session() as session:
            result = session.run(query)
            data = result.data()
            print(f"✅ {description}")
            return data
    except Exception as e:
        print(f"⚠️  {description}: {str(e)}")
        return None

def init_neo4j():
    """Initialize Neo4j knowledge graph"""
    print("🚀 Initializing Neo4j Knowledge Graph...\n")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    try:
        # 1. Create constraints
        print("📋 Creating constraints...")
        constraints = [
            ("CREATE CONSTRAINT module_name IF NOT EXISTS FOR (m:Module) REQUIRE m.name IS UNIQUE", "Module name constraint"),
            ("CREATE CONSTRAINT config_name IF NOT EXISTS FOR (c:Configuration) REQUIRE c.name IS UNIQUE", "Configuration name constraint"),
            ("CREATE CONSTRAINT developer_email IF NOT EXISTS FOR (d:Developer) REQUIRE d.email IS UNIQUE", "Developer email constraint"),
            ("CREATE CONSTRAINT issue_id IF NOT EXISTS FOR (i:Issue) REQUIRE i.id IS UNIQUE", "Issue ID constraint"),
            ("CREATE CONSTRAINT procedure_full_name IF NOT EXISTS FOR (p:Procedure) REQUIRE p.full_name IS UNIQUE", "Procedure full_name constraint"),
            ("CREATE CONSTRAINT function_full_name IF NOT EXISTS FOR (f:Function) REQUIRE f.full_name IS UNIQUE", "Function full_name constraint"),
        ]

        for query, desc in constraints:
            execute_cypher(driver, query, desc)

        # 2. Create indexes
        print("\n📊 Creating indexes...")
        indexes = [
            ("CREATE INDEX module_type IF NOT EXISTS FOR (m:Module) ON (m.type)", "Module type index"),
            ("CREATE INDEX module_path IF NOT EXISTS FOR (m:Module) ON (m.path)", "Module path index"),
            ("CREATE INDEX config_version IF NOT EXISTS FOR (c:Configuration) ON (c.version)", "Configuration version index"),
            ("CREATE INDEX developer_name IF NOT EXISTS FOR (d:Developer) ON (d.name)", "Developer name index"),
            ("CREATE INDEX issue_status IF NOT EXISTS FOR (i:Issue) ON (i.status)", "Issue status index"),
            ("CREATE INDEX issue_priority IF NOT EXISTS FOR (i:Issue) ON (i.priority)", "Issue priority index"),
        ]

        for query, desc in indexes:
            execute_cypher(driver, query, desc)

        # 3. Create sample data
        print("\n🌱 Creating sample data...")

        # Developer
        execute_cypher(driver, """
            MERGE (d:Developer {email: 'a.terletskiy@sodrugestvo.ru'})
            SET d.name = 'Terletskiy Alexander',
                d.role = 'Senior 1C Developer',
                d.expertise = ['BSL', 'Architecture', 'Performance', 'Framework Design'],
                d.created_at = datetime()
        """, "Developer node")

        # Configuration
        execute_cypher(driver, """
            MERGE (cfg:Configuration {name: '1C-Enterprise-Framework'})
            SET cfg.version = '8.3.26.1521',
                cfg.platform = '1C:Enterprise',
                cfg.description = 'AI-powered development framework',
                cfg.created_at = datetime(),
                cfg.last_modified = datetime()
        """, "Configuration node")

        # Modules
        modules = [
            ("гкс_РаботаСДанными", "Общие функции работы с данными", 450, 15),
            ("гкс_Интеграция", "Функции интеграции с внешними системами", 320, 12),
            ("гкс_Валидация", "Валидация данных", 280, 8),
        ]

        for name, desc, loc, complexity in modules:
            execute_cypher(driver, f"""
                MERGE (m:Module {{name: '{name}'}})
                SET m.type = 'CommonModule',
                    m.path = 'CommonModules/{name}.bsl',
                    m.description = '{desc}',
                    m.lines_of_code = {loc},
                    m.complexity = {complexity},
                    m.last_modified = datetime(),
                    m.created_at = datetime()
            """, f"Module: {name}")

        # Issue
        execute_cypher(driver, """
            MERGE (i:Issue {id: 'INIT-001'})
            SET i.title = 'AI Memory System Implementation',
                i.description = 'Implement enterprise-grade AI memory system for 1C Framework',
                i.status = 'In Progress',
                i.priority = 'High',
                i.created_at = datetime(),
                i.updated_at = datetime()
        """, "Issue node")

        # Procedures
        execute_cypher(driver, """
            MERGE (p:Procedure {full_name: 'гкс_РаботаСДанными.ПолучитьДанныеДокумента'})
            SET p.name = 'ПолучитьДанныеДокумента',
                p.module = 'гкс_РаботаСДанными',
                p.parameters = ['Ссылка'],
                p.return_type = 'Структура',
                p.lines = 25,
                p.description = 'Получить данные документа по ссылке',
                p.created_at = datetime()
        """, "Procedure: ПолучитьДанныеДокумента")

        execute_cypher(driver, """
            MERGE (p:Procedure {full_name: 'гкс_Интеграция.ОтправитьДанные'})
            SET p.name = 'ОтправитьДанные',
                p.module = 'гкс_Интеграция',
                p.parameters = ['Данные', 'Адрес'],
                p.return_type = 'Булево',
                p.lines = 45,
                p.description = 'Отправить данные во внешнюю систему',
                p.created_at = datetime()
        """, "Procedure: ОтправитьДанные")

        # 4. Create relationships
        print("\n🔗 Creating relationships...")

        relationships = [
            ("MATCH (d:Developer {email: 'a.terletskiy@sodrugestvo.ru'}), (cfg:Configuration {name: '1C-Enterprise-Framework'}) MERGE (d)-[:AUTHORED {date: datetime()}]->(cfg)", "Developer → Configuration"),
            ("MATCH (d:Developer {email: 'a.terletskiy@sodrugestvo.ru'}), (m:Module) WHERE m.name IN ['гкс_РаботаСДанными', 'гкс_Интеграция', 'гкс_Валидация'] MERGE (d)-[:AUTHORED {date: datetime()}]->(m)", "Developer → Modules"),
            ("MATCH (cfg:Configuration {name: '1C-Enterprise-Framework'}), (m:Module) WHERE m.name IN ['гкс_РаботаСДанными', 'гкс_Интеграция', 'гкс_Валидация'] MERGE (cfg)-[:CONTAINS]->(m)", "Configuration → Modules"),
            ("MATCH (m1:Module {name: 'гкс_Интеграция'}), (m2:Module {name: 'гкс_РаботаСДанными'}) MERGE (m1)-[:DEPENDS_ON {type: 'function_call', critical: true}]->(m2)", "Module dependency: Интеграция → РаботаСДанными"),
            ("MATCH (m1:Module {name: 'гкс_Валидация'}), (m2:Module {name: 'гкс_РаботаСДанными'}) MERGE (m1)-[:DEPENDS_ON {type: 'function_call', critical: false}]->(m2)", "Module dependency: Валидация → РаботаСДанными"),
            ("MATCH (d:Developer {email: 'a.terletskiy@sodrugestvo.ru'}), (i:Issue {id: 'INIT-001'}) MERGE (d)-[:ASSIGNED_TO]->(i)", "Developer → Issue"),
            ("MATCH (i:Issue {id: 'INIT-001'}), (cfg:Configuration {name: '1C-Enterprise-Framework'}) MERGE (i)-[:RELATED_TO]->(cfg)", "Issue → Configuration"),
            ("MATCH (m:Module {name: 'гкс_РаботаСДанными'}), (p:Procedure {full_name: 'гкс_РаботаСДанными.ПолучитьДанныеДокумента'}) MERGE (m)-[:CONTAINS]->(p)", "Module → Procedure"),
            ("MATCH (m:Module {name: 'гкс_Интеграция'}), (p:Procedure {full_name: 'гкс_Интеграция.ОтправитьДанные'}) MERGE (m)-[:CONTAINS]->(p)", "Module → Procedure"),
            ("MATCH (p1:Procedure {full_name: 'гкс_Интеграция.ОтправитьДанные'}), (p2:Procedure {full_name: 'гкс_РаботаСДанными.ПолучитьДанныеДокумента'}) MERGE (p1)-[:CALLS {frequency: 'high'}]->(p2)", "Procedure calls"),
        ]

        for query, desc in relationships:
            execute_cypher(driver, query, desc)

        # 5. Get summary
        print("\n📈 Database Summary:")
        summary = execute_cypher(driver, """
            MATCH (d:Developer) WITH count(d) as developers
            MATCH (m:Module) WITH developers, count(m) as modules
            MATCH (p:Procedure) WITH developers, modules, count(p) as procedures
            MATCH (i:Issue) WITH developers, modules, procedures, count(i) as issues
            MATCH (cfg:Configuration) WITH developers, modules, procedures, issues, count(cfg) as configs
            RETURN developers, modules, procedures, issues, configs
        """, "Retrieving stats")

        if summary:
            stats = summary[0]
            print(f"   Developers: {stats['developers']}")
            print(f"   Configurations: {stats['configs']}")
            print(f"   Modules: {stats['modules']}")
            print(f"   Procedures: {stats['procedures']}")
            print(f"   Issues: {stats['issues']}")

        print("\n✅ Neo4j Knowledge Graph initialized successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        driver.close()

if __name__ == "__main__":
    init_neo4j()
