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
import { login, register } from "@/lib/auth";

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

export default function RegisterPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [isPending, startTransition] = useTransition();
  const [form, setForm] = useState({
    username: "",
    full_name: "",
    whatsapp_number: "",
    password: "",
  });

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (form.password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }

    startTransition(async () => {
      try {
        await register(form);
        await login({ username: form.username, password: form.password });
        toast.success("Account created!");
        router.push("/onboarding");
      } catch (error) {
        toast.error(
          error instanceof Error ? error.message : "Registration failed"
        );
      }
    });
  };

  const updateField = (field: keyof typeof form, value: string) => {
    setForm((previous) => ({ ...previous, [field]: value }));
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
                Create your store
              </CardTitle>
              <CardDescription>
                Sign up to start selling on WhatsApp with AI.
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
                  minLength={3}
                  placeholder="toko_budi"
                  value={form.username}
                  onChange={(event) =>
                    updateField("username", event.target.value)
                  }
                />
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="full_name">Full name</Label>
                <Input
                  id="full_name"
                  name="full_name"
                  autoComplete="name"
                  required
                  placeholder="Budi Santoso"
                  value={form.full_name}
                  onChange={(event) =>
                    updateField("full_name", event.target.value)
                  }
                />
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="whatsapp_number">WhatsApp number</Label>
                <Input
                  id="whatsapp_number"
                  name="whatsapp_number"
                  autoComplete="tel"
                  placeholder="+62 812 3456 7890"
                  value={form.whatsapp_number}
                  onChange={(event) =>
                    updateField("whatsapp_number", event.target.value)
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
                    autoComplete="new-password"
                    required
                    minLength={8}
                    placeholder="••••••••"
                    value={form.password}
                    onChange={(event) =>
                      updateField("password", event.target.value)
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
                <p className="text-muted-foreground text-xs">
                  Must be at least 8 characters.
                </p>
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
                    Creating account...
                  </>
                ) : (
                  "Create account"
                )}
              </Button>
            </form>

            <p className="text-muted-foreground mt-6 text-center text-sm">
              Already have an account?{" "}
              <Link
                href="/login"
                className="text-primary font-medium hover:underline"
              >
                Sign in
              </Link>
            </p>
          </CardContent>
        </Card>
      </FadeIn>
    </main>
  );
}
