# Client for the Vector Database

from qdrant_client import QdrantClient
from config import QDRANT_PATH

COLLECTION = "docs"

try:
    client = QdrantClient(path=QDRANT_PATH)
    # Helper to ensure collection exists
    collections = client.get_collections().collections
    if not any(c.name == COLLECTION for c in collections):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config={"size": 384, "distance": "Cosine"}
        )
        print(f"Created collection '{COLLECTION}'")
    else:
        print(f"Connected to collection '{COLLECTION}'")
except Exception as e:
    print(f"⚠️ Failed to initialize persistent Qdrant client: {e}")
    print("⚠️ Falling back to IN-MEMORY Qdrant client (Data will not be saved!)")
    client = QdrantClient(location=":memory:")
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config={"size": 384, "distance": "Cosine"}
    )
