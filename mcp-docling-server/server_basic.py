#!/usr/bin/env python3
"""
Basic MCP server for document processing using Docling library.
Simplified version without docling_sdg dependency for Q&A generation.
"""

import anyio
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import base64
import io
import os
import logging
import hashlib
import json
import gc
import click
import uuid
import mcp.types as types
from mcp.server.lowlevel import Server
from docling.document_converter import DocumentConverter

try:
    from docling.datamodel.pipeline_options import PdfPipelineOptions, OcrEngine, EasyOcrOptions
    from docling.datamodel.base_models import InputFormat
    ADVANCED_FEATURES = True
except ImportError:
    PdfPipelineOptions = None
    OcrEngine = None
    EasyOcrOptions = None
    InputFormat = None
    ADVANCED_FEATURES = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a cache directory
CACHE_DIR = Path.home() / ".cache" / "mcp-docling"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_cache_key(source: str, enable_ocr: bool, ocr_language: Optional[List[str]]) -> str:
    """Generate a cache key for the document conversion."""
    key_data = {
        "source": source,
        "enable_ocr": enable_ocr,
        "ocr_language": ocr_language or []
    }
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()

def cleanup_memory():
    """Force garbage collection to free up memory."""
    gc.collect()

def get_cached_result(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached conversion result."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
    return None

def save_to_cache(cache_key: str, result: Dict[str, Any]):
    """Save conversion result to cache."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save cache: {e}")

def create_document_converter(enable_ocr: bool = False, ocr_language: Optional[List[str]] = None) -> DocumentConverter:
    """Create and configure document converter."""
    if not ADVANCED_FEATURES or not enable_ocr:
        # Basic converter without OCR
        return DocumentConverter()
    
    # Advanced converter with OCR support
    pipeline_options = PdfPipelineOptions()
    if enable_ocr:
        pipeline_options.do_ocr = True
        pipeline_options.ocr_engine = OcrEngine.EASYOCR
        if ocr_language:
            pipeline_options.ocr_options = EasyOcrOptions(lang=ocr_language)
    
    return DocumentConverter(
        format_options={
            InputFormat.PDF: pipeline_options,
        }
    )

async def convert_document_base(source: str, enable_ocr: bool = False, ocr_language: Optional[List[str]] = None) -> Dict[str, Any]:
    """Base document conversion function."""
    # Check cache first
    cache_key = get_cache_key(source, enable_ocr, ocr_language)
    cached_result = get_cached_result(cache_key)
    if cached_result:
        logger.info(f"Using cached result for {source}")
        return cached_result
    
    try:
        converter = create_document_converter(enable_ocr, ocr_language)
        
        # Convert document
        if source.startswith(('http://', 'https://')):
            # URL source
            result = converter.convert(source)
        else:
            # Local file
            if not os.path.exists(source):
                raise FileNotFoundError(f"File not found: {source}")
            result = converter.convert(source)
        
        # Get markdown content
        markdown_content = result.document.export_to_markdown()
        
        # Prepare result
        conversion_result = {
            "source": source,
            "markdown": markdown_content,
            "num_pages": len(result.document.pages) if hasattr(result.document, 'pages') else 1,
            "title": getattr(result.document, 'title', '') or source.split('/')[-1],
            "timestamp": str(uuid.uuid4()),
            "ocr_enabled": enable_ocr,
            "ocr_language": ocr_language
        }
        
        # Save to cache
        save_to_cache(cache_key, conversion_result)
        
        # Cleanup memory
        cleanup_memory()
        
        return conversion_result
        
    except Exception as e:
        logger.error(f"Conversion failed for {source}: {e}")
        raise

# Initialize the MCP server
server = Server("mcp-docling-basic")

@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available tools."""
    tools = [
        types.Tool(
            name="convert_document",
            description="Convert a document from URL or local path to markdown format",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "URL or local file path to the document"
                    },
                    "enable_ocr": {
                        "type": "boolean",
                        "description": "Whether to enable OCR for scanned documents",
                        "default": False
                    },
                    "ocr_language": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of language codes for OCR (e.g., ['en', 'fr'])",
                        "default": None
                    }
                },
                "required": ["source"]
            }
        ),
        types.Tool(
            name="get_system_info",
            description="Get information about system configuration and available features",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]
    
    return tools

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls."""
    try:
        if name == "convert_document":
            source = arguments.get("source")
            if not source:
                raise ValueError("Source parameter is required")
                
            enable_ocr = arguments.get("enable_ocr", False)
            ocr_language = arguments.get("ocr_language")
            
            result = await convert_document_base(source, enable_ocr, ocr_language)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Document converted successfully!\n\n"
                         f"**Source:** {result['source']}\n"
                         f"**Title:** {result['title']}\n"
                         f"**Pages:** {result['num_pages']}\n"
                         f"**OCR Enabled:** {result['ocr_enabled']}\n\n"
                         f"**Markdown Content:**\n\n{result['markdown']}"
                )
            ]
        
        elif name == "get_system_info":
            info = {
                "docling_available": True,
                "advanced_features": ADVANCED_FEATURES,
                "ocr_support": ADVANCED_FEATURES,
                "cache_directory": str(CACHE_DIR),
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                "server_version": "basic-1.0.0"
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=f"**MCP Docling Server System Information**\n\n"
                         f"```json\n{json.dumps(info, indent=2)}\n```"
                )
            ]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Tool call failed: {e}")
        return [
            types.TextContent(
                type="text", 
                text=f"Error: {str(e)}"
            )
        ]

async def main():
    """Main entry point for the server."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

@click.command()
@click.option("--transport", default="stdio", help="Transport type (stdio)")
@click.option("--port", default=8000, help="Port for SSE transport")
def cli(transport: str, port: int):
    """Run the MCP Docling server."""
    if transport == "stdio":
        anyio.run(main)
    else:
        raise ValueError(f"Unsupported transport: {transport}")

if __name__ == "__main__":
    cli()