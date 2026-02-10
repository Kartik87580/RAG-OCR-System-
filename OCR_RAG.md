# OCR + RAG System Implementation Guide
## Complete Interview Preparation Document

Welcome to the **MOST COMPREHENSIVE** guide for your **OCR + RAG (Retrieval-Augmented Generation) System**. This document explains EVERY file, EVERY line, and EVERY decision so you can ace technical interviews.

---

## 📋 TABLE OF CONTENTS

### BACKEND (Python/FastAPI)
1. **app.py** — The Gatekeeper
2. **config.py** — The Vault (Secrets Manager)
3. **api/documents.py** — The Document Manager
4. **api/query.py** — The Query Handler
5. **pipelines/pdf_pipeline.py** — The Orchestrator
6. **services/ocr_service.py** — The Eyes
7. **services/chunk_service.py** — The Brain (Segmenting)
8. **services/embedding_service.py** — The Translator (Text → Numbers)
9. **services/vector_service.py** — The Memory (Qdrant)
10. **services/rag_service.py** — The Mouth (Gemini AI)
11. **db/vector_client.py** — The Database Connection

### FRONTEND (React/Vite)
12. **Dashboard.jsx** — The Main Control Room
13. **ChatPanel.jsx** — The Conversation Interface
14. **UploadPanel.jsx** — The File Receiver
15. **api/config.js** — The Address Book

---

## 🛠 Project Architecture Overview

This project is built using a **Modular Multi-Service Architecture**.

### The Big Picture Flow:
[Frontend (React/Vite)]
      ↓ (1. User uploads PDF or asks a question)
[Backend (FastAPI)]
      ↓ (2. Routes request to API handlers)
[Processing Pipeline]
      ↓ (3a. Upload: OCR → Chunking → Embeddings → Vector DB)
      ↓ (3b. Query: Embedding → Vector Search → Context → LLM)
[Database (Supabase & Qdrant)]

---

## 1️⃣ `backend/app.py` — The Gatekeeper

### 1.1 FILE PURPOSE
- This is the **Entry Point** of the entire backend.
- It initializes the web server and connects all the different "roads" (routes) together.
- Think of it as the **Receptionist** of a building who directs visitors to the right floor.

### 1.2 BIG PICTURE VISUAL
`app.py` (FastAPI)
 ├── → `api/documents.py` (Upload/Delete PDF)
 ├── → `api/query.py` (Chat/RAG)
 └── → `CORSMiddleware` (Security Checker)

### 1.3 LINE-BY-LINE CODE EXPLANATION

| Line | Code | Plain English Meaning | Technical Meaning | Interview Explanation | What if Removed? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `from fastapi import FastAPI` | Import web server tools. | Importing the class. | "We use FastAPI for speed." | The code throws a `NameError` and the server won't start. |
| 2 | `CORSMiddleware` | Import security tool. | CORS handling. | "Allows React to talk to Python." | Frontend will get "Blocked by CORS" error. |
| 17-23 | `app.add_middleware(...)` | Enable the security tool. | Applying CORS configuration. | "Mandatory for modern web apps." | Browsers will block all API calls from the frontend. |
| 26-27 | `app.include_router(...)` | Connect the routes. | Router registration. | "Modularizes the app." | The API links like `/api/upload` will return 404 Not Found. |

### 1.4 SUMMARY (INTERVIEW READY)
- **What is it?** The FastAPI entry point.
- **Why is it needed?** To coordinate routes, handle security (CORS), and start the server.
- **Key Feature:** Uses **Modular Routing** to keep the codebase clean.
- **Mistake to avoid:** Forgetting to allow CORS, which leads to "Request Blocked" errors on the frontend.

---

## 2️⃣ `backend/api/documents.py` — The Document Manager

### 2.1 FILE PURPOSE
- This file handles **Document Lifecycle**: Uploading, Listing, and Deleting.
- It acts as the **Post Office** that receives a package (PDF) and sends it to the factory for processing.

### 2.2 BIG PICTURE VISUAL
`POST /upload` → `process_pdf()` (in `pdf_pipeline.py`) → Returns Success
`DELETE /{id}` → Delete from Database + Delete from Vector DB + Delete from Storage

