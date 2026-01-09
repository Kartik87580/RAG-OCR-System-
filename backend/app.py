from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.documents import router as documents_router
from api.query import router as query_router
import uvicorn
import os

app = FastAPI(title="OCR+RAG API", description="Backend for OCR and RAG services", version="1.0.0")

# Configure CORS
origins = [
    "http://localhost:5173", # Vite default
    "http://localhost:3000",
    "*" # For development ease
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
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
    uvicorn.run("app:app", host="0.0.0.0", port=port)
