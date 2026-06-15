"use client";

import { useState, useTransition } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Eye, EyeOff, Loader2, Store } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@chat-kasir/ui/components/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@chat-kasir/ui/components/card";
import { Input } from "@chat-kasir/ui/components/input";
import { Label } from "@chat-kasir/ui/components/label";
import { login } from "@/lib/auth";
import { getMyStore } from "@/lib/store";

function FadeIn({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
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
    <main className="flex min-h-[calc(100dvh-4rem)] items-center justify-center px-4 py-12">
      <FadeIn>
        <Card className="w-full max-w-md rounded-3xl border">
          <CardHeader className="space-y-1 text-center">
            <div className="mx-auto mb-4 flex size-12 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
              <Store className="size-6" />
            </div>
            <CardTitle className="text-2xl font-bold tracking-tight">
              Sign in to ChatKasir
            </CardTitle>
            <CardDescription>
              Enter your username and password to access your store.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
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

              <div className="space-y-2">
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
                    className="absolute inset-y-0 right-0 flex items-center justify-center px-3 text-muted-foreground outline-none hover:text-foreground"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                  </button>
                </div>
              </div>

              <Button type="submit" className="w-full rounded-full" disabled={isPending}>
                {isPending ? (
                  <>
                    <Loader2 className="mr-2 size-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  "Sign in"
                )}
              </Button>
            </form>

            <p className="text-muted-foreground mt-6 text-center text-sm">
              Don't have an account?{" "}
              <Link href="/register" className="font-medium text-primary hover:underline">
                Create one
              </Link>
            </p>
          </CardContent>
        </Card>
      </FadeIn>
    </main>
  );
}
