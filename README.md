# AI-Powered University Student Services Assistant

A practical, transparent, and interview-ready AI Assistant designed for university students, developed for the HCLTech AI Engineer Hackathon.

## Architecture & Project Structure

The project emphasizes readable code, explicit control flow, deterministic rule evaluation backed by SQLite, and modular separation of concerns.

```text
university-ai-assistant/
├── app/
│   ├── main.py                 # FastAPI application, CORS setup, and GET /health
│   ├── ui.py                   # Streamlit user interface (prototype)
│   ├── schemas.py              # Pydantic v2 data models aligned with Annex C
│   ├── config.py               # Pydantic BaseSettings loading environment configurations
│   ├── rag/
│   │   ├── ingestion.py        # Policy document loader (RAG ingestion skeleton)
│   │   └── retrieval.py        # Semantic retrieval skeleton
│   ├── tools/
│   │   ├── student_data.py     # SQLite queries for students, courses, attendance, results, rules
│   │   ├── eligibility.py      # Deterministic checks (attendance, exam, supp, placement)
│   │   └── rule_resolution.py  # Routes service requests to rule evaluation functions
│   ├── workflow/
│   │   └── graph.py            # LangGraph state machine skeleton
│   └── audit.py                # Transparency logger capturing queries, rules, and sources
├── scripts/
│   ├── generate_students.py    # Generates 35 synthetic students & Annex C CSV datasets
│   ├── validate_students.py    # Validates data integrity, CGPA scale, and judge ID reservations
│   ├── load_students.py        # Initializes 5 SQLite tables and imports CSV datasets
│   └── evaluate.py             # Benchmark evaluation skeleton
├── data/
│   ├── documents/              # University policy documents (synthetic demo template)
│   ├── students/               # Annex C CSV datasets and SQLite database
│   └── chroma/                 # Persistent ChromaDB vector storage (pending ingestion)
├── tests/
│   ├── test_health.py          # Pytest unit tests for FastAPI /health endpoint
│   └── test_eligibility.py     # Pytest unit tests for rule registry and eligibility checks
├── reports/                    # Audit logs and evaluation benchmark outputs
├── .env.example                # Example environment variables template
├── .gitignore                  # Git ignore rules for DBs, cache, and secrets
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container build definition
├── docker-compose.yml          # Multi-container orchestration (FastAPI + Streamlit)
└── README.md                   # Setup guide and documentation
```

---

## Windows PowerShell Setup Instructions

### 1. Prerequisites
- Windows 10/11
- PowerShell terminal
- Python 3.11 (installed in `.venv` via `uv`)

### 2. Activate Virtual Environment

The project uses a Python 3.11 virtual environment in `.venv`:

```powershell
.venv\Scripts\activate
```

*(If you ever need to recreate it from scratch using `uv`:)*
```powershell
uv venv .venv --python 3.11
.venv\Scripts\activate
uv pip install -r requirements.txt
```

### 3. Configure Environment Variables

```powershell
Copy-Item .env.example .env
```

Key configuration parameters in `.env`:
- `SQLITE_DB_PATH=data/students/university.db`
- `CHROMA_PERSIST_DIR=data/chroma`
- `DOCUMENTS_DIR=data/documents`
- `API_PORT=8000`

### 4. Generate, Validate, and Load Student Data (Annex C)

The student data follows the Annex C schema with 5 SQLite tables: `students`, `courses`, `attendance`, `results`, and `rule_registry`.

```powershell
# Step 1: Generate synthetic CSV files (35 students, 2 programmes, 2 batches, 6 courses)
.venv\Scripts\python.exe scripts/generate_students.py

# Step 2: Validate data integrity, 0-10 CGPA scale, and judge reservations
.venv\Scripts\python.exe scripts/validate_students.py

# Step 3: Create SQLite schema and load CSVs into data/students/university.db
.venv\Scripts\python.exe scripts/load_students.py
```

### 5. Ingest Documents into ChromaDB (RAG)

Ingest official PDFs and synthetic Markdown documents page-by-page into persistent ChromaDB:

```powershell
# Ingest all documents from data/documents/
.venv\Scripts\python.exe scripts/ingest_documents.py

# Inspect ingested sources and metadata
.venv\Scripts\python.exe scripts/inspect_sources.py
```

### 6. Run Unit Tests

Verify the health check, Annex C schema, rule eligibility, and RAG ingestion/retrieval:

```powershell
.venv\Scripts\pytest.exe
```

### 7. Run the Backend API

```powershell
.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

- API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Ingest Documents: `POST http://127.0.0.1:8000/ingest`
- List Sources: `GET http://127.0.0.1:8000/sources`

### 8. Run Streamlit UI (Prototype)

In a separate terminal:

```powershell
.venv\Scripts\activate
streamlit run app/ui.py
```

---

## Current Implementation Status

- [x] **FastAPI & Health Endpoint**: Implemented and verified via unit tests and live HTTP calls.
- [x] **Annex C Student Data**: 35 synthetic students, 2 programmes, 2 batches, 6 courses generated into CSVs and loaded into SQLite.
- [x] **Rule-Based Eligibility Engine**: Built on `rule_registry` table with zero hardcoded thresholds.
- [x] **Document Ingestion (RAG Stage 2)**: Page-by-page PDF & Markdown extraction, persistent ChromaDB, `POST /ingest`, and `GET /sources`.
- [ ] **LangGraph Workflow Orchestration**: Skeletons in place; node execution scheduled for workflow phase.
- [ ] **Ollama LLM Integration**: Scheduled for workflow integration.
- [ ] **Docker Container Verification**: Dockerfile and compose defined; full container testing pending.
