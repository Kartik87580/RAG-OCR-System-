# How to Run the OCR + RAG System

## 1. Start the Backend
The backend is built with FastAPI and handles PDF processing, OCR, and RAG queries.
(This is already running if you see the terminal output from the agent)

If you need to restart it:
```bash
# In the root directory
python backend/app.py
```
*Port: 5000*

## 2. Start the Frontend
The frontend is a React + Vite application.

Since `node` was not detected in the agent's path, please run this manually:

```bash
cd frontend
npm run dev
```
*Port: 5173 (usually)*

## 3. Usage
1. Open the frontend URL (e.g., http://localhost:5173).
2. Upload a PDF in the left panel.
3. Wait for the "Processed" status.
4. Ask questions in the right panel!
