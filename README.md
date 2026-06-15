# Chat Kasir

**AI-powered WhatsApp commerce assistant.** Customers can browse products, order, pay, and track orders — all through WhatsApp without installing any app. Store owners can manage inventory, monitor revenue, and handle orders from the same chat interface.

Built with **Python (FastAPI)** for the backend, **Next.js 16** for the web dashboard, and **GoWA** for WhatsApp connectivity. Uses a **LangChain ReAct agent** with an LLM (OpenAI-compatible) so the bot understands natural conversations and responds like a real shop assistant.

---

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│  WhatsApp     │────▶│  GoWA Service    │────▶│  Webhook             │
│  Customer     │◀────│  (whatsapp)      │◀────│  /api/v1/webhook/gowa│
└──────────────┘     └──────────────────┘     └──────────┬───────────┘
                                                          │
                                              ┌──────────▼───────────┐
                                              │  GowaWebhookHandler  │
                                              │  - verify webhook    │
                                              │  - resolve store     │
                                              │  - check merchant    │
                                              └──────────┬───────────┘
                                                          │
                                              ┌──────────▼───────────┐
                                              │  AgentExecutor       │
                                              │  (LangGraph ReAct)   │
                                              └──────────┬───────────┘
                                                          │
                                    ┌─────────────────────┼─────────────────────┐
                                    │                     │                     │
                            ┌───────▼───────┐    ┌────────▼───────┐    ┌───────▼────────┐
                            │   call_agent  │    │  execute_tools │    │  should_continue│
                            │  (LLM + tools)│    │  (tool dispatch)│    │  (router)       │
                            └───────────────┘    └────────┬───────┘    └────────────────┘
                                                          │
                                          ┌───────────────┼───────────────────┐
                                          │               │                   │
                                   ┌──────▼──────┐ ┌──────▼──────┐  ┌─────────▼─────────┐
                                   │ search_prod │ │ create_order│  │ get_payment_info  │
                                   │ upsell_prod │ │ add_to_cart │  │ confirm_payment   │
                                   │  ... (30+)  │ │ submit_refnd│  │ forward_message   │
                                   └─────────────┘ └─────────────┘  └───────────────────┘
