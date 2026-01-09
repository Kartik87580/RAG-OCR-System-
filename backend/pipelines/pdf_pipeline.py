# Pipeline for processing PDFs

import sys
import os
import tempfile
import uuid

import shutil

# Add the backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.ocr_service import init_ocr, fast_extract_pdf
from services.chunk_service import extract_hierarchy_and_chunk
from services.embedding_service import embed_chunks
from services.vector_service import store_embeddings

def process_pdf(file):
    print("Processing PDF...")
    # Create a temporary file to save the uploaded content
    # Use mkstemp to generate a unique safe path with .pdf extension
    fd, temp_file_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd) # Close the file descriptor immediately, we just need the path

    try:
        # Save the uploaded file to the temporary path
        with open(temp_file_path, "wb") as buffer:
            # Check if it's a FastAPI UploadFile (has .file attribute)
            if hasattr(file, "file"):
                shutil.copyfileobj(file.file, buffer)
            else:
                # Fallback for other file-like objects
                shutil.copyfileobj(file, buffer)
        
        # Initialize OCR (idempotent, loads once)
        init_ocr()
        
        # Generate a job ID
        job_id = str(uuid.uuid4())
        
        # Extract Text and JSON Pages
        # Returns (full_markdown, json_pages)
        markdown_text, json_pages = fast_extract_pdf(temp_file_path, job_id)
        
        if not json_pages:
            print("No text/content extracted.")
            return
            
        original_filename = getattr(file, 'filename', 'uploaded_file.pdf')

        # Advanced Chunking with Hierarchy
        result = extract_hierarchy_and_chunk(json_pages)
        print("Chunking.........")
        chunks_data = result['chunks']
        
        if not chunks_data:
             print("No chunks created from content.")
             return None

        # Inject document-level metadata into each chunk
        for chunk in chunks_data:
            chunk['metadata']['document_id'] = job_id
            chunk['metadata']['filename'] = original_filename

        # Prepare for embedding - extract just the text content
        texts_to_embed = [c['content'] for c in chunks_data]
        
        vectors = embed_chunks(texts_to_embed)
        store_embeddings(chunks_data, vectors)
        
        print(f"Successfully processed {original_filename}")
        print(f"Total Chunks: {len(chunks_data)}")
        
        return job_id

    except Exception as e:
        print(f"Error processing PDF: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == "__main__":
    print("This pipeline is intended to be run via the API with a file upload.")
   