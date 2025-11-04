"""
Memory MCP Server - FIXED VERSION with lazy initialization

MCP (Model Context Protocol) server для интеграции системы долгосрочной памяти с Claude.
Предоставляет tools для сохранения, поиска и восстановления контекста разговоров.

ИСПРАВЛЕНИЕ: Lazy initialization для быстрого старта MCP сервера
"""

import sys
from pathlib import Path
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

# Import MCP modules FIRST, before adding local paths
from mcp.server import Server
from mcp import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

# NOW add parent directory to path for local service imports
sys.path.insert(0, str(Path(__file__).parent.parent / "services"))

from conversation_storage import ConversationStorage
from message_vectorization import MessageVectorization
from context_restoration import ContextRestoration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("memory-mcp")

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ai_memory',
    'user': 'ai_user',
    'password': 'ai_memory_secure_2025'
}

# Lazy initialization for fast startup - services будут созданы при первом использовании
_services = None

def get_services():
    """
    Lazy initialization of database services.
    This allows MCP server to start quickly (< 1 second) and only connect to DB when first tool is called.
    """
    global _services
    if _services is None:
        logger.info("Initializing database services (lazy load)...")
        storage = ConversationStorage(DB_CONFIG)
        vectorizer = MessageVectorization(
            qdrant_host="localhost",
            qdrant_port=6333,
            collection_name="conversation_memory"
        )
        restoration = ContextRestoration(storage, vectorizer)
        _services = {'storage': storage, 'vectorizer': vectorizer, 'restoration': restoration}
        logger.info("Database services initialized successfully")
    return _services

# Create MCP server
app = Server("memory-server")

# Global session state
current_session = {
    "session_id": None,
    "conversation_id": None,
    "project_context": None
}