```

### Agent Flow

The system uses a **LangGraph ReAct (Reasoning + Acting) agent** with a state graph of 3 nodes:

1. **`call_agent`** — LLM receives system prompt + conversation history, decides to reply or call a tool
2. **`execute_tools`** — Runs any tool calls the LLM made, injects context params (`store_id`, `customer_phone`) automatically, enforces merchant-only guards
3. **`should_continue`** — Routes back to the LLM if tools were called, or ends if the LLM responded directly

The agent loops (`agent → tools → agent → tools → ...`) until the LLM produces a final reply without tool calls. Each conversation gets an isolated thread via an in-memory checkpointer.

---

## Features

### For Customers

| Category | Feature | How to use |
|---|---|---|
| 🔍 **Product Search** | Search by name or keyword | "ada kipas angin?", "cari celana jeans" |
| 🛒 **Shopping Cart** | Add, view, update, remove items | "tambah nasi goreng 2", "lihat keranjang" |
| 📦 **Order & Checkout** | Place orders with auto payment info | "saya mau pesan nasi goreng 2 dan es teh 2" |
| 💳 **Payment** | Confirm transfer to merchant | "udah transfer ya", "saya sudah bayar" |
| 📍 **Order Status** | Check order progress | "pesanan saya dimana?", "status pesanan" |
| 📋 **Order History** | View past purchases | "riwayat pesanan saya" |
| 💬 **Talk to Owner** | Forward message to store owner | "tolong sampaikan ke pemilik bahwa ..." |
| 📝 **Complaint** | Submit a complaint | "saya mau komplain tentang ..." |
| 🔄 **Refund** | Request a refund | "saya minta refund" |

### For Store Owners

| Category | Feature | How to use |
|---|---|---|
| ✅ **Payment Verification** | Verify customer payments | "konfirmasi pembayaran" |
| 📦 **All Orders** | View all transactions filtered by status | "lihat semua pesanan", "pesanan pending" |
| 📊 **Store Stats** | Total revenue, order count, top products, low stock alerts | "statistik toko", "produk terlaris" |
| 📈 **Revenue Report** | Daily revenue breakdown | "laporan omzet hari ini" |
| 📉 **Daily Summary** | Today's sales recap | "ringkasan harian" |
| ⚠️ **Low Stock Alerts** | Products running out | "stok menipis", "produk mau habis" |
| 📦 **Stock Management** | Add stock or update product info | "tambah stok nasi goreng 10" |
| 🆕 **Create Product** | Add new products via chat | "buat produk baru: ..." |
| ✏️ **Update Product** | Change name, price, description, stock | "ubah harga nasi goreng jadi 15000" |
| ❌ **Cancel Order** | Cancel pending orders | "batalkan pesanan ..." |
| 💬 **Reply to Customer** | Send message to customer | "sampaikan ke [nama] bahwa ..." |

### System Features

| Feature | Details |
|---|---|
| **Multi-store** | Each WhatsApp number maps to one store. The agent identifies which store from the incoming device ID |
| **Owner Detection** | If the sender's WhatsApp number matches the store owner's, the agent unlocks merchant-only tools |
| **Semantic Search** | Qdrant-based RAG untuk pencarian produk berdasarkan makna (opsional — fallback ke keyword search jika Qdrant tidak tersedia) |
| **Shopping Cart** | Full cart system with add/update/remove/checkout |
| **Auto Notifications** | New orders automatically notify the merchant via WhatsApp |
| **Order Auto-Payment Info** | When an order is created, the agent automatically sends payment details |
| **Conversation Memory** | LangGraph thread-based checkpointer keeps conversation context within each session |
| **Web Dashboard** | Next.js 16 admin panel with product management, order tracking, and analytics |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.14, FastAPI, LangGraph, SQLAlchemy 2.0, PostgreSQL (asyncpg) |
| **AI Agent** | LangChain ReAct agent, GPT (OpenAI) via OpenAI-compatible API |
| **WhatsApp** | GoWA (Go WhatsApp Web Multidevice REST API) |
| **Vector Search** | Qdrant (terkonfigurasi di kode, fallback ke keyword search jika Qdrant tidak tersedia) |
| **Frontend** | Next.js 16, shadcn/ui, TailwindCSS |
| **Monorepo** | Nx + Bun workspaces |
| **Python Tools** | uv (package manager), Ruff (linting), MyPy (type checking) |
| **JS Tools** | Ultracite (linting/formatting) |
| **Auth** | JWT (HS256) with bcrypt password hashing |

---

## Setup & Installation

### Prerequisites

- **Bun** (JavaScript package manager)
- **Python 3.11+** with `uv` installed
- **PostgreSQL** (local or cloud via Neon)
- **GoWA container** (WhatsApp service, runs via Docker)
- **OpenAI API key** (or any OpenAI-compatible provider)

### 1. Clone

```bash
git clone https://github.com/HeraldoArman/chat-kasir.git
cd chat-kasir
```

### 2. Install Dependencies

```bash
# JavaScript dependencies (Next.js, shadcn, etc.)
bun install

# Python dependencies (FastAPI, LangChain, SQLAlchemy, etc.)
cd apps/core && uv sync
cd ../..
```

### 3. Configure Environment

```bash
cp apps/core/.env.example apps/core/.env
```

Edit `.env` with your configuration:

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ | OpenAI or OpenAI-compatible API key |
| `DATABASE_URL` | ✅ | PostgreSQL connection string (asyncpg) |
| `JWT_SECRET_KEY` | ✅ | At least 32 chars — generate with `openssl rand -hex 32` |
| `GOWA_BASE_URL` | ✅ | GoWA service URL (default: `http://localhost:8080`) |
| `GOWA_DEVICE_ID` | ✅ | WhatsApp device ID (e.g. `628xxx@s.whatsapp.net`) |
| `GOWA_WEBHOOK_SECRET` | ✅ | Secret for webhook HMAC verification |
| `QDRANT_URL` | Optional | Qdrant cloud URL for RAG features |
| `QDRANT_API_KEY` | Optional | Qdrant API key |

