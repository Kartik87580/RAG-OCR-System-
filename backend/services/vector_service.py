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

def search(query_vector, k=4, document_id=None):
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

    try:
        # Using query_points (Universal Query) as client.search seems unavailable
        result = client.query_points(
            collection_name=COLLECTION,
            query=query_vector,
            query_filter=query_filter,
            limit=k
        )
        return result.points
    except Exception as e:
        print(f"VECTOR SEARCH FAILED: {e}")
        # Log detailed cloud error if available
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Qdrant Error Response: {e.response.text}")
        raise e


def delete_vectors_by_doc_id(document_id):
    """Delete all vectors associated with a document ID."""
    try:
        client.delete(
            collection_name=COLLECTION,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id)
                        )
                    ]
                )
            )
        )
        print(f"Vectors for document {document_id} deleted successfully.")
    except Exception as e:
        print(f"Error deleting vectors for {document_id}: {e}")
        # Log but maybe don't raise? Or raise if critical. 
        # Usually better to try and clean up as much as possible.
        raise e

if __name__ == "__main__":
    query = "what is generative ai"
    # Convert query text to vector
    query_vectors = embed_chunks([query])
    # Search with the first vector
    try:
        retrieved = search(query_vectors[0])
        if retrieved:
            print(f"Result: {retrieved[0].payload.get('text', 'No text')}")
        else:
            print("No results found.")
    except Exception as e:
        print(f"Test failed: {e}")