# Tech Stack & Project Structure

Document generated from codebase analysis.

## Overview

Chat Kasir is a **polyglot monorepo** combining a Python/FastAPI backend with a Next.js 16 frontend, sharing UI components via `packages/ui`. Uses Nx for task orchestration and Bun for package management.

```
chat-kasir/
├── apps/
│   ├── core/           # Python FastAPI backend
│   └── web/            # Next.js 16 frontend
├── packages/
│   ├── ui/             # Shared shadcn/ui components (55+)
│   ├── env/            # @t3-oss/env-nextjs environment validation
│   └── config/         # Shared TypeScript base config
├── .agents/            # Agent skills & configuration
├── skills-lock.json
├── package.json        # Bun workspace root
├── nx.json             # Nx monorepo config
├── bts.jsonc           # Better-T-Stack config
└── docker-compose.yml  # Multi-service orchestration
```

---

## Project Structure

### Full Directory Tree

```
chat-kasir/
├── .agents/
│   └── skills/                    # Agent skill definitions
│       ├── hallmark/
│       ├── deep-agents-memory/
│       ├── devops-engineer/
│       ├── devops-rollout-plan/
│       ├── fastapi/
│       ├── fastapi-python/
│       ├── find-skills/
│       ├── hallmark/
│       ├── langchain-fundamentals/
│       ├── langchain-middleware/
│       ├── langchain-rag/
│       ├── langgraph-docs/
│       ├── langgraph-fundamentals/
│       ├── langgraph-human-in-the-loop/
│       ├── langgraph-persistence/
│       ├── next-best-practices/
│       ├── shadcn/
│       ├── sqlalchemy-alembic-expert-best-practices-code-review/
│       ├── ultracite/
│       ├── vercel-composition-patterns/
│       ├── vercel-react-best-practices/
│       ├── web-design-guidelines/
│       └── whatsapp-automation/
│
├── apps/
│   ├── core/                       # Python FastAPI Backend
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py              # FastAPI app factory (create_app), uvicorn runner
│   │   │   ├── AGENTS.md            # Agent context for core
│   │   │   │
│   │   │   ├── api/
│   │   │   │   └── v1/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── router.py    # API route aggregation (/api/v1)
│   │   │   │       └── routes/
│   │   │   │           ├── __init__.py
│   │   │   │           ├── auth.py   # /api/v1/auth/* - register, login, me, Google OAuth
│   │   │   │           ├── chat.py   # /api/v1/chat/* - health, chat endpoint
│   │   │   │           ├── docs.py   # /api/v1/docs/gowa/* - OpenAPI spec, webhook docs
│   │   │   │           └── rag.py    # /api/v1/rag/* - ingest, query (RAG disabled by default)
│   │   │   │
│   │   │   ├── core/                # Application core
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py        # YAML config loader + Pydantic settings (LLM, DB, JWT, RAG, OAuth)
│   │   │   │   ├── env_validator.py # Required env vars validation (DEEPINFRA_API_KEY, DATABASE_URL, JWT_SECRET_KEY)
│   │   │   │   ├── exceptions.py    # AppException, LLMException, ConfigurationException
│   │   │   │   └── logging.py       # structlog configuration (JSON/console, levels)
│   │   │   │
│   │   │   ├── services/            # Business logic
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py          # JWT token creation/verification, password hashing (scrypt)
│   │   │   │   ├── chat.py          # Chat service (LLM calls via httpx)
│   │   │   │   ├── llm.py           # LLM provider abstraction (DeepInfra + Gemini fallback strategy)
│   │   │   │   ├── oauth.py         # Google OAuth2 integration, user creation from Google
│   │   │   │   ├── embedding.py     # FastEmbed text embeddings (BAAI/bge-small-en-v1.5)
│   │   │   │   └── rag.py           # Qdrant vector store, document retrieval
│   │   │   │
│   │   │   ├── schemas/             # Pydantic request/response models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat.py          # ChatRequest, ChatResponse
│   │   │   │   └── user.py          # UserCreate, UserResponse, Token, TokenPayload, LoginRequest
│   │   │   │
│   │   │   ├── models/              # SQLAlchemy ORM models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── database.py      # Base declarative, Message model
│   │   │   │   └── user.py          # User (UUID, username, full_name, whatsapp, hashed_password, is_active)
│   │   │   │                        # OAuthAccount (provider, provider_account_id, tokens)
│   │   │   │
│   │   │   ├── db/                  # Database configuration
│   │   │   │   ├── __init__.py
│   │   │   │   └── session.py       # AsyncSessionLocal, get_db(), PostgreSQL async engine
│   │   │   │
│   │   │   ├── middleware/
│   │   │   │   ├── __init__.py
│   │   │   │   └── logging.py       # LoggingMiddleware (request ID, duration, structured logs)
│   │   │   │
│   │   │   ├── docs/
│   │   │   │   └── gowa/            # GoWA WhatsApp API documentation
│   │   │   │       ├── openapi.yaml
│   │   │   │       └── webhook-payload.md
│   │   │   │
│   │   │   └── dependencies.py      # FastAPI dependencies (get_current_user, get_db)
│   │   │
│   │   ├── .env                     # Environment variables (gitignored)
│   │   ├── .env.example             # Example environment variables
│   │   ├── .venv/                   # Python virtual environment
│   │   ├── pyproject.toml           # Python dependencies (fastapi, langchain, langgraph, sqlalchemy, etc.)
│   │   ├── config.yaml              # YAML configuration (LLM, mem0, server, logging)
│   │   ├── Dockerfile
│   │   ├── uv.lock
│   │   └── .gitignore
│   │
│   └── web/                         # Next.js 16 Frontend
│       ├── src/
│       │   ├── app/
│       │   │   ├── layout.tsx       # Root layout (Providers, Header, Geist fonts)
│       │   │   ├── page.tsx         # Home page (ASCII art banner)
│       │   │   ├── manifest.ts      # PWA manifest (metadata route)
│       │   │   └── favicon.ico
│       │   │
│       │   ├── components/
│       │   │   ├── header.tsx       # Navigation header with mode toggle
│       │   │   ├── mode-toggle.tsx  # Dark/light theme switcher
│       │   │   ├── providers.tsx    # ThemeProvider + Toaster (client components)
│       │   │   ├── theme-provider.tsx # next-themes wrapper
│       │   │   ├── loader.tsx       # Loading spinner component
│       │   │   └── AGENTS.md
│       │   │
│       │   └── index.css            # Tailwind CSS entry point
│       │
│       ├── package.json             # Next.js 16, React 19, Tailwind CSS 4, shadcn/ui
│       ├── next.config.ts           # Typed routes, React Compiler enabled
│       └── AGENTS.md
│
├── packages/
│   ├── ui/                          # Shared shadcn/ui component library (59 components)
│   │   ├── src/
│   │   │   ├── components/           # 55+ shadcn/ui primitives (all .tsx files)
│   │   │   │   ├── accordion.tsx
│   │   │   │   ├── alert.tsx
│   │   │   │   ├── alert-dialog.tsx
│   │   │   │   ├── aspect-ratio.tsx
│   │   │   │   ├── avatar.tsx
│   │   │   │   ├── badge.tsx
│   │   │   │   ├── breadcrumb.tsx
│   │   │   │   ├── button.tsx
│   │   │   │   ├── calendar.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── carousel.tsx
│   │   │   │   ├── checkbox.tsx
│   │   │   │   ├── collapsible.tsx
│   │   │   │   ├── combobox.tsx
│   │   │   │   ├── context-menu.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   ├── direction.tsx
│   │   │   │   ├── drawer.tsx
│   │   │   │   ├── dropdown-menu.tsx
│   │   │   │   ├── empty.tsx
│   │   │   │   ├── field.tsx
│   │   │   │   ├── hover-card.tsx
│   │   │   │   ├── input-otp.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── input-group.tsx
│   │   │   │   ├── item.tsx
│   │   │   │   ├── kbd.tsx
│   │   │   │   ├── label.tsx
│   │   │   │   ├── menubar.tsx
│   │   │   │   ├── native-select.tsx
│   │   │   │   ├── navigation-menu.tsx
│   │   │   │   ├── pagination.tsx
│   │   │   │   ├── popover.tsx
│   │   │   │   ├── progress.tsx
│   │   │   │   ├── radio-group.tsx
│   │   │   │   ├── resizable.tsx
│   │   │   │   ├── scroll-area.tsx
│   │   │   │   ├── select.tsx
│   │   │   │   ├── separator.tsx
│   │   │   │   ├── sheet.tsx
│   │   │   │   ├── skeleton.tsx
│   │   │   │   ├── slider.tsx
│   │   │   │   ├── sonner.tsx
│   │   │   │   ├── spinner.tsx
│   │   │   │   ├── switch.tsx
│   │   │   │   ├── table.tsx
│   │   │   │   ├── tabs.tsx
│   │   │   │   ├── textarea.tsx
│   │   │   │   ├── toggle.tsx
│   │   │   │   ├── toggle-group.tsx
│   │   │   │   ├── tooltip.tsx
│   │   │   │   └── command.tsx
│   │   │   │
│   │   │   ├── hooks/
│   │   │   │   └── use-mobile.ts
│   │   │   │
│   │   │   ├── lib/
│   │   │   │   └── utils.ts          # cn() utility (clsx + tailwind-merge)
│   │   │   │
│   │   │   ├── styles/
│   │   │   │   └── globals.css       # Tailwind + shadcn design tokens
│   │   │   │
│   │   │   └── components.json      # shadcn registry configuration
│   │   │
│   │   ├── package.json             # shadcn, tailwindcss, recharts, embla-carousel, etc.
│   │   ├── postcss.config.mjs
│   │   ├── tsconfig.json
│   │   └── AGENTS.md
│   │
│   ├── env/                         # Environment validation
│   │   ├── src/
│   │   │   └── web.ts               # @t3-oss/env-nextjs + Zod validation
│   │   └── package.json
│   │
│   └── config/                      # Shared TypeScript config
│       └── package.json
│
├── .github/
│   └── workflows/
│       └── ci.yml                  # CI pipeline (missing pytest, wrong docker-compose path)
│
├── .vscode/
│   └── extensions.json
│
├── package.json                     # Root workspace (Bun), Nx, Ultracite, ESLint
├── tsconfig.json                    # Base TypeScript config (strict mode)
├── nx.json                          # Nx task orchestration
├── bts.jsonc                        # Better-T-Stack configuration
├── bunfig.toml                      # Bun workspace config
├── bun.lock                         # Dependency lock file
├── eslint.config.mjs                # ESLint flat config
├── prettier.config.mjs             # Prettier config
├── stylelint.config.mjs            # Stylelint config
├── opencode.json                   # OpenCode agent config
├── skills-lock.json                # Skills dependency lock
├── docker-compose.yml              # core + whatsapp services
└── tech-stack.md                   # This document
```

