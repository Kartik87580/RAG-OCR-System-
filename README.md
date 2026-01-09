# 📄 RAG-OCR-System

An **advanced document intelligence system** that combines **OCR**, **vector search**, and **Retrieval-Augmented Generation (RAG)** to enable intelligent querying of PDF documents.  
This project allows users to upload PDFs (digital or scanned), extract structured text using OCR, store embeddings in a vector database, and ask natural language questions powered by **Google Gemini**.

---

## 🚀 Project Overview

**RAG-OCR-System** is designed to bridge the gap between unstructured documents and conversational AI.  
It processes PDFs, understands their structure (chapters, sections, headings), and enables **context-aware Q&A** through a modern web interface.

---

## 🧠 How It Works (High-Level Flow)

1. **PDF Upload** (Digital / Scanned)
2. **OCR & Structure Extraction** using Docling
3. **Smart Chunking** (chapters, sections, metadata)
4. **Embedding Generation** (Sentence-Transformers)
5. **Vector Storage** in Qdrant
6. **User Query**
7. **Semantic Search + RAG**
8. **Context-Aware Answer** using Google Gemini

---

## ✨ Key Features

### 📑 PDF Upload & Processing
- Supports **digital PDFs** and **scanned documents**
- Extracts text, layout, and structural information

### 🧩 Smart Chunking
- Intelligent chunking by **chapters, sections, and headings**
- Stores rich metadata for better retrieval accuracy

### ⚡ Vector Search
- Fast and scalable **semantic search** using **Qdrant**
- High-quality embeddings via **Sentence-Transformers**

### 🤖 RAG Pipeline
- Combines retrieved context with **Google Gemini**
- Produces **accurate, context-aware answers**

### 💬 Modern UI
- Clean and responsive **React + Vite** interface
- Upload documents and chat with them seamlessly

---

## 🛠️ Tech Stack

### Backend
- **Python**
- **FastAPI**
- **Uvicorn**

### Frontend
- **React v19**
- **Vite**

### AI & Machine Learning
- **OCR**: Docling (PDF structure & text extraction)
- **Embeddings**: Sentence-Transformers
- **LLM**: Google Generative AI (Gemini)
- **Vector Database**: Qdrant

---

## 📂 Project Structure

```

rag-doc-prototype/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   │
│   ├── api/
│   │   ├── documents.py      # upload + process pdf
│   │   └── query.py          # ask questions
│   │
│   ├── services/
│   │   ├── ocr_service.py
│   │   ├── chunk_service.py
│   │   ├── embedding_service.py
│   │   ├── vector_service.py
│   │   └── rag_service.py
│   │
│   ├── pipelines/
│   │   └── pdf_pipeline.py
│   │
│   ├── db/
│   │   └── vector_client.py
│   │
│   └── utils/
│       └── file_utils.py
│
├── frontend/
│   
│   
│
├── storage/
│   ├── pdfs/
│   └── ocr/
│
├── vector-db/
│   └── qdrant_data/   
│
├── .env
└── README.md

````

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/RAG-OCR-System.git
cd RAG-OCR-System
````

---

## 🔧 Backend Setup

```bash
cd backend
```

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file inside the `backend` directory:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key   # if applicable
COLLECTION_NAME=rag_ocr_documents
```

### Run Backend Server

```bash
python app.py
```

**OR**

```bash
uvicorn app:app --reload
```

Backend will run at:

```
http://localhost:8000
```

---

## 🎨 Frontend Setup

```bash
cd frontend
```

### Install Dependencies

```bash
npm install
```

### Start Development Server

```bash
npm run dev
```

Frontend will run at:

```
http://localhost:5173
```

---

## 🧪 Usage

1. Open the frontend in your browser
2. Upload a PDF document
3. Wait for OCR & indexing to complete
4. Ask questions in natural language
5. Get **context-aware answers** from your documents

---

## 🔐 Environment Requirements

* Python **3.9+**
* Node.js **18+**
* Running Qdrant instance (local or cloud)
* Google Generative AI (Gemini) API Key

---

## 📌 Future Enhancements

* Multi-document chat
* Source citations in answers
* Role-based authentication
* Support for DOCX & Images
* Streaming responses from LLM
* Hybrid search (keyword + semantic)

---

## 🤝 Contributing

Contributions are welcome!
Feel free to fork the repository, create a feature branch, and submit a pull request.

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 🙌 Acknowledgements

* **Docling** for document OCR & structure extraction
* **Sentence-Transformers** for embeddings
* **Qdrant** for vector search
* **Google Gemini** for generative AI

---

⭐ If you find this project useful, don’t forget to **star the repository


