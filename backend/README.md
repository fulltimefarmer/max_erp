# Max ERP Backend

FastAPI backend for Max ERP. See the repository root `README.md` for the full
project overview, technology stack and deployment instructions.

## Stack

- Python 3.12+, managed with [uv](https://docs.astral.sh/uv/)
- FastAPI (auto-generated Swagger docs at `/docs`)
- SQLAlchemy 2.0 (async) + asyncpg + PostgreSQL
- Pydantic v2 + pydantic-settings
- JWT (PyJWT) + OAuth2 password flow + bcrypt
- structlog structured JSON logging
- pytest + pytest-asyncio (SQLite in-memory for unit tests)
- LangChain / LangGraph / BGE embeddings (optional `ai` extra)

## Local development

```bash
uv sync --extra dev
cp .env.example .env
uv run uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for the interactive API docs.

## Testing

```bash
uv run pytest
```

## Default account

On first startup the database is initialized with:

| Role | Username | Password  |
|------|----------|-----------|
| root | root     | root12345 |

Change the root credentials via `ROOT_USERNAME`, `ROOT_EMAIL` and
`ROOT_PASSWORD` in your `.env` file.