---

## Frontend (`apps/web`)

### Entry Points

| File | Purpose |
|------|---------|
| `src/app/page.tsx` | Home route (`/`) - ASCII art banner |
| `src/app/layout.tsx` | Root layout wrapping all pages (Header, Providers) |
| `src/app/manifest.ts` | PWA manifest (metadata route) |

### Components

| Component | Type | Purpose |
|-----------|------|---------|
| `header.tsx` | Client | Navigation with links + ModeToggle |
| `mode-toggle.tsx` | Client | Dark/light theme switcher |
| `providers.tsx` | Client | ThemeProvider + Sonner toaster |
| `theme-provider.tsx` | Client | next-themes wrapper |
| `loader.tsx` | Component | Loading spinner |

### Tech Stack

| Category | Technology | Version |
|----------|------------|---------|
| Framework | Next.js | 16.2.0 |
| UI Library | React | 19.2.6 |
| Styling | Tailwind CSS | 4.1.18 |
| Type Safety | TypeScript | 6 |
| Toast Notifications | sonner | 2.0.5 |
| Icons | lucide-react | 0.546.0 |
| Dark Mode | next-themes | 0.4.6 |
| React Compiler | babel-plugin-react-compiler | 1.0.0 |
| PWA | next-pwa (implied) | - |

