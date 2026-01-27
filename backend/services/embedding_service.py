# Service for generating embeddings

_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print("🔄 Loading embedding model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed_chunks(chunks):
    model = get_model()
    print("embeddings created Successfully")
    return model.encode(chunks).tolist()

