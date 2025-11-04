#!/usr/bin/env python3
"""
Task Manager CLI Utility
Manages projects, features, and tasks in Task Orchestrator SQLite database
"""

import sqlite3
import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Define paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DB_PATH = PROJECT_ROOT / "data" / "tasks.db"


class TaskManager:
    """Task management operations"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Check if database exists"""
        if not self.db_path.exists():
            print(f"❌ Database not found at: {self.db_path}", file=sys.stderr)
            print(f"💡 Run: python scripts/init-tasks-database.py", file=sys.stderr)
            sys.exit(1)

    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(str(self.db_path))

    # ========== Projects ==========

    def list_projects(self, status: Optional[str] = None) -> List[Dict]:
        """List all projects"""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM v_project_summary"
        if status:
            query += f" WHERE status = '{status}'"

        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        projects = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return projects

    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get project by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()

        conn.close()
        return dict(zip(columns, row)) if row else None

    # ========== Features ==========

    def list_features(self, project_id: Optional[int] = None) -> List[Dict]:
        """List features"""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM features"
        if project_id:
            query += f" WHERE project_id = {project_id}"
        query += " ORDER BY priority DESC, created_at"

        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        features = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return features

    # ========== Tasks ==========

    def list_tasks(self, status: Optional[str] = None, feature_id: Optional[int] = None) -> List[Dict]:
        """List tasks with filters"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if status:
            query = "SELECT * FROM v_active_tasks"
            if status != "active":
                query = f"SELECT * FROM tasks WHERE status = '{status}'"
        else:
            query = "SELECT * FROM tasks"

        if feature_id:
            query += f" {'WHERE' if 'WHERE' not in query else 'AND'} feature_id = {feature_id}"

        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        tasks = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return tasks

    def create_task(self, title: str, description: str, project_id: int,
                    feature_id: Optional[int] = None, priority: str = "medium",
                    status: str = "pending") -> int:
        """Create new task"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tasks (title, description, project_id, feature_id, priority, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, project_id, feature_id, priority, status))

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return task_id

    def update_task_status(self, task_id: int, status: str) -> bool:
        """Update task status"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Update completed_at if status is completed
        completed_at = datetime.now().isoformat() if status == "completed" else None

        cursor.execute("""
            UPDATE tasks
            SET status = ?, completed_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, completed_at, task_id))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    def add_task_note(self, task_id: int, content: str, note_type: str = "comment") -> int:
        """Add note to task"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO task_notes (task_id, content, note_type)
            VALUES (?, ?, ?)
        """, (task_id, content, note_type))

        note_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return note_id

    # ========== Reporting ==========

    def get_summary(self) -> Dict:
        """Get overall project summary"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM v_project_summary")
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()

        summary = dict(zip(columns, row)) if row else {}

        # Add more stats
        cursor.execute("SELECT COUNT(*) FROM features")
        summary['total_features'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed' AND completed_at >= date('now', '-7 days')")
        summary['completed_this_week'] = cursor.fetchone()[0]

        conn.close()
        return summary


# ========== CLI Commands ==========

def cmd_list_projects(args):
    """List projects command"""
    tm = TaskManager()
    projects = tm.list_projects(args.status)

    if not projects:
        print("No projects found.")
        return

    print("\n📁 Projects:")
    for p in projects:
        print(f"\n  [{p['id']}] {p['name']}")
        print(f"      Status: {p['status']}")
        print(f"      Features: {p['feature_count']}, Tasks: {p['task_count']}")
        print(f"      Completed: {p['completed_tasks']}, Active: {p['active_tasks']}")


def cmd_list_features(args):
    """List features command"""
    tm = TaskManager()
    features = tm.list_features(args.project)

    if not features:
        print("No features found.")
        return

    print("\n🎯 Features:")
    for f in features:
        print(f"\n  [{f['id']}] {f['name']}")
        print(f"      Priority: {f['priority']}, Status: {f['status']}")
        print(f"      {f['description']}")


def cmd_list_tasks(args):
    """List tasks command"""
    tm = TaskManager()
    tasks = tm.list_tasks(args.status, args.feature)

    if not tasks:
        print("No tasks found.")
        return

    print(f"\n📋 Tasks ({args.status or 'all'}):")
    for t in tasks:
        status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "blocked": "🚫", "cancelled": "❌"}.get(t['status'], "")
        print(f"\n  {status_icon} [{t['id']}] {t['title']}")
        print(f"      Status: {t['status']}, Priority: {t.get('priority', 'N/A')}")
        if t.get('description'):
            print(f"      {t['description']}")


def cmd_create_task(args):
    """Create task command"""
    tm = TaskManager()
    task_id = tm.create_task(
        title=args.title,
        description=args.description,
        project_id=args.project,
        feature_id=args.feature,
        priority=args.priority,
        status=args.status
    )
    print(f"✅ Task created: ID={task_id}")


def cmd_update_status(args):
    """Update task status command"""
    tm = TaskManager()
    if tm.update_task_status(args.task_id, args.status):
        print(f"✅ Task {args.task_id} status updated to: {args.status}")
    else:
        print(f"❌ Task {args.task_id} not found", file=sys.stderr)
        sys.exit(1)


def cmd_summary(args):
    """Show summary command"""
    tm = TaskManager()
    summary = tm.get_summary()

    print("\n📊 Project Summary:")
    print(f"   Project: {summary.get('name', 'N/A')}")
    print(f"   Status: {summary.get('status', 'N/A')}")
    print(f"   Features: {summary.get('total_features', 0)}")
    print(f"   Tasks: {summary.get('task_count', 0)}")
    print(f"   ├─ Completed: {summary.get('completed_tasks', 0)}")
    print(f"   ├─ Active: {summary.get('active_tasks', 0)}")
    print(f"   └─ Blocked: {summary.get('blocked_tasks', 0)}")
    print(f"   Completed this week: {summary.get('completed_this_week', 0)}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Task Manager CLI")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List projects
    parser_projects = subparsers.add_parser('projects', help='List projects')
    parser_projects.add_argument('--status', choices=['active', 'archived', 'completed'], help='Filter by status')

    # List features
    parser_features = subparsers.add_parser('features', help='List features')
    parser_features.add_argument('--project', type=int, help='Filter by project ID')

    # List tasks
    parser_tasks = subparsers.add_parser('tasks', help='List tasks')
    parser_tasks.add_argument('--status', choices=['pending', 'in_progress', 'completed', 'blocked', 'cancelled', 'active'], help='Filter by status')
    parser_tasks.add_argument('--feature', type=int, help='Filter by feature ID')

    # Create task
    parser_create = subparsers.add_parser('create', help='Create new task')
    parser_create.add_argument('title', help='Task title')
    parser_create.add_argument('description', help='Task description')
    parser_create.add_argument('--project', type=int, required=True, help='Project ID')
    parser_create.add_argument('--feature', type=int, help='Feature ID')
    parser_create.add_argument('--priority', choices=['low', 'medium', 'high', 'critical'], default='medium')
    parser_create.add_argument('--status', choices=['pending', 'in_progress', 'completed', 'blocked'], default='pending')

    # Update status
    parser_update = subparsers.add_parser('update-status', help='Update task status')
    parser_update.add_argument('task_id', type=int, help='Task ID')
    parser_update.add_argument('status', choices=['pending', 'in_progress', 'completed', 'blocked', 'cancelled'])

    # Summary
    parser_summary = subparsers.add_parser('summary', help='Show project summary')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    commands = {
        'projects': cmd_list_projects,
        'features': cmd_list_features,
        'tasks': cmd_list_tasks,
        'create': cmd_create_task,
        'update-status': cmd_update_status,
        'summary': cmd_summary,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
