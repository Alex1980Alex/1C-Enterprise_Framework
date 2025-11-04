#!/usr/bin/env python3
"""
EasyOCR integration module for Docling MCP server.
Provides OCR functionality as replacement for docling_sdg.
"""

import asyncio
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging

# Set up logging
logger = logging.getLogger(__name__)

class EasyOCRProcessor:
    """OCR processor using EasyOCR library."""
    
    def __init__(self, languages: List[str] = ['en', 'ru'], gpu: bool = False):
        """Initialize EasyOCR processor."""
        self.languages = languages
        self.gpu = gpu
        self._reader = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy initialization of EasyOCR reader."""
        if not self._initialized:
            try:
                import easyocr
                logger.info(f"Initializing EasyOCR with languages: {self.languages}")
                self._reader = easyocr.Reader(self.languages, gpu=self.gpu, verbose=False)
                self._initialized = True
                logger.info("EasyOCR reader initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")
                raise
    
    def process_image(self, image_path: str, confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """Process image with OCR and return structured results."""
        
        self._ensure_initialized()
        
        try:
            # Run OCR
            results = self._reader.readtext(image_path)
            
            # Process results
            ocr_results = {
                "success": True,
                "image_path": image_path,
                "total_detections": len(results),
                "text_blocks": [],
                "full_text": "",
                "confidence_stats": {
                    "min_confidence": 1.0,
                    "max_confidence": 0.0,
                    "avg_confidence": 0.0
                }
            }
            
            confidences = []
            full_text_parts = []
            
            for i, (bbox, text, confidence) in enumerate(results):
                if confidence >= confidence_threshold:
                    text_block = {
                        "id": i,
                        "text": text.strip(),
                        "confidence": round(confidence, 3),
                        "bbox": {
                            "top_left": [int(bbox[0][0]), int(bbox[0][1])],
                            "top_right": [int(bbox[1][0]), int(bbox[1][1])],
                            "bottom_right": [int(bbox[2][0]), int(bbox[2][1])],
                            "bottom_left": [int(bbox[3][0]), int(bbox[3][1])]
                        }
                    }
                    ocr_results["text_blocks"].append(text_block)
                    full_text_parts.append(text.strip())
                    confidences.append(confidence)
            
            # Calculate statistics
            if confidences:
                ocr_results["confidence_stats"]["min_confidence"] = min(confidences)
                ocr_results["confidence_stats"]["max_confidence"] = max(confidences)
                ocr_results["confidence_stats"]["avg_confidence"] = sum(confidences) / len(confidences)
            
            # Create full text
            ocr_results["full_text"] = " ".join(full_text_parts)
            ocr_results["filtered_detections"] = len(ocr_results["text_blocks"])
            
            logger.info(f"OCR processed {image_path}: {len(results)} detections, {len(ocr_results['text_blocks'])} above threshold")
            
            return ocr_results
            
        except Exception as e:
            logger.error(f"OCR processing failed for {image_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path
            }
    
    def process_pdf_with_ocr(self, pdf_path: str, page_numbers: Optional[List[int]] = None) -> Dict[str, Any]:
        """Process PDF with OCR for specified pages."""
        
        try:
            from pdf2image import convert_from_path
        except ImportError:
            logger.error("pdf2image not installed. Run: pip install pdf2image")
            return {
                "success": False,
                "error": "pdf2image not installed - required for PDF OCR"
            }
        
        try:
            # Convert PDF to images
            if page_numbers:
                pages = convert_from_path(pdf_path, first_page=min(page_numbers), last_page=max(page_numbers))
            else:
                pages = convert_from_path(pdf_path)
            
            pdf_results = {
                "success": True,
                "pdf_path": pdf_path,
                "total_pages": len(pages),
                "pages": [],
                "combined_text": ""
            }
            
            # Process each page
            with tempfile.TemporaryDirectory() as temp_dir:
                for i, page in enumerate(pages):
                    page_num = i + 1
                    if page_numbers and page_num not in page_numbers:
                        continue
                    
                    # Save page as image
                    page_image_path = os.path.join(temp_dir, f"page_{page_num}.png")
                    page.save(page_image_path, 'PNG')
                    
                    # Process with OCR
                    page_result = self.process_image(page_image_path)
                    page_result["page_number"] = page_num
                    
                    pdf_results["pages"].append(page_result)
                    
                    if page_result["success"]:
                        pdf_results["combined_text"] += f"\n--- Page {page_num} ---\n{page_result['full_text']}\n"
            
            pdf_results["processed_pages"] = len(pdf_results["pages"])
            return pdf_results
            
        except Exception as e:
            logger.error(f"PDF OCR processing failed for {pdf_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "pdf_path": pdf_path
            }

# Global OCR processor instance
_ocr_processor = None

def get_ocr_processor(languages: List[str] = ['en', 'ru'], gpu: bool = False) -> EasyOCRProcessor:
    """Get global OCR processor instance."""
    global _ocr_processor
    if _ocr_processor is None:
        _ocr_processor = EasyOCRProcessor(languages, gpu)
    return _ocr_processor

async def ocr_document_async(source: str, languages: List[str] = ['en', 'ru'], 
                           confidence_threshold: float = 0.5) -> Dict[str, Any]:
    """Async wrapper for OCR document processing."""
    
    processor = get_ocr_processor(languages)
    
    # Determine file type and process accordingly
    source_path = Path(source)
    
    if source_path.suffix.lower() == '.pdf':
        # Process PDF with OCR
        return processor.process_pdf_with_ocr(source)
    else:
        # Process as image
        return processor.process_image(source, confidence_threshold)

def test_ocr_integration():
    """Test OCR integration functionality."""
    
    print("=== Testing OCR Integration ===")
    
    try:
        # Test processor creation
        processor = get_ocr_processor(['en', 'ru'])
        print("SUCCESS: OCR processor created")
        
        # Test initialization
        processor._ensure_initialized()
        print("SUCCESS: OCR processor initialized")
        
        print("OCR integration ready for use!")
        return True
        
    except Exception as e:
        print(f"ERROR: OCR integration test failed: {e}")
        return False

if __name__ == "__main__":
    test_ocr_integration()