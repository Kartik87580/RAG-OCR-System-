# API endpoints for document upload and processing

from fastapi import APIRouter, UploadFile, File, HTTPException
from pipelines.pdf_pipeline import process_pdf
import logging

router = APIRouter()

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    """
    Upload a PDF file for processing.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # process_pdf is synchronous, but we can call it here. 
        # Since it does CPU bound work, in a real async app we might want to run it in a threadpool
        # but for now calling it directly (FastAPI runs non-async routes in threadpool, but this is an async def).
        # Actually, if I make this 'def upload' instead of 'async def', FastAPI will run it in a threadpool automatically.
        # However, UploadFile typically suggests async usage for method calls if needed.
        # But we are passing 'file' object downstream.
        
        # We'll just call it. process_pdf handles the reading from file.file
        doc_id = process_pdf(file)
        
        return {"status": "processed", "filename": file.filename, "document_id": doc_id}
    except Exception as e:
        logging.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