### 2.3 LINE-BY-LINE CODE EXPLANATION (Main Upload Function)

| Line | Code | Plain English Meaning | Technical Meaning | Interview Explanation |
| :--- | :--- | :--- | :--- | :--- |
| 1-3 | `from fastapi import ...`, `from pipelines...` | Bring in tools for routes and the processing pipeline. | Importing route decorators and the core processing function `process_pdf`. | "We import `process_pdf` from our pipeline because the API shouldn't handle heavy work." |
| 8-9 | `@router.post("/upload")` | Create a doorway for file uploads. | Defining a POST endpoint that accepts a `File` and a `user_id`. | "We use a POST request because we are sending data (a file) to the server." |
| 13-14 | `if not file.filename.endswith('.pdf'):` | Check if it's really a PDF. | Input validation to ensure the file format is correct. | "Security check: We only allow PDFs to prevent users from uploading malicious scripts." |
| 18 | `doc_id = process_pdf(file, user_id)` | Send the file to the "Heavy Machinery" (Pipeline). | Calling the orchestrator function that handles OCR and Vectorization. | "This is where the magic happens; we hand off the file to our background pipeline." |
| 20 | `return {"status": "processed", ...}` | Tell the user everything went well. | Returning a JSON response with the new `document_id`. | "We return the `document_id` so the frontend can use it to ask questions later." |

### 2.4 DATA FLOW VISUAL
File Input → Validation → **Pipeline Execution** → Success Response

### 2.5 COMMON INTERVIEW QUESTIONS
- **Q: Why don't you process the PDF inside the API line?**
- **A:** API endpoints should be fast. Processing a 100-page PDF takes time. In a real-world app, we'd use a **Task Queue (like Celery)** to do this in the background.

---

## 3️⃣ `backend/pipelines/pdf_pipeline.py` — The Orchestrator

### 3.1 FILE PURPOSE
- This is the **Project Manager**. It doesn't do the work itself, but it tells everyone else what to do.
- It coordinates: Saving to Storage → OCR → Chunking → Vectors.

### 3.2 BIG PICTURE VISUAL
[PDF File] → [Supabase Storage]
      ↓
[OCR Service] → Extract Text
      ↓
[Chunk Service] → Cut into small pieces
      ↓
[Embedding Service] → Turn text into numbers
      ↓
[Vector Service] → Save to Qdrant (Memory)

### 3.3 LINE-BY-LINE CODE EXPLANATION (`process_pdf`)

| Line | Code | Plain English Meaning | Technical Meaning | Interview Explanation |
| :--- | :--- | :--- | :--- | :--- |
| 31-32 | `tempfile.mkstemp(...)` | Create a safe, temporary spot for the file. | Creating a unique temporary file path on the server. | "We save the file temporarily because OCR tools often need a file path, not just bytes." |
| 38-44 | `with open... shutil.copyfileobj(...)` | Save the uploaded content into that temporary spot. | Writing the streamed file content to the disk. | "FastAPI streams files for efficiency; we write that stream to our temp file." |
| 47 | `init_ocr()` | Wake up the "Eyes" (OCR tool). | Initializing the OCR model (PaddleOCR or Marker). | "We only load the model once to save RAM and time." |
| 50 | `job_id = str(uuid.uuid4())` | Give this task a unique ID name. | Generating a Universally Unique Identifier for the document. | "Every document gets a `job_id` so we can track its vectors and metadata uniquely." |
| 54 | `markdown_text, json_pages = fast_extract_pdf(...)` | Convert the PDF into structured text. | Calling the OCR service to get both raw text and structural data. | "We extract text as Markdown to preserve headers and tables, which helps the LLM." |
| 71-75 | `supabase.storage...upload(...)` | Save a backup copy in the cloud. | Uploading the PDF to Supabase Storage. | "We persist the original file so the user can download or view it later." |
| 85 | `supabase.table("documents").insert(...)` | Save the details in the database. | Storing document metadata (name, user_id) in a SQL table. | "This acts as our 'Registry' to know which user owns which document." |
| 93 | `result = extract_hierarchy_and_chunk(...)` | Slice the long text into small snippets. | Calling the chunking service to create context windows. | "LLMs have limits; we slice text into 500-character chunks so they fit in memory." |
| 109 | `vectors = embed_chunks(...)` | Turn text into a list of numbers (coordinates). | Using an Embedding Model to vectorize the text. | "Computers don't understand words; they understand 'Vectors' (numerical positions)." |
| 110 | `store_embeddings(...)` | Save those numbers in the Vector Memory. | Inserting vectors and metadata into the Qdrant database. | "This lets us perform a 'Semantic Search' later during the RAG process." |

