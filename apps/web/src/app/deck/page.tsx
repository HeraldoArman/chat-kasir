"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import {
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  Banknote,
  Bot,
  Brain,
  CheckCircle2,
  ChevronRight,
  CircleDot,
  Database,
  LineChart,
  MessageCircle,
  MessagesSquare,
  ScanSearch,
  ShieldCheck,
  ShoppingCart,
  Sparkles,
  Store,
  TrendingUp,
  Users,
  Wallet,
  Zap,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type JSX,
  type ReactNode,
} from "react";

import { Badge } from "@chat-kasir/ui/components/badge";
import { Card, CardContent } from "@chat-kasir/ui/components/card";
import { cn } from "@chat-kasir/ui/lib/utils";

/* ------------------------------------------------------------------ */
/* Tokens (mirroring apps/web landing page)                            */
/* ------------------------------------------------------------------ */

const EASE = [0.16, 1, 0.3, 1] as const;
const CREAM = "#faf7f1";
const INK = "#1a1a18";
const AMBER = "#c8a45c";

/* ------------------------------------------------------------------ */
/* Reusable atoms                                                      */
/* ------------------------------------------------------------------ */

function Eyebrow({
  children,
  tone = "light",
}: {
  children: ReactNode;
  tone?: "light" | "dark";
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 text-[11px] font-semibold tracking-[0.22em] uppercase",
        tone === "dark" ? "text-[#faf7f1]/60" : "text-[#1a1a18]/55"
      )}
    >
      <span className="inline-block size-1.5 rounded-full bg-[#c8a45c]" />
      {children}
    </span>
  );
}

function Kbd({ children }: { children: ReactNode }) {
  return (
    <kbd className="inline-flex h-5 min-w-5 items-center justify-center rounded-md border border-[#1a1a18]/15 bg-white/80 px-1.5 font-mono text-[10.5px] font-semibold text-[#1a1a18] dark:border-[#faf7f1]/15 dark:bg-white/5 dark:text-[#faf7f1]">
      {children}
    </kbd>
  );
}

function GrainLayer() {
  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0 opacity-[0.04] mix-blend-multiply"
      style={{
        backgroundImage:
          "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2'/><feColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>\")",
      }}
    />
  );
}

function Blob({
  className,
  color = AMBER,
}: {
  className: string;
  color?: string;
}) {
  return (
    <div
      aria-hidden
      className={cn(
        "pointer-events-none absolute rounded-full blur-3xl",
        className
      )}
      style={{ backgroundColor: color, opacity: 0.18 }}
    />
  );
}

/* ------------------------------------------------------------------ */
/* Slide chrome                                                        */
/* ------------------------------------------------------------------ */

type SlideProps = {
  index: number;
  total: number;
  eyebrow: string;
  title: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  tone?: "light" | "dark";
};

function Slide({
  index,
  total,
  eyebrow,
  title,
  children,
  footer,
  tone = "light",
}: SlideProps) {
  const isDark = tone === "dark";
  return (
    <motion.article
      key={index}
      initial={{ opacity: 0, y: 24, filter: "blur(6px)" }}
      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      exit={{ opacity: 0, y: -24, filter: "blur(6px)" }}
      transition={{ duration: 0.55, ease: EASE }}
      className={cn(
        "absolute inset-0 flex flex-col overflow-hidden",
        isDark ? "text-[#faf7f1]" : "text-[#1a1a18]"
      )}
      style={{ background: isDark ? INK : CREAM }}
    >
      <GrainLayer />
      {isDark ? (
        <>
          <Blob className="-top-32 -right-24 size-[28rem]" color="#c8a45c" />
          <Blob className="-bottom-40 -left-32 size-[26rem]" color="#e9c884" />
        </>
      ) : (
        <Blob className="-top-40 -right-40 size-[30rem]" color="#c8a45c" />
      )}

      {/* Top bar */}
      <header className="relative z-10 flex items-center justify-between px-6 pt-6 md:px-14 md:pt-8">
        <div className="flex items-center gap-3">
          <span
            className={cn(
              "flex size-7 items-center justify-center rounded-md text-[10.5px] font-bold tracking-tight",
              isDark
                ? "bg-[#faf7f1] text-[#1a1a18]"
                : "bg-[#1a1a18] text-[#faf7f1]"
            )}
          >
            CK
          </span>
          <span
            className={cn(
              "text-[11px] font-semibold tracking-[0.2em] uppercase",
              isDark ? "text-[#faf7f1]/65" : "text-[#1a1a18]/65"
            )}
          >
            ChatKasir · Strategy Deck 2026
          </span>
        </div>
        <div
          className={cn(
            "flex items-center gap-4 text-[11px] font-semibold tracking-[0.2em] uppercase",
            isDark ? "text-[#faf7f1]/65" : "text-[#1a1a18]/65"
          )}
        >
          <span className="hidden sm:inline">
            0{index} — {eyebrow}
          </span>
          <span
            className={cn(
              "tabular-nums",
              isDark ? "text-[#faf7f1]/40" : "text-[#1a1a18]/40"
            )}
          >
            {String(index + 1).padStart(2, "0")} /{" "}
            {String(total).padStart(2, "0")}
          </span>
        </div>
      </header>

      {/* Body */}
      <div className="relative z-10 flex-1 overflow-y-auto px-6 pt-8 pb-24 md:px-14 md:pt-12 md:pb-28">
        <div className="mx-auto flex h-full max-w-7xl flex-col">
          <Eyebrow tone={isDark ? "dark" : "light"}>{eyebrow}</Eyebrow>
          <h1
            className={cn(
              "mt-5 max-w-5xl font-extrabold tracking-[-0.03em] text-balance",
              "text-[clamp(2.25rem,4.6vw,4.25rem)] leading-[1.02]"
            )}
          >
            {title}
          </h1>
          <div className="mt-8 flex-1 md:mt-12">{children}</div>
          {footer ? (
            <div
              className={cn(
                "mt-8 border-t pt-5 md:mt-12 md:pt-6",
                isDark ? "border-[#faf7f1]/10" : "border-[#1a1a18]/10"
              )}
            >
              {footer}
            </div>
          ) : null}
        </div>
      </div>
    </motion.article>
  );
}

