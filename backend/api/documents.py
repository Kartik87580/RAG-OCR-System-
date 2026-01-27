from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pipelines.pdf_pipeline import process_pdf, get_supabase
from services.vector_service import delete_vectors_by_doc_id
import logging

router = APIRouter()

@router.post("/upload")
async def upload(file: UploadFile = File(...), user_id: str = Form(...)):
    """
    Upload a PDF file for processing.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # We'll just call it. process_pdf handles the reading from file.file
        doc_id = process_pdf(file, user_id)
        
        return {"status": "processed", "filename": file.filename, "document_id": doc_id}
    except Exception as e:
        logging.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """
    Delete a document and all associated data (DB, Storage, Vectors).
    """
    supabase = get_supabase()
    try:
        # Get document metadata first to find job_id and storage_path
        print(f"Attempting to delete document {doc_id}")
        response = supabase.table("documents").select("*").eq("id", doc_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc = response.data[0]
        job_id = doc.get("job_id")  # This is the Qdrant document_id
        storage_path = doc.get("storage_path")
        
        # 1. Delete from Qdrant
        if job_id:
            try:
                print(f"Deleting vectors for job_id: {job_id}")
                delete_vectors_by_doc_id(job_id)
            except Exception as e:
                logging.error(f"Failed to delete vectors: {e}")
                # We continue to delete from DB
        
        # 2. Delete from Supabase Storage
        if storage_path:
            try:
                print(f"Deleting file from storage: {storage_path}")
                supabase.storage.from_("documents").remove([storage_path])
            except Exception as e:
                logging.error(f"Failed to delete file from storage: {e}")
                
        # 3. Delete from Supabase Database
        print("Deleting record from database")
        supabase.table("documents").delete().eq("id", doc_id).execute()
        
        return {"status": "deleted", "id": doc_id}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
