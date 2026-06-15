"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  MessageCircle,
  Bot,
  Banknote,
  Receipt,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  Store,
} from "lucide-react";

import { Button } from "@chat-kasir/ui/components/button";
import { Card, CardContent } from "@chat-kasir/ui/components/card";
import { Badge } from "@chat-kasir/ui/components/badge";
import { Separator } from "@chat-kasir/ui/components/separator";

const features = [
  {
    icon: MessageCircle,
    title: "WhatsApp-native storefront",
    description:
      "Customers message your store the same way they chat friends. No new app, no login, no friction.",
  },
  {
    icon: Bot,
    title: "AI that sells for you",
    description:
      "It answers product questions, recommends items from your catalog, and remembers each customer's preferences.",
  },
  {
    icon: Banknote,
    title: "Bank transfer, verified fast",
    description:
      "Checkout gives your store's account number. When the buyer confirms payment, the AI pings you to verify.",
  },
  {
    icon: Receipt,
    title: "Orders, not spreadsheets",
    description:
      "Every quote, cart, and order is logged automatically. Ask the AI for today's sales or stock warnings.",
  },
];

const steps = [
  {
    number: "01",
    title: "Customer opens your store link",
    description: "They land on WhatsApp with your store slug pre-filled.",
  },
  {
    number: "02",
    title: "AI helps them choose",
    description: "Natural chat turns into a cart, then a priced order.",
  },
  {
    number: "03",
    title: "Transfer to your account",
    description:
      "Your bank details, the exact total, and a confirmation prompt.",
  },
  {
    number: "04",
    title: "You verify, AI follows up",
    description:
      "One reply confirms payment; the customer gets their receipt instantly.",
  },
];

const highlights = [
  "Setup in under 5 minutes",
  "No website required",
  "Works with any Indonesian bank",
  "Merchants verify from WhatsApp",
];

