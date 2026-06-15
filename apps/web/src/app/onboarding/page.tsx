"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Loader2, Store } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@chat-kasir/ui/components/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@chat-kasir/ui/components/card";
import { Input } from "@chat-kasir/ui/components/input";
import { Label } from "@chat-kasir/ui/components/label";
import { createStore } from "@/lib/store";

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

export default function OnboardingPage() {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [form, setForm] = useState({
    name: "",
    description: "",
    category: "",
    whatsapp_number: "",
  });

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.name.trim()) {
      toast.error("Store name is required");
      return;
    }

    startTransition(async () => {
      try {
        await createStore(form);
        toast.success("Store created!");
        router.push("/dashboard");
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "Failed to create store");
      }
    });
  };

  return (
    <main className="flex min-h-[calc(100dvh-4rem)] items-center justify-center px-4 py-12">
      <FadeIn>
        <Card className="w-full max-w-lg rounded-3xl border">
          <CardHeader className="space-y-1 text-center">
            <div className="bg-primary text-primary-foreground mx-auto mb-4 flex size-12 items-center justify-center rounded-2xl">
              <Store className="size-6" />
            </div>
            <CardTitle className="text-2xl font-bold tracking-tight">Set up your store</CardTitle>
            <CardDescription>
              Tell customers what you sell and how to reach you.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Store name</Label>
                <Input
                  id="name"
                  name="name"
                  required
                  placeholder="Toko Budi"
                  value={form.name}
                  onChange={(event) =>
                    setForm((previous) => ({
                      ...previous,
                      name: event.target.value,
                    }))
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Input
                  id="category"
                  name="category"
                  placeholder="Retail, Food, Spare Parts..."
                  value={form.category}
                  onChange={(event) =>
                    setForm((previous) => ({
                      ...previous,
                      category: event.target.value,
                    }))
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="whatsapp_number">WhatsApp number</Label>
                <Input
                  id="whatsapp_number"
                  name="whatsapp_number"
                  placeholder="+62 812 3456 7890"
                  value={form.whatsapp_number}
                  onChange={(event) =>
                    setForm((previous) => ({
                      ...previous,
                      whatsapp_number: event.target.value,
                    }))
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <textarea
                  id="description"
                  name="description"
                  rows={3}
                  placeholder="Short description of your store..."
                  className="border-input placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 w-full rounded-none border bg-transparent px-2.5 py-2 text-xs transition-colors outline-none focus-visible:ring-1"
                  value={form.description}
                  onChange={(event) =>
                    setForm((previous) => ({
                      ...previous,
                      description: event.target.value,
                    }))
                  }
                />
              </div>

              <Button
                type="submit"
                className="w-full rounded-full"
                disabled={isPending}
              >
                {isPending ? (
                  <>
                    <Loader2 className="mr-2 size-4 animate-spin" />
                    Creating store...
                  </>
                ) : (
                  "Create store"
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </FadeIn>
    </main>
  );
}
