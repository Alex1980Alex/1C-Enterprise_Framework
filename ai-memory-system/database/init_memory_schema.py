"""
Initialize Memory Schema in TimescaleDB
Применение SQL схемы для системы памяти
"""

import sys
from pathlib import Path
import psycopg2
from psycopg2 import sql
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ai_memory',
    'user': 'ai_user',
    'password': 'ai_memory_secure_2025'
}

def load_schema_file(schema_path: str) -> str:
    """Load SQL schema from file"""
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Schema file not found: {schema_path}")
        sys.exit(1)

def init_schema():
    """Initialize memory schema in TimescaleDB"""
    logger.info("Starting schema initialization...")

    # Load schema
    schema_file = Path(__file__).parent / "schemas" / "timescale_memory_core.sql"
    schema_sql = load_schema_file(str(schema_file))

    # Connect to database
    try:
        logger.info(f"Connecting to {DB_CONFIG['database']} at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()

        logger.info("Connected successfully!")

        # Execute schema
        logger.info("Executing schema SQL...")
        cursor.execute(schema_sql)

        # Verify installation
        cursor.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename IN ('conversations', 'messages', 'message_entities')
            ORDER BY tablename
        """)

        tables = cursor.fetchall()
        logger.info("Created tables:")
        for table in tables:
            logger.info(f"  ✅ {table[0]}")

        # Check hypertable
        cursor.execute("""
            SELECT hypertable_name
            FROM timescaledb_information.hypertables
            WHERE hypertable_name = 'messages'
        """)

        if cursor.fetchone():
            logger.info("  ✅ messages (hypertable)")
        else:
            logger.warning("  ⚠️ messages hypertable not created")

        # Check views
        cursor.execute("""
            SELECT viewname
            FROM pg_views
            WHERE schemaname = 'public'
            AND viewname LIKE 'v_%'
            ORDER BY viewname
        """)

        views = cursor.fetchall()
        if views:
            logger.info("Created views:")
            for view in views:
                logger.info(f"  ✅ {view[0]}")

        # Check continuous aggregates
        cursor.execute("""
            SELECT view_name
            FROM timescaledb_information.continuous_aggregates
        """)

        aggs = cursor.fetchall()
        if aggs:
            logger.info("Created continuous aggregates:")
            for agg in aggs:
                logger.info(f"  ✅ {agg[0]}")

        logger.info("\n🎉 Schema initialization completed successfully!")

        # Close connection
        cursor.close()
        conn.close()

    except psycopg2.OperationalError as e:
        logger.error(f"❌ Connection error: {e}")
        logger.error("Make sure TimescaleDB is running: docker ps | grep timescale")
        sys.exit(1)
    except psycopg2.Error as e:
        logger.error(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_schema()