**Key Features:**
- App Router with typed routes
- React Compiler enabled
- PWA support (port 3001)
- Zod schema validation via `@t3-oss/env-nextjs`

---

## Backend (`apps/core`)

### Application Structure

```
app/
├── main.py              # FastAPI factory: create_app()
├── dependencies.py      # get_current_user, get_db, CurrentToken, DBSession
├── api/v1/
│   ├── router.py        # Route aggregation (/api/v1)
│   └── routes/
│       ├── auth.py      # /auth/register, /auth/login, /auth/me, /auth/login/google, /auth/callback/google
│       ├── chat.py      # /chat/health, /chat/chat
│       ├── docs.py      # /docs/gowa/openapi.yaml, /docs/gowa/webhook
│       └── rag.py       # /rag/ingest, /rag/query
├── core/
│   ├── config.py        # AppConfig with LLM, mem0, server, logging, jwt, database, google_oauth, rag settings
│   ├── env_validator.py # validate_env() - DEEPINFRA_API_KEY, DATABASE_URL, JWT_SECRET_KEY
│   ├── exceptions.py    # AppException, LLMException, ConfigurationException
│   └── logging.py       # init_logging() - structlog JSON/console configuration
├── services/
│   ├── auth.py          # verify_password, hash_password, create_access_token, decode_token
│   ├── chat.py          # ChatService.process() - LLM HTTP calls
│   ├── llm.py           # LLMService (DeepInfra primary + Gemini fallback strategy)
│   ├── oauth.py         # Google OAuth2, get_or_create_user_from_google, create_jwt_for_user
│   ├── embedding.py     # EmbeddingService.embed_documents/embed_query (FastEmbed)
│   └── rag.py           # RAGService - Qdrant collection, add_documents, retrieve
├── schemas/
│   ├── chat.py          # ChatRequest, ChatResponse
│   └── user.py          # UserBase, UserCreate, UserUpdate, UserResponse, Token, TokenPayload, LoginRequest
├── models/
│   ├── database.py      # Base (DeclarativeBase), Message model
│   └── user.py          # User, OAuthAccount, OAuthProvider
├── db/
│   └── session.py       # AsyncSessionLocal, get_db(), create_async_engine
├── middleware/
│   └── logging.py       # LoggingMiddleware (request ID, method, path, client IP, duration)
└── docs/gowa/
    ├── openapi.yaml     # GoWA WhatsApp API OpenAPI spec
    └── webhook-payload.md # Webhook payload documentation
```

