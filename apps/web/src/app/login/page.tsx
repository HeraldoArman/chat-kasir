"use client";

import { useState, useTransition } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Eye, EyeOff, Loader2, Store } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@chat-kasir/ui/components/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@chat-kasir/ui/components/card";
import { Input } from "@chat-kasir/ui/components/input";
import { Label } from "@chat-kasir/ui/components/label";
import { login } from "@/lib/auth";
import { getMyStore } from "@/lib/store";

function FadeIn({
  children,
  delay = 0,
}: {
  children: React.ReactNode;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 32 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </motion.div>
  );
}

export default function LoginPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [isPending, startTransition] = useTransition();
  const [form, setForm] = useState({ username: "", password: "" });

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    startTransition(async () => {
      try {
        await login(form);
        const store = await getMyStore();
        toast.success("Welcome back!");
        router.push(store ? "/dashboard" : "/onboarding");
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "Login failed");
      }
    });
  };

  return (
    <main className="relative flex min-h-[calc(100dvh-4rem)] items-center justify-center overflow-hidden px-4 py-12">
      {/* Warm ambient glow — matches landing page CTA pattern */}
      <div
        aria-hidden
        className="bg-primary/5 dark:bg-primary/10 pointer-events-none absolute -top-32 -right-32 size-[32rem] rounded-full blur-3xl"
      />
      <div
        aria-hidden
        className="bg-primary/5 dark:bg-primary/10 pointer-events-none absolute -bottom-40 -left-40 size-[28rem] rounded-full blur-3xl"
      />

      <FadeIn>
        <Card className="w-full max-w-3xl rounded-3xl border shadow-sm">
          <CardHeader className="flex flex-col items-center gap-4 text-center">
            <div className="bg-primary/10 text-primary flex size-12 items-center justify-center rounded-2xl">
              <Store className="size-6" />
            </div>
            <div className="flex flex-col gap-1">
              <CardTitle className="text-2xl font-bold tracking-tight">
                Sign in to ChatKasir
              </CardTitle>
              <CardDescription>
                Enter your username and password to access your store.
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="flex flex-col gap-5">
              <div className="flex flex-col gap-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  name="username"
                  autoComplete="username"
                  required
                  placeholder="toko_budi"
                  value={form.username}
                  onChange={(event) =>
                    setForm((previous) => ({
                      ...previous,
                      username: event.target.value,
                    }))
                  }
                />
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    required
                    placeholder="••••••••"
                    value={form.password}
                    onChange={(event) =>
                      setForm((previous) => ({
                        ...previous,
                        password: event.target.value,
                      }))
                    }
                    className="pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((previous) => !previous)}
                    className="text-muted-foreground hover:text-foreground absolute inset-y-0 right-0 flex items-center justify-center px-3 outline-none"
                    aria-label={
                      showPassword ? "Hide password" : "Show password"
                    }
                  >
                    {showPassword ? (
                      <EyeOff className="size-4" />
                    ) : (
                      <Eye className="size-4" />
                    )}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full rounded-full"
                disabled={isPending}
              >
                {isPending ? (
                  <>
                    <Loader2
                      className="size-4 animate-spin"
                      data-icon="inline-start"
                    />
                    Signing in...
                  </>
                ) : (
                  "Sign in"
                )}
              </Button>
            </form>

            <p className="text-muted-foreground mt-6 text-center text-sm">
              Don&apos;t have an account?{" "}
              <Link
                href="/register"
                className="text-primary font-medium hover:underline"
              >
                Create one
              </Link>
            </p>
          </CardContent>
        </Card>
      </FadeIn>
    </main>
  );
}
