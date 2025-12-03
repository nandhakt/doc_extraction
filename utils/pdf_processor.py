"""
PDF Processing utilities for document extraction.
"""

import io
import base64
from pathlib import Path
from typing import List, Tuple, Optional

import fitz  # PyMuPDF
from PIL import Image


class PDFProcessor:
    """Process PDF documents for text extraction and rendering."""
    
    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        doc = fitz.open(pdf_path)
        text_parts = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
        
        doc.close()
        return "\n\n".join(text_parts)
    
    @staticmethod
    def extract_text_from_bytes(pdf_bytes: bytes) -> str:
        """
        Extract text from PDF bytes.
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Extracted text content
        """
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text_parts = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
        
        doc.close()
        return "\n\n".join(text_parts)
    
    @staticmethod
    def get_page_count(pdf_path: str) -> int:
        """Get the number of pages in a PDF."""
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count
    
    @staticmethod
    def render_page_to_image(
        pdf_path: str,
        page_num: int = 0,
        zoom: float = 2.0
    ) -> bytes:
        """
        Render a PDF page to PNG image bytes.
        
        Args:
            pdf_path: Path to the PDF file
            page_num: Page number (0-indexed)
            zoom: Zoom factor for resolution
            
        Returns:
            PNG image as bytes
        """
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        
        # Create a matrix for scaling
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image and then to bytes
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        doc.close()
        return img_bytes
    
    @staticmethod
    def render_all_pages_to_images(
        pdf_path: str,
        zoom: float = 1.5
    ) -> List[bytes]:
        """
        Render all PDF pages to PNG images.
        
        Args:
            pdf_path: Path to the PDF file
            zoom: Zoom factor for resolution
            
        Returns:
            List of PNG images as bytes
        """
        doc = fitz.open(pdf_path)
        images = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            images.append(img_byte_arr.getvalue())
        
        doc.close()
        return images
    
    @staticmethod
    def pdf_to_base64_images(pdf_path: str, zoom: float = 1.5) -> List[str]:
        """
        Convert PDF pages to base64 encoded images.
        
        Args:
            pdf_path: Path to the PDF file
            zoom: Zoom factor for resolution
            
        Returns:
            List of base64 encoded PNG images
        """
        images = PDFProcessor.render_all_pages_to_images(pdf_path, zoom)
        return [base64.b64encode(img).decode('utf-8') for img in images]
    
    @staticmethod
    def get_pdf_metadata(pdf_path: str) -> dict:
        """
        Get PDF metadata.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF metadata
        """
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        page_count = len(doc)
        
        # Get first page dimensions
        first_page = doc[0]
        rect = first_page.rect
        
        doc.close()
        
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "page_count": page_count,
            "page_width": rect.width,
            "page_height": rect.height
        }


# Singleton instance
pdf_processor = PDFProcessor()


