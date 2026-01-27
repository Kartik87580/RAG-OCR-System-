from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY

_supabase_client = None

def get_supabase():
    global _supabase_client
    if _supabase_client is None:
        from supabase import create_client
        # Use Service Key if available to bypass RLS for backend operations
        key_to_use = SUPABASE_SERVICE_KEY if SUPABASE_SERVICE_KEY else SUPABASE_KEY
        _supabase_client = create_client(SUPABASE_URL, key_to_use)
    return _supabase_client

def process_pdf(file, user_id: str):
    import os
    import tempfile
    import uuid
    import shutil
    import time
    from services.ocr_service import init_ocr, fast_extract_pdf
    from services.chunk_service import extract_hierarchy_and_chunk
    from services.embedding_service import embed_chunks
    from services.vector_service import store_embeddings

    supabase = get_supabase()

    print(f"Processing PDF for user {user_id}...")
    
    # Create a temporary file to save the uploaded content
    # Use mkstemp to generate a unique safe path with .pdf extension
    fd, temp_file_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd) # Close the file descriptor immediately, we just need the path
    
    job_id = None

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


        # --- Supabase Integration ---
        try:
            print("Uploading to Supabase...")
            bucket_name = "documents"
            # Organize by user_id to prevent collisions and for RLS policies if needed later
            storage_path = f"{user_id}/{original_filename}"
            
            with open(temp_file_path, "rb") as f:
                supabase.storage.from_(bucket_name).upload(
                    path=storage_path, 
                    file=f, 
                    file_options={"content-type": "application/pdf", "upsert": "true"}
                )
            
            # Save Metadata
            metadata = {
                "filename": original_filename,
                "user_id": user_id, 
                "upload_time": time.strftime('%Y-%m-%dT%H:%M:%S'),
                "storage_path": storage_path,
                "job_id": job_id
            }
            supabase.table("documents").insert(metadata).execute()
            print("Metadata saved to Supabase.")

        except Exception as e:
            print(f"Error uploading to Supabase: {e}")
            raise e

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
        raise e # Ensure the API knows it failed
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        # Cleanup extracted chapters directory
        if job_id:
            try:
                chapters_dir = f"extracted_chapters_{job_id}"
                if os.path.exists(chapters_dir):
                    shutil.rmtree(chapters_dir)
            except Exception as e:
                print(f"Error cleaning up chapters directory: {e}")

if __name__ == "__main__":
    print("This pipeline is intended to be run via the API with a file upload.")