# SmartDocs AI
Complete RAG + MCP Knowledge Assistant

SmartDocs AI is a document knowledge assistant. You upload PDF documents, the system indexes their content natively, and you can query using RAG powered semantic vector search.

It is broken down into exactly 3 robust parts as defined by system specifications.

## Prerequisites
- Node.js LTS (v18+)
- Python 3.11+
- Virtual Environment Support

---

## 🏗️ 1. Backend Integration (FastAPI + RAG Pipeline)
This represents the foundational logic engine. It embeds text via HuggingFace models, parses PDFs by PyMuPDF, and stores vectors inside a local `ChromaDB` layer whilst saving metrics to `SQLite`.

### To Run:
1. Open a new terminal in the project root: `cd backend`
2. Create virtual python environment: `python -m venv venv`
3. Activate environment: 
   - Windows: `.\venv\Scripts\activate` 
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt` (Note: It also installs `langchain-community` implicitly on modern setup, otherwise manually pip install it alongside `sentence-transformers`)
5. Start server: `uvicorn app.main:app --reload --port 8000`

---

## 🤖 2. MCP Server 
Provides an isolated native python server running the `1.0 Model Context Protocol` via the `mcp.server.fastmcp` implementation wrapper. AI tools map directly to SQLite document telemetry.

### To Run:
1. Open a new terminal in the project root: `cd mcp_server`
2. (Optional but recommended) Activate your Python venv or create a new one.
3. Install dependencies: `pip install -r requirements.txt` 
4. Start the MCP pipeline: `python server.py`
5. Note: An MCP inspector can bridge the STDIO loop directly since `fastmcp` listens passively to pipeline logs hooks.

---

## 🖥 3. Frontend App (React + Vite + TailwindCSS)
Designed as the polished portal frontend user interface. Allows querying against documents, live streaming AI tool states, uploading chunks, and tracking knowledge base uploads.

### To Run:
1. Open a new terminal in project root: `cd frontend`
2. Install packages: `npm install`
3. **Important Check**: Make sure tailwindcss modules install completely. You can re-run `npm i -D tailwindcss@3 postcss autoprefixer` followed by `npx tailwindcss init -p` if styling visually breaks!
4. Start web server: `npm run dev`

---
*Built accurately from the SmartDocs_AI_Complete_Implementation blueprint!*