### 3.4 SUMMARY (INTERVIEW READY)
- **Role:** Execution Pipeline.
- **Workflow:** Temp Save → Cloud Upload → OCR → Chunk → Embed → Vector Store.
- **Why UUID?** To prevent duplicate document conflicts.
- **Why Temp Cleanup?** To prevent the server's hard drive from filling up with old PDFs.

---

## 4️⃣ `backend/services/ocr_service.py` — The Eyes

### 4.1 FILE PURPOSE
- This file extracts text from the PDF.
- It uses **Docling**, a modern tool that understands headers, tables, and paragraphs.

### 4.2 LINE-BY-LINE CODE EXPLANATION (`init_ocr`)

| Line | Code | Plain English Meaning | Technical Meaning | Interview Explanation |
| :--- | :--- | :--- | :--- | :--- |
| 15-34 | `def init_ocr():` | Prepare the OCR engine. | Implementing a Singleton pattern for the DocumentConverter. | "We initialize the model once and store it in a global variable to avoid reloading it every time." |
| 25-26 | `pipeline_options.do_ocr = True` | Turn on text and table recognition. | Configuring the conversion pipeline to include OCR and table structure analysis. | "We enable OCR specifically so we can handle scanned PDFs, not just digital ones." |

### 4.3 LINE-BY-LINE CODE EXPLANATION (`export_chapters_final`)

| Line | Code | Plain English Meaning | Technical Meaning | Interview Explanation |
| :--- | :--- | :--- | :--- | :--- |
| 59-65 | `for item, level in doc.iterate_items():` | Go through the PDF item by item. | Iterating through the hierarchical document structure. | "Docling provides a tree-like structure. We look for 'heading' items at level 0 to split the document into logical chapters." |
| 77-80 | `if isinstance(item, TableItem):` | If you find a table, treat it specially. | Detecting table elements and exporting them to Markdown. | "I export tables as Markdown because LLMs are very good at reading markdown tables compared to raw text." |

---

## 5️⃣ `backend/services/chunk_service.py` — The Brain (Segmenting)

### 5.1 FILE PURPOSE
- Cutting a long book into small, readable snippets (Chunks).
- **Why?** LLMs (like Gemini) have a limit on how much text they can "read" at once.

### 5.2 LINE-BY-LINE CODE EXPLANATION (`create_chunks`)

| Line | Code | Plain English Meaning | Technical Meaning | Interview Explanation |
| :--- | :--- | :--- | :--- | :--- |
| 123-125 | `MAX_CHARS = 2000` | Set a limit for each snippet. | Defining the chunk size threshold (~500 tokens). | "We aim for 500 tokens per chunk. This provides enough context for the AI without overwhelming it." |
| 135 | `if len(current_chunk) + len(para) > MAX_CHARS:` | If adding this paragraph makes the snippet too long, stop. | Implementing a greedy chunking algorithm with paragraph awareness. | "We try to keep paragraphs intact. We only split a paragraph if it's exceptionally long." |

---

## 6️⃣ `backend/services/vector_service.py` — The Memory (Qdrant)

### 6.1 FILE PURPOSE
- Saving and Searching the "numerical" version of our text.
- It uses **Qdrant**, a specialized database for AI vectors.

### 6.2 LINE-BY-LINE CODE EXPLANATION (`search`)

| Line | Code | Plain English Meaning | Technical Meaning | Interview Explanation |
| :--- | :--- | :--- | :--- | :--- |
| 35-43 | `query_filter = ...` | Only search inside ONE document. | Applying a metadata filter for multi-tenancy. | "This is crucial. If User A asks a question, we only search User A's document, not everyone else's." |
| 47 | `client.query_points(...)` | Find the top 4 most similar snippets. | Performing a Vector Similarity Search (HNSW). | "This isn't a keyword search (like Ctrl+F). It's a semantic search that finds meaning even if words are different." |

