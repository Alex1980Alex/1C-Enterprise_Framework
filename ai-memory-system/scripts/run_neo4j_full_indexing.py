"""
Полная индексация Neo4j Knowledge Graph
Запуск: python scripts/run_neo4j_full_indexing.py
"""

import sys
import logging
from pathlib import Path

# Добавление путей для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.neo4j.bsl_dependency_analyzer import BSLDependencyAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/neo4j_full_indexing.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Основная функция"""
    logger.info("=" * 70)
    logger.info("🕸️  NEO4J FULL INDEXING - BSL Dependency Graph")
    logger.info("=" * 70)

    # Создание анализатора
    analyzer = BSLDependencyAnalyzer(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password123"
    )

    try:
        # Путь к проекту
        project_path = Path(__file__).parent.parent.parent / "src"

        logger.info(f"📂 Source path: {project_path}")
        logger.info(f"📊 Total BSL files to analyze: ~3973")
        logger.info(f"⏱️  Estimated time: 2-3 hours")
        logger.info("")

        # Полная индексация (max_files=None)
        analyzer.analyze_project(
            project_path=project_path,
            project_name="1C Enterprise Framework",
            max_files=None  # Все файлы!
        )

        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ INDEXING COMPLETE!")
        logger.info("=" * 70)
        logger.info("📊 View graph: http://localhost:7474")
        logger.info("🔐 Login: neo4j / password123")
        logger.info("")
        logger.info("Example queries:")
        logger.info("  // Find all modules")
        logger.info("  MATCH (m:Module) RETURN m.name LIMIT 25")
        logger.info("")
        logger.info("  // Find circular dependencies")
        logger.info("  MATCH (m1)-[:CALLS]->(m2)-[:CALLS]->(m3)-[:CALLS]->(m1)")
        logger.info("  RETURN m1.name, m2.name, m3.name")
        logger.info("")

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
