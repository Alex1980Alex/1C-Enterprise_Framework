#!/usr/bin/env python3
"""
Enhanced MCP server for document processing using Docling library with EasyOCR integration.
Includes OCR functionality as replacement for docling_sdg dependency.
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

# Import our OCR integration
from easyocr_integration import get_ocr_processor, ocr_document_async

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a cache directory
CACHE_DIR = Path.home() / ".cache" / "mcp-docling"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_cache_key(source: str, enable_ocr: bool, ocr_language: Optional[List[str]], use_easyocr: bool = False) -> str:
    """Generate a cache key for the document conversion."""
    key_data = {
        "source": source,
        "enable_ocr": enable_ocr,
        "ocr_language": ocr_language or [],
        "use_easyocr": use_easyocr
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
            "ocr_language": ocr_language,
            "ocr_method": "docling_builtin"
        }
        
        # Save to cache
        save_to_cache(cache_key, conversion_result)
        
        # Cleanup memory
        cleanup_memory()
        
        return conversion_result
        
    except Exception as e:
        logger.error(f"Conversion failed for {source}: {e}")
        raise

async def convert_document_with_easyocr(source: str, ocr_language: Optional[List[str]] = None, 
                                      confidence_threshold: float = 0.7) -> Dict[str, Any]:
    """Convert document using EasyOCR for OCR functionality."""
    
    # Check cache first
    cache_key = get_cache_key(source, True, ocr_language, use_easyocr=True)
    cached_result = get_cached_result(cache_key)
    if cached_result:
        logger.info(f"Using cached EasyOCR result for {source}")
        return cached_result
    
    try:
        # Use EasyOCR for OCR processing
        ocr_result = await ocr_document_async(source, ocr_language or ['en', 'ru'], confidence_threshold)
        
        if not ocr_result['success']:
            raise Exception(f"OCR processing failed: {ocr_result.get('error', 'Unknown error')}")
        
        # Try Docling conversion as well for comparison
        try:
            docling_result = await convert_document_base(source, enable_ocr=False)
            docling_markdown = docling_result['markdown']
        except:
            docling_markdown = ""
        
        # Combine results
        if 'pages' in ocr_result:
            # PDF processing
            combined_markdown = f"# OCR Extracted Content\n\n{ocr_result['combined_text']}"
            num_pages = ocr_result['total_pages']
            ocr_details = {
                "total_pages": ocr_result['total_pages'],
                "processed_pages": ocr_result['processed_pages'],
                "page_results": ocr_result['pages']
            }
        else:
            # Image processing
            combined_markdown = f"# OCR Extracted Content\n\n{ocr_result['full_text']}"
            num_pages = 1
            ocr_details = {
                "total_detections": ocr_result['total_detections'],
                "filtered_detections": ocr_result['filtered_detections'],
                "confidence_stats": ocr_result['confidence_stats'],
                "text_blocks": ocr_result['text_blocks']
            }
        
        # If we have both OCR and Docling results, create comparison
        if docling_markdown:
            combined_markdown += f"\n\n# Docling Extracted Content\n\n{docling_markdown}"
        
        # Prepare enhanced result
        enhanced_result = {
            "source": source,
            "markdown": combined_markdown,
            "num_pages": num_pages,
            "title": source.split('/')[-1],
            "timestamp": str(uuid.uuid4()),
            "ocr_enabled": True,
            "ocr_language": ocr_language or ['en', 'ru'],
            "ocr_method": "easyocr",
            "confidence_threshold": confidence_threshold,
            "ocr_details": ocr_details,
            "docling_available": bool(docling_markdown),
            "enhanced_processing": True
        }
        
        # Save to cache
        save_to_cache(cache_key, enhanced_result)
        
        # Cleanup memory
        cleanup_memory()
        
        return enhanced_result
        
    except Exception as e:
        logger.error(f"Enhanced OCR conversion failed for {source}: {e}")
        raise

# Initialize the MCP server
server = Server("mcp-docling-enhanced")

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
                        "description": "List of language codes for OCR (e.g., ['en', 'ru'])",
                        "default": None
                    }
                },
                "required": ["source"]
            }
        ),
        types.Tool(
            name="convert_document_with_easyocr",
            description="Convert document using enhanced EasyOCR processing (recommended for scanned documents)",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "URL or local file path to the document"
                    },
                    "ocr_language": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of language codes for OCR (e.g., ['en', 'ru'])",
                        "default": ["en", "ru"]
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "description": "Minimum confidence threshold for OCR text (0.0-1.0)",
                        "default": 0.7
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
                         f"**OCR Enabled:** {result['ocr_enabled']}\n"
                         f"**OCR Method:** {result.get('ocr_method', 'none')}\n\n"
                         f"**Markdown Content:**\n\n{result['markdown']}"
                )
            ]
        
        elif name == "convert_document_with_easyocr":
            source = arguments.get("source")
            if not source:
                raise ValueError("Source parameter is required")
                
            ocr_language = arguments.get("ocr_language", ["en", "ru"])
            confidence_threshold = arguments.get("confidence_threshold", 0.7)
            
            result = await convert_document_with_easyocr(source, ocr_language, confidence_threshold)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Enhanced OCR document conversion completed!\n\n"
                         f"**Source:** {result['source']}\n"
                         f"**Title:** {result['title']}\n"
                         f"**Pages:** {result['num_pages']}\n"
                         f"**OCR Method:** {result['ocr_method']}\n"
                         f"**OCR Languages:** {', '.join(result['ocr_language'])}\n"
                         f"**Confidence Threshold:** {result['confidence_threshold']}\n"
                         f"**Enhanced Processing:** {result['enhanced_processing']}\n\n"
                         f"**OCR Details:**\n{json.dumps(result['ocr_details'], indent=2)}\n\n"
                         f"**Markdown Content:**\n\n{result['markdown']}"
                )
            ]
        
        elif name == "get_system_info":
            # Test EasyOCR availability
            easyocr_available = False
            try:
                import easyocr
                easyocr_available = True
            except ImportError:
                pass
            
            info = {
                "docling_available": True,
                "advanced_features": ADVANCED_FEATURES,
                "easyocr_available": easyocr_available,
                "ocr_support": ADVANCED_FEATURES or easyocr_available,
                "cache_directory": str(CACHE_DIR),
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                "server_version": "enhanced-1.0.0",
                "enhanced_features": [
                    "EasyOCR integration",
                    "Dual OCR processing",
                    "Enhanced caching",
                    "Confidence threshold control"
                ]
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=f"**MCP Docling Enhanced Server System Information**\n\n"
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
    """Run the Enhanced MCP Docling server."""
    if transport == "stdio":
        anyio.run(main)
    else:
        raise ValueError(f"Unsupported transport: {transport}")

if __name__ == "__main__":
    cli()