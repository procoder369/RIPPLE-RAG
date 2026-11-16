# RippleRAG

RippleRAG is a Retrieval-Augmented Generation (RAG) system for long-form fiction. It indexes stories chapter by chapter, builds a canon graph of characters, places, events, and facts, and uses that graph to answer questions, detect continuity contradictions, and trace how a change in one part of a story ripples into others.

## Features

- **Story indexing**: Splits stories into chapters and chunks, creates embeddings, and stores them in PostgreSQL with pgvector (or a local SQLite database for development).
- **Hybrid retrieval**: Combines dense vector search (pgvector / FAISS), sparse keyword search (BM25 as a fallback), and canon-graph lookups, then merges the results with fusion.
- **Re-ranking**: An LLM re-ranks retrieved passages before generation.
- **Grounded generation**: Builds prompts from retrieved context, generates answers, and runs a verifier that checks citations and factuality.
- **Canon graph**: Stores entities, relationships, approved and proposed facts, and timeline data, with a rules engine for deterministic checks.
- **Continuity checking**: Uses an LLM-driven consistency check to flag contradictions against established canon.
- **Ripple analysis**: Traverses dependencies in the canon graph to show what else is affected when a fact or event changes.
- **Pluggable LLM backend**: Supports Ollama (default), OpenAI-compatible endpoints, and a mock provider for testing.
- **REST API**: Built with FastAPI, with a health-check endpoint.

## Project Structure

```
RIPPLE RAG/
├── app/
│   ├── core/            # Settings (get_settings() reads .env)
│   ├── retrieval/       # query_processor, dense / sparse / graph / hybrid retrievers, reranker
│   ├── generation/      # context_builder, prompt_builder, llm_client, generator, verifier
│   ├── canon_graph/     # entities, relationships, fact_store, temporal, graph_service, rules_engine
│   ├── continuity/      # contradiction.py, ripple_analyzer.py
│   ├── database/        # connection (SQLAlchemy), models (Story, Chapter, Vector), vector_store, migrations/
│   └── pipelines/       # indexing_pipeline.py (Pipeline A), rag_pipeline.py (Pipeline B)
├── prompts/             # continuity_check.txt, fact_extraction.txt, story_qa.txt
├── evaluation/          # dataset.json, generation_metrics.py, retrieval_metrics.py
├── scripts/             # init_db.py, seed_stories.py, test_new_story.py, verify_api.py
├── tests/               # Unit and integration tests
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── .env.example
```

## Architecture

The system has two pipelines that share the same database and canon graph:

1. **Indexing pipeline (Pipeline A)**: Ingests a story, chunks it by chapter, extracts facts and entities with the `fact_extraction` prompt, generates embeddings, and updates the canon graph.
2. **RAG pipeline (Pipeline B)**: Takes a question, runs hybrid retrieval, re-ranks the results, builds a prompt, generates a grounded answer, and verifies it.

Continuity checks and ripple analysis run on top of the canon graph whenever a story is added or changed.

## Requirements

- Python 3.11 or newer
- PostgreSQL 15+ with the pgvector extension (production), or SQLite (development)
- An LLM provider: [Ollama](https://ollama.com) (default), or any OpenAI-compatible API
- Docker and Docker Compose (optional, for containerized runs)

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url> ripple-rag
cd ripple-rag
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the example file and edit it:

```bash
cp .env.example .env
```

A typical local configuration using Ollama looks like this:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2

# Only needed for OpenAI-compatible providers
OPENAI_API_KEY=
OPENAI_BASE_URL=
```

### 3. Start the LLM backend

If you use Ollama:

```bash
ollama pull llama3.2
ollama serve
```

### 4. Initialize the database

```bash
python scripts/init_db.py        # Creates tables and runs migrations
python scripts/seed_stories.py   # Optional: loads demo stories
```

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs are at `http://localhost:8000/docs`.

### Docker alternative

```bash
docker compose up --build
```

## Usage

### Indexing a new story

```bash
python scripts/test_new_story.py
```

This script shows an example of indexing a new story. Use it as a template for your own content.

### Asking a question

Once the API is running, query it over HTTP. For example:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Where did the protagonist first meet the mentor?"}'
```

Responses include the generated answer, the supporting passages, and verification results.

### Checking the API

```bash
python scripts/verify_api.py
```

This runs an end-to-end health check against the running server.

## Testing

Run the full test suite with pytest:

```bash
pytest
```

Test modules cover the canon graph, chunker, continuity checks, embeddings, retrieval, the RAG pipeline, and versioning.

## Evaluation

The `evaluation/` folder contains a labeled dataset (`dataset.json`) and metrics scripts:

```bash
python evaluation/retrieval_metrics.py
python evaluation/generation_metrics.py
```

## Configuration Reference

| Variable | Description | Default |
| --- | --- | --- |
| `LLM_PROVIDER` | `ollama`, `openai`, or `mock` | `ollama` |
| `LLM_MODEL` | Model name used for generation and checks | `llama3.2` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OPENAI_API_KEY` | API key for OpenAI-compatible providers | — |
| `OPENAI_BASE_URL` | Base URL for OpenAI-compatible providers | — |
| `DATABASE_URL` | SQLAlchemy connection string | SQLite dev DB |

## Troubleshooting

- **Import errors**: Every directory has an `__init__.py`. If you add a new package, add one too.
- **Empty retrieval results**: Check that the story has been indexed (`scripts/init_db.py` and `seed_stories.py`) and that embeddings were created.
- **LLM connection errors**: Confirm the provider is running and that `LLM_PROVIDER`, the base URL, and the model name in `.env` match.
- **pgvector errors**: Make sure the extension is installed in your PostgreSQL database with `CREATE EXTENSION vector;`.

## Development Notes

- The development database is `ripplerag_dev.db` (SQLite). Do not commit it; it is listed in `.gitignore`.
- Schema changes go through Alembic migrations in `app/database/migrations/`.
- Keep prompts in `prompts/` rather than hard-coding them in Python.

## License

http://www.apache.org/licenses/LICENSE-2.0
