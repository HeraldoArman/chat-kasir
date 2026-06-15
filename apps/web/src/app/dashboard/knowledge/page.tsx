"use client";

import { useEffect, useState, useTransition } from "react";
import { motion } from "framer-motion";
import { BookOpen, Loader2, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@chat-kasir/ui/components/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@chat-kasir/ui/components/card";
import { Input } from "@chat-kasir/ui/components/input";
import { Label } from "@chat-kasir/ui/components/label";
import {
  createKnowledgeEntry,
  deleteKnowledge,
  listKnowledge,
  type KnowledgeEntry,
} from "@/lib/store";

export default function KnowledgePage() {
  const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [isPending, startTransition] = useTransition();
  const [form, setForm] = useState({
    category: "",
    question: "",
    answer: "",
  });

  const load = async () => {
    try {
      const data = await listKnowledge();
      setEntries(data);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to load knowledge"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.category.trim() || !form.answer.trim()) {
      toast.error("Category and answer are required");
      return;
    }

    startTransition(async () => {
      try {
        await createKnowledgeEntry(form);
        toast.success("Knowledge added");
        setForm({ category: "", question: "", answer: "" });
        await load();
      } catch (error) {
        toast.error(
          error instanceof Error ? error.message : "Failed to add knowledge"
        );
      }
    });
  };

  const handleDelete = (id: string) => {
    startTransition(async () => {
      try {
        await deleteKnowledge(id);
        toast.success("Entry removed");
        await load();
      } catch (error) {
        toast.error(
          error instanceof Error ? error.message : "Failed to remove"
        );
      }
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Knowledge Base</h1>
        <p className="text-muted-foreground mt-1">
          FAQs and store policies for the AI to answer.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="rounded-3xl border">
          <CardHeader>
            <CardTitle className="text-sm font-medium">Add entry</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div className="space-y-1">
                <Label htmlFor="category">Category</Label>
                <Input
                  id="category"
                  value={form.category}
                  onChange={(event) =>
                    setForm((previous) => ({
                      ...previous,
                      category: event.target.value,
                    }))
                  }
                  placeholder="FAQ, Policy, Hours..."
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="question">Question (optional)</Label>
                <Input
                  id="question"
                  value={form.question}
                  onChange={(event) =>
                    setForm((previous) => ({
                      ...previous,
                      question: event.target.value,
                    }))
                  }
                  placeholder="What are your opening hours?"
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="answer">Answer</Label>
                <textarea
                  id="answer"
                  rows={3}
                  value={form.answer}
                  onChange={(event) =>
                    setForm((previous) => ({
                      ...previous,
                      answer: event.target.value,
                    }))
                  }
                  placeholder="We are open every day from 9 AM to 9 PM."
                  className="border-input placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 w-full rounded-none border bg-transparent px-2.5 py-2 text-xs transition-colors outline-none focus-visible:ring-1"
                />
              </div>
              <Button
                type="submit"
                className="w-full rounded-full"
                disabled={isPending}
              >
                {isPending ? (
                  <Loader2 className="mr-2 size-4 animate-spin" />
                ) : (
                  <Plus className="mr-2 size-4" />
                )}
                Add entry
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="text-primary size-6 animate-spin" />
            </div>
          ) : entries.length === 0 ? (
            <Card className="rounded-3xl border">
              <CardContent className="flex flex-col items-center justify-center gap-3 py-12">
                <BookOpen className="text-muted-foreground size-10" />
                <p className="text-muted-foreground">
                  No knowledge entries yet.
                </p>
              </CardContent>
            </Card>
          ) : (
            entries.map((entry, index) => (
              <motion.div
                key={entry.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className="rounded-3xl border">
                  <CardContent className="flex items-start justify-between gap-4 p-4">
                    <div className="min-w-0">
                      <span className="bg-primary/10 text-primary rounded-full px-2 py-0.5 text-[10px]">
                        {entry.category}
                      </span>
                      {entry.question && (
                        <p className="mt-2 font-medium">{entry.question}</p>
                      )}
                      <p className="text-muted-foreground mt-1 text-sm">
                        {entry.answer}
                      </p>
                    </div>
                    <Button
                      size="icon-xs"
                      variant="ghost"
                      onClick={() => handleDelete(entry.id)}
                      aria-label="Delete entry"
                    >
                      <Trash2 className="size-4" />
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