---

## 7️⃣ `backend/services/rag_service.py` — The Mouth (Gemini AI)

### 7.1 FILE PURPOSE
- This is the final step. It takes the "Question" + "Context" and generates an "Answer".
- It uses **Gemini 1.5 Flash**.

### 7.2 THE RAG FORMULA
[Question] + [4 Best Chunks from Vector DB] → [Prompt] → [LLM] → [Final Answer]

### 7.3 LINE-BY-LINE CODE EXPLANATION (`answer_question`)

| Line | Code | Plain English Meaning | Technical Meaning | Interview Explanation |
| :--- | :--- | :--- | :--- | :--- |
| 133 | `rag_data = build_rag_context(...)` | Get the snippets and build the instructions. | Orchestrating the retrieval and prompt engineering. | "We first retrieve the relevant document parts before even talking to the AI." |
| 139 | `model.generate_content(...)` | Ask the AI to answer using ONLY the retrieved parts. | Invoking the LLM generation. | "We use Gemini 1.5 Flash because it's fast, has a large context window, and is cost-effective." |
| 141-146 | `except exceptions.ResourceExhausted:` | If we ask too many questions too fast, wait. | Implementing an Exponential Backoff retry logic. | "I added retry logic for rate limits to ensure a smooth user experience even on the free tier." |

---

## 8️⃣ SUMMARY (INTERVIEW READY)

### 🏆 Top 3 "Pro" Features to Mention:
1. **Hierarchical Chunking:** We don't just cut text blindly; we respect chapters and sections.
2. **Table Preservation:** We extract tables as Markdown so the AI can "read" the data format correctly.
3. **Multi-Tenant Search:** We use metadata filtering in Qdrant to ensure users only see their own data (System Security).

### 🛠 How to handle "What could go wrong?":
- **OCR Errors:** Scanned documents might have blurry text. Solution: Use high-quality OCR like Marker or Docling.
- **Lost Context:** If a chunk is too small, it loses meaning. Solution: Use "Overlapping Chunks" or "Parent Document Retrieval".
- **Hallucinations:** AI making things up. Solution: In the prompt, tell the AI: "If the answer is not in the text, say you don't know."

### 🚀 Future Improvements:
- **Hybrid Search:** Combine Vector search with Keyword search (BM25) for better accuracy.
- **Reranking:** Use a second AI model to double-check the 20 best results and pick the top 5.
- **Streaming:** Make the AI answer appear word-by-word (better UX).

---

## 9️⃣ `backend/config.py` — The Vault (Secrets Manager)

### 9.1 FILE PURPOSE
- **Central Configuration**: All API keys and sensitive credentials are loaded from ONE place.
- **Security**: We use a `.env` file to prevent secrets from being committed to GitHub.

### 9.2 LINE-BY-LINE CODE EXPLANATION

| Line | Code | Plain English Meaning | Technical Meaning | Interview Explanation | What if Removed? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2 | `from dotenv import load_dotenv` | Import a tool to read secret files. | Loading the python-dotenv library. | "We use dotenv to read environment variables from a `.env` file." | Secrets won't load; API calls will fail with 'None' keys. |
| 5-9 | `dotenv_path = ...` | Find the `.env` file (backend or root). | Implementing a fallback path resolution. | "I added fallback logic so the app works from any directory." | The app might not find `.env` if run from a different folder. |
| 13-20 | `GEMINI_API_KEY = os.getenv(...)` | Read each secret from the file. | Loading environment variables into Python constants. | "These are our credentials for Gemini, Qdrant, and Supabase." | Services will crash with authentication errors. |

### 9.3 INTERVIEW TALKING POINTS
- **Q: Why not hardcode API keys?**
- **A:** "Hardcoding keys is a security risk. If I push code to GitHub, anyone can steal my keys. Using `.env` and `.gitignore` prevents this."

---

## 🔟 `backend/db/vector_client.py` — The Database Connection

### 10.1 FILE PURPOSE
- Connects to **Qdrant Cloud** (Vector Database).
- Creates the collection if it doesn't exist.

### 10.2 LINE-BY-LINE CODE EXPLANATION