/* ------------------------------------------------------------------ */
/* Slide 1 — Cover                                                     */
/* ------------------------------------------------------------------ */

function Bubble({
  who,
  children,
  accent = false,
}: {
  who: "them" | "bot";
  children: ReactNode;
  accent?: boolean;
}) {
  const isBot = who === "bot";
  return (
    <div
      className={cn(
        "max-w-[88%] rounded-2xl px-3.5 py-2",
        isBot
          ? accent
            ? "bg-[#c8a45c]/25 text-[#faf7f1] ring-1 ring-[#c8a45c]/45"
            : "bg-[#faf7f1]/8 text-[#faf7f1]/90"
          : "ml-auto bg-[#0b6150] text-[#faf7f1]"
      )}
    >
      <p className="text-[9.5px] font-semibold tracking-[0.18em] text-[#faf7f1]/55 uppercase">
        {isBot ? "ChatKasir" : "Customer"}
      </p>
      <p className="mt-0.5 text-[12.5px] leading-relaxed">{children}</p>
    </div>
  );
}

function CoverSlide() {
  return (
    <Slide
      index={0}
      total={5}
      eyebrow="Cover"
      title={
        <>
          ChatKasir.
          <span className="block text-[#c8a45c]">An AI commerce employee</span>
          <span className="block">for Indonesia's 64.6M micro merchants.</span>
        </>
      }
      tone="dark"
      footer={
        <div className="flex flex-col items-start justify-between gap-4 text-[11px] font-semibold tracking-[0.2em] uppercase md:flex-row md:items-center">
          <div className="flex flex-wrap items-center gap-3 text-[#faf7f1]/55">
            <span>Tim Nekat Solo Squad</span>
            <span className="text-[#faf7f1]/25">·</span>
            <span>Universitas Indonesia</span>
            <span className="text-[#faf7f1]/25">·</span>
            <span>2026</span>
          </div>
          <div className="flex items-center gap-2 text-[#faf7f1]/65">
            <CircleDot className="size-3 text-[#c8a45c]" />
            <span>Press &nbsp;↵&nbsp; or &nbsp;→&nbsp; to advance</span>
          </div>
        </div>
      }
    >
      <div className="grid grid-cols-1 items-end gap-10 lg:grid-cols-12 lg:gap-12">
        <div className="lg:col-span-7">
          <Badge
            variant="outline"
            className="mb-7 rounded-full border-[#c8a45c]/40 bg-[#c8a45c]/10 px-3 py-1 text-[10.5px] font-semibold tracking-[0.22em] text-[#e9c884] uppercase"
          >
            <Sparkles className="mr-1.5 size-3" /> AI Commerce Employee
          </Badge>
          <p className="max-w-2xl text-[clamp(1.1rem,1.5vw,1.45rem)] leading-[1.45] font-light text-balance text-[#faf7f1]/85">
            An autonomous storefront, customer-service rep, and cashier —
            running entirely inside the WhatsApp number that 64.6 million
            Indonesian micro-merchants already use to run their business.
          </p>

          <div className="mt-10 grid grid-cols-1 gap-px overflow-hidden rounded-3xl border border-[#faf7f1]/10 bg-[#faf7f1]/10 sm:grid-cols-3">
            {[
              { k: "98.7%", v: "of Indonesian MSMEs are micro" },
              { k: "95%", v: "WhatsApp penetration" },
              { k: "< 5 min", v: "to onboard" },
            ].map((s) => (
              <div key={s.k} className="bg-[#0b0b0a] p-5 md:p-6">
                <p className="text-[clamp(1.5rem,2.2vw,2.25rem)] leading-none font-extrabold tracking-tight text-[#e9c884]">
                  {s.k}
                </p>
                <p className="mt-2 text-[12px] leading-snug text-[#faf7f1]/55">
                  {s.v}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* WhatsApp mockup */}
        <div className="lg:col-span-5">
          <div className="relative mx-auto w-full max-w-sm">
            <div className="absolute -inset-6 rounded-[2.5rem] bg-[#c8a45c]/20 blur-2xl" />
            <Card className="relative overflow-hidden rounded-3xl border border-[#faf7f1]/10 bg-[#161614] shadow-2xl ring-0">
              <div className="flex items-center justify-between border-b border-[#faf7f1]/5 px-5 py-4">
                <div className="flex items-center gap-3">
                  <div className="flex size-9 items-center justify-center rounded-full bg-[#c8a45c]/20 text-[#e9c884]">
                    <Store className="size-4" />
                  </div>
                  <div>
                    <p className="text-[13px] font-semibold text-[#faf7f1]">
                      Toko Budi
                    </p>
                    <p className="text-[10.5px] text-[#faf7f1]/50">
                      online · AI assistant
                    </p>
                  </div>
                </div>
                <Badge
                  variant="outline"
                  className="rounded-full border-[#c8a45c]/30 bg-[#c8a45c]/10 px-2 py-0.5 text-[9px] font-semibold tracking-widest text-[#e9c884] uppercase"
                >
                  Live
                </Badge>
              </div>
              <CardContent className="space-y-3 px-5 py-5 text-[12.5px] leading-relaxed">
                <Bubble who="them">kak, oli matic masih ada?</Bubble>
                <Bubble who="bot">
                  Ada kak! Oli matic merk X — Rp45.000 / botol. Mau sekalian 2
                  biar hemat ongkir? 🚚
                </Bubble>
                <Bubble who="them">oke 2 ya, transfer ke mana?</Bubble>
                <Bubble who="bot">
                  Total <b>Rp90.000</b>. Transfer ke BCA <b>123-456-7890</b>{" "}
                  a.n. Budi Santoso. Setelah bayar, kirim “sudah” di sini ya kak
                  — AI kami yang konfirmasi 🤝
                </Bubble>
                <Bubble who="them">sudah kak 🙏</Bubble>
                <Bubble who="bot" accent>
                  Pembayaran Rp90.000 diterima ✓ Pesanan #1281 diproses. Terima
                  kasih kak Budi!
                </Bubble>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </Slide>
  );
}

/* ------------------------------------------------------------------ */
/* Slide 2 — Why digitalization fails                                  */
/* ------------------------------------------------------------------ */

function StatCard({
  figure,
  label,
  detail,
  emphasis = false,
}: {
  figure: string;
  label: string;
  detail: string;
  emphasis?: boolean;
}) {
  return (
    <Card
      className={cn(
        "h-full rounded-2xl p-0 ring-0 transition-all",
        emphasis
          ? "border-0 bg-[#1a1a18] text-[#faf7f1]"
          : "border border-[#1a1a18]/10 bg-white/70 dark:border-[#faf7f1]/10 dark:bg-white/5"
      )}
    >
      <CardContent className="flex h-full flex-col p-6 md:p-7">
        <p
          className={cn(
            "leading-none font-extrabold tracking-[-0.04em]",
            "text-[clamp(2.25rem,3.8vw,3.5rem)]",
            emphasis ? "text-[#e9c884]" : "text-[#1a1a18]"
          )}
        >
          {figure}
        </p>
        <p
          className={cn(
            "mt-4 text-[13px] font-semibold tracking-tight",
            emphasis ? "text-[#faf7f1]" : "text-[#1a1a18]"
          )}
        >
          {label}
        </p>
        <p
          className={cn(
            "mt-2 text-[12.5px] leading-relaxed",
            emphasis ? "text-[#faf7f1]/65" : "text-[#1a1a18]/65"
          )}
        >
          {detail}
        </p>
      </CardContent>
    </Card>
  );
}

function ProblemRow({
  n,
  title,
  desc,
}: {
  n: string;
  title: string;
  desc: string;
}) {
  return (
    <Card className="rounded-2xl border border-[#1a1a18]/10 bg-white/70 p-0 ring-0 dark:border-[#faf7f1]/10 dark:bg-white/5">
      <CardContent className="grid grid-cols-[auto_1fr] items-start gap-5 p-5 md:p-6">
        <span className="mt-0.5 font-mono text-[11.5px] font-bold tracking-[0.18em] text-[#c8a45c]">
          {n}
        </span>
        <div>
          <p className="text-[15px] font-semibold tracking-tight">{title}</p>
          <p className="mt-1.5 text-[12.5px] leading-relaxed text-[#1a1a18]/65 dark:text-[#faf7f1]/65">
            {desc}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function ProblemSlide() {
  return (
    <Slide
      index={1}
      total={5}
      eyebrow="Diagnosis"
      title={
        <>
          Why digitization keeps failing the
          <span className="text-[#c8a45c]"> people who need it most.</span>
        </>
      }
      footer={
        <p className="max-w-3xl text-[13px] leading-relaxed text-[#1a1a18]/60 dark:text-[#faf7f1]/60">
          <span className="font-semibold text-[#1a1a18] dark:text-[#faf7f1]">
            Diagnosis.&nbsp;
          </span>
          The Indonesian MSME market is overwhelmingly micro, mobile-first, and
          WhatsApp-native. Tools designed for omnichannel retailers collide with
          a one-man-show reality — high learning curves, double-entry
          bookkeeping, and silent checkout drop-offs.
        </p>
      }
    >
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 md:gap-8">
        <div>
          <Eyebrow tone="light">
            Three operational leaks inside every micro store
          </Eyebrow>
          <div className="mt-5 space-y-3.5">
            <ProblemRow
              n="01"
              title="Manual customer service"
              desc="A merchant spends ~40% of their working day answering the same five questions — price, stock, variants, shipping, total."
            />
            <ProblemRow
              n="02"
              title="Double-entry bookkeeping"
              desc="Orders are copy-pasted from WhatsApp into a notebook or spreadsheet, then re-typed into a POS. One typo kills a margin."
            />
            <ProblemRow
              n="03"
              title="Fragmented checkout"
              desc="Send account number → customer opens m-banking → screenshots → merchant checks mutasi → replies. Every step is a drop-off."
            />
          </div>
        </div>

        <div>
          <Eyebrow tone="light">The market no one is designing for</Eyebrow>
          <div className="mt-5 grid grid-cols-2 gap-3 md:gap-4">
            <StatCard
              figure="64.6M"
              label="Micro MSMEs in Indonesia"
              detail="98.7% of all MSME units. One-person operations, no admin staff, no digital books."
            />
            <StatCard
              figure="30M"
              label="Already digitally onboarded"
              detail="Have internet, smartphone & an active WhatsApp Business number. Zero new infra needed."
            />
            <StatCard
              figure="95%"
              label="WhatsApp penetration"
              detail="The de-facto operating system for Indonesian commerce. Higher than Instagram, TikTok, Facebook."
            />
            <StatCard
              figure="70%"
              label="Customers expect <5 min reply"
              detail="Slower than that and impulse buyers vanish — straight to a competitor who replies faster."
              emphasis
            />
          </div>
        </div>
      </div>
    </Slide>
  );
}

/* ------------------------------------------------------------------ */
/* Slide 3 — What is ChatKasir                                         */
/* ------------------------------------------------------------------ */

function Principle({ label, sub }: { label: string; sub: string }) {
  return (
    <div className="flex items-start gap-3">
      <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-[#c8a45c]" />
      <div>
        <p className="text-[13.5px] font-semibold tracking-tight">{label}</p>
        <p className="text-[12px] text-[#1a1a18]/60 dark:text-[#faf7f1]/60">
          {sub}
        </p>
      </div>
    </div>
  );
}

function PillarCard({
  icon: Icon,
  n,
  title,
  desc,
  tools,
}: {
  icon: typeof Bot;
  n: string;
  title: string;
  desc: string;
  tools: string;
}) {
  return (
    <Card className="group h-full rounded-2xl border border-[#1a1a18]/10 bg-white/70 p-0 ring-0 transition-all hover:border-[#1a1a18]/25 dark:border-[#faf7f1]/10 dark:bg-white/5 dark:hover:border-[#faf7f1]/30">
      <CardContent className="flex h-full flex-col p-6 md:p-7">
        <div className="flex items-center justify-between">
          <div className="flex size-11 items-center justify-center rounded-xl bg-[#1a1a18] text-[#e9c884] transition-transform duration-500 group-hover:scale-105 dark:bg-[#faf7f1] dark:text-[#1a1a18]">
            <Icon className="size-5" />
          </div>
          <span className="font-mono text-[10.5px] font-semibold tracking-[0.18em] text-[#1a1a18]/45 uppercase dark:text-[#faf7f1]/45">
            Pillar {n}
          </span>
        </div>
        <h3 className="mt-5 text-[19px] leading-tight font-semibold tracking-tight">
          {title}
        </h3>
        <p className="mt-2.5 text-[12.5px] leading-relaxed text-[#1a1a18]/65 dark:text-[#faf7f1]/65">
          {desc}
        </p>
        <div className="mt-5 border-t border-[#1a1a18]/10 pt-4 dark:border-[#faf7f1]/10">
          <p className="text-[10.5px] font-semibold tracking-[0.18em] text-[#1a1a18]/45 uppercase dark:text-[#faf7f1]/45">
            Tools
          </p>
          <p className="mt-1.5 font-mono text-[11.5px] text-[#1a1a18]/80 dark:text-[#faf7f1]/80">
            {tools}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function SolutionSlide() {
  return (
    <Slide
      index={2}
      total={5}
      eyebrow="Solution"
      title={
        <>
          ChatKasir is an AI commerce employee,
          <span className="text-[#c8a45c]"> not a chatbot.</span>
        </>
      }
      footer={
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <FootKV
            icon={ShieldCheck}
            k="No hallucination"
            v="Every price, stock count, and total is read from PostgreSQL — never invented by the LLM."
          />
          <FootKV
            icon={Database}
            k="Hybrid memory"
            v="PostgreSQL holds the deterministic state. A vector store grounds the LLM in product copy and FAQs."
          />
          <FootKV
            icon={Wallet}
            k="Works with any bank"
            v="Merchant supplies their own BCA / BRI / Mandiri / BNI account. AI handles the rest, including reconciliation."
          />
        </div>
      }
    >
      <div className="grid grid-cols-1 gap-10 lg:grid-cols-12 lg:gap-12">
        <div className="lg:col-span-4">
          <p className="text-[14px] leading-relaxed text-[#1a1a18]/70 dark:text-[#faf7f1]/70">
            ChatKasir is an autonomous sales rep, customer-service agent,
            cashier and analyst — all operating from inside the merchant's
            existing WhatsApp number. It learns the store's catalog, tone and
            policies from a single 5-minute onboarding, then runs the shop 24/7
            with no dashboard dependency.
          </p>

          <div className="mt-7 space-y-3.5">
            <Principle
              label="Single point of interface"
              sub="One WhatsApp number = storefront + POS + CRM."
            />
            <Principle
              label="Invisible software"
              sub="Zero install, zero password, zero learning curve."
            />
            <Principle
              label="Agentic, not scripted"
              sub="LLM that plans, calls tools, and executes — keyword bots can't."
            />
            <Principle
              label="Deterministic by design"
              sub="PostgreSQL holds the truth. The LLM only writes the copy."
            />
          </div>
        </div>

        <div className="lg:col-span-8">
          <Eyebrow tone="light">The four pillars of the AI employee</Eyebrow>
          <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <PillarCard
              icon={MessagesSquare}
              n="01"
              title="AI Sales Assistant"
              desc="Understands intent and slang. Recommends products from a semantic catalog, performs upsell, recovers cold leads."
              tools="RAG · Vector DB · mem0 memory"
            />
            <PillarCard
              icon={MessageCircle}
              n="02"
              title="AI Customer Service"
              desc="Answers FAQs, handles returns, absorbs complaints. Never tired, never rude, available 24/7 including holidays."
              tools="Knowledge base · Tone profiles"
            />
            <PillarCard
              icon={Banknote}
              n="03"
              title="Autonomous Cashier"
              desc="Builds the cart, computes the total, hands the customer a bank account to transfer to, then verifies the payment and closes the order."
              tools="PostgreSQL cart · Bank-transfer flow"
            />
            <PillarCard
              icon={LineChart}
              n="04"
              title="Business Intelligence Analyst"
              desc="The merchant texts 'how much did I sell this week?' in plain Indonesian. The AI writes the SQL, returns a one-line answer."
              tools="Text-to-SQL · PostgreSQL analytics"
            />
          </div>
        </div>
      </div>
    </Slide>
  );
}

function FootKV({
  icon: Icon,
  k,
  v,
}: {
  icon: typeof Bot;
  k: string;
  v: string;
}) {
  return (
    <div className="flex items-start gap-3">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-lg border border-[#1a1a18]/10 bg-white/60 dark:border-[#faf7f1]/10 dark:bg-white/5">
        <Icon className="size-4 text-[#c8a45c]" />
      </div>
      <div>
        <p className="text-[12px] font-semibold tracking-tight">{k}</p>
        <p className="mt-0.5 text-[11.5px] leading-relaxed text-[#1a1a18]/55 dark:text-[#faf7f1]/55">
          {v}
        </p>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Slide 4 — How it works                                              */
/* ------------------------------------------------------------------ */

function FlowStep({
  n,
  icon: Icon,
  title,
  desc,
  artifact,
  last = false,
}: {
  n: string;
  icon: typeof MessageCircle;
  title: string;
  desc: string;
  artifact: string;
  last?: boolean;
}) {
  return (
    <Card className="relative h-full rounded-2xl border border-[#1a1a18]/10 bg-white/70 p-0 ring-0 dark:border-[#faf7f1]/10 dark:bg-white/5">
      <CardContent className="flex h-full flex-col p-5 md:p-6">
        <div className="flex items-center justify-between">
          <div className="flex size-9 items-center justify-center rounded-lg bg-[#1a1a18] text-[#e9c884] dark:bg-[#faf7f1] dark:text-[#1a1a18]">
            <Icon className="size-4" />
          </div>
          <span className="font-mono text-[10.5px] font-semibold tracking-[0.18em] text-[#1a1a18]/45 uppercase dark:text-[#faf7f1]/45">
            Step {n}
          </span>
        </div>
        <h3 className="mt-4 text-[15px] leading-tight font-semibold tracking-tight">
          {title}
        </h3>
        <p className="mt-2 text-[12px] leading-relaxed text-[#1a1a18]/65 dark:text-[#faf7f1]/65">
          {desc}
        </p>
        <div className="mt-4 flex-1 rounded-lg border border-dashed border-[#1a1a18]/15 bg-[#faf7f1] p-3 font-mono text-[10.5px] leading-relaxed text-[#1a1a18]/75 dark:border-[#faf7f1]/15 dark:bg-[#161614] dark:text-[#faf7f1]/75">
          {artifact}
        </div>
      </CardContent>
      {!last && (
        <ChevronRight className="absolute top-1/2 -right-3 hidden size-5 -translate-y-1/2 text-[#1a1a18]/30 md:block dark:text-[#faf7f1]/30" />
      )}
    </Card>
  );
}

function HowItWorksSlide() {
  return (
    <Slide
      index={3}
      total={5}
      eyebrow="Product & architecture"
      title={
        <>
          From first <span className="text-[#c8a45c] italic">"halo"</span> to
          paid order — in four steps, no dashboard.
        </>
      }
      footer={
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <FootKV
            icon={ShieldCheck}
            k="No hallucination"
            v="Every price, stock count, and total is read from PostgreSQL — never invented by the LLM."
          />
          <FootKV
            icon={Database}
            k="Hybrid memory"
            v="PostgreSQL holds the deterministic state. A vector store grounds the LLM in product copy and FAQs."
          />
          <FootKV
            icon={Wallet}
            k="Works with any bank"
            v="Merchant supplies their own BCA / BRI / Mandiri / BNI account. AI handles the rest, including reconciliation."
          />
        </div>
      }
    >
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <FlowStep
          n="01"
          icon={ScanSearch}
          title="Customer opens the link"
          desc="A deep-link lands them in WhatsApp with a pre-filled message. The AI greets, identifies the store and the user."
          artifact="GET /toko/:slug  →  wa.me/62xxx?text=toko*budi"
        />
        <FlowStep
          n="02"
          icon={Bot}
          title="AI understands intent"
          desc="Vector search matches the chat to catalog items. The AI answers in seconds, in the store's own tone — never 'type MENU'."
          artifact="embed(query) → top-k products in Qdrant"
        />
        <FlowStep
          n="03"
          icon={ShoppingCart}
          title="Cart forms itself"
          desc="Customer says 'dua ya'. The AI calls add_to_cart(), confirms the total in plain language, and proposes the next step."
          artifact="cart = { items:[…], total:Rp90.000 }"
        />
        <FlowStep
          n="04"
          icon={Banknote}
          title="Bank-transfer checkout"
          desc="AI hands over the merchant's account number. After the customer transfers, the merchant replies 'sudah' — AI confirms and cuts stock."
          artifact="status = PAID  →  stock -= 1"
          last
        />
      </div>

      {/* Bank transfer deep-dive */}
      <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card className="rounded-2xl border border-[#1a1a18]/10 bg-white/70 p-0 ring-0 dark:border-[#faf7f1]/10 dark:bg-white/5">
          <CardContent className="p-6 md:p-7">
            <div className="flex items-center gap-2">
              <Banknote className="size-4 text-[#c8a45c]" />
              <Eyebrow tone="light">Payment flow — bank transfer</Eyebrow>
            </div>
            <ol className="mt-6 space-y-4">
              {[
                {
                  k: "AI presents the total & the account",
                  v: "BCA 123-456-7890 · a.n. Budi Santoso · Rp90.000 · order #1281",
                },
                {
                  k: "Customer transfers from any bank / e-wallet",
                  v: "No app switch, no QR scan — they're already in their bank app.",
                },
                {
                  k: "Customer says 'sudah' in the chat",
                  v: "Optional screenshot. AI logs the claim and notifies the merchant.",
                },
                {
                  k: "Merchant confirms with one reply",
                  v: "Reply 'ok' in WhatsApp. AI marks the order PAID, cuts stock, sends a receipt.",
                },
              ].map((row, i) => (
                <li key={row.k} className="grid grid-cols-[auto_1fr] gap-4">
                  <span className="mt-0.5 font-mono text-[10.5px] font-bold tracking-[0.18em] text-[#c8a45c]">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <div>
                    <p className="text-[13.5px] font-semibold tracking-tight">
                      {row.k}
                    </p>
                    <p className="mt-0.5 text-[12px] leading-relaxed text-[#1a1a18]/60 dark:text-[#faf7f1]/60">
                      {row.v}
                    </p>
                  </div>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border border-[#1a1a18]/10 bg-white/70 p-0 ring-0 dark:border-[#faf7f1]/10 dark:bg-white/5">
          <CardContent className="p-6 md:p-7">
            <div className="flex items-center gap-2">
              <Brain className="size-4 text-[#c8a45c]" />
              <Eyebrow tone="light">Why prices never hallucinate</Eyebrow>
            </div>
            <p className="mt-4 text-[13px] leading-relaxed text-[#1a1a18]/70 dark:text-[#faf7f1]/70">
              The LLM never invents a price. It is restricted to a small set of
              <span className="font-mono text-[12.5px]"> tools </span>
              backed by PostgreSQL —{" "}
              <span className="font-mono">check_stock</span>,{" "}
              <span className="font-mono">quote_total</span>,{" "}
              <span className="font-mono">confirm_payment</span>. Every quote
              the customer sees is a SQL result.
            </p>
            <pre className="mt-5 overflow-x-auto rounded-xl bg-[#1a1a18] p-4 font-mono text-[11px] leading-relaxed text-[#e9c884]">
              {`@tool
def quote_total(items: list[str]) -> int:
    """Sum the unit prices of items in the cart."""
    rows = db.query(
        "SELECT id, price FROM products WHERE id = ANY(:ids)",
        ids=items,
    )
    return sum(r.price for r in rows)`}
            </pre>
          </CardContent>
        </Card>
      </div>
    </Slide>
  );
}

/* ------------------------------------------------------------------ */
/* Slide 5 — Impact & why now                                          */
/* ------------------------------------------------------------------ */

function ImpactCard({
  icon: Icon,
  n,
  audience,
  headline,
  bullets,
}: {
  icon: typeof Store;
  n: string;
  audience: string;
  headline: string;
  bullets: { k: string; v: string }[];
}) {
  return (
    <Card className="h-full rounded-2xl border border-[#faf7f1]/10 bg-[#161614] p-0 ring-0">
      <CardContent className="flex h-full flex-col p-6 md:p-7">
        <div className="flex items-center justify-between">
          <div className="flex size-10 items-center justify-center rounded-xl bg-[#c8a45c]/15 text-[#e9c884]">
            <Icon className="size-5" />
          </div>
          <span className="font-mono text-[10.5px] font-semibold tracking-[0.18em] text-[#faf7f1]/45 uppercase">
            {n}
          </span>
        </div>
        <p className="mt-4 text-[10.5px] font-semibold tracking-[0.22em] text-[#c8a45c]/85 uppercase">
          {audience}
        </p>
        <h3 className="mt-2 text-[19px] leading-tight font-semibold tracking-tight text-[#faf7f1] md:text-[20px]">
          {headline}
        </h3>
        <ul className="mt-5 space-y-3.5">
          {bullets.map((b) => (
            <li
              key={b.k}
              className="grid grid-cols-[auto_1fr] items-baseline gap-3 border-t border-[#faf7f1]/8 pt-3.5 first:border-t-0 first:pt-0"
            >
              <ArrowUpRight className="size-3.5 shrink-0 text-[#c8a45c]" />
              <div>
                <p className="text-[12.5px] font-semibold tracking-tight text-[#faf7f1]">
                  {b.k}
                </p>
                <p className="mt-0.5 text-[11.5px] leading-relaxed text-[#faf7f1]/60">
                  {b.v}
                </p>
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}

function ImpactSlide() {
  return (
    <Slide
      index={4}
      total={5}
      eyebrow="Impact & why now"
      title={
        <>
          From informal to data-driven —
          <span className="text-[#c8a45c]">
            {" "}
            the cost of waiting is the cost of losing the next order.
          </span>
        </>
      }
      tone="dark"
      footer={
        <div className="flex flex-col items-start justify-between gap-5 md:flex-row md:items-center">
          <p className="max-w-2xl text-[13px] leading-relaxed text-[#faf7f1]/65">
            <span className="font-semibold text-[#faf7f1]">Why now.&nbsp;</span>
            WhatsApp penetration has saturated. The LLM cost-curve has crossed
            the threshold where an AI employee is cheaper than an admin hire.
            The first mover that owns the merchant relationship in chat owns the
            data — and the data is the moat.
          </p>
          <a
            href="/"
            className="group inline-flex items-center gap-2 rounded-full border border-[#c8a45c]/40 bg-[#c8a45c]/10 px-5 py-2.5 text-[12px] font-semibold tracking-tight text-[#e9c884] transition-all hover:border-[#c8a45c] hover:bg-[#c8a45c]/20"
          >
            See the product
            <ArrowUpRight className="size-3.5 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
          </a>
        </div>
      }
    >
      <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
        <ImpactCard
          icon={Store}
          n="01"
          audience="For the merchant"
          headline="<3 second response. Zero double-entry. 24/7 cashier."
          bullets={[
            {
              k: "40% of the day, reclaimed",
              v: "Hours spent copy-pasting answers and checking mutasi go back into stocking, sourcing, and serving walk-ins.",
            },
            {
              k: "No more phantom orders",
              v: "One source of truth — every cart, total and stock change is a row in PostgreSQL, not a line in a notebook.",
            },
            {
              k: "Sales intelligence, in chat",
              v: "“What sold best this week?” The merchant texts the question. The AI answers. No dashboard login required.",
            },
          ]}
        />
        <ImpactCard
          icon={Users}
          n="02"
          audience="For the customer"
          headline="A premium retail experience, delivered from a chat window."
          bullets={[
            {
              k: "No app, no signup, no password",
              v: "The friction that kills 70% of micro-store checkouts is structurally removed — the storefront is the app they already have.",
            },
            {
              k: "Remembers you",
              v: "Last week's order, the size you always buy, the variant you keep asking about — surfaced in the greeting.",
            },
            {
              k: "One window, one payment",
              v: "Bank account, total, and a 'sudah' prompt in the same thread. No context switching, no screenshot chase.",
            },
          ]}
        />
        <ImpactCard
          icon={TrendingUp}
          n="03"
          audience="For Indonesia"
          headline="A new credit-scoring substrate, built one chat at a time."
          bullets={[
            {
              k: "Informal → data-driven",
              v: "WhatsApp chat becomes structured PostgreSQL rows — a real transaction history for businesses that have never had one.",
            },
            {
              k: "Financial inclusion, finally",
              v: "A clean order & payment ledger is the missing input for any modern credit-scoring model. Lending becomes possible.",
            },
            {
              k: "Compounding network effect",
              v: "Every new merchant on ChatKasir makes the platform more attractive to the next — and harder to leave.",
            },
          ]}
        />
      </div>

      {/* Closing strip */}
      <div className="mt-8 grid grid-cols-1 items-center gap-6 rounded-3xl border border-[#c8a45c]/25 bg-[#c8a45c]/8 p-6 md:grid-cols-[1fr_auto] md:p-7">
        <div>
          <p className="text-[10.5px] font-semibold tracking-[0.22em] text-[#e9c884] uppercase">
            The bottom line
          </p>
          <p className="mt-3 max-w-3xl text-[15.5px] leading-snug font-light text-[#faf7f1] md:text-[17px]">
            We don't sell software to merchants. We give them an employee who
            already knows how to run a store, is already inside the only app
            their customers open, and never sleeps.
          </p>
        </div>
        <div className="flex flex-col items-start gap-2 md:items-end">
          <div className="flex items-center gap-2 text-[10.5px] font-semibold tracking-[0.2em] text-[#faf7f1]/70 uppercase">
            <Zap className="size-3.5 text-[#e9c884]" />
            <span>End of deck</span>
          </div>
          <p className="text-[11.5px] text-[#faf7f1]/50">
            Press &nbsp;←&nbsp; to review, or close this tab.
          </p>
        </div>
      </div>
    </Slide>
  );
}

/* ------------------------------------------------------------------ */
/* Deck controller                                                     */
/* ------------------------------------------------------------------ */

const SLIDES: Array<{ id: string; label: string; render: () => JSX.Element }> =
  [
    { id: "cover", label: "Cover", render: CoverSlide },
    { id: "problem", label: "Why digitalization fails", render: ProblemSlide },
    { id: "solution", label: "What is ChatKasir", render: SolutionSlide },
    { id: "how", label: "How it works", render: HowItWorksSlide },
    { id: "impact", label: "Impact & why now", render: ImpactSlide },
  ];

const DARK_SLIDE_IDS = new Set(["cover", "impact"]);

export default function DeckPage() {
  const [index, setIndex] = useState(0);
  const reducedMotion = useReducedMotion();

  const go = useCallback((next: number) => {
    setIndex((_current) => {
      if (next < 0) {
        return 0;
      }
      if (next > SLIDES.length - 1) {
        return SLIDES.length - 1;
      }
      return next;
    });
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      if (target) {
        const tag = target.tagName;
        if (tag === "INPUT" || tag === "TEXTAREA" || target.isContentEditable) {
          return;
        }
      }
      switch (e.key) {
        case "Enter":
        case "ArrowRight":
        case " ":
        case "PageDown":
          e.preventDefault();
          go(index + 1);
          break;
        case "ArrowLeft":
        case "Backspace":
        case "PageUp":
          e.preventDefault();
          go(index - 1);
          break;
        case "Home":
          e.preventDefault();
          go(0);
          break;
        case "End":
          e.preventDefault();
          go(SLIDES.length - 1);
          break;
        default:
          break;
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [go, index]);

  const Current = useMemo(
    () => SLIDES[index]?.render ?? SLIDES[0].render,
    [index]
  );

  const isDarkNav = DARK_SLIDE_IDS.has(SLIDES[index].id);

  return (
    <main className="bg-background relative h-[100dvh] w-full overflow-hidden">
      {/* Slide stage */}
      <div className="relative h-full w-full">
        <AnimatePresence mode="wait" initial={false} custom={reducedMotion}>
          <Current key={SLIDES[index].id} />
        </AnimatePresence>
      </div>

      {/* Bottom navigation bar */}
      <nav
        className={cn(
          "absolute right-0 bottom-0 left-0 z-30 flex items-center justify-between gap-4 border-t px-5 py-3 backdrop-blur-md md:px-10",
          isDarkNav
            ? "border-[#faf7f1]/10 bg-[#0e0e0c]/85"
            : "border-[#1a1a18]/10 bg-[#faf7f1]/92 dark:bg-[#0e0e0c]/85"
        )}
        aria-label="Slide navigation"
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            {SLIDES.map((s, i) => (
              <button
                key={s.id}
                type="button"
                onClick={() => go(i)}
                aria-label={`Go to slide ${i + 1}: ${s.label}`}
                className={cn(
                  "h-1.5 rounded-full transition-all",
                  i === index
                    ? "w-8 bg-[#c8a45c]"
                    : isDarkNav
                      ? "w-2.5 bg-[#faf7f1]/25 hover:bg-[#faf7f1]/50"
                      : "w-2.5 bg-[#1a1a18]/20 hover:bg-[#1a1a18]/40 dark:bg-[#faf7f1]/25 dark:hover:bg-[#faf7f1]/45"
                )}
              />
            ))}
          </div>
          <span
            className={cn(
              "hidden text-[10.5px] font-semibold tracking-[0.2em] uppercase sm:inline",
              isDarkNav
                ? "text-[#faf7f1]/70"
                : "text-[#1a1a18]/65 dark:text-[#faf7f1]/70"
            )}
          >
            {SLIDES[index].label}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <KeyHint k="←" label="prev" dark={isDarkNav} />
          <KeyHint k="↵" label="next" dark={isDarkNav} />
          <KeyHint k="→" label="next" dark={isDarkNav} />
        </div>
      </nav>

      {/* Side arrows (desktop) */}
      <button
        type="button"
        onClick={() => go(index - 1)}
        disabled={index === 0}
        aria-label="Previous slide"
        className={cn(
          "absolute top-1/2 left-4 z-30 hidden size-10 -translate-y-1/2 items-center justify-center rounded-full border backdrop-blur-md transition-all md:flex",
          isDarkNav
            ? "border-[#faf7f1]/10 bg-[#0e0e0c]/85 text-[#faf7f1]/60 hover:bg-[#0e0e0c] hover:text-[#faf7f1]"
            : "border-[#1a1a18]/10 bg-[#faf7f1]/85 text-[#1a1a18]/60 hover:bg-[#faf7f1] hover:text-[#1a1a18]",
          "disabled:cursor-not-allowed disabled:opacity-0"
        )}
      >
        <ArrowLeft className="size-4" />
      </button>
      <button
        type="button"
        onClick={() => go(index + 1)}
        disabled={index === SLIDES.length - 1}
        aria-label="Next slide"
        className={cn(
          "absolute top-1/2 right-4 z-30 hidden size-10 -translate-y-1/2 items-center justify-center rounded-full border backdrop-blur-md transition-all md:flex",
          isDarkNav
            ? "border-[#faf7f1]/10 bg-[#0e0e0c]/85 text-[#faf7f1]/60 hover:bg-[#0e0e0c] hover:text-[#faf7f1]"
            : "border-[#1a1a18]/10 bg-[#faf7f1]/85 text-[#1a1a18]/60 hover:bg-[#faf7f1] hover:text-[#1a1a18]",
          "disabled:cursor-not-allowed disabled:opacity-40"
        )}
      >
        <ArrowRight className="size-4" />
      </button>
    </main>
  );
}

function KeyHint({
  k,
  label,
  dark = false,
}: {
  k: string;
  label: string;
  dark?: boolean;
}) {
  return (
    <span
      className={cn(
        "hidden items-center gap-1.5 text-[10.5px] font-semibold tracking-[0.16em] uppercase sm:inline-flex",
        dark ? "text-[#faf7f1]/55" : "text-[#1a1a18]/55 dark:text-[#faf7f1]/55"
      )}
    >
      <Kbd>{k}</Kbd>
      <span>{label}</span>
    </span>
  );
}