function FadeIn({
  children,
  delay = 0,
  className = "",
}: {
  children: React.ReactNode;
  delay?: number;
  className?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 32 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export default function Home() {
  return (
    <main className="flex flex-col overflow-x-hidden">
      {/* Hero — editorial split */}
      <section className="relative min-h-[100dvh] border-b px-4 py-24 md:py-32">
        <div className="container mx-auto grid min-h-[calc(100dvh-12rem)] max-w-7xl grid-cols-1 items-center gap-12 lg:grid-cols-2 lg:gap-8">
          <FadeIn className="order-2 lg:order-1">
            <Badge
              variant="outline"
              className="mb-6 rounded-full px-3 py-1 text-[11px] font-medium tracking-widest uppercase"
            >
              <Sparkles className="mr-1.5 size-3" />
              AI Commerce Employee
            </Badge>
            <h1 className="max-w-2xl text-4xl leading-[1.05] font-extrabold tracking-tight text-balance md:text-5xl lg:text-6xl">
              Run your store from WhatsApp.
            </h1>
            <p className="text-muted-foreground mt-6 max-w-lg text-lg leading-relaxed text-balance md:text-xl">
              ChatKasir gives Indonesian MSMEs an AI employee that sells,
              answers, and takes payments — all inside the chat app everyone
              already uses.
            </p>
            <div className="mt-10 flex flex-wrap items-center gap-4">
              <Link href="#cta">
                <Button size="lg" className="rounded-full px-7">
                  Start free
                  <ArrowRight data-icon="inline-end" className="size-4" />
                </Button>
              </Link>
              <Link href="#how-it-works">
                <Button
                  size="lg"
                  variant="outline"
                  className="rounded-full px-7"
                >
                  See how it works
                </Button>
              </Link>
            </div>
            <div className="text-muted-foreground mt-10 flex flex-wrap gap-x-6 gap-y-2 text-sm">
              {highlights.map((text) => (
                <div key={text} className="flex items-center gap-2">
                  <CheckCircle2 className="text-primary size-4" />
                  <span>{text}</span>
                </div>
              ))}
            </div>
          </FadeIn>

          <FadeIn delay={0.15} className="order-1 lg:order-2">
            <div className="bg-muted relative mx-auto aspect-[4/5] w-full max-w-md overflow-hidden rounded-3xl lg:ml-auto lg:max-w-lg">
              <img
                src="https://picsum.photos/seed/chatkasir-hero-warm/800/1000"
                alt="A warm, candid photo of a small shop owner chatting with a customer"
                className="size-full object-cover"
              />
              <div className="from-background/80 absolute inset-0 bg-gradient-to-t via-transparent to-transparent" />
              <div className="bg-card/90 absolute right-6 bottom-6 left-6 rounded-2xl border p-4 shadow-sm backdrop-blur">
                <div className="flex items-start gap-3">
                  <div className="bg-primary text-primary-foreground flex size-10 shrink-0 items-center justify-center rounded-full">
                    <Store className="size-5" />
                  </div>
                  <div>
                    <p className="font-medium">Toko Budi</p>
                    <p className="text-muted-foreground text-sm">
                      New order #1281 — waiting for payment confirmation
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* Trust strip */}
      <section className="border-b px-4 py-10">
        <div className="container mx-auto max-w-7xl">
          <FadeIn>
            <div className="flex flex-col items-center justify-between gap-8 md:flex-row">
              <p className="text-muted-foreground text-sm font-medium tracking-widest uppercase">
                Built for Indonesian MSMEs
              </p>
              <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
                {[
                  "No app download",
                  "Bank transfer ready",
                  "AI-powered 24/7",
                ].map((item) => (
                  <div
                    key={item}
                    className="text-muted-foreground flex items-center gap-2 text-sm"
                  >
                    <span className="bg-primary size-1.5 rounded-full" />
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* Features — asymmetric bento */}
      <section id="features" className="px-4 py-24 md:py-32">
        <div className="container mx-auto max-w-7xl">
          <FadeIn>
            <div className="mb-16 max-w-2xl">
              <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
                Everything your store needs, in one chat.
              </h2>
              <p className="text-muted-foreground mt-4 text-lg">
                No dashboard fatigue. Customers chat, the AI handles the rest.
              </p>
            </div>
          </FadeIn>

          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-12">
            {features.map(({ icon: Icon, title, description }, index) => {
              const isLarge = index === 0 || index === 3;
              return (
                <FadeIn
                  key={title}
                  delay={index * 0.08}
                  className={`${
                    isLarge ? "lg:col-span-7" : "lg:col-span-5"
                  } ${index === 1 ? "md:row-span-2" : ""}`}
                >
                  <Card className="group bg-card h-full overflow-hidden rounded-3xl border transition-all duration-500 hover:shadow-md">
                    <CardContent className="flex h-full flex-col p-8 md:p-10">
                      <div className="bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground mb-6 flex size-12 items-center justify-center rounded-2xl transition-colors">
                        <Icon className="size-6" />
                      </div>
                      <h3 className="text-xl font-semibold tracking-tight md:text-2xl">
                        {title}
                      </h3>
                      <p className="text-muted-foreground mt-3 max-w-md text-base leading-relaxed">
                        {description}
                      </p>
                      {index === 0 && (
                        <div className="mt-auto pt-8">
                          <div className="bg-muted relative overflow-hidden rounded-2xl">
                            <img
                              src="https://picsum.photos/seed/chatkasir-whatsapp/600/340"
                              alt="Phone showing a WhatsApp chat with a store"
                              className="w-full object-cover transition-transform duration-700 group-hover:scale-105"
                            />
                          </div>
                        </div>
                      )}
                      {index === 3 && (
                        <div className="mt-auto pt-8">
                          <div className="grid grid-cols-2 gap-3">
                            <div className="bg-background rounded-xl border p-4">
                              <p className="text-muted-foreground text-xs tracking-wider uppercase">
                                Today's sales
                              </p>
                              <p className="mt-1 text-2xl font-bold">Rp 1.2M</p>
                            </div>
                            <div className="bg-background rounded-xl border p-4">
                              <p className="text-muted-foreground text-xs tracking-wider uppercase">
                                Orders
                              </p>
                              <p className="mt-1 text-2xl font-bold">18</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </FadeIn>
              );
            })}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section
        id="how-it-works"
        className="bg-muted/30 border-t px-4 py-24 md:py-32"
      >
        <div className="container mx-auto max-w-7xl">
          <FadeIn>
            <div className="mb-16 max-w-2xl">
              <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
                From first message to paid order.
              </h2>
              <p className="text-muted-foreground mt-4 text-lg">
                The customer never leaves WhatsApp. The merchant never checks a
                dashboard.
              </p>
            </div>
          </FadeIn>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
            {steps.map(({ number, title, description }, index) => (
              <FadeIn key={title} delay={index * 0.1}>
                <div className="bg-card relative h-full rounded-3xl border p-8">
                  <span className="text-primary/20 text-5xl font-extrabold">
                    {number}
                  </span>
                  <h3 className="mt-6 text-lg font-semibold">{title}</h3>
                  <p className="text-muted-foreground mt-2 text-sm leading-relaxed">
                    {description}
                  </p>
                  {index !== steps.length - 1 && (
                    <ArrowRight className="text-muted-foreground/40 absolute top-1/2 -right-4 hidden size-5 -translate-y-1/2 lg:block" />
                  )}
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section id="cta" className="px-4 py-24 md:py-32">
        <div className="container mx-auto max-w-5xl">
          <FadeIn>
            <div className="bg-primary text-primary-foreground relative overflow-hidden rounded-[2.5rem] px-8 py-16 md:px-16 md:py-24">
              <div className="relative z-10 mx-auto max-w-2xl text-center">
                <h2 className="text-3xl font-bold tracking-tight md:text-5xl">
                  Give your store an AI employee today.
                </h2>
                <p className="mt-6 text-lg opacity-90">
                  Sign up free, add your products and bank account, then share
                  your WhatsApp store link.
                </p>
                <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
                  <Link href="/register">
                    <Button
                      size="lg"
                      variant="secondary"
                      className="rounded-full px-8"
                    >
                      Create your store
                      <ArrowRight data-icon="inline-end" className="size-4" />
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="pointer-events-none absolute -top-24 -right-24 size-[28rem] rounded-full bg-white/10 blur-3xl" />
              <div className="pointer-events-none absolute -bottom-32 -left-32 size-[24rem] rounded-full bg-white/10 blur-3xl" />
            </div>
          </FadeIn>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t px-4 py-12">
        <div className="container mx-auto max-w-7xl">
          <div className="flex flex-col items-start justify-between gap-8 md:flex-row md:items-center">
            <div className="flex items-center gap-2">
              <span className="bg-primary text-primary-foreground flex size-9 items-center justify-center rounded-xl text-lg font-bold">
                C
              </span>
              <span className="text-xl font-semibold tracking-tight">
                ChatKasir
              </span>
            </div>
            <p className="text-muted-foreground text-sm">
              © {new Date().getFullYear()} ChatKasir. AI Commerce Employee for
              Indonesian MSMEs.
            </p>
          </div>
          <Separator className="my-8" />
          <div className="text-muted-foreground flex flex-wrap gap-6 text-sm">
            <Link href="#" className="hover:text-foreground">
              Privacy
            </Link>
            <Link href="#" className="hover:text-foreground">
              Terms
            </Link>
            <Link href="#" className="hover:text-foreground">
              Contact
            </Link>
          </div>
        </div>
      </footer>
    </main>
  );
}
