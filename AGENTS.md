# PROJECT KNOWLEDGE BASE

**Generated:** 2026-05-26 **Stack:** Nx monorepo + Bun workspaces | Python/FastAPI + Next.js 16 | shadcn/ui + Ultracite

## OVERVIEW

Chat Kasir is a polyglot monorepo combining a **Python/FastAPI backend** (`apps/core`) with a **Next.js 16 frontend** (`apps/web`), sharing UI components via `packages/ui`. Uses Nx for task orchestration and Bun for package management.

## STRUCTURE

```
chat-kasir/
├── apps/
│   ├── core/           # Python FastAPI backend
│   │   └── app/
│   │       ├── api/v1/routes/  # auth, chat, docs, rag endpoints
│   │       ├── core/           # config, env_validator, exceptions, logging
│   │       ├── services/       # auth, chat, embedding, llm, oauth, rag
│   │       ├── schemas/        # Pydantic models
│   │       ├── models/         # Data models
│   │       ├── db/             # Database
│   │       ├── middleware/     # Logging middleware
│   │       └── main.py        # FastAPI entry point
│   └── web/             # Next.js 16 frontend
│       └── src/
│           ├── app/            # App Router (layout, page, manifest)
│           └── components/     # App-specific components
├── packages/
│   ├── ui/              # Shared shadcn/ui components (55+ components)
│   ├── env/              # @t3-oss/env-nextjs environment validation
│   └── config/           # Shared TypeScript base config
└── .agents/skills/       # Agent skill definitions
```

## WHERE TO LOOK

| Task | Location | Notes |
| --- | --- | --- |
| Backend API | `apps/core/app/` | FastAPI with Pydantic, structlog |
| API Routes | `apps/core/app/api/v1/routes/` | auth, chat, docs, rag |
| Frontend | `apps/web/src/app/` | Next.js 16 App Router |
| Shared UI | `packages/ui/src/components/` | shadcn/ui primitives |
| Env validation (web) | `packages/env/src/web.ts` | Zod schemas |
| Config | `packages/config/tsconfig.base.json` | strict: true |

## CODE MAP

| Symbol | Type | Location | Role |
| --- | --- | --- | --- |
| `create_app()` | FastAPI factory | `apps/core/app/main.py` | App initialization |
| `api_router` | APIRouter | `apps/core/app/api/v1/router.py` | Route aggregation |
| `get_config()` | Config loader | `apps/core/app/core/config.py` | YAML config + Pydantic |
| `validate_env()` | Validator | `apps/core/app/core/env_validator.py` | Env validation |
| `AppException` | Exception | `apps/core/app/core/exceptions.py` | Custom exception handler |

## CONVENTIONS

- **Monorepo**: Nx task orchestration + Bun workspaces
- **Python**: ruff (lint), mypy (types), pydantic-settings (config)
- **TypeScript**: Ultracite (lint/format), strict mode, no barrel files
- **UI**: shadcn/ui via `packages/ui`, import from `@chat-kasir/ui/components/*`
- **Catalog**: Centralized versions in root `package.json` catalog block

## ANTI-PATTERNS (THIS PROJECT)

- **No tests yet** - `apps/core/tests/` exists but empty, `apps/web/` has no test config
- **CI missing test job** - `.github/workflows/ci.yml` has no pytest execution
- **Docker compose path wrong** - CI validates `apps/core/docker-compose.yml` (doesn't exist)
- **Hardcoded JWT secret** - `config.py` line 43: `"change-me-in-production"`

## UNIQUE STYLES

- **Polyglot**: Python backend in TypeScript-dominant monorepo
- **AI integration**: Deepinfra LLM, mem0 memory, Qdrant RAG (disabled by default)
- **PWA**: Next.js PWA via `apps/web/next.config.ts` + manifest.ts
- **GoWA docs**: Custom documentation system in `apps/core/app/docs/gowa/`

## COMMANDS

```bash
bun run dev           # All apps via Nx
bun run dev:web      # Next.js only (port 3001)
bun run build        # Build all
bun run check        # Ultracite lint check
bun run fix          # Ultracite auto-fix
cd apps/core && .venv/bin/uvicorn app.main:app --reload  # Backend only
```

## NOTES

- `apps/core/` uses **Python 3.11+** with `.venv` virtualenv
- `apps/web/` runs on **port 3001** (not default 3000)
- Frontend env validation via `@t3-oss/env-nextjs` + Zod in `packages/env`
- LLM defaults to Deepinfra/DeepSeek-V4-Flash (configurable via `apps/core/config.yaml`)
