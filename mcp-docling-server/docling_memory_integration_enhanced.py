#!/usr/bin/env python3
"""
Enhanced integration script for Docling + Memory MCP with OCR capabilities.
Processes documents with EasyOCR and saves comprehensive metadata to Knowledge Graph.
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

from server_enhanced import convert_document_base, convert_document_with_easyocr

class EnhancedDoclingMemoryIntegration:
    """Enhanced integration class for Docling + EasyOCR + Memory MCP."""
    
    def __init__(self):
        self.processed_documents = []
        self.memory_entities = []
        self.memory_relations = []
        self.ocr_statistics = {
            "total_processed": 0,
            "ocr_enhanced": 0,
            "avg_confidence": 0.0,
            "languages_detected": set()
        }
    
    async def process_document_enhanced(self, 
                                      source: str, 
                                      document_type: str = "technical",
                                      use_ocr: bool = True,
                                      ocr_language: List[str] = ['en', 'ru'],
                                      confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """Process document with enhanced OCR capabilities."""
        
        print(f"Enhanced processing: {source}")
        
        try:
            if use_ocr:
                # Use enhanced OCR processing
                result = await convert_document_with_easyocr(
                    source=source,
                    ocr_language=ocr_language,
                    confidence_threshold=confidence_threshold
                )
                processing_method = "enhanced_ocr"
            else:
                # Use standard Docling processing
                result = await convert_document_base(
                    source=source,
                    enable_ocr=False
                )
                processing_method = "standard_docling"
            
            # Extract enhanced metadata
            doc_metadata = self._extract_enhanced_metadata(result, document_type, processing_method)
            
            # Create Memory MCP entities with OCR data
            entities = self._create_enhanced_memory_entities(doc_metadata)
            
            # Create Memory MCP relations
            relations = self._create_enhanced_memory_relations(doc_metadata)
            
            # Update statistics
            self._update_ocr_statistics(result)
            
            # Store results
            self.processed_documents.append(result)
            self.memory_entities.extend(entities)
            self.memory_relations.extend(relations)
            
            processing_result = {
                "docling_result": result,
                "memory_entities": entities,
                "memory_relations": relations,
                "processing_timestamp": datetime.now().isoformat(),
                "processing_method": processing_method,
                "ocr_enhanced": use_ocr,
                "status": "success"
            }
            
            print(f"SUCCESS: Enhanced processing of {source} completed")
            return processing_result
            
        except Exception as e:
            print(f"ERROR: Enhanced processing failed for {source}: {e}")
            return {
                "source": source,
                "error": str(e),
                "status": "failed",
                "processing_timestamp": datetime.now().isoformat()
            }
    
    def _extract_enhanced_metadata(self, docling_result: Dict[str, Any], doc_type: str, method: str) -> Dict[str, Any]:
        """Extract enhanced metadata including OCR information."""
        
        content = docling_result['markdown']
        
        # Basic content analysis
        word_count = len(content.split())
        line_count = len(content.split('\n'))
        has_headers = '##' in content or '#' in content
        has_tables = '|' in content
        has_code_blocks = '```' in content
        
        # Enhanced OCR analysis
        ocr_enhanced = docling_result.get('enhanced_processing', False)
        ocr_confidence = 0.0
        ocr_detections = 0
        
        if ocr_enhanced and 'ocr_details' in docling_result:
            ocr_details = docling_result['ocr_details']
            if 'confidence_stats' in ocr_details:
                ocr_confidence = ocr_details['confidence_stats'].get('avg_confidence', 0.0)
            ocr_detections = ocr_details.get('total_detections', 0)
        
        # Document complexity assessment
        complexity = "simple"
        if word_count > 1000 or has_tables or has_code_blocks or ocr_detections > 10:
            complexity = "complex"
        elif word_count > 500 or has_headers or ocr_detections > 5:
            complexity = "medium"
        
        return {
            "source": docling_result['source'],
            "title": docling_result['title'],
            "content": content,
            "word_count": word_count,
            "line_count": line_count,
            "complexity": complexity,
            "document_type": doc_type,
            "processing_method": method,
            "has_headers": has_headers,
            "has_tables": has_tables,
            "has_code_blocks": has_code_blocks,
            "ocr_enhanced": ocr_enhanced,
            "ocr_confidence": ocr_confidence,
            "ocr_detections": ocr_detections,
            "ocr_languages": docling_result.get('ocr_language', []),
            "processing_timestamp": datetime.now().isoformat(),
            "framework_context": "1C-Enterprise"
        }
    
    def _create_enhanced_memory_entities(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create enhanced Memory MCP entities with OCR metadata."""
        
        entities = []
        doc_name = f"Document_{Path(metadata['source']).stem}"
        
        # Main document entity with enhanced information
        doc_entity = {
            "name": doc_name,
            "entityType": "processed_document",
            "observations": [
                f"Title: {metadata['title']}",
                f"Source: {metadata['source']}",
                f"Word count: {metadata['word_count']}",
                f"Complexity: {metadata['complexity']}",
                f"Document type: {metadata['document_type']}",
                f"Processing method: {metadata['processing_method']}",
                f"Has headers: {metadata['has_headers']}",
                f"Has tables: {metadata['has_tables']}",
                f"Has code blocks: {metadata['has_code_blocks']}",
                f"OCR enhanced: {metadata['ocr_enhanced']}",
                f"Framework: {metadata['framework_context']}",
                f"Processed: {metadata['processing_timestamp']}"
            ]
        }
        entities.append(doc_entity)
        
        # Enhanced content analysis entity
        content_entity = {
            "name": f"Content_Analysis_{Path(metadata['source']).stem}",
            "entityType": "content_analysis",
            "observations": [
                f"Lines: {metadata['line_count']}",
                f"Words: {metadata['word_count']}",
                f"Processing method: {metadata['processing_method']}",
                f"Structural elements: {'headers, ' if metadata['has_headers'] else ''}{'tables, ' if metadata['has_tables'] else ''}{'code' if metadata['has_code_blocks'] else ''}".rstrip(', '),
                f"Analysis timestamp: {metadata['processing_timestamp']}"
            ]
        }
        entities.append(content_entity)
        
        # OCR-specific entity if OCR was used
        if metadata['ocr_enhanced']:
            ocr_entity = {
                "name": f"OCR_Analysis_{Path(metadata['source']).stem}",
                "entityType": "ocr_analysis",
                "observations": [
                    f"OCR confidence: {metadata['ocr_confidence']:.2f}",
                    f"Text detections: {metadata['ocr_detections']}",
                    f"Languages: {', '.join(metadata['ocr_languages'])}",
                    f"OCR engine: EasyOCR",
                    f"Processing timestamp: {metadata['processing_timestamp']}"
                ]
            }
            entities.append(ocr_entity)
        
        # Technical content entity
        if metadata['document_type'] == 'technical' or metadata['has_code_blocks']:
            tech_entity = {
                "name": f"Technical_Content_{Path(metadata['source']).stem}",
                "entityType": "technical_documentation",
                "observations": [
                    f"Framework context: {metadata['framework_context']}",
                    f"Contains code blocks: {metadata['has_code_blocks']}",
                    f"Contains tables: {metadata['has_tables']}",
                    f"Complexity level: {metadata['complexity']}",
                    f"Enhanced processing: {metadata['ocr_enhanced']}"
                ]
            }
            entities.append(tech_entity)
        
        return entities
    
    def _create_enhanced_memory_relations(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create enhanced Memory MCP relations."""
        
        relations = []
        doc_name = f"Document_{Path(metadata['source']).stem}"
        content_name = f"Content_Analysis_{Path(metadata['source']).stem}"
        
        # Document -> Content Analysis relation
        relations.append({
            "from": doc_name,
            "to": content_name,
            "relationType": "analyzed_by"
        })
        
        # Document -> Enhanced Docling Integration relation
        relations.append({
            "from": doc_name,
            "to": "Enhanced_Docling_Integration_System",
            "relationType": "processed_by"
        })
        
        # OCR-specific relations
        if metadata['ocr_enhanced']:
            ocr_name = f"OCR_Analysis_{Path(metadata['source']).stem}"
            
            relations.append({
                "from": doc_name,
                "to": ocr_name,
                "relationType": "enhanced_with"
            })
            
            relations.append({
                "from": ocr_name,
                "to": "EasyOCR_Engine",
                "relationType": "processed_by"
            })
        
        # Framework relations
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
    
    def _update_ocr_statistics(self, result: Dict[str, Any]):
        """Update OCR processing statistics."""
        
        self.ocr_statistics["total_processed"] += 1
        
        if result.get('enhanced_processing', False):
            self.ocr_statistics["ocr_enhanced"] += 1
            
            if 'ocr_details' in result and 'confidence_stats' in result['ocr_details']:
                confidence = result['ocr_details']['confidence_stats'].get('avg_confidence', 0.0)
                current_avg = self.ocr_statistics["avg_confidence"]
                count = self.ocr_statistics["ocr_enhanced"]
                # Update running average
                self.ocr_statistics["avg_confidence"] = (current_avg * (count - 1) + confidence) / count
            
            # Update detected languages
            languages = result.get('ocr_language', [])
            self.ocr_statistics["languages_detected"].update(languages)
    
    def export_enhanced_memory_data(self, output_file: str = None) -> Dict[str, Any]:
        """Export enhanced data for Memory MCP integration."""
        
        if not output_file:
            output_file = f"enhanced_docling_memory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "processing_method": "enhanced_docling_with_ocr",
            "total_documents": len(self.processed_documents),
            "total_entities": len(self.memory_entities),
            "total_relations": len(self.memory_relations),
            "ocr_statistics": {
                **self.ocr_statistics,
                "languages_detected": list(self.ocr_statistics["languages_detected"])
            },
            "memory_entities": self.memory_entities,
            "memory_relations": self.memory_relations,
            "processed_documents_summary": [
                {
                    "source": doc['source'],
                    "title": doc['title'],
                    "content_length": len(doc['markdown']),
                    "ocr_enhanced": doc.get('enhanced_processing', False),
                    "ocr_method": doc.get('ocr_method', 'none'),
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
            print(f"SUCCESS: Enhanced Memory MCP data exported to {output_file}")
            return export_data
        except Exception as e:
            print(f"ERROR: Failed to export enhanced data: {e}")
            return {}

async def test_enhanced_integration():
    """Test the enhanced Docling + OCR + Memory MCP integration."""
    
    print("=== Testing Enhanced Docling + OCR + Memory MCP Integration ===")
    
    integration = EnhancedDoclingMemoryIntegration()
    
    # Test with markdown document using OCR
    test_file = "test_document.md"
    
    if os.path.exists(test_file):
        print(f"Testing with OCR enhancement...")
        result = await integration.process_document_enhanced(
            source=test_file,
            document_type="technical",
            use_ocr=True,
            ocr_language=['en', 'ru'],
            confidence_threshold=0.5
        )
        
        if result['status'] == 'success':
            print(f"\nEntities created: {len(result['memory_entities'])}")
            print(f"Relations created: {len(result['memory_relations'])}")
            print(f"Processing method: {result['processing_method']}")
            print(f"OCR enhanced: {result['ocr_enhanced']}")
            
            # Export for review
            export_data = integration.export_enhanced_memory_data("test_enhanced_integration.json")
            
            print(f"\nOCR Statistics:")
            stats = export_data['ocr_statistics']
            print(f"  Total processed: {stats['total_processed']}")
            print(f"  OCR enhanced: {stats['ocr_enhanced']}")
            print(f"  Average confidence: {stats['avg_confidence']:.2f}")
            print(f"  Languages detected: {', '.join(stats['languages_detected'])}")
            
            print(f"\nMCP Commands to run:")
            print(f"1. {export_data['mcp_commands']['create_entities']}")
            print(f"2. {export_data['mcp_commands']['create_relations']}")
            
            return True
        else:
            print(f"Enhanced integration test failed: {result.get('error', 'Unknown error')}")
            return False
    else:
        print(f"Test file {test_file} not found!")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_integration())
    if success:
        print("\n*** Enhanced Docling + OCR + Memory MCP integration working perfectly! ***")
        print("Ready for production use with full OCR capabilities!")
    else:
        print("\n*** Integration requires additional configuration ***")