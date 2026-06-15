# ChatKasir

## AI Commerce Employee for Indonesian MSMEs

### Powered by WhatsApp + Bank Transfer + Agentic AI

---

# Executive Summary

ChatKasir adalah AI Commerce Employee yang membantu UMKM Indonesia menjalankan customer service, penjualan, pembayaran, dan operasional bisnis langsung melalui WhatsApp.

Alih-alih memaksa UMKM menggunakan dashboard e-commerce yang kompleks, ChatKasir memanfaatkan WhatsApp sebagai antarmuka utama karena merupakan platform yang sudah digunakan sehari-hari oleh mayoritas pelaku UMKM dan pelanggan di Indonesia.

Merchant hanya melakukan setup awal melalui website. Setelah itu seluruh aktivitas bisnis dapat dilakukan melalui WhatsApp.

---

# Problem Statement

Mayoritas UMKM Indonesia merupakan usaha mikro dan kecil.

Mereka menghadapi beberapa masalah utama:

- Tidak memiliki website
- Tidak memahami dashboard e-commerce yang kompleks
- Kesulitan membalas pelanggan satu per satu
- Tidak memiliki customer service khusus
- Sulit melakukan digitalisasi operasional
- Sulit mengelola pembayaran dan verifikasi transfer secara otomatis

Di sisi lain, pelanggan Indonesia sudah sangat terbiasa menggunakan WhatsApp sebagai sarana komunikasi dan transaksi.

Hal ini menciptakan peluang untuk menghadirkan AI Employee yang bekerja langsung melalui WhatsApp.

---

# Vision

Membuat AI Employee yang dapat menjalankan operasional bisnis dasar UMKM secara otomatis melalui WhatsApp.

---

# Product Positioning

Bukan chatbot.

Bukan auto reply.

Bukan website builder.

ChatKasir adalah:

- Sales Assistant
- Customer Service
- Cashier
- Business Assistant

Dalam satu sistem.

---

# User Roles

## Merchant

Pemilik UMKM

## Customer

Pembeli

## AI Employee

Agent yang menjalankan operasional bisnis

---

# Core Architecture

Customer ↓ WhatsApp ↓ WhatsApp Gateway ↓ FastAPI Backend ↓ LangGraph Agent ↓ PostgreSQL ↓ Qdrant ↓ Bank Transfer + Merchant Verification

---

# Merchant Onboarding (Web Only)

Website hanya digunakan untuk setup awal.

---

## Merchant Registration

Merchant mengisi:

- Nama toko
- Nomor WhatsApp
- Kategori usaha
- Deskripsi usaha

Output:

- Store ID
- Store Slug

Contoh:

mydomain.id/tokobudi

---

## Product Setup

Merchant dapat:

- Upload foto produk
- Nama produk
- Harga
- Deskripsi

Optional:

- Stok
- Variasi
- Berat

Data produk akan:

- Disimpan di PostgreSQL
- Di-index ke Qdrant untuk semantic search

---

## Knowledge Base Setup

Merchant mengisi:

- FAQ
- Jam operasional
- Area pengiriman
- Kebijakan retur
- Informasi toko

Data akan di-ingest ke Qdrant.

---

## Bank Account Setup

Merchant memasukkan:

- Nama bank
- Nomor rekening
- Nama pemilik rekening

Informasi rekening ditampilkan ke pembeli saat checkout.

Merchant bertanggung jawab memverifikasi setiap transfer masuk.

---

## AI Personality Setup

Pilihan:

- Professional
- Friendly
- Casual

Merchant juga dapat menambahkan custom prompt.

---

## Store Link Generation

Output:

mydomain.id/tokobudi

Ketika dibuka:

Redirect ke WhatsApp.

Contoh:

wa.me/628xxxx?text=tokobudi

---

# Customer Experience

## Product Discovery

Customer:

"Saya cari oli untuk Beat"

AI:

- memahami intent
- mencari produk
- merekomendasikan produk

---

## Product Consultation

AI menjelaskan:

- harga
- spesifikasi
- stok
- promo

---

## Cart Creation

Customer:

"Saya beli 2"

AI membuat cart.

---

## Order Creation

AI membuat order.

Disimpan ke PostgreSQL.

---

## Bank Transfer Checkout

AI memberikan:

