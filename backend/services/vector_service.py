import sys
import os

# Add the backend directory to sys.path so we can import from db and services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.vector_client import client, COLLECTION
from services.embedding_service import embed_chunks

def store_embeddings(chunks_data, vectors):
    # chunks_data is expected to be [{"id":..., "content":..., "metadata":...}, ...]
    payloads = []
    for chunk in chunks_data:
        # Flatten metadata and content into one payload
        payload = {
            "text": chunk.get("content", ""),
            "chunk_id": chunk.get("id", ""),
            **chunk.get("metadata", {})
        }
        payloads.append(payload)
        
    client.upload_collection(
        collection_name=COLLECTION,
        vectors=vectors,
        payload=payloads
    )
    print("embeddings stored Successfully")


from qdrant_client import models

def search(query_vector, k=5, document_id=None):
    # client.search is missing in this version, using query_points
    query_filter = None
    if document_id:
        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=document_id)
                )
            ]
        )

    result = client.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        query_filter=query_filter,
        limit=k
    )
    return result.points

if __name__ == "__main__":
    query = "what is generative ai"
    # Convert query text to vector
    query_vectors = embed_chunks([query])
    # Search with the first vector
    retrieved = search(query_vectors[0])
    print(retrieved[0].payload['text'])