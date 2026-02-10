from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.documents import router as documents_router
from api.query import router as query_router
import uvicorn
import os

app = FastAPI(title="OCR+RAG API", description="Backend for OCR and RAG services", version="1.0.0")

# Configure CORS - Allow all origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, consider restricting this to your frontend domain
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register Routers
app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])
app.include_router(query_router, prefix="/api", tags=["Query"])

@app.get("/")
def read_root():
    return {"message": "OCR+RAG API is running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting server on port {port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)