- Nomor rekening tujuan sesuai toko
- Total yang harus ditransfer
- Instruksi konfirmasi setelah transfer

---

## Payment Verification

Setelah pembeli transfer, AI menunggu pembeli mengonfirmasi bahwa transfer sudah dilakukan.

Flow:

Pembeli Konfirmasi Transfer ↓ AI Notifikasi Merchant ↓ Merchant Cek Rekening ↓ Merchant Verifikasi di WhatsApp ↓ Order Updated ↓ WhatsApp Notification

---

## Order Confirmation

Customer menerima:

- status pembayaran
- ringkasan pesanan

---

## Merchant Notification

Merchant menerima:

Pesanan baru masuk.

---

# AI Commerce Features

## Product Recommendation

AI merekomendasikan produk berdasarkan kebutuhan customer.

---

## Upselling

Contoh:

Customer membeli kopi.

AI menawarkan:

- gula aren
- mug
- snack

---

## Cross Selling

Customer membeli helm.

AI menawarkan:

- visor
- jas hujan

---

## Promotion Recommendation

AI menawarkan promo yang relevan.

---

## Abandoned Payment Recovery

Pembayaran belum selesai.

AI melakukan follow up otomatis.

---

# AI Customer Service Features

## FAQ Automation

Menjawab pertanyaan umum.

---

## Store Information

Jam buka.

Area pengiriman.

Kebijakan toko.

---

## Order Status

Melihat status pesanan.

---

## Complaint Intake

AI menerima komplain awal.

---

## Refund Request Intake

AI menerima permintaan refund.

---

# AI Business Assistant

Merchant dapat chat AI.

---

## Revenue Analytics

"Omzet bulan ini berapa?"

---

## Best Seller Analytics

"Produk paling laris?"

---

## Customer Analytics

"Pelanggan terbaik saya siapa?"

---

## Repeat Customer Analytics

"Siapa yang belum repeat order?"

---

## Inventory Insight

"Produk yang hampir habis apa?"

---

## Daily Summary

AI mengirim ringkasan harian.

---

# Customer Memory System

AI mengingat:

- nama pelanggan
- histori pembelian
- preferensi produk

---

## Example

Customer:

"Saya biasanya beli kopi robusta"

Memory disimpan.

Pada pembelian berikutnya:

AI dapat memberikan rekomendasi personal.

---

# Qdrant Usage

Digunakan hanya untuk:

- FAQ retrieval
- Product semantic search
- Customer memory retrieval
- Conversation summary retrieval

Tidak digunakan untuk:

- Inventory
- Payment
- Orders
- Transaction status

Data kritikal tetap berada di PostgreSQL.

---

# QRIS Integration (future)

---

# Agent Workflow

## Sales Flow

Customer Message ↓ Intent Detection ↓ Product Search ↓ Recommendation ↓ Order Creation ↓ Payment Creation ↓ Payment Verification ↓ Order Confirmation

---

## Merchant Analytics Flow

Merchant Question ↓ Agent Reasoning ↓ PostgreSQL Query ↓ Result Summary ↓ WhatsApp Response

---

# Technical Stack

## Frontend

Next.js 16

React 19

TypeScript

Tailwind CSS 4

shadcn/ui

---

## Backend

FastAPI

SQLAlchemy

PostgreSQL

---

## AI

LangGraph

LangChain

Gemini 2.5 Flash

---

## Vector Search

Qdrant

FastEmbed

---

## Messaging

GoWA

WhatsApp Web Multi Device

---

## Payment

Bank Transfer (manual)

Nomor rekening merchant

Konfirmasi manual oleh merchant

---

## Infrastructure

Docker

Nx Monorepo

Bun

---

# MVP Scope

## Phase 1 (Hackathon)

Merchant:

- onboarding
- upload produk
- setup nomor rekening bank

Customer:

- tanya produk
- order produk
- pembayaran via transfer bank

AI:

- product recommendation
- FAQ answering
- customer memory

Merchant Assistant:

- omzet
- produk terlaris
- order masuk

---

# Success Metrics

Merchant onboarding < 5 menit

Checkout completion > 60%

AI response accuracy > 80%

Pembayaran via transfer bank dengan verifikasi merchant melalui WhatsApp

Minimal 1 transaksi end-to-end berhasil didemokan selama Demo Day