| Line | Code | Plain English Meaning | Technical Meaning | Interview Explanation | What if Removed? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 8-11 | `if _client is not None: return _client` | Use the existing connection. | Implementing the Singleton pattern. | "We only connect to Qdrant once to save time and resources." | We'd create multiple connections, wasting memory and API calls. |
| 19 | `_client = QdrantClient(url=..., api_key=...)` | Establish the connection. | Instantiating the Qdrant client with Cloud credentials. | "We use Qdrant Cloud so we don't need to host our own vector database." | The app crashes with 'No module' or connection error. |
| 28 | `vectors_config=...size=384...` | Set the dimensions of our vectors. | Defining vector space dimensions to match the embedding model. | "384 dimensions because we use 'all-MiniLM-L6-v2' embedding model." | Vectors won't upload; dimension mismatch error. |
| 33-37 | `create_payload_index(...)` | Speed up filtering by document_id. | Creating an index for fast metadata filtering. | "This is critical for multi-user apps. It lets us filter 'Show only User A's docs.'" | Searches become slow; no user isolation. |

### 10.3 INTERVIEW TALKING POINTS
- **Q: What is Qdrant?**
- **A:** "Qdrant is a specialized vector database. Unlike SQL databases that store rows and columns, Qdrant stores high-dimensional vectors and performs similarity searches using HNSW algorithm."

---

## 🧠 `backend/services/embedding_service.py` — The Translator

### 11.1 FILE PURPOSE
- Converts text into **vectors** (numerical representations).
- Uses **SentenceTransformers** with the `all-MiniLM-L6-v2` model.

### 11.2 WHY EMBEDDINGS?
Computers can't understand "What is AI?"
But they CAN understand: `[0.45, -0.12, 0.89, ..., 0.34]` (384 numbers)

Similar meanings → Similar vectors → Found by Vector Search

### 11.3 LINE-BY-LINE CODE EXPLANATION

| Line | Code | Plain English Meaning | Technical Meaning | Interview Explanation | What if Removed? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 10 | `SentenceTransformer("all-MiniLM-L6-v2")` | Load a pre-trained AI model. | Loading a 22MB transformer model from HuggingFace. | "This model converts text to 384-dimensional vectors. It's lightweight and fast." | No embeddings; the entire RAG system fails. |
| 16 | `model.encode(chunks).tolist()` | Convert text list to number list. | Batching text encoding and converting numpy to Python list. | "We process multiple chunks at once for efficiency." | Can't store text in Qdrant; only vectors allowed. |

### 11.4 INTERVIEW TALKING POINTS
- **Q: Why not use OpenAI embeddings?**
- **A:** "OpenAI embeddings cost money per API call. SentenceTransformers runs locally, so it's free and private."

---

# 📱 FRONTEND SYSTEM

## The Frontend Flow:
```
[User Opens App]
     ↓
[Landing Page] → Login/Signup
     ↓
[Dashboard] (Sidebar + Main Area)
     ↓ (Upload)
[UploadPanel] → POST /api/documents/upload → Backend Pipeline
     ↓ (Select Document)
[ChatPanel] → POST /api/query → RAG Service → Answer
```

---

## 1️⃣2️⃣ `frontend/src/pages/Dashboard.jsx` — The Control Room

### 12.1 FILE PURPOSE
- The **main landing page** after login.
- Shows a **sidebar** with all user documents.
- Shows the **chat area** for the selected document.

### 12.2 BIG PICTURE VISUAL
```
+------------------+------------------------+
|   SIDEBAR        |    MAIN AREA           |
| [+ New Doc]      |                        |
| - Doc1.pdf       |   [ChatPanel]          |
| - Doc2.pdf       |   or                   |
|                  |   [UploadPanel Modal]  |
+------------------+------------------------+
```

### 12.3 KEY LOGIC BREAKDOWN

| Lines | What It Does | Why It's Needed | Interview Explanation |
| :--- | :--- | :--- | :--- |
| 68-72 | `useEffect(() => fetchDocuments())` | Load user's documents on page load. | "This React hook fetches the document list from Supabase when the component mounts." |
| 74-83 | `fetchDocuments()` | Query Supabase for all docs. | "We filter by `user_id` so users only see their own documents (security)." |
| 38-40 | `DELETE /api/documents/${docId}` | Delete document from everywhere. | "This calls our backend which deletes from DB, Storage, and Qdrant in one go." |
| 147 | `setCurrentDocumentId(doc.job_id)` | Switch to the clicked document. | "When a user clicks a document, we update the state which re-renders ChatPanel." |

