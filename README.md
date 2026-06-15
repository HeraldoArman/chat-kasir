# Chat Kasir

**Asisten toko online lewat WhatsApp.** Pelanggan bisa chat, pesan, bayar, dan cek status pesanan — semuanya lewat WhatsApp tanpa perlu install aplikasi. Pemilik toko bisa kelola stok, lihat laporan omzet, dan pantau pesanan dari mana aja.

Dibangun pake Python (FastAPI) buat backend-nya, Next.js buat web dashboard, dan GoWA buat koneksi WhatsApp. Pake AI (LangGraph + DeepSeek) biar bot-nya ngerti konteks dan bisa jawab natural kayak penjaga toko beneran.

## Fitur

### Buat Pelanggan

- **Cari Produk** — Tinggal ketik "ada kipas angin?" atau "cari celana jeans", bot langsung nyariin
- **Keranjang Belanja** — Tambah, lihat, ubah jumlah, atau hapus item di keranjang
- **Pesan & Checkout** — Pesan langsung dari chat, bot bakal ngasih info pembayaran otomatis
- **Bayar** — Konfirmasi pembayaran tinggal bilang "udah transfer ya"
- **Cek Status** — Tanya "pesanan saya dimana?" atau "status pesanan gimana?"
- **Forward ke Owner** — Kalau mau ngomong langsung ke pemilik toko, bilang aja "tolong sampaikan ke pemilik toko bahwa ..."
- **Komplain & Refund** — Bisa lapor masalah atau minta refund lewat chat

### Buat Pemilik Toko

- **Konfirmasi Pembayaran** — Verifikasi pembayaran pelanggan, otomatis ngirim notifikasi
- **Kelola Stok** — Tambah stok produk atau update info produk (nama, harga, deskripsi)
- **Tambah Produk Baru** — Bikin produk baru langsung dari chat
- **Lihat Semua Pesanan** — Cek semua transaksi, filter berdasarkan status
- **Laporan Omzet** — Laporan harian pendapatan toko
- **Statistik Toko** — Total omzet, jumlah pesanan, produk terlaris, stok menipis
- **Produk Stok Menipis** — Cek produk yang stoknya tinggal sedikit
- **Ringkasan Harian** — Rekap penjualan hari ini
- **Forward ke Pelanggan** — Kirim pesan langsung ke pelanggan lewat bot

## Cara Kerja

```
Pelanggan → WhatsApp → Chat Kasir Bot → AI Agent → Database/Toko
              ↑                                        |
              └──────── Balasan lewat WhatsApp ←────────┘
```

Pelanggan kirim chat ke nomor WhatsApp toko. Bot pake AI untuk ngerti maksudnya, trus milih tool yang tepat (cari produk, bikin pesanan, cek status, dll). Semua respons dikirim balik ke WhatsApp pelanggan.

Pemilik toko juga bisa akses lewat WhatsApp yang sama — bot otomatis tau siapa pemilik dan ngasih akses ke fitur-fitur khusus.

## Tech Stack

| Lapisan | Teknologi |
|---|---|
| Backend | Python 3.13, FastAPI, LangGraph, SQLAlchemy, PostgreSQL |
| AI Agent | LangChain ReAct agent, DeepSeek V4 Flash (via Deepinfra) |
| WhatsApp | GoWA (WhatsApp Web Multidevice) |
| Frontend | Next.js 16, shadcn/ui, TailwindCSS |
| Tools | Nx, Bun, uv, Ruff, MyPy |

## Cara Jalanin

### Persiapan

1. **Clone repo:**
   ```bash
   git clone https://github.com/HeraldoArman/chat-kasir.git
   cd chat-kasir
   ```

2. **Install dependencies:**
   ```bash
   bun install                  # JS dependencies
   cd apps/core && uv sync      # Python dependencies
   cd ../..
   ```

3. **Setup environment:**
   ```bash
   cp apps/core/.env.example apps/core/.env
   ```
   Isi `.env` dengan konfigurasi yang diperlukan (database, API key, dll).

### Jalanin

```bash
bun run dev
```

Ini bakal jalanin semua service sekaligus:
- **Web dashboard** → [http://localhost:3001](http://localhost:3001)
- **Backend API** → [http://localhost:8000](http://localhost:8000)
- **Dokumentasi API** → [http://localhost:8000/docs](http://localhost:8000/docs)

Atau jalanin satu-satu:
```bash
bun run dev:web      # Frontend aja
bun run dev:core     # Backend aja (uvicorn)
```

### Docker

```bash
docker compose up -d
```

Jalanin semua service (backend, PostgreSQL, GoWA) pake Docker.

## Project Structure

```
chat-kasir/
├── apps/
│   ├── core/                  # Python FastAPI backend
│   │   └── app/
│   │       ├── agent/         # AI agent (tools, prompts, graph, nodes)
│   │       ├── api/           # API routes (webhook, auth, chat)
│   │       ├── services/      # Business logic (order, product, payment)
│   │       ├── models/        # SQLAlchemy models
│   │       ├── schemas/       # Pydantic schemas
│   │       └── core/          # Config, exceptions, logging
│   └── web/                   # Next.js frontend
├── packages/
│   ├── ui/                    # Shared shadcn/ui components
│   ├── env/                   # Environment validation
│   └── config/                # TypeScript base config
└── docker-compose.yml
```

## Scripts

```bash
bun run dev          # Jalanin semua app (Nx)
bun run build        # Build semua app
bun run check        # Lint check (Ultracite)
bun run fix          # Auto-fix lint
bun run check-types  # TypeScript type check
```

Python-specific (dari `apps/core/`):
```bash
uv run ruff check .  # Lint Python
uv run mypy app      # Type check Python
uv run pytest        # Test Python
```