### API Routes

| Prefix | Route File | Endpoints |
|--------|------------|-----------|
| `/api/v1/chat` | `routes/chat.py` | `GET /health`, `POST /chat` |
| `/api/v1/auth` | `routes/auth.py` | `POST /register`, `POST /login`, `GET /me`, `GET /login/google`, `GET /callback/google` |
| `/api/v1/docs/gowa` | `routes/docs.py` | `GET /openapi.yaml`, `GET /webhook` |
| `/api/v1/rag` | `routes/rag.py` | `POST /ingest`, `POST /query` |

### Services

| Service | Class | Purpose |
|---------|-------|---------|
| Auth | `auth.py` | JWT tokens, password hashing (scrypt) |
| Chat | `chat.py` | Direct LLM calls (httpx) |
| LLM | `llm.py` | Provider abstraction (DeepInfra + Gemini fallback) |
| OAuth | `oauth.py` | Google OAuth2 integration |
| Embedding | `embedding.py` | FastEmbed text embeddings |
| RAG | `rag.py` | Qdrant vector store operations |

### Data Models

**User Model:**
- `id` (UUID, primary key)
- `username` (unique, indexed)
- `full_name`
- `whatsapp_number`
- `hashed_password`
- `is_active`, `is_superuser`
- `created_at`, `updated_at`
- OAuth accounts relationship

**OAuthAccount Model:**
- `id` (UUID)
- `user_id` (FK to users)
- `provider` (OAuthProvider enum: GOOGLE, GITHUB)
- `provider_account_id`
- `access_token`, `refresh_token`, `expires_at`

**Message Model:**
- `id` (String, primary key)
- `session_id` (indexed)
- `user_id` (indexed, nullable)
- `role`, `content`
- `created_at`

### Tech Stack

