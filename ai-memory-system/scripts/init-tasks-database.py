#!/usr/bin/env python3
"""
Task Orchestrator Database Initialization
Creates SQLite database for projects, features, and tasks management
"""

import sqlite3
import os
import sys
from pathlib import Path

# Define paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "tasks.db"
SQL_SCHEMA_PATH = SCRIPT_DIR / "init-tasks-db.sql"

def create_database():
    """Create and initialize the tasks database"""

    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Check if database already exists
    db_exists = DB_PATH.exists()

    # Connect to database (creates if doesn't exist)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    try:
        # Read SQL schema
        with open(SQL_SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Execute schema
        cursor.executescript(schema_sql)
        conn.commit()

        # Verify tables created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print(f"✅ Database initialized successfully at: {DB_PATH}")
        print(f"\n📊 Created tables:")
        for table in tables:
            print(f"   - {table[0]}")

        # Check views
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")
        views = cursor.fetchall()

        if views:
            print(f"\n📈 Created views:")
            for view in views:
                print(f"   - {view[0]}")

        return True

    except Exception as e:
        print(f"❌ Error initializing database: {e}", file=sys.stderr)
        conn.rollback()
        return False

    finally:
        conn.close()

def insert_sample_data():
    """Insert sample project structure"""

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    try:
        # Insert root project
        cursor.execute("""
            INSERT INTO projects (name, description, status, tags)
            VALUES (?, ?, ?, ?)
        """, (
            "1C-Enterprise Framework",
            "AI-powered development framework for 1C platform",
            "active",
            '["1c", "bsl", "framework", "ai"]'
        ))
        project_id = cursor.lastrowid

        # Insert features
        features = [
            ("AI Memory System", "Persistent context and memory management", "high", "in_progress"),
            ("BSL Code Intelligence", "Semantic search and analysis of BSL code", "high", "in_progress"),
            ("Timeline Tracking", "Historical project event tracking", "medium", "planning"),
            ("Knowledge Graph", "Module dependency and relationship mapping", "medium", "planning"),
        ]

        feature_ids = []
        for name, desc, priority, status in features:
            cursor.execute("""
                INSERT INTO features (project_id, name, description, priority, status)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, name, desc, priority, status))
            feature_ids.append(cursor.lastrowid)

        # Insert tasks for Week 1
        tasks = [
            (feature_ids[0], "Setup infrastructure", "Docker, Ollama, databases", "completed", "high"),
            (feature_ids[0], "Configure Task Orchestrator", "SQLite DB, Memory MCP integration", "in_progress", "high"),
            (feature_ids[0], "Initialize project structure", "Create project hierarchy in systems", "pending", "high"),
            (feature_ids[1], "Setup Qdrant vector database", "Configure and test vector search", "completed", "high"),
            (feature_ids[1], "Download Ollama models", "deepseek-coder and embeddings", "completed", "high"),
            (feature_ids[1], "Test BSL code analysis", "Verify model understands 1C BSL", "completed", "medium"),
        ]

        for feature_id, title, desc, status, priority in tasks:
            cursor.execute("""
                INSERT INTO tasks (feature_id, project_id, title, description, status, priority)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (feature_id, project_id, title, desc, status, priority))

        conn.commit()

        print(f"\n✅ Sample data inserted successfully")
        print(f"   - 1 project")
        print(f"   - {len(features)} features")
        print(f"   - {len(tasks)} tasks")

        return True

    except Exception as e:
        print(f"❌ Error inserting sample data: {e}", file=sys.stderr)
        conn.rollback()
        return False

    finally:
        conn.close()

def show_summary():
    """Display database summary"""

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    try:
        # Query summary view
        cursor.execute("SELECT * FROM v_project_summary")
        row = cursor.fetchone()

        if row:
            print(f"\n📊 Project Summary:")
            print(f"   Project: {row[1]}")
            print(f"   Status: {row[2]}")
            print(f"   Features: {row[3]}")
            print(f"   Total Tasks: {row[4]}")
            print(f"   Completed: {row[5]}")
            print(f"   Active: {row[6]}")
            print(f"   Blocked: {row[7]}")
            if row[8]:
                print(f"   Estimated Hours: {row[8]:.1f}")
            if row[9]:
                print(f"   Actual Hours: {row[9]:.1f}")

        # Show active tasks
        cursor.execute("SELECT title, status, priority, feature_name FROM v_active_tasks LIMIT 5")
        active_tasks = cursor.fetchall()

        if active_tasks:
            print(f"\n📋 Active Tasks (Top 5):")
            for task in active_tasks:
                print(f"   [{task[2]}] {task[0]} - {task[1]} ({task[3]})")

    except Exception as e:
        print(f"❌ Error querying database: {e}", file=sys.stderr)

    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Initializing Task Orchestrator Database...\n")

    if create_database():
        insert_sample_data()
        show_summary()
        print(f"\n✅ Task Orchestrator database ready!")
        print(f"📍 Location: {DB_PATH}")
    else:
        sys.exit(1)