### 12.4 STATE MANAGEMENT

| State Variable | Purpose | Interview Explanation |
| :--- | :--- | :--- |
| `documents` | List of all user documents | "Holds metadata fetched from Supabase." |
| `currentDocumentId` | Which document is active | "This is the 'job_id' passed to ChatPanel for filtering queries." |
| `showUpload` | Show/hide upload modal | "Boolean flag for modal visibility." |

### 12.5 INTERVIEW TALKING POINTS
- **Q: Why use `job_id` instead of database `id`?**
- **A:** "The `job_id` is the UUID we generate during processing. It's the same ID stored in Qdrant vectors. The database `id` is just the row ID in Supabase."

---

## 1️⃣3️⃣ `frontend/src/components/ChatPanel.jsx` — The Conversation UI

### 13.1 FILE PURPOSE
- Displays the **chat history** for the selected document.
- Sends user questions to the backend.
- Shows AI responses.

### 13.2 LINE-BY-LINE CODE EXPLANATION (Key Functions)

| Lines | Code | Plain English Meaning | Technical Meaning | Interview Explanation |
| :--- | :--- | :--- | :--- | :--- |
| 22-53 | `useEffect(() => fetchHistory())` | Load old chats from database. | Querying Supabase 'chats' table on component mount. | "When a user selects a document, we load their previous questions and answers from Supabase." |
| 68-76 | `fetch("/api/query", {...})` | Ask the backend a question. | Making a POST request with question, document_id, and user_id. | "We send the question to our RAG pipeline. The backend handles retrieval and generation." |
| 81-89 | `setChatHistory([...prev, {...}])` | Add the answer to the screen. | Immutably updating React state to re-render the UI. | "We append the new Q&A to the history array so it displays immediately." |
| 107-114 | `fetch("/api/summary", {...})` | Request a document summary. | Triggering the summary endpoint. | "The backend uses a different prompt template for summaries vs. quick questions." |
| 135-138 | `if (e.key === 'Enter' && !e.shiftKey)` | Send message on Enter key. | Handling keyboard events for UX. | "Enter sends the message. Shift+Enter creates a new line." |

### 13.3 DATA FLOW VISUAL
```
User Types Question → [State: question]
     ↓ (Presses Enter)
POST /api/query {question, document_id, user_id}
     ↓
Backend: Embed → Search Qdrant → Build Prompt → Gemini → Answer
     ↓
Frontend: Receives {answer: "..."}
     ↓
Update chatHistory → Re-render → User Sees Answer
```

### 13.4 INTERVIEW TALKING POINTS
- **Q: Why save history to Supabase?**
- **A:** "So users can close the app and come back later to see their previous conversations. It's like ChatGPT's chat history feature."

---

## 1️⃣4️⃣ `frontend/src/components/UploadPanel.jsx` — The File Receiver

### 14.1 FILE PURPOSE
- Lets users **upload PDF files**.
- Shows **drag-and-drop** UI.
- Shows **progress bar** and success state.

### 14.2 LINE-BY-LINE CODE EXPLANATION (Core Logic)

| Lines | Code | Plain English Meaning | Technical Meaning | Interview Explanation |
| :--- | :--- | :--- | :--- | :--- |
| 18-27 | `validateAndSetFile()` | Check if it's a PDF. | Client-side validation before upload. | "We validate the file type on the frontend first to give instant feedback." |
| 56-59 | `formData.append("file", file)` | Package the file for upload. | Creating a multipart/form-data request body. | "FormData is the standard way to send files via HTTP. The backend expects 'file' and 'user_id' fields." |
| 62-68 | `setInterval(() => setProgress(...))` | Fake progress bar. | UX enhancement with simulated progress. | "PDF processing takes 5-20 seconds. We show a fake progress bar for better UX until the real response arrives." |
| 70-73 | `fetch("/api/documents/upload", {...})` | Send file to backend. | Making a POST request with FormData. | "We don't use JSON here; we use form-data because we're sending a binary file." |
| 82-84 | `onUploadSuccess(data.document_id)` | Tell parent component. | Calling a callback prop. | "This triggers the Dashboard to refresh the document list and switch to the new doc." |
| 29-43 | Drag-and-drop handlers | Allow file dropping. | Implementing HTML5 drag-and-drop API. | "Modern UX: Users can drag files from their desktop directly into the app." |