@app.list_tools()
async def list_tools() -> List[Tool]:
    """
    List all available memory tools
    """
    return [
        Tool(
            name="save_conversation_fact",
            description="Save an important fact or message from the current conversation to long-term memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The text content to save (message, fact, or important information)"
                    },
                    "importance": {
                        "type": "number",
                        "description": "Importance score from 0.0 to 1.0 (default: 0.5)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.5
                    },
                    "role": {
                        "type": "string",
                        "description": "Role of the message sender",
                        "enum": ["user", "assistant", "system"],
                        "default": "assistant"
                    },
                    "has_code": {
                        "type": "boolean",
                        "description": "Whether the content contains code",
                        "default": False
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata (optional)",
                        "default": {}
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="search_memory",
            description="Search for relevant information in long-term memory using semantic and text search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (will use both semantic and text search)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    },
                    "project_context": {
                        "type": "string",
                        "description": "Filter by project context (optional)"
                    },
                    "min_score": {
                        "type": "number",
                        "description": "Minimum relevance score (0.0-1.0, default: 0.5)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_session_context",
            description="Retrieve relevant context for the current or a specific session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to get context for (uses current session if not specified)"
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional query to focus context retrieval"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of context items (default: 20)",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="start_memory_session",
            description="Start a new memory session for a project or conversation",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_name": {
                        "type": "string",
                        "description": "Name for the session"
                    },
                    "project_context": {
                        "type": "string",
                        "description": "Project or conversation context"
                    }
                },
                "required": ["session_name"]
            }
        ),
        Tool(
            name="get_project_summary",
            description="Get a summary of all stored information for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_context": {
                        "type": "string",
                        "description": "Project context (uses current session if not specified)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_important_messages",
            description="Retrieve the most important messages from memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of messages to return (default: 10)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    },
                    "min_importance": {
                        "type": "number",
                        "description": "Minimum importance score (0.0-1.0, default: 0.7)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.7
                    },
                    "project_context": {
                        "type": "string",
                        "description": "Filter by project context (optional)"
                    }
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """
    Handle tool calls from Claude
    """
    # Initialize services lazily on first tool call
    services = get_services()
    storage = services['storage']
    vectorizer = services['vectorizer']
    restoration = services['restoration']

    try:
        if name == "save_conversation_fact":
            return await save_conversation_fact(arguments, storage, vectorizer)
        elif name == "search_memory":
            return await search_memory(arguments, vectorizer, storage)
        elif name == "get_session_context":
            return await get_session_context(arguments, restoration)
        elif name == "start_memory_session":
            return await start_memory_session(arguments, storage)
        elif name == "get_project_summary":
            return await get_project_summary(arguments, storage)
        elif name == "get_important_messages":
            return await get_important_messages(arguments, storage)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def save_conversation_fact(args: Dict, storage, vectorizer) -> List[TextContent]:
    """Save a fact to memory"""

    content = args["content"]
    importance = args.get("importance", 0.5)
    role = args.get("role", "assistant")
    has_code = args.get("has_code", False)
    metadata = args.get("metadata", {})

    # Get or create session
    if current_session["session_id"] is None:
        session_id = str(uuid4())
        conversation_id = storage.create_conversation(
            session_id=session_id,
            project_context=current_session.get("project_context", "default"),
            metadata={}
        )
        current_session["session_id"] = session_id
        current_session["conversation_id"] = conversation_id

    conversation_id = current_session["conversation_id"]

    # Save message to database
    message_id = storage.add_message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        importance_score=importance,
        has_code=has_code,
        metadata=metadata
    )

    # Create vector embedding
    message_timestamp = datetime.utcnow().isoformat()
    vector_id = vectorizer.vectorize_message(
        message_id=message_id,
        message_timestamp=message_timestamp,
        conversation_id=str(conversation_id),
        role=role,
        content=content,
        importance_score=importance,
        metadata=metadata
    )

    return [TextContent(
        type="text",
        text=f"✅ Saved to memory (ID: {message_id}, importance: {importance:.2f})"
    )]


async def search_memory(args: Dict, vectorizer, storage) -> List[TextContent]:
    """Search memory"""

    query = args["query"]
    limit = args.get("limit", 10)
    project_ctx = args.get("project_context")
    min_score = args.get("min_score", 0.5)

    # Semantic search
    results = vectorizer.search_similar_messages(
        query=query,
        limit=limit,
        min_score=min_score
    )

    if not results:
        return [TextContent(
            type="text",
            text=f"No results found for: {query}"
        )]

    result_text = f"🔍 Found {len(results)} results for '{query}':\n\n"

    for i, result in enumerate(results, 1):
        score = result.get("score", 0)
        content = result.get("content_preview", "")
        role = result.get("role", "unknown")

        result_text += f"{i}. [{score:.2f}] ({role})\n"
        result_text += f"   {content[:200]}...\n\n"

    return [TextContent(type="text", text=result_text)]


async def get_session_context(args: Dict, restoration) -> List[TextContent]:
    """Get session context"""

    session_id = args.get("session_id", current_session.get("session_id"))
    query = args.get("query")
    limit = args.get("limit", 20)

    if not session_id:
        return [TextContent(
            type="text",
            text="No active session. Use start_memory_session first."
        )]

    context = restoration.restore_context(
        conversation_id=session_id,
        query=query,
        max_messages=limit
    )

    result_text = f"📋 Session Context (last {len(context)} messages):\n\n"

    for msg in context:
        role_icon = "👤" if msg["role"] == "user" else "🤖"
        result_text += f"{role_icon} {msg['content'][:150]}...\n\n"

    return [TextContent(type="text", text=result_text)]


async def start_memory_session(args: Dict, storage) -> List[TextContent]:
    """Start a new session"""

    session_name = args["session_name"]
    project_ctx = args.get("project_context", "default")

    session_id = str(uuid4())
    conversation_id = storage.create_conversation(
        session_id=session_id,
        project_context=project_ctx,
        metadata={"session_name": session_name}
    )

    current_session["session_id"] = session_id
    current_session["conversation_id"] = conversation_id
    current_session["project_context"] = project_ctx

    return [TextContent(
        type="text",
        text=f"✨ Started new session: {session_name}\nProject: {project_ctx}\nID: {session_id}"
    )]


async def get_project_summary(args: Dict, storage) -> List[TextContent]:
    """Get project summary"""

    project_ctx = args.get("project_context", current_session.get("project_context", "default"))

    # get_stats() returns global statistics (no project filtering available)
    stats = storage.get_stats()

    result_text = f"📊 Project Summary: {project_ctx}\n\n"
    result_text += f"  Total conversations: {stats.get('total_conversations', 0)}\n"
    result_text += f"  Active conversations: {stats.get('active_conversations', 0)}\n"
    result_text += f"  Total messages: {stats.get('total_messages', 0)}\n"
    result_text += f"  Avg messages per conversation: {stats.get('avg_messages_per_conversation', 0):.2f}\n"
    result_text += f"  Avg importance: {stats.get('avg_importance_score', 0):.2f}\n"

    return [TextContent(type="text", text=result_text)]


async def get_important_messages(args: Dict, storage) -> List[TextContent]:
    """Get important messages from memory"""

    limit = args.get("limit", 10)
    min_importance = args.get("min_importance", 0.7)
    project_ctx = args.get("project_context", current_session.get("project_context"))

    messages = storage.get_important_messages(
        limit=limit,
        min_score=min_importance,
        project_context=project_ctx
    )

    if not messages:
        return [TextContent(
            type="text",
            text=f"No important messages found (min score: {min_importance})"
        )]

    result_text = f"⭐ Top {len(messages)} Important Messages\n\n"

    for i, msg in enumerate(messages, 1):
        role_icon = "👤" if msg["role"] == "user" else "🤖"
        result_text += f"{i}. {role_icon} [{msg['importance_score']:.2f}]\n"
        result_text += f"   {msg['content_preview'][:150]}...\n\n"

    return [TextContent(type="text", text=result_text)]


async def main():
    """Run the MCP server"""
    logger.info("Starting Memory MCP Server (fast startup mode)...")
    logger.info(f"Database: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
    logger.info(f"Qdrant: localhost:6333")
    logger.info("Services will initialize on first tool call (lazy loading)")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
