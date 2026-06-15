# apps/core/app/

**FastAPI backend entry point and core application**

## OVERVIEW

Python/FastAPI backend with Pydantic models, structlog logging, and custom middleware.

## STRUCTURE

```
app/
├── api/v1/           # API routes (router + /routes/.py files)
├── core/             # config.py, env_validator.py, exceptions.py, logging.py
├── services/         # auth.py, chat.py, embedding.py, llm.py, oauth.py, rag.py
├── schemas/          # Pydantic models (empty __pycache__ only)
├── models/           # Data models
├── db/               # Database
├── middleware/       # LoggingMiddleware
├── main.py           # create_app() factory + uvicorn runner
└── docs/gowa/        # Custom GoWA documentation system
```

## ENTRY POINTS

- `main.py`: `create_app()` returns FastAPI app, runnable via `uvicorn app.main:app`
- API routes registered in `api/v1/router.py` with prefix `/api/v1`
- Lifespan context manager handles logging init + env validation

## KEY CONVENTIONS

- **Linting**: `ruff` (E, F, I, N, W, UP rules)
- **Types**: `mypy` strict mode + pydantic plugin
- **Config**: YAML via `config.yaml` in `apps/core/`, loaded by `config.py`
- **Async**: Uses `asynccontextmanager` for lifespan
- **CORS**: Wide open (`allow_origins=["*"]`) - NOT for production

## ANTI-PATTERNS

- JWT secret hardcoded: `config.py` line 43 `"change-me-in-production"`
- CORS allows all origins

## NOTES

- Uses Python 3.11+ virtualenv at `apps/core/.venv`
- LLM: Deepinfra/DeepSeek-V4-Flash default
- RAG disabled by default (Qdrant config optional)
