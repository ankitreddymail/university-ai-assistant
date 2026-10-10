# AI-Powered University Student Services Assistant

A practical, transparent, and interview-ready AI Assistant designed for university students, submitted for the HCLTech AI Engineer Hackathon.

## Architecture & Project Structure

The project emphasizes readable code, explicit control flow, deterministic rule evaluation for student academic standing, and modular separation of concerns.

```text
university-ai-assistant/
├── app/
│   ├── main.py                 # FastAPI application, CORS setup, and HTTP routes
│   ├── ui.py                   # Streamlit user interface for students and advisors
│   ├── schemas.py              # Pydantic v2 data models for API and data validation
│   ├── config.py               # Pydantic BaseSettings loading environment configurations
│   ├── rag/
│   │   ├── ingestion.py        # Markdown policy loader, chunker, and ChromaDB vectorizer
│   │   └── retrieval.py        # Semantic search against indexed university policies
│   ├── tools/
│   │   ├── student_data.py     # SQLite queries for student records, credits, and holds
│   │   ├── eligibility.py      # Deterministic academic checks (graduation, Dean's List)
│   │   └── rule_resolution.py  # Maps student inquiry types to business rule evaluators
│   ├── workflow/
│   │   └── graph.py            # LangGraph state machine orchestrating end-to-end reasoning
│   └── audit.py                # Transparency logger capturing queries, rules, and sources
├── scripts/
│   ├── generate_students.py    # Generates synthetic student scenarios into JSON
│   ├── validate_students.py    # Validates data integrity of student records
│   ├── load_students.py        # Seeds SQLite database from JSON dataset
│   └── evaluate.py             # Evaluation benchmark for retrieval and rule accuracy
├── data/
│   ├── documents/              # University policy markdown files
│   ├── students/               # Student JSON files and SQLite database
│   └── chroma/                 # Persistent ChromaDB vector storage
├── tests/
│   └── test_health.py          # Pytest unit tests for API endpoints
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
- Python 3.11 installed (or managed via `uv`)
- PowerShell terminal

### 2. Set Up Virtual Environment & Dependencies

From the project root in Windows PowerShell:

```powershell
# If using uv (recommended for ultra-fast setup):
uv venv .venv --python 3.11
.venv\Scripts\activate
uv pip install -r requirements.txt

# Or using standard python:
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```powershell
Copy-Item .env.example .env
```

Review `.env` to verify:
- `MODEL_NAME=qwen2.5:7b`
- `OLLAMA_BASE_URL=http://localhost:11434`
- `SQLITE_DB_PATH=data/students/university.db`
- `CHROMA_PERSIST_DIR=data/chroma`
- `API_PORT=8000`

### 4. Seed Mock Student Data

```powershell
# 1. Generate test students
python scripts/generate_students.py

# 2. Validate student integrity
python scripts/validate_students.py

# 3. Load into SQLite database
python scripts/load_students.py
```

### 5. Run the Backend API

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Visit the interactive API docs at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
Health Check endpoint: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 6. Run the Streamlit UI

In a separate terminal:

```powershell
.venv\Scripts\Activate.ps1
streamlit run app/ui.py
```

The web dashboard will be available at: [http://localhost:8501](http://localhost:8501)

### 7. Run Unit Tests

```powershell
pytest
```

---

## Docker Deployment (Optional)

To start both the API and Streamlit UI in containers:

```powershell
docker compose up --build
```