| Category | Technology | Version |
|----------|------------|---------|
| Framework | FastAPI | 0.128.0+ |
| Python | Python | 3.11+ |
| ASGI Server | uvicorn[standard] | 0.30.0+ |
| Data Validation | Pydantic | 2.9.0+ |
| Settings | pydantic-settings | 2.5.0+ |
| ORM | SQLAlchemy | 2.0.30+ |
| AI Framework | LangChain | 1.3.1+ |
| Agent Framework | LangGraph | 1.2.1+ |
| Memory | mem0ai | 2.0.2+ |
| Vector DB | qdrant-client | 1.14.0+ |
| Embeddings | fastembed | - |
| HTTP Client | httpx | 0.27.0+ |
| JWT | python-jose[cryptography] | 3.3.0+ |
| Password Hashing | passlib[scrypt] | 1.7.4+ |
| Logging | structlog | 24.0.0+ |
| Retry | tenacity | 8.2.0+ |
| OAuth | httpx-oauth | 0.17.0+ |
| Config | pyyaml | 6.0.0+ |

### LLM Configuration (config.yaml)

```yaml
llm:
  provider: "deepinfra"
  model: "deepseek-ai/DeepSeek-V4-Flash"
  base_url: "https://api.deepinfra.com/v1/openai"
  temperature: 0.7
  max_tokens: 4096
  timeout: 120

mem0:
  persistence_enabled: false
  limit: 10

server:
  host: "0.0.0.0"
  port: 8000
  reload: false
  workers: 1

logging:
  level: "INFO"
  format: "json"
```

### Dev Tools (Python)

- **Testing:** pytest + pytest-asyncio
- **Type Checking:** mypy (strict mode, pydantic plugin)
- **Linting:** ruff (E, F, I, N, W, UP rules)

---

## Shared UI (`packages/ui`)

**59 components** - shadcn/ui primitives

### Components

| Category | Components |
|----------|------------|
| Layout | `accordion`, `collapsible`, `resizable`, `scroll-area`, `separator` |
| Forms | `checkbox`, `input`, `input-otp`, `label`, `radio-group`, `select`, `slider`, `switch`, `textarea`, `toggle`, `toggle-group`, `native-select` |
| Data Display | `badge`, `card`, `table`, `avatar`, `calendar`, `Skeleton`, `progress`, `kbd` |
| Feedback | `alert`, `alert-dialog`, `toast`, `sonner`, `spinner`, `empty` |
| Navigation | `breadcrumb`, `dropdown-menu`, `navigation-menu`, `tabs`, `pagination` |
| Overlays | `dialog`, `drawer`, `popover`, `sheet`, `tooltip`, `hover-card` |
| Composition | `command`, `combobox`, `menubar`, `context-menu`, `item`, `field`, `button-group`, `input-group` |
| Charts | `chart` (recharts) |
| Carousel | `carousel` (embla-carousel-react) |

### Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| shadcn | 3.6.2 | Component framework |
| tailwindcss | 4.x | Styling |
| class-variance-authority | 0.7.1 | Component variants |
| clsx | 2.1.1 | Class merging |
| tailwind-merge | 3.3.1 | Tailwind utility merge |
| tw-animate-css | 1.3.4 | Animation |
| cmdk | 1.1.1 | Command palette |
| react-day-picker | 10.0.1 | Date picker |
| embla-carousel-react | 8.6.0 | Carousel |
| input-otp | 1.4.2 | OTP input |
| react-resizable-panels | 4.11.2 | Resizable panels |
| recharts | 3.8.0 | Charts |
| vaul | 1.1.2 | Drawer |
| @base-ui/react | 1.5.0 | Base UI primitives |

---

## Packages

### `@chat-kasir/env`

Environment validation with `@t3-oss/env-nextjs` + Zod

```typescript
// packages/env/src/web.ts
import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

export const env = createEnv({
  emptyStringAsUndefined: true,
});
```

### `@chat-kasir/config`

Shared TypeScript configuration (strict mode)

---

## Infrastructure

| Category | Technology |
|----------|------------|
| Package Manager | Bun (1.3.9) |
| Monorepo | Nx (21.5.2) |
| JS/TS Linting | Ultracite (7.7.0) |
| Type Checking | TypeScript (strict) |
| Python Linting | Ruff |
| Python Type Checking | Mypy |
| Build Orchestration | Nx run-many |

### Nx Configuration (nx.json)

