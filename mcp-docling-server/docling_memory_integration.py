#!/usr/bin/env python3
"""
Integration script for Docling + Memory MCP.
Processes documents and saves metadata to Knowledge Graph.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from server_basic import convert_document_base

class DoclingMemoryIntegration:
    """Integration class for Docling document processing with Memory MCP storage."""
    
    def __init__(self):
        self.processed_documents = []
        self.memory_entities = []
        self.memory_relations = []
    
    async def process_document(self, source: str, document_type: str = "technical", 
                              enable_ocr: bool = False, ocr_language: List[str] = None) -> Dict[str, Any]:
        """Process document with Docling and prepare Memory MCP data."""
        
        print(f"Processing document: {source}")
        
        try:
            # Convert document using Docling
            result = await convert_document_base(source, enable_ocr, ocr_language)
            
            # Extract metadata for Memory MCP
            doc_metadata = self._extract_document_metadata(result, document_type)
            
            # Create Memory MCP entities
            entities = self._create_memory_entities(doc_metadata)
            
            # Create Memory MCP relations
            relations = self._create_memory_relations(doc_metadata)
            
            # Store results
            self.processed_documents.append(result)
            self.memory_entities.extend(entities)
            self.memory_relations.extend(relations)
            
            processing_result = {
                "docling_result": result,
                "memory_entities": entities,
                "memory_relations": relations,
                "processing_timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            print(f"SUCCESS: Document {source} processed and prepared for Memory MCP")
            return processing_result
            
        except Exception as e:
            print(f"ERROR: Failed to process {source}: {e}")
            return {
                "source": source,
                "error": str(e),
                "status": "failed",
                "processing_timestamp": datetime.now().isoformat()
            }
    
    def _extract_document_metadata(self, docling_result: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Extract meaningful metadata from Docling conversion result."""
        
        content = docling_result['markdown']
        
        # Basic content analysis
        word_count = len(content.split())
        line_count = len(content.split('\n'))
        has_headers = '##' in content or '#' in content
        has_tables = '|' in content
        has_code_blocks = '```' in content
        
        # Document complexity assessment
        complexity = "simple"
        if word_count > 1000 or has_tables or has_code_blocks:
            complexity = "complex"
        elif word_count > 500 or has_headers:
            complexity = "medium"
        
        return {
            "source": docling_result['source'],
            "title": docling_result['title'],
            "content": content,
            "word_count": word_count,
            "line_count": line_count,
            "complexity": complexity,
            "document_type": doc_type,
            "has_headers": has_headers,
            "has_tables": has_tables,
            "has_code_blocks": has_code_blocks,
            "processing_timestamp": datetime.now().isoformat(),
            "framework_context": "1C-Enterprise"
        }
    
    def _create_memory_entities(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create Memory MCP entities from document metadata."""
        
        entities = []
        
        # Main document entity
        doc_entity = {
            "name": f"Document_{Path(metadata['source']).stem}",
            "entityType": "processed_document",
            "observations": [
                f"Title: {metadata['title']}",
                f"Source: {metadata['source']}",
                f"Word count: {metadata['word_count']}",
                f"Complexity: {metadata['complexity']}",
                f"Document type: {metadata['document_type']}",
                f"Has headers: {metadata['has_headers']}",
                f"Has tables: {metadata['has_tables']}",
                f"Has code blocks: {metadata['has_code_blocks']}",
                f"Framework: {metadata['framework_context']}",
                f"Processed: {metadata['processing_timestamp']}"
            ]
        }
        entities.append(doc_entity)
        
        # Content analysis entity
        content_entity = {
            "name": f"Content_Analysis_{Path(metadata['source']).stem}",
            "entityType": "content_analysis",
            "observations": [
                f"Lines: {metadata['line_count']}",
                f"Words: {metadata['word_count']}",
                f"Structural elements: {'headers, ' if metadata['has_headers'] else ''}{'tables, ' if metadata['has_tables'] else ''}{'code' if metadata['has_code_blocks'] else ''}".rstrip(', '),
                f"Analysis timestamp: {metadata['processing_timestamp']}"
            ]
        }
        entities.append(content_entity)
        
        # If document has technical content, create technical entity
        if metadata['document_type'] == 'technical' or metadata['has_code_blocks']:
            tech_entity = {
                "name": f"Technical_Content_{Path(metadata['source']).stem}",
                "entityType": "technical_documentation",
                "observations": [
                    f"Framework context: {metadata['framework_context']}",
                    f"Contains code blocks: {metadata['has_code_blocks']}",
                    f"Contains tables: {metadata['has_tables']}",
                    f"Complexity level: {metadata['complexity']}"
                ]
            }
            entities.append(tech_entity)
        
        return entities
    
    def _create_memory_relations(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create Memory MCP relations between entities."""
        
        relations = []
        doc_name = f"Document_{Path(metadata['source']).stem}"
        content_name = f"Content_Analysis_{Path(metadata['source']).stem}"
        
        # Document -> Content Analysis relation
        relations.append({
            "from": doc_name,
            "to": content_name,
            "relationType": "analyzed_by"
        })
        
        # Document -> Docling Integration relation
        relations.append({
            "from": doc_name,
            "to": "Docling_Integration_System",
            "relationType": "processed_by"
        })
        
        # Content Analysis -> 1C Framework relation
        if metadata['framework_context'] == '1C-Enterprise':
            relations.append({
                "from": content_name,
                "to": "1C_Enterprise_Framework",
                "relationType": "related_to"
            })
        
        # Technical content relations
        if metadata['document_type'] == 'technical' or metadata['has_code_blocks']:
            tech_name = f"Technical_Content_{Path(metadata['source']).stem}"
            relations.append({
                "from": doc_name,
                "to": tech_name,
                "relationType": "contains"
            })
            relations.append({
                "from": tech_name,
                "to": "Technical_Documentation_System",
                "relationType": "categorized_by"
            })
        
        return relations
    
    def export_memory_data(self, output_file: str = None) -> Dict[str, Any]:
        """Export all collected data for Memory MCP integration."""
        
        if not output_file:
            output_file = f"docling_memory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_documents": len(self.processed_documents),
            "total_entities": len(self.memory_entities),
            "total_relations": len(self.memory_relations),
            "memory_entities": self.memory_entities,
            "memory_relations": self.memory_relations,
            "processed_documents_summary": [
                {
                    "source": doc['source'],
                    "title": doc['title'],
                    "content_length": len(doc['markdown']),
                    "timestamp": doc.get('timestamp', 'unknown')
                }
                for doc in self.processed_documents
            ],
            "mcp_commands": {
                "create_entities": f"mcp__memory__create_entities({len(self.memory_entities)} entities)",
                "create_relations": f"mcp__memory__create_relations({len(self.memory_relations)} relations)"
            }
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            print(f"SUCCESS: Memory MCP data exported to {output_file}")
            return export_data
        except Exception as e:
            print(f"ERROR: Failed to export data: {e}")
            return {}

async def test_integration():
    """Test the Docling + Memory MCP integration."""
    
    print("=== Testing Docling + Memory MCP Integration ===")
    
    integration = DoclingMemoryIntegration()
    
    # Test with our markdown document
    test_file = "test_document.md"
    
    if os.path.exists(test_file):
        result = await integration.process_document(
            source=test_file,
            document_type="technical",
            enable_ocr=False
        )
        
        if result['status'] == 'success':
            print(f"\nEntities created: {len(result['memory_entities'])}")
            print(f"Relations created: {len(result['memory_relations'])}")
            
            # Export for review
            export_data = integration.export_memory_data("test_docling_memory_integration.json")
            
            print(f"\nMCP Commands to run:")
            print(f"1. {export_data['mcp_commands']['create_entities']}")
            print(f"2. {export_data['mcp_commands']['create_relations']}")
            
            return True
        else:
            print(f"Integration test failed: {result.get('error', 'Unknown error')}")
            return False
    else:
        print(f"Test file {test_file} not found!")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_integration())
    if success:
        print("\n✓ Docling + Memory MCP integration working correctly!")
    else:
        print("\n✗ Integration requires additional configuration")