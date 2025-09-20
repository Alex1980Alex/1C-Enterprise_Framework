#!/bin/bash

echo "Starting Serena MCP Server for 1C-Enterprise Framework..."
cd "$(dirname "$0")/serena"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv is not installed or not in PATH"
    echo "Please install uv: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Install dependencies if needed
if [ ! -f ".venv/pyvenv.cfg" ]; then
    echo "Installing dependencies..."
    uv sync
fi

echo "Starting Serena MCP Server..."
uv run serena-mcp-server --project "1C-Enterprise_Framework"