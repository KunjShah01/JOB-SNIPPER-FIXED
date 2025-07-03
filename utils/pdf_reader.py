"""
PDF Reader Utility
Extracts text from PDF files with error handling
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path):
    """
    Extract text from PDF file using pypdf
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        Extracted text as string
    """
    try:
        # Try pypdf first (recommended)
        try:
            from pypdf import PdfReader
            
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        text += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num}: {e}")
                        continue
                
                if text.strip():
                    logger.info(f"Successfully extracted {len(text)} characters using pypdf")
                    return text.strip()
                else:
                    raise Exception("No text extracted")
                    
        except ImportError:
            logger.warning("pypdf not available, trying PyPDF2...")
            
            # Fallback to PyPDF2
            try:
                from PyPDF2 import PdfReader
                
                with open(file_path, 'rb') as file:
                    reader = PdfReader(file)
                    text = ""
                    
                    for page_num, page in enumerate(reader.pages):
                        try:
                            page_text = page.extract_text()
                            text += page_text + "\n"
                        except Exception as e:
                            logger.warning(f"Error extracting text from page {page_num}: {e}")
                            continue
                    
                    if text.strip():
                        logger.info(f"Successfully extracted {len(text)} characters using PyPDF2")
                        return text.strip()
                    else:
                        raise Exception("No text extracted")
                        
            except ImportError:
                logger.error("Neither pypdf nor PyPDF2 is available")
                raise Exception("PDF reading libraries not available. Please install pypdf: pip install pypdf")
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        
        # Try to provide helpful error messages
        if not Path(file_path).exists():
            raise Exception(f"PDF file not found: {file_path}")
        elif not Path(file_path).suffix.lower() == '.pdf':
            raise Exception(f"File is not a PDF: {file_path}")
        else:
            raise Exception(f"Failed to extract text from PDF: {e}")

def validate_pdf(file_path):
    """
    Validate if file is a readable PDF
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        bool: True if valid PDF, False otherwise
    """
    try:
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            return False
        
        # Check file extension
        if file_path.suffix.lower() != '.pdf':
            logger.error(f"File is not a PDF: {file_path}")
            return False
        
        # Check file size
        if file_path.stat().st_size == 0:
            logger.error(f"PDF file is empty: {file_path}")
            return False
        
        # Try to open with PDF reader
        try:
            from pypdf import PdfReader
        except ImportError:
            try:
                from PyPDF2 import PdfReader
            except ImportError:
                logger.error("No PDF reading library available")
                return False
        
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            
            # Check if PDF has pages
            if len(reader.pages) == 0:
                logger.error("PDF has no pages")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"PDF validation failed: {e}")
        return False

def get_pdf_info(file_path):
    """
    Get information about the PDF file
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        dict: PDF information
    """
    try:
        if not validate_pdf(file_path):
            return {"valid": False, "error": "Invalid PDF file"}
        
        try:
            from pypdf import PdfReader
        except ImportError:
            from PyPDF2 import PdfReader
        
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            
            info = {
                "valid": True,
                "pages": len(reader.pages),
                "file_size": Path(file_path).stat().st_size,
                "metadata": {}
            }
            
            # Try to get metadata
            try:
                if hasattr(reader, 'metadata') and reader.metadata:
                    metadata = reader.metadata
                    info["metadata"] = {
                        "title": metadata.get("/Title", ""),
                        "author": metadata.get("/Author", ""),
                        "subject": metadata.get("/Subject", ""),
                        "creator": metadata.get("/Creator", ""),
                        "producer": metadata.get("/Producer", ""),
                        "creation_date": str(metadata.get("/CreationDate", "")),
                        "modification_date": str(metadata.get("/ModDate", ""))
                    }
            except Exception as e:
                logger.warning(f"Could not extract metadata: {e}")
            
            return info
            
    except Exception as e:
        logger.error(f"Error getting PDF info: {e}")
        return {"valid": False, "error": str(e)}