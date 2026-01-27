import os
from qdrant_client import QdrantClient

# Client for the Vector Database
COLLECTION = "docs"
_client = None

def get_vector_client():
    global _client
    if _client is not None:
        return _client

    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url or not qdrant_api_key:
        raise ValueError("Qdrant Cloud credentials missing: set QDRANT_URL and QDRANT_API_KEY")

    _client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    # Helper to ensure collection exists (Run once)
    try:
        collections = _client.get_collections().collections
        if not any(c.name == COLLECTION for c in collections):
            from qdrant_client import models
            _client.create_collection(
                collection_name=COLLECTION,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
            )
            print(f"Created collection '{COLLECTION}'")
            
            # Ensure payload index exists for filtering
            _client.create_payload_index(
                collection_name=COLLECTION,
                field_name="document_id",
                field_schema="keyword"
            )
            print(f"Verified index for 'document_id' in '{COLLECTION}'")
        else:
            print(f"Connected to collection '{COLLECTION}'")
        
    except Exception as e:
        print(f"Error checking/creating collection: {e}")
        # We don't necessarily want to crash here if it's just a transient check failure, 
        # but the original logic raised so we'll keep it for now.
        raise e
        
    return _client

