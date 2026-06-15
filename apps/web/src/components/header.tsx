"use client";

import Link from "next/link";
import { useState } from "react";
import { Menu, X, Store } from "lucide-react";

import { Button } from "@chat-kasir/ui/components/button";
import { ModeToggle } from "./mode-toggle";

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  const links = [
    { to: "#features", label: "Features" },
    { to: "#how-it-works", label: "How it works" },
  ] as const;

  return (
    <header className="fixed top-0 right-0 left-0 z-50 px-4 pt-4">
      <div className="container mx-auto max-w-7xl">
        <nav className="bg-background/80 flex items-center justify-between rounded-full border px-4 py-2 shadow-sm backdrop-blur-xl">
          <Link href="/" className="flex items-center gap-2">
            <span className="bg-primary text-primary-foreground flex size-8 items-center justify-center rounded-full">
              <Store className="size-4" />
            </span>
            <span className="text-base font-semibold tracking-tight">
              ChatKasir
            </span>
          </Link>

          <div className="hidden items-center gap-8 md:flex">
            {links.map(({ to, label }) => (
              <Link
                key={to}
                href={to}
                className="text-muted-foreground hover:text-foreground text-sm font-medium transition-colors"
              >
                {label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <div className="hidden md:block">
              <ModeToggle />
            </div>
            <Link href="#cta" className="hidden md:block">
              <Button size="sm" className="rounded-full px-4">
                Start free
              </Button>
            </Link>

            <button
              type="button"
              onClick={() => setMenuOpen((v) => !v)}
              className="flex size-9 items-center justify-center rounded-full border md:hidden"
              aria-label="Toggle menu"
            >
              {menuOpen ? (
                <X className="size-4" />
              ) : (
                <Menu className="size-4" />
              )}
            </button>
          </div>
        </nav>

        {menuOpen && (
          <div className="bg-background/95 mt-2 rounded-2xl border p-4 shadow-lg backdrop-blur-xl md:hidden">
            <div className="flex flex-col gap-3">
              {links.map(({ to, label }) => (
                <Link
                  key={to}
                  href={to}
                  onClick={() => setMenuOpen(false)}
                  className="text-muted-foreground hover:text-foreground text-sm font-medium transition-colors"
                >
                  {label}
                </Link>
              ))}
              <div className="flex items-center justify-between pt-2">
                <ModeToggle />
                <Link href="#cta" onClick={() => setMenuOpen(false)}>
                  <Button size="sm" className="rounded-full px-4">
                    Start free
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
