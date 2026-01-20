import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

# Client for the Vector Database

COLLECTION = "docs"

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

if not qdrant_url or not qdrant_api_key:
    raise ValueError("Qdrant Cloud credentials missing: set QDRANT_URL and QDRANT_API_KEY")

client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

# Helper to ensure collection exists
try:
    collections = client.get_collections().collections
    if not any(c.name == COLLECTION for c in collections):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config={"size": 384, "distance": "Cosine"}
        )
        print(f"Created collection '{COLLECTION}'")
    else:
        print(f"Connected to collection '{COLLECTION}'")
    
    # Ensure payload index exists for filtering
    client.create_payload_index(
        collection_name=COLLECTION,
        field_name="document_id",
        field_schema="keyword"
    )
    print(f"Verified index for 'document_id' in '{COLLECTION}'")
except Exception as e:
    print(f"Error checking/creating collection: {e}")
    raise e
