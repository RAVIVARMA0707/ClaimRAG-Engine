# 📘 **ClaimRAG-Engine**

### *AI‑Powered Insurance Claims Processing & Intelligence System with Streamlit Chatbot UI*

ClaimRAG-Engine is an **AI-native claims automation and intelligence platform** built with:

*   **FastAPI backend** for RAG, LLM agents, workflows
*   **Streamlit frontend** for interactive chatbot & dashboards
*   **RAG ingestion pipeline**
*   **Fraud detection intelligence**
*   **Human-in-the-loop review flow**

The system enables **policy interpretation**, **claim evaluation**, **document analysis**, and **real-time Q/A** using modern Retrieval-Augmented Generation.

***

# ✨ **Features Overview**

## 🔍 RAG + LLM Agent Capabilities

*   Context-aware policy lookup
*   Claim coverage interpretation
*   Document-based answer generation
*   Multi-step reasoning engines
*   Custom agent workflows

## 🤖 Automated Claim Processing

*   Eligibility validation
*   Coverage constraints extraction
*   Missing info detection
*   Automated decision support

## 🔒 Fraud Intelligence

*   ML + LLM signal verification
*   Risk score generation
*   Suspicious activity detection
*   Manual review triggers

## 📄 Document Workflow Automation

*   Policy ingestion
*   PDF → text parsing
*   Cleanup, chunking & vectorization
*   Vector store indexing

## 💬 Streamlit Frontend

*   Chatbot interface
*   Real-time RAG responses
*   Claim submission UI
*   Logs / analytics (optional)

***

# 🏗 **Project Structure**

    ClaimRAG-Engine/
    │
    ├── backend/
    │   ├── src/
    │   │   ├── api/
    │   │   ├── core/
    │   │   ├── ingestion/
    │   │   ├── rag/
    │   │   └── agents/
    │   ├── main.py
    │   ├── pyproject.toml
    │   └── uv.lock
    │
    ├── frontend/
    │   ├── app.py
    │   ├── components/
    │   ├── utils/
    │   └── requirements.txt
    │
    ├── .gitignore
    ├── README.md
    └── LICENSE (optional)

***

# ⚙️ **Backend Setup (FastAPI)**

### **1. Move into backend**

```bash
cd backend
```

### **2. Create environment**

```bash
uv venv
.\.venv\Scripts\activate
```

### **3. Install dependencies**

```bash
uv sync
```

### **4. Run API server**

```bash
uvicorn backend.main:app --reload
```

### API will run at:

📍 <http://localhost:8000>  
📍 <http://127.0.0.1:8000/api/v1/query/> (Swagger UI)

***

# 📥 **RAG Document Ingestion**

To ingest policy documents:

```bash
uv run -m src.ingestion.ingestion
```

This will:

*   Load PDFs / docs
*   Clean + chunk text
*   Create embeddings
*   Store into vector database

***

# 💬 **Frontend Setup (Streamlit UI)**

### **1. Move into frontend**

```bash
cd frontend
```

### **2. Install UI dependencies**

```bash
pip install -r requirements.txt
```

### **3. Run streamlit**

```bash
streamlit run app.py
```

### Streamlit UI will run at:

📍 <http://localhost:8501>

***

# 🔌 **Frontend–Backend Communication**

The Streamlit UI communicates with the FastAPI backend through endpoints like:

### **POST /api/v1/query**

For RAG-based chatbot responses.

### **POST /api/v1/claims/evaluate**

For claim scoring & eligibility.

### **POST /api/v1/fraud/check**

For fraud detection workflows.

Make sure the FastAPI backend is running **before** starting the Streamlit UI.

***

# 📘 **Environment Variables**

Create `backend/.env`:

    OPENAI_API_KEY=your_key_here
    VECTOR_DB_PATH=./data/vector_store
    MODEL_NAME=gpt-4o-mini

Create `frontend/.env`:

    API_URL=http://localhost:8000

⚠️ **Never commit `.env` to Git.**  
Add to `.gitignore`.

***

# 🚀 **Run the System End-to-End**

### 1️⃣ Start backend

```bash
cd backend
uvicorn backend.main:app --reload
```

### 2️⃣ Start frontend

```bash
cd frontend
streamlit run app.py
```

### 3️⃣ Interact with the chatbot UI at:

<http://localhost:8501>

***

# 🧱 **Tech Stack**

| Component    | Technology                |
| ------------ | ------------------------- |
| Backend      | FastAPI, LangChain, RAG   |
| Frontend     | Streamlit                 |
| Embeddings   | Gemini                    |
| Vector Store | Postgres-Pgvector         |
| Agents       | LangChain Agents          |
| Packaging    | UV                        |

***

# 🌟 Support

If this project helps you, consider starring ⭐ the repo!

***
