@echo off
REM Start Neo4j in Docker with known password
REM This creates a fresh Neo4j instance with:
REM - Username: neo4j
REM - Password: mcp12345
REM - Bolt port: 7687
REM - HTTP port: 7474

echo ============================================
echo Starting Neo4j in Docker
echo ============================================
echo.
echo Configuration:
echo   Username: neo4j
echo   Password: mcp12345
echo   Bolt: bolt://localhost:7687
echo   HTTP: http://localhost:7474
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo.
    echo Please start Docker Desktop first.
    echo.
    pause
    exit /b 1
)

REM Stop and remove existing neo4j-mcp container if exists
echo Cleaning up existing container...
docker stop neo4j-mcp >nul 2>&1
docker rm neo4j-mcp >nul 2>&1

echo.
echo Starting Neo4j container...
docker run -d ^
  --name neo4j-mcp ^
  -p 7474:7474 -p 7687:7687 ^
  -e NEO4J_AUTH=neo4j/mcp12345 ^
  -e NEO4J_server_bolt_enabled=true ^
  -e NEO4J_server_bolt_listen__address=:7687 ^
  -v neo4j-mcp-data:/data ^
  -v neo4j-mcp-logs:/logs ^
  neo4j:latest

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Neo4j!
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo SUCCESS! Neo4j is starting...
echo ============================================
echo.
echo Waiting for Neo4j to be ready (30 seconds)...
timeout /t 30 /nobreak >nul

echo.
echo Testing connection...
timeout 5 curl -s http://localhost:7474 >nul 2>&1
if errorlevel 1 (
    echo WARNING: Neo4j HTTP interface not ready yet
    echo Please wait another 10-20 seconds
) else (
    echo SUCCESS: Neo4j HTTP interface is responding!
)

echo.
echo ============================================
echo Neo4j is ready!
echo ============================================
echo.
echo Access Neo4j Browser: http://localhost:7474
echo   Username: neo4j
echo   Password: mcp12345
echo.
echo Bolt URI: bolt://localhost:7687
echo.
echo To set the password for MCP server:
echo   set NEO4J_PASSWORD=mcp12345
echo.
echo Or update Claude Code config with:
echo   "NEO4J_PASSWORD": "mcp12345"
echo.
echo To stop Neo4j:
echo   docker stop neo4j-mcp
echo.
echo To view logs:
echo   docker logs neo4j-mcp -f
echo.
pause