### 14.3 STATE FLOW VISUAL
```
[No File Selected] → Drag & Drop Area Visible
     ↓ (User selects file)
[File Selected] → Shows file name and size
     ↓ (User clicks "Upload & Process")
[Uploading...] → Progress bar 0% → 100%
     ↓ (Backend responds)
[Success] → Green checkmark "Ready to Chat"
     ↓
Dashboard switches to ChatPanel
```

### 14.4 INTERVIEW TALKING POINTS
- **Q: Why not use a library for file upload?**
- **A:** "For a simple use case like this, vanilla JavaScript FormData is sufficient. Adding a library would increase bundle size unnecessarily."

---

## 1️⃣5️⃣ `frontend/src/api/config.js` — The Address Book

### 15.1 FILE PURPOSE
- **Single source of truth** for the backend API URL.
- Supports **environment variables** for deployment.

### 15.2 LINE-BY-LINE CODE EXPLANATION

| Line | Code | Plain English Meaning | Technical Meaning | Interview Explanation |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `import.meta.env.VITE_API_URL \|\| "http://localhost:5000"` | Use custom URL or default. | Reading Vite environment variables with fallback. | "In production, we set `VITE_API_URL` to our deployed backend. Locally, it defaults to port 5000." |

### 15.3 WHY THIS MATTERS
**Without this:**
- Every API call would hardcode `http://localhost:5000`
- Deployment would require changing 50+ files

**With this:**
- One file change updates ALL API calls
- Easy to switch between dev/staging/production

---

## 🎯 COMPLETE SYSTEM DATA FLOW

### Upload Flow:
```
[User] → Dashboard → Click "New Document"
   ↓
UploadPanel → Select PDF → Click "Upload"
   ↓
POST /api/documents/upload {file, user_id}
   ↓
[Backend] process_pdf()
   ↓
1. Save to Supabase Storage
2. Save metadata to Supabase DB
3. OCR → Extract text (Docling)
4. Chunk → Split into 500-token pieces
5. Embed → Convert to vectors (SentenceTransformer)
6. Store → Save to Qdrant with metadata
   ↓
Return {document_id: "abc-123"}
   ↓
Dashboard refreshes → Shows new document in sidebar
```

### Query Flow:
```
[User] → ChatPanel → Type "What is AI?"
   ↓
POST /api/query {question, document_id, user_id}
   ↓
[Backend] answer_question()
   ↓
1. Embed question → [0.12, -0.45, ...]
2. Search Qdrant → Find top 4 similar chunks
   (Filter: only this document_id)
3. Build prompt → Combine question + chunks
4. Call Gemini → Generate answer
5. Save to Supabase chats table
   ↓
Return {answer: "AI is..."}
   ↓
ChatPanel displays answer → User reads response
```

---

## 🎓 INTERVIEW MASTERY GUIDE

### 💡 Explaining the "Smart" Parts:

1. **Hierarchical Chunking**
   - **What:** We detect chapter headers and section headers using regex.
   - **Why:** Preserves document structure. A chunk like "# Introduction..." is more useful than random mid-paragraph text.
   - **How to explain:** "I don't just split at 500 tokens. I respect semantic boundaries like chapters."

2. **Table Preservation**
   - **What:** We export tables as Markdown tables.
   - **Why:** LLMs are trained on Markdown. They can "read" table structure.
   - **How to explain:** "Instead of OCR spitting out 'Name Address Phone' as raw text, we format it as a proper table."

3. **Multi-Tenant Filtering**
   - **What:** We add `document_id` to every vector.
   - **Why:** Prevents data leakage between users.
   - **How to explain:** "When User A asks a question, we filter Qdrant to ONLY search User A's vectors. It's like row-level security."

### ⚙️ Edge Cases & Debugging:

| Problem | Cause | Solution | Interview Answer |
| :--- | :--- | :--- | :--- |
| Blurry scanned PDF | OCR fails to read text | Use better OCR (Marker) or image preprocessing | "I'd implement image enhancement before OCR." |
| AI hallucinates | LLM makes up facts | Add constraint in prompt: "If not in doc, say I don't know" | "I use defensive prompting to reduce hallucinations." |
| Slow page load | Large documents = many vectors | Implement pagination or lazy loading | "I'd add virtual scrolling for chat history." |
| CORS error | Frontend can't reach backend | Enable CORS middleware | "I added CORSMiddleware with proper origins." |

### 🚀 Scaling Considerations:

**Current System:** 
- Good for 1-100 users
- Processes 1 document at a time

**To Scale to 10,000 users:**
1. **Background Jobs:** Use Celery + Redis for async PDF processing
2. **CDN:** Serve frontend from Vercel/Netlify
3. **Database:** Add read replicas to Supabase
4. **Caching:** Cache embeddings in Redis to avoid re-computing
5. **Rate Limiting:** Prevent API abuse

---

## 🏆 FINAL INTERVIEW CHEAT SHEET

### When asked "Walk me through your project":

> "I built an OCR + RAG system that lets users upload PDFs and ask questions about them. 
>
> On the **backend**, I use FastAPI for the API layer. When a PDF is uploaded, I:
> 1. Store it in Supabase (cloud storage)
> 2. Use Docling for OCR to extract text and tables
> 3. Apply intelligent chunking that respects document structure
> 4. Generate embeddings using SentenceTransformers
> 5. Store vectors in Qdrant for semantic search
>
> When a user asks a question, I:
> 1. Embed the question
> 2. Search Qdrant for the 4 most relevant chunks
> 3. Send those chunks + the question to Gemini
> 4. Return the AI-generated answer
>
> On the **frontend**, I use React with Vite. The Dashboard shows all documents in a sidebar. When you select a document, the ChatPanel lets you ask questions. I implemented drag-and-drop upload, real-time progress tracking, and chat history persistence.
>
> Key technical decisions:
> - Used Qdrant over Pinecone because it's open-source
> - Used Gemini 1.5 Flash for speed and cost-efficiency
> - Used SentenceTransformers to avoid per-query API costs
> - Implemented metadata filtering for multi-user support"

### Top 5 Questions You'll Get:

1. **"Why RAG instead of fine-tuning?"**
   - "Fine-tuning requires thousands of examples and is expensive. RAG works immediately with any document and can be updated in real-time."

2. **"How do you handle large PDFs?"**
   - "I chunk them into 500-token pieces. Even a 1000-page book becomes ~2000 chunks. Qdrant can handle millions of vectors."

3. **"What if two chunks have the same similarity score?"**
   - "Qdrant returns them in order. I take the top 4. If there's a tie, it doesn't matter much because they're equally relevant."

4. **"How did you secure user data?"**
   - "Supabase Row Level Security (RLS) ensures users only see their own documents. Qdrant filtering ensures users only search their own vectors."

5. **"What's the biggest challenge you faced?"**
   - "Handling table extraction. Initially, OCR would jumble table cells. I switched to Docling which preserves table structure as Markdown, and accuracy improved dramatically."

---

## 🔥 BONUS: Technical Terminology to Use

Using the right technical terms makes you sound experienced:

- ❌ Don't say: "I save the text in a database"
- ✅ Say: "I store embeddings in a vector database using cosine similarity for retrieval"

- ❌ Don't say: "I cut the text into small pieces"
- ✅ Say: "I implement semantic chunking with a 500-token window"

- ❌ Don't say: "The AI reads the document"
- ✅ Say: "The LLM performs retrieval-augmented generation using context from the vector store"

---

## ✅ COMPLETION CHECKLIST

Before your interview, make sure you can:
- [ ] Draw the system architecture on a whiteboard
- [ ] Explain what RAG is in 30 seconds
- [ ] Describe the difference between embeddings and tokens
- [ ] Walk through the upload flow from button click to database
- [ ] Walk through the query flow from user question to AI answer
- [ ] Explain why you chose each technology (FastAPI, Qdrant, Gemini, React)
- [ ] Describe one thing you'd improve if you had more time

**You're now ready to confidently explain every part of your OCR + RAG system!** 🚀
