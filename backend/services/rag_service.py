# Service for RAG (Retrieval-Augmented Generation)

from services.embedding_service import embed_chunks
from services.vector_service import search
import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def detect_mode(question: str) -> str:
    """
    Detects if the user wants a full summary or a quick chat answer.
    """
    keywords = ["summary", "summarize", "overview", "explain document", "full explanation", "document summary"]
    q_lower = question.lower()
    
    for k in keywords:
        if k in q_lower:
            return "summary"
            
    return "chat"

SUMMARY_PROMPT_TEMPLATE = """You are an assistant that summarizes documents.

Format the answer in clean Markdown using this structure:

## Summary
(2–3 short sentences)

## Key Concepts
- Bullet points only

## Architecture / Details
- Bullet points

## Conclusion
(1 short paragraph)

## Sources
- Page X — Section Y

Rules:
- Use simple language.
- No emojis.
- No inline sources.
- No markdown inside sentences.
- Use blank lines between sections.

Context:
{retrieved_context}

Question:
{user_question}

Answer:"""

CHAT_PROMPT_TEMPLATE = """You are a helpful assistant chatting with a user about the uploaded document.

Rules:
- Answer in 2–5 short sentences.
- No headings, no bullet points, no markdown.
- No emojis.
- Use simple language.
- If not found in the document, say: "I could not find that in the document."

Context:
{retrieved_context}

Question:
{user_question}

Answer:"""

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
            "chapter": payload.get("chapter"),
            "section": payload.get("section")
        }
        if source not in sources:
            sources.append(source)

    # Format context with metadata for citation support
    formatted_context_parts = []
    for c in retrieved_chunks:
        meta = c["metadata"]
        header = f"[Source: Page {meta.get('page', '?')}, Chapter: {meta.get('chapter', 'Unknown')}, Section: {meta.get('section', 'Unknown')}]"
        formatted_context_parts.append(f"{header}\n{c['content']}")
    
    context_str = "\n\n".join(formatted_context_parts)
    
    # DETERMINE MODE & SELECT PROMPT
    mode = detect_mode(question)
    print(f"DEBUG: Detected Mode: {mode}")

    if mode == "summary":
        prompt = SUMMARY_PROMPT_TEMPLATE.format(retrieved_context=context_str, user_question=question)
    else:
        prompt = CHAT_PROMPT_TEMPLATE.format(retrieved_context=context_str, user_question=question)
    
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

