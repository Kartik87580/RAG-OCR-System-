# Service for generating embeddings

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunks(chunks):
    print("embeddings created Successfully")
   
    return model.encode(chunks).tolist()

