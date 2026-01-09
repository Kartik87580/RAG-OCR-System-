# Service for RAG (Retrieval-Augmented Generation)

from services.embedding_service import embed_chunks
from services.vector_service import search
import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def build_rag_context(question, document_id=None):
    # Step 4: RAG Query Function
    q_vec = embed_chunks([question])[0]
    results = search(q_vec, document_id=document_id)
    print(f"DEBUG: Retrieved {len(results)} chunks for question: {question}")
    
    retrieved_chunks = []
    sources = []
    
    for r in results:
        # Check if payload exists and handle it safely
        payload = getattr(r, 'payload', {}) or {}
        text = payload.get("text", "")
        
        # Build chunk object for return
        chunk_obj = {
            "id": getattr(r, 'id', 'unknown'),
            "score": getattr(r, 'score', 0.0),
            "content": text,
            "metadata": {k:v for k,v in payload.items() if k != "text"}
        }
        retrieved_chunks.append(chunk_obj)
        
        # Extract source (deduplicate later if needed, but list implied)
        source = {
            "page": payload.get("page"),
            "chapter": payload.get("chapter")
        }
        if source not in sources:
            sources.append(source)

    # Format context with metadata for citation support
    formatted_context_parts = []
    for c in retrieved_chunks:
        meta = c["metadata"]
        header = f"[Source: Page {meta.get('page', '?')}, Chapter: {meta.get('chapter', 'Unknown')}]"
        formatted_context_parts.append(f"{header}\n{c['content']}")
    
    context_str = "\n\n".join(formatted_context_parts)
    
    prompt = f"""You are an expert AI assistant designed to answer questions based strictly on the provided document context.

INSTRUCTIONS:
1. Answer the user's question using ONLY the provided context below.
2. If the answer is not in the context, explicitly state "I cannot answer this based on the provided document." Do not make up information.
3. Whenever possible, refer to the specific Page or Chapter mentioned in the [Source] tags to support your answer.
4. Keep the answer professional, concise, and accurate.

CONTEXT:
{context_str}

USER QUESTION: 
{question}

ANSWER:"""
    
    return {
        "retrieved_chunks": retrieved_chunks,
        "prompt": prompt,
        "sources": sources
    }

def answer_question(question, document_id=None):
    rag_data = build_rag_context(question, document_id=document_id)
    
    # Generate answer using the prompt
    response = model.generate_content(rag_data["prompt"])
    return response.text