### 4. Configure LLM & App Settings

Edit `apps/core/config.yaml`:

```yaml
llm:
  provider: "openai"
  model: "gpt-5.4-mini"            # any OpenAI-compatible model ID
  base_url: "https://api.openai.com/v1"
  temperature: 0.3
  max_tokens: 4096
  timeout: 120

rag:
  enabled: true                      # set false to disable Qdrant semantic search
  qdrant_url: "http://localhost:6333"
  collection_name: "documents"
  embedding_model: "BAAI/bge-small-en-v1.5"
```

> **Catatan Qdrant:** Qdrant dikonfigurasi sebagai vector search opsional. Jika Qdrant tidak tersedia (koneksi gagal atau koleksi belum dibuat), agent otomatis fallback ke keyword-based search via SQL — jadi fitur pencarian produk tetap jalan tanpa Qdrant. Untuk mengaktifkan Qdrant, jalankan instance Qdrant terpisah (tidak termasuk dalam docker-compose default) dan isi `QDRANT_URL` + `QDRANT_API_KEY` di `.env`.

### 5. Run Database Migrations

```bash
cd apps/core
source .venv/bin/activate
alembic upgrade head
cd ../..
```

### 6. Run

```bash
# Run everything (backend + frontend)
bun run dev

# Or run individually:
bun run dev:web      # Next.js frontend only (port 3001)
bun run dev:core     # FastAPI backend only (port 8000)
```

### Docker (Alternative)

```bash
docker compose up -d
```

This starts all services: FastAPI backend, PostgreSQL 18, and GoWA WhatsApp service.

---

## Configuration Reference

### `config.yaml` (`apps/core/`)

| Section | Key | Default | Description |
|---|---|---|---|
| `llm` | `model` | `gpt-5.4-mini` | LLM model identifier |
| `llm` | `base_url` | `https://api.openai.com/v1` | OpenAI-compatible API base URL |
| `llm` | `temperature` | `0.3` | LLM temperature (lower = more deterministic) |
| `llm` | `max_tokens` | `4096` | Max tokens per response |
| `llm` | `timeout` | `120` | API call timeout in seconds |
| `rag` | `enabled` | `true` | Enable Qdrant RAG for semantic product search |
| `rag` | `qdrant_url` | `http://localhost:6333` | Qdrant gRPC endpoint |
| `cors` | `origins` | `["http://localhost:3001"]` | Allowed CORS origins |
| `jwt` | `expire_hours` | `24` | JWT token expiry |
| `logging` | `format` | `json` | Log format (json or text) |

### Environment Variables

| Variable | Used In | Default |
|---|---|---|
| `DATABASE_URL` | Database connection | — |
| `OPENAI_API_KEY` | LLM provider auth | — |
| `JWT_SECRET_KEY` | JWT signing | — |
| `GOWA_BASE_URL` | WhatsApp API calls | `http://localhost:8080` |
| `GOWA_DEVICE_ID` | Webhook routing | — |
| `GOWA_WEBHOOK_SECRET` | HMAC verification | — |
| `QDRANT_URL` | RAG vector search | — |
| `QDRANT_API_KEY` | Qdrant auth | — |
| `NEXT_PUBLIC_API_URL` | Frontend API endpoint | `http://localhost:8000/api/v1` |

---

## WhatsApp Integration

### How It Works

