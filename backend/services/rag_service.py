from config import GEMINI_API_KEY

_gemini_model = None

def get_gemini_model():
    global _gemini_model
    if _gemini_model is None:
        import google.generativeai as genai
        print("🔄 Initializing Gemini AI...")
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel("gemini-1.5-flash") # Using 1.5-flash as default stable choice
    return _gemini_model

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
    from services.embedding_service import embed_chunks
    from services.vector_service import search
    
    q_vec = embed_chunks([question])[0]
    results = search(q_vec, document_id=document_id)
    
    retrieved_chunks = []
    sources = []
    for r in results:
        payload = getattr(r, 'payload', {}) or {}
        text = payload.get("text", "")
        chunk_obj = {
            "id": getattr(r, 'id', 'unknown'),
            "score": getattr(r, 'score', 0.0),
            "content": text,
            "metadata": {k:v for k,v in payload.items() if k != "text"}
        }
        retrieved_chunks.append(chunk_obj)
        source = {
            "page": payload.get("page"),
            "chapter": payload.get("chapter"),
            "section": payload.get("section")
        }
        if source not in sources:
            sources.append(source)

    formatted_context_parts = []
    for c in retrieved_chunks:
        meta = c["metadata"]
        header = f"[Source: Page {meta.get('page', '?')}, Chapter: {meta.get('chapter', 'Unknown')}, Section: {meta.get('section', 'Unknown')}]"
        safe_content = c['content'].replace("{", "{{").replace("}", "}}")
        formatted_context_parts.append(f"{header}\n{safe_content}")
    
    context_str = "\n\n".join(formatted_context_parts)
    if not context_str.strip():
        context_str = "No relevant content found in document."
    
    mode = detect_mode(question)
    try:
        if mode == "summary":
            prompt = SUMMARY_PROMPT_TEMPLATE.format(retrieved_context=context_str, user_question=question)
        else:
            prompt = CHAT_PROMPT_TEMPLATE.format(retrieved_context=context_str, user_question=question)
    except Exception as e:
        prompt = f"Context:\n{context_str}\n\nQuestion:\n{question}\n\nAnswer:"
    
    return {
        "retrieved_chunks": retrieved_chunks,
        "prompt": prompt,
        "sources": sources
    }

def answer_question(question, document_id=None):
    import time
    from google.api_core import exceptions
    
    rag_data = build_rag_context(question, document_id=document_id)
    model = get_gemini_model()
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(rag_data["prompt"])
            return response.text
        except exceptions.ResourceExhausted:
            if attempt < max_retries - 1:
                sleep_time = (attempt + 1) * 2
                time.sleep(sleep_time)
            else:
                return "### ⚠️ Rate Limit Reached\n\nYou have hit the free tier limit for the AI model. Please wait a minute before trying again."
        except Exception as e:
             raise e
    return "Failed to generate answer."


