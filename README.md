# RippleRAG

**Narrative Intelligence Engine for Lore Q&A, Canon Graph Tracking, Continuity Auditing, and Ripple Analysis.**

RippleRAG serves as an independent AI service powering storytelling platforms, worldbuilding wikis, and interactive narrative systems. It bridges vector embeddings with graph-based narrative state tracking to ensure story manuscripts remain coherent across complex chapters.

---

## 🏛️ System Architecture

```
┌────────────────────────────────────────────────────────┐
│               RIPPLE — Main Application                │
│                 (React / Next.js + FastAPI)            │
│         Story Editor · Reader · Version Control        │
└──────────────────────────┬─────────────────────────────┘
                           │ REST API / HTTP
┌──────────────────────────▼─────────────────────────────┐
│             RippleRAG — Independent AI Service         │
│          Python + FastAPI + Sentence Transformers      │
│                                                        │
│   ┌────────────────────────┐  ┌────────────────────┐   │
│   │       PIPELINE A       │  │     PIPELINE B     │   │
│   │   Index chapters,      │  │  Hybrid retrieval, │   │
│   │   scene-aware chunks,  │  │  reranker, context │   │
│   │   fact extraction      │  │  generation & verif│   │
│   └────────────────────────┘  └────────────────────┘   │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│               RippleRAG Knowledge Storage              │
│            PostgreSQL + pgvector + CanonGraph          │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Features

1. **Pipeline A: Scene-Aware Ingestion**
   - Chunks fiction along scene breaks (`***`, `---`, `### Scene`) without cutting character dialogue in half.
   - Generates dense vector representations and proposes extracted story facts.

2. **Pipeline B: Hybrid & Graph Retrieval**
   - Dense vector similarity (`pgvector`).
   - Sparse lexical keyword retrieval (BM25).
   - Graph fact retrieval (relational k-hop neighborhood from `CanonGraph`).
   - Reciprocal Rank Fusion (RRF) and narrative reranking.

3. **Canon Graph (State & Knowledge Graph)**
   - Tracks characters, locations, items, factions, and relationships with temporal validity (`valid_from_chapter` to `valid_to_chapter`).
   - Human-in-the-loop fact review: facts transition from `PROPOSED` to `APPROVED` or `REJECTED`.

4. **Continuity Engine**
   - Deterministic rule checks (e.g. deceased characters cannot take actions in future chapters without flashbacks).
   - Semantic contradiction detection for trait, state, and plot consistency.

5. **Ripple Analyzer (What-If Counterfactuals)**
   - Computes the downstream impact radius of changing a plot event or character state across downstream chapters and dependent facts.

---

## 🛠️ Quickstart

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Initialize & Seed Sample Story

```bash
# Initialize DB tables
python scripts/init_db.py

# Seed sample story ("The Obsidian Crown") with chapters and canon facts
python scripts/seed_stories.py
```

### 4. Run the API Server

```bash
uvicorn app.main:app --reload --port 8000
```
Interactive API docs are available at `http://localhost:8000/docs`.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health status |
| `POST` | `/api/v1/indexing/chapter` | Ingest and index chapter manuscript (Pipeline A) |
| `POST` | `/api/v1/query/ask` | Ask lore/narrative questions with citations (Pipeline B) |
| `POST` | `/api/v1/continuity/check` | Audit manuscript text for plot holes & contradictions |
| `POST` | `/api/v1/ripple/analyze` | Run what-if counterfactual impact analysis |
| `GET` | `/api/v1/canon/facts` | Query approved or proposed canon facts |
| `POST` | `/api/v1/canon/facts/review` | Approve or reject proposed facts |
| `POST` | `/api/v1/canon/entities` | Register character, location, or faction |
| `POST` | `/api/v1/canon/relationships`| Link entities with directional narrative relationships |

---

## 🧪 Testing

Run test suite with `pytest`:
```bash
pytest tests/ -v
```

---

## 🐳 Docker Deployment

```bash
docker-compose up --build
```
This spins up PostgreSQL with `pgvector` and the FastAPI service.