1. **GoWA** runs as a Docker container and connects to WhatsApp Web Multidevice
2. When a message arrives, GoWA forwards it to the webhook URL (`/api/v1/webhook/gowa`) via HTTP POST
3. The webhook handler:
   - Verifies the HMAC signature (`x-hub-signature-256`)
   - Looks up the store by the WhatsApp device ID (the store's phone number)
   - Checks if the sender is the store owner (merchant) or a customer
   - Passes the message to the AI agent
4. The agent processes the message, calls tools as needed, and sends a reply
5. The reply is sent back via GoWA's `/send/message` API

### Setting Up a New Store

1. Add a `Store` record in the database with:
   - `whatsapp_number` — the store's WhatsApp number (e.g., `6285719122253`)
   - `owner_id` — references a `User` (the store owner)
   - `name` — store display name
2. Add a `User` record for the owner with their WhatsApp number for auto-detection
3. Configure `GOWA_DEVICE_ID` and `GOWA_WEBHOOK_SECRET` in `.env`
4. Start the GoWA container and scan the QR code to link WhatsApp
5. Done — customers can now message the store's WhatsApp number

---

## Agent System

### Prompt Structure

The system prompt (`app/agent/prompts.py`) has 5 sections:

| Section | Purpose |
|---|---|
| **Role setting** | "Kamu adalah {store_name}, asisten toko online..." |
| **Tool listing** | All 30+ available tools with descriptions |
| **Speaking rules** | Tone, customer address, formatting conventions |
| **Flow instructions** | When to use each tool, ordering workflow, payment flow |
| **Context injection** | Store name, store ID, customer info, merchant flag |

### Available Tools (30+)

**Customer-facing:**
`search_products`, `search_products_semantic`, `create_order`, `get_payment_info`, `confirm_payment_notify_merchant`, `get_order_status`, `answer_faq`, `add_to_cart`, `get_cart`, `update_cart_item`, `remove_from_cart`, `checkout_cart`, `recommend_products`, `upsell_product`, `cross_sell_product`, `get_active_promotions`, `submit_complaint`, `submit_refund_request`, `get_customer_order_history`, `forward_to_merchant`

**Merchant-only:**
`verify_order_payment`, `get_merchant_analytics`, `get_low_stock_products`, `get_daily_summary`, `update_product_stock`, `create_product`, `get_all_orders`, `get_store_stats`, `cancel_order`, `update_product`, `get_revenue_report`, `forward_to_customer`

### Tool Execution Flow

For each tool call the LLM makes:
1. **Merchant guard** — if the tool is merchant-only and sender isn't the owner, reject
2. **Context injection** — `store_id` is always injected; `customer_phone` is injected for tools that need it (order, cart, payment, etc.)
3. **Execution** — the tool runs and returns JSON result
4. **Loop** — result goes back to the LLM for the next decision

---

## Project Structure

```
chat-kasir/
├── apps/
│   ├── core/                          # Python FastAPI backend
│   │   ├── app/
│   │   │   ├── agent/                 # AI agent system
│   │   │   │   ├── prompts.py         # System prompts (ID)
│   │   │   │   ├── tools.py           # 30+ LangChain tools
│   │   │   │   ├── nodes.py           # LangGraph nodes (call_agent, execute_tools)
│   │   │   │   ├── graph.py           # State graph builder
│   │   │   │   ├── executor.py        # High-level AgentExecutor facade
│   │   │   │   ├── state.py           # AgentState schema
│   │   │   │   ├── errors.py          # Custom exceptions
│   │   │   │   └── notifications.py   # WhatsApp notifications
│   │   │   ├── api/v1/
│   │   │   │   └── routes/            # FastAPI route modules
│   │   │   │       ├── gowa_webhook.py    # WhatsApp webhook endpoint
│   │   │   │       ├── auth.py            # Login/register/me
│   │   │   │       ├── store.py           # Store CRUD + products
│   │   │   │       ├── orders.py          # Order management
│   │   │   │       ├── cart.py            # Cart operations
│   │   │   │       ├── chat.py            # HTTP chat API
│   │   │   │       ├── promotions.py      # Promo management
│   │   │   │       ├── insights.py        # Store analytics
│   │   │   │       ├── rag.py             # RAG/document management
│   │   │   │       └── docs.py            # GoWA docs
│   │   │   ├── services/              # Business logic layer
│   │   │   │   ├── gowa_webhook.py    # Webhook handler + verification
│   │   │   │   ├── gowa.py            # GoWA REST client
│   │   │   │   ├── chat.py            # HTTP chat service
│   │   │   │   ├── order.py           # Order service
│   │   │   │   ├── product.py         # Product service
│   │   │   │   ├── cart.py            # Cart service
│   │   │   │   ├── store.py           # Store service
│   │   │   │   ├── bank.py            # Bank account service
│   │   │   │   ├── auth.py            # Auth service (JWT, bcrypt)
│   │   │   │   ├── llm.py             # LLM wrapper
│   │   │   │   ├── rag.py             # Qdrant RAG service
│   │   │   │   ├── embedding.py       # Embedding generation
│   │   │   │   ├── indexing.py        # Document indexing
│   │   │   │   ├── knowledge.py       # FAQ knowledge base
│   │   │   │   ├── promotion.py       # Promotion service
│   │   │   │   ├── complaint.py       # Complaint service
│   │   │   │   ├── refund.py          # Refund service
│   │   │   │   └── recommendation.py  # Multi-strategy recommendation
│   │   │   ├── models/
│   │   │   │   ├── commerce.py        # Store, Product, Order models
│   │   │   │   └── user.py            # User model
│   │   │   ├── schemas/               # Pydantic models
│   │   │   ├── db/                    # Database session + init
│   │   │   ├── core/                  # Config, exceptions, logging
│   │   │   ├── middleware/            # Logging middleware
│   │   │   └── main.py                # FastAPI app factory
│   │   ├── config.yaml                # LLM, RAG, server config
│   │   ├── alembic/                   # DB migrations
│   │   └── Dockerfile
│   └── web/                           # Next.js 16 frontend
│       └── src/
│           ├── app/                   # App Router pages
│           └── components/            # UI components
├── packages/
│   ├── ui/                            # Shared shadcn/ui components (55+)
│   ├── env/                           # @t3-oss/env-nextjs validation
│   └── config/                        # TypeScript base config
├── docker-compose.yml                 # Backend + Postgres + GoWA
└── .github/workflows/ci.yml           # CI pipeline (lint, type-check)
```

---

## Scripts Reference

### Root (Nx + Bun)

```bash
bun run dev            # Run all apps (backend + frontend) with hot reload
bun run dev:web        # Next.js frontend only (port 3001)
bun run dev:core       # FastAPI backend only (uvicorn --reload, port 8000)
bun run build          # Build all apps
bun run check          # Lint check (Ultracite/oxlint)
bun run fix            # Auto-fix lint issues
bun run check-types    # TypeScript type checking
```

### Python (from `apps/core/`)

```bash
uv run ruff check .    # Lint Python with Ruff
uv run mypy app        # Type-check Python with MyPy (strict mode)
uv run pytest          # Run tests
uv run alembic upgrade head  # Run database migrations
uv run uvicorn app.main:app --reload --port 8000  # Dev server
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/webhook/gowa` | WhatsApp webhook receiver |
| `POST` | `/api/v1/auth/login` | Login with email + password |
| `POST` | `/api/v1/auth/register` | Register new user |
| `GET` | `/api/v1/auth/me` | Current user info |
| `GET` | `/api/v1/stores/me` | Current user's store |
| `GET` | `/api/v1/stores/me/products` | Store products |
| `GET` | `/api/v1/stores/me/products/{id}` | Single product detail |
| `GET` | `/api/v1/orders` | List orders |
| `GET` | `/api/v1/orders/{id}` | Order detail |
| `POST` | `/api/v1/chat` | HTTP chat with agent |
| `GET` | `/api/v1/cart` | Get current cart |
| `POST` | `/api/v1/cart/add` | Add item to cart |
| `GET` | `/api/v1/gowa/phone` | Get WhatsApp phone config |
| `GET` | `/api/v1/docs/gowa` | GoWA documentation |

Interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Development

### Code Quality

```bash
# Python
cd apps/core
uv run ruff check .    # Lint
uv run mypy app        # Type-check
uv run pytest          # Tests

# TypeScript (from root)
bun run check          # Ultracite lint
bun run check-types    # TypeScript type-check
```

### CI Pipeline

`.github/workflows/ci.yml` runs on every push:
1. Python lint (Ruff) + type check (MyPy) — `apps/core`
2. TypeScript lint (Ultracite) + type check — root + `packages/*`

---

## Environment

| | |
|---|---|
| **Timezone** | Asia/Jakarta (WIB) |
| **Language** | Indonesian (Bahasa) — both UI and agent responses |
| **Currency** | Indonesian Rupiah (Rp) |
| **WhatsApp** | GoWA WhatsApp Web Multidevice |