```json
{
  "targetDefaults": {
    "build": { "dependsOn": ["^build"], "inputs": ["production", "^production"] },
    "check-types": { "dependsOn": ["^check-types"], "inputs": ["default", "^default"] },
    "dev": { "cache": false }
  }
}
```

---

## Docker Services

### docker-compose.yml

```yaml
services:
  core:
    build:
      context: .
      dockerfile: apps/core/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DEEPINFRA_API_KEY=${DEEPINFRA_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    networks:
      - core-network

  whatsapp:
    image: aldinokemal2104/go-whatsapp-web-multidevice:latest
    ports:
      - "8080:8080"
    command: ["--debug", "true"]
    restart: unless-stopped
    networks:
      - core-network

networks:
  core-network:
    driver: bridge
```

### WhatsApp Service (GOWA)

**Go WhatsApp Web Multi-Device** - https://github.com/aldinokemal/go-whatsapp-web-multidevice

| Attribute | Value |
|-----------|-------|
| Stars | ~4K |
| Latest Version | v8.5.1 |
| Architecture | ARM & AMD support |
| Features | Multi-device, Webhooks, MCP, Chatwoot CRM |

#### GOWA API Endpoints

| Feature | Method | Endpoint |
|---------|--------|----------|
| List Devices | GET | `/devices` |
| Add Device | POST | `/devices` |
| Get Device Info | GET | `/devices/:device_id` |
| Remove Device | DELETE | `/devices/:device_id` |
| Login (QR) | GET | `/devices/:device_id/login` |
| Login (Code) | POST | `/devices/:device_id/login/code` |
| Logout | POST | `/devices/:device_id/logout` |
| Reconnect | POST | `/devices/:device_id/reconnect` |
| Send Message | POST | `/messages` |

---

## Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend (Next.js) | 3001 | http://localhost:3001 |
| Backend (FastAPI) | 8000 | http://localhost:8000 |
| WhatsApp Gateway | 8080 | http://localhost:8080 |

---

## Environment Variables

### Required (validated by `env_validator.py`)

| Variable | Purpose |
|----------|---------|
| `DEEPINFRA_API_KEY` | LLM API key for Deepinfra/Gemini |
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET_KEY` | JWT signing secret |

### Optional

| Variable | Default | Purpose |
|----------|---------|---------|
| `LOG_LEVEL` | INFO | Logging level |
| `GOOGLE_OAUTH_CLIENT_ID` | - | Google OAuth client ID |
| `GOOGLE_OAUTH_CLIENT_SECRET` | - | Google OAuth client secret |
| `GOOGLE_OAUTH_REDIRECT_URI` | - | Google OAuth callback URI |
| `QDRANT_URL` | - | Qdrant vector DB URL (for RAG) |
| `QDRANT_API_KEY` | - | Qdrant API key (for RAG) |

---

## Scripts

```bash
# Development
bun run dev           # All apps via Nx
bun run dev:web      # Next.js only (port 3001)

# Build
bun run build        # Build all applications

# Quality
bun run check        # Ultracite lint check
bun run fix          # Ultracite auto-fix
bun run check-types  # TypeScript type checking

# Backend
cd apps/core && .venv/bin/uvicorn app.main:app --reload

# PWA
cd apps/web && bun run generate-pwa-assets
```

---

## Anti-Patterns

| Issue | Location | Description |
|-------|----------|-------------|
| Hardcoded JWT secret | `config.py` line 43 | `"change-me-in-production"` |
| CORS allows all | `main.py` | `allow_origins=["*"]` - NOT for production |
| No tests | `apps/core/tests/` | Empty tests directory |
| CI missing pytest | `.github/workflows/ci.yml` | No pytest execution |
| Wrong docker-compose path | CI | Validates `apps/core/docker-compose.yml` (doesn't exist) |

---

## Code Map

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `create_app()` | FastAPI factory | `apps/core/app/main.py` | App initialization |
| `api_router` | APIRouter | `apps/core/app/api/v1/router.py` | Route aggregation |
| `get_config()` | Config loader | `apps/core/app/core/config.py` | YAML config + Pydantic |
| `validate_env()` | Validator | `apps/core/app/core/env_validator.py` | Env validation |
| `AppException` | Exception | `apps/core/app/core/exceptions.py` | Custom exception handler |