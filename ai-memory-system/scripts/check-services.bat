@echo off
REM Check status of all services

echo ========================================
echo Checking 1C AI Memory System Services
echo ========================================
echo.

cd /d %~dp0\..\docker

echo Docker Compose Services:
echo ----------------------------------------
docker-compose ps
echo.

echo.
echo Service Health Checks:
echo ----------------------------------------

echo Checking Qdrant...
curl -s http://localhost:6333/healthz >nul 2>&1 && echo [OK] Qdrant is healthy || echo [FAIL] Qdrant is down

echo Checking TimescaleDB...
docker exec 1c-timescaledb pg_isready -U ai_user -d ai_memory >nul 2>&1 && echo [OK] TimescaleDB is healthy || echo [FAIL] TimescaleDB is down

echo Checking Neo4j...
curl -s http://localhost:7474 >nul 2>&1 && echo [OK] Neo4j is healthy || echo [FAIL] Neo4j is down

echo Checking Redis...
docker exec 1c-redis redis-cli --pass redis_secure_2025 PING >nul 2>&1 && echo [OK] Redis is healthy || echo [FAIL] Redis is down

echo Checking Prometheus...
curl -s http://localhost:9090/-/healthy >nul 2>&1 && echo [OK] Prometheus is healthy || echo [FAIL] Prometheus is down

echo Checking Grafana...
curl -s http://localhost:3000/api/health >nul 2>&1 && echo [OK] Grafana is healthy || echo [FAIL] Grafana is down

echo.
echo ========================================

pause
