# 📄 DocuChat AI - OCR + RAG System

A production-ready AI application that allows users to upload PDF documents, extract content using advanced OCR (Docling), and chat with them using Retrieval-Augmented Generation (RAG).

## 🚀 Features

-   **Advanced OCR**: Uses `Docling` to extract clean text, tables, and document hierarchy from PDFs (scanned or digital).
-   **Smart Chunking**: Hierarchy-aware chunking strategies to preserve context (Chapters > Sections > Paragraphs).
-   **Vector Search**: Stores embeddings in **Qdrant Cloud** for semantic retrieval.
-   **Generative AI**: Powered by **Google Gemini** for accurate and context-aware answers.
-   **Secure Storage**: Uses **Supabase** for file storage, database, and authentication.
-   **Modern UI**: Built with React + Vite, featuring a responsive and clean design.

---

## 🛠️ Tech Stack

### Backend
-   **Framework**: FastAPI
-   **OCR**: Docling & Docling Core
-   **LLM**: Google Gemini (via `google-generativeai`)
-   **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
-   **Vector DB**: Qdrant
-   **Database/Auth/Storage**: Supabase
-   **Language**: Python 3.10+

### Frontend
-   **Framework**: React (Vite)
-   **Styling**: Vanilla CSS (Scoped & Global)
-   **Routing**: React Router DOM
-   **State**: Context API (Auth)

---

## 📂 Project Structure

```bash
proj-1-ocr+rag/
├── backend/                # FastAPI Backend
│   ├── api/                # API Routes (Documents, Query)
│   ├── db/                 # Database Clients
│   ├── pipelines/          # PDF Processing Pipeline
│   ├── services/           # Business Logic (OCR, Chunking, RAG)
│   ├── app.py              # Entry Point
│   ├── config.py           # Config & Env Vars
│   └── requirements.txt    # Python Dependencies
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # Reusable Components
│   │   ├── context/        # Auth Context
│   │   ├── pages/          # Application Pages
│   │   ├── services/       # API Services & Clients
│   │   └── App.jsx         # Main Component
│   └── vite.config.js      # Vite Config
│
└── README.md               # Project Documentation
```

---

## 🚦 Getting Started

### Prerequisites
-   Python 3.10+
-   Node.js 16+
-   Supabase Account
-   Qdrant Cloud Account
-   Google AI Studio Key

### 1. Environment Setup

```ini
GEMINI_API_KEY=...
QDRANT_URL=...
QDRANT_API_KEY=...
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_SERVICE_KEY=...
VITE_SUPABASE_URL=...
VITE_SUPABASE_ANON_KEY=...
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
*Backend runs on `http://localhost:5000`*

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:5173`*

### 4. Database Setup
Run the SQL script located at `backend/supabase_schema.sql` in your Supabase SQL Editor to create the necessary tables and policies.

---

## 🛡️ Security
-   **Row Level Security (RLS)** is enabled on Supabase to ensure users only access their own documents.
-   **Service Keys** are used strictly on the backend for administrative overrides.
-   **Environment Variables** handle all sensitive credentials.

---

## 🤝 Contributing
1.  Fork the repository
2.  Create your feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`git commit -m 'Add some amazing feature'`)
4.  Push to the branch (`git push origin feature/amazing-feature`)
5.  Open a Pull Request
