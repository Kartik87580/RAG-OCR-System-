# API endpoints for querying

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.rag_service import answer_question

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    document_id: str | None = None

@router.post("/query")
def query_endpoint(request: QueryRequest):
    try:
        answer = answer_question(request.question, document_id=request.document_id)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SummaryRequest(BaseModel):
    document_id: str | None = None

@router.post("/summary")
def summary_endpoint(request: SummaryRequest = SummaryRequest()):
    try:
        summary_prompt = "Provide a comprehensive summary of the provided document, highlighting the main topics, key findings, and conclusions."
        answer = answer_question(summary_prompt, document_id=request.document_id)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
