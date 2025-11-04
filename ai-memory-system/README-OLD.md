# 1C-Enterprise AI Memory System

Enterprise-grade AI-powered memory and context management system for 1C-Enterprise Framework.

## 🎯 Overview

This system provides:
- **0% context loss** between sessions
- **Intelligent BSL code search** via local LLM (Ollama + DeepSeek)
- **Multi-dimensional memory** (semantic, temporal, graph)
- **100% privacy** (all processing local)
- **Production-ready monitoring**

## 🏗️ Architecture

```
├── docker/                 # Docker Compose configuration
├── scripts/               # Utility scripts and DB initialization
├── config/                # Service configurations
├── data/                  # Persistent data (git-ignored)
├── logs/                  # Application logs (git-ignored)
└── backup/                # Database backups (git-ignored)
```

## 📦 Components

- **Task Orchestrator**: Persistent task management (Kotlin + SQLite)
- **Qdrant**: Vector database for semantic search
- **TimescaleDB**: Time-series database for project timeline
- **Neo4j**: Knowledge graph for module dependencies
- **Redis**: Cache layer for performance
- **Ollama**: Local LLM serving (DeepSeek-Coder, Phi-3)
- **Prometheus + Grafana**: Monitoring and metrics

## 🚀 Quick Start

### Prerequisites

1. **Docker Desktop** (required)
   ```bash
   # Download from: https://www.docker.com/products/docker-desktop
   # Or install via winget:
   winget install Docker.DockerDesktop
   ```

2. **Ollama** (required)
   ```bash
   # Download from: https://ollama.com/download
   # Or install via winget:
   winget install Ollama.Ollama
   ```

3. **Python 3.11+** (required)
   - Already installed ✅

### Installation

1. **Start Docker Desktop**
   - Ensure Docker is running

2. **Start all services**
   ```bash
   cd D:\1C-Enterprise_Framework\ai-memory-system
   scripts\start-services.bat
   ```

3. **Install Ollama models**
   ```bash
   # Primary models
   ollama pull deepseek-coder:6.7b
   ollama pull deepseek-coder-v2:16b
   ollama pull phi3:mini

   # Embedding models
   ollama pull nomic-embed-text
   ollama pull bge-m3
   ```

4. **Verify installation**
   ```bash
   scripts\check-services.bat
   ```

### Access Points

- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Neo4j Browser**: http://localhost:7474
  - Username: `neo4j`
  - Password: (from .env file)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: (from .env file)

## 🔧 Management Scripts

### Start Services
```bash
scripts\start-services.bat
```

### Stop Services
```bash
scripts\stop-services.bat
```

### Check Service Health
```bash
scripts\check-services.bat
```

### View Logs
```bash
# All services
scripts\logs.bat

# Specific service
scripts\logs.bat qdrant
scripts\logs.bat timescaledb
scripts\logs.bat neo4j
```

## 📊 Database Initialization

### TimescaleDB

Database is automatically initialized on first start with:
- 4 hypertables: `project_events`, `configuration_changes`, `session_activities`, `performance_metrics`
- Retention policies (2 years, 1 year, 3 months, 6 months)
- Continuous aggregates for daily/weekly summaries
- Indexes for common queries

### Neo4j

Knowledge graph is automatically initialized with:
- Constraints for unique nodes
- Indexes for common queries
- Sample data (developers, modules, procedures)
- Sample relationships

Manual initialization (if needed):
```bash
# Copy init script to container
docker cp scripts/init-neo4j.cypher 1c-neo4j:/var/lib/neo4j/import/

# Execute in Neo4j browser or cypher-shell
cat scripts/init-neo4j.cypher | docker exec -i 1c-neo4j cypher-shell -u neo4j -p <password>
```

## 🔐 Security

- All passwords configured in `.env` file (not committed to Git)
- Redis requires password authentication
- Neo4j requires password authentication
- TimescaleDB uses PostgreSQL authentication

## 📈 Monitoring

### Prometheus Metrics

Available at http://localhost:9090

- Qdrant performance metrics
- TimescaleDB connection pool stats
- Neo4j query performance
- Redis cache hit rates
- System resource usage

### Grafana Dashboards

Available at http://localhost:3000

Pre-configured datasources:
- Prometheus (system metrics)
- TimescaleDB (application data)
- Redis (cache statistics)

## 🐛 Troubleshooting

### Services won't start

1. Check Docker Desktop is running
2. Check ports are not in use:
   ```bash
   netstat -ano | findstr "6333 5432 7474 6379 9090 3000"
   ```
3. View logs:
   ```bash
   cd docker
   docker-compose logs
   ```

### Ollama not responding

1. Check Ollama service:
   ```bash
   ollama list
   ```
2. Restart Ollama service (Windows Services)

### Database connection errors

1. Check service health:
   ```bash
   scripts\check-services.bat
   ```
2. Verify credentials in `.env` file
3. Check container logs:
   ```bash
   docker logs 1c-timescaledb
   docker logs 1c-neo4j
   ```

## 📚 Next Steps

1. Configure Task Orchestrator in Claude Code (see Week 1, Day 2)
2. Initialize project structure
3. Deploy Python services (Context Manager, BSL Analyzer)
4. Configure MCP Server
5. Index existing BSL code

## 🤝 Support

For issues and questions, refer to the main project documentation:
- `D:\Проекты\План_Максимальное_AI_Решение_1C_Framework_2025-10-30.md`
- `D:\Проекты\EXECUTIVE_SUMMARY_Максимальное_Решение.md`

## 📝 License

Internal project for 1C-Enterprise Framework development.

---

**Status**: Week 1, Day 1 Implementation
**Version**: 1.0
**Last Updated**: 2025-10-30
