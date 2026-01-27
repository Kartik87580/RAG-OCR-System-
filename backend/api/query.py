from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.rag_service import answer_question
from pipelines.pdf_pipeline import get_supabase

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    document_id: str | None = None
    user_id: str | None = None # Added for saving history

@router.post("/query")
def query_endpoint(request: QueryRequest):
    supabase = get_supabase()
    try:
        answer = answer_question(request.question, document_id=request.document_id)
        
        # Save chat history if user_id is provided
        if request.user_id:
            try:
                data = {
                    "user_id": request.user_id,
                    "document_id": request.document_id,
                    "question": request.question,
                    "answer": answer
                }
                print(f"DEBUG: Inserting chat history: {data}")
                res = supabase.table("chats").insert(data).execute()
            except Exception as store_err:
                print(f"Failed to store chat history: {store_err}")

        return {"answer": answer}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class SummaryRequest(BaseModel):
    document_id: str | None = None
    user_id: str | None = None # Added for saving history

@router.post("/summary")
def summary_endpoint(request: SummaryRequest = SummaryRequest()):
    supabase = get_supabase()
    try:
        summary_prompt = "Provide a comprehensive summary of the provided document, highlighting the main topics, key findings, and conclusions."
        answer = answer_question(summary_prompt, document_id=request.document_id)

        # Save summary history if user_id is provided
        if request.user_id:
            try:
                data = {
                    "user_id": request.user_id,
                    "document_id": request.document_id,
                    "question": "Generate Summary",
                    "answer": answer
                }
                print(f"DEBUG: Inserting summary history: {data}")
                res = supabase.table("chats").insert(data).execute()
            except Exception as store_err:
                print(f"Failed to store summary history: {store_err}")

        return {"answer": answer}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
