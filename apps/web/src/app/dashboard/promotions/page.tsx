"use client";

import { useEffect, useState, useTransition } from "react";
import { motion } from "framer-motion";
import { Calendar, Loader2, Percent, Plus, Trash2 } from "lucide-react";
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@chat-kasir/ui/components/select";

import {
  createPromotion,
  deletePromotion,
  listPromotions,
  type Promotion,
} from "@/lib/store";

export default function PromotionsPage() {
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [loading, setLoading] = useState(true);
  const [isPending, startTransition] = useTransition();
  const [form, setForm] = useState({
    name: "",
    description: "",
    discount_type: "percentage" as "percentage" | "fixed",
    discount_value: "",
    min_quantity: "",
    start_at: "",
    end_at: "",
  });

  const load = async () => {
    try {
      const data = await listPromotions();
      setPromotions(data);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to load promotions"
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
    if (!form.name.trim()) {
      toast.error("Name is required");
      return;
    }
    const discountValue = Number(form.discount_value);
    if (Number.isNaN(discountValue) || discountValue <= 0) {
      toast.error("Discount value must be positive");
      return;
    }

    startTransition(async () => {
      try {
        await createPromotion({
          name: form.name,
          description: form.description || undefined,
          discount_type: form.discount_type,
          discount_value: discountValue,
          min_quantity: form.min_quantity
            ? Number(form.min_quantity)
            : undefined,
          start_at: form.start_at || undefined,
          end_at: form.end_at || undefined,
          is_active: true,
        });
        toast.success("Promotion created");
        setForm({
          name: "",
          description: "",
          discount_type: "percentage",
          discount_value: "",
          min_quantity: "",
          start_at: "",
          end_at: "",
        });
        await load();
      } catch (error) {
        toast.error(
          error instanceof Error ? error.message : "Failed to create promotion"
        );
      }
    });
  };

  const handleDelete = (id: string) => {
    startTransition(async () => {
      try {
        await deletePromotion(id);
        toast.success("Promotion removed");
        await load();
      } catch (error) {
        toast.error(
          error instanceof Error ? error.message : "Failed to remove promotion"
        );
      }
    });
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "No limit";
    return new Date(dateStr).toLocaleDateString("id-ID", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Promotions</h1>
        <p className="text-muted-foreground mt-1">
          Create and manage discounts for your store.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="rounded-3xl border">
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Create promotion
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="flex flex-col gap-3">
              <div className="flex flex-col gap-1">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={form.name}
                  onChange={(event) =>
                    setForm((previous) => ({
                      ...previous,
                      name: event.target.value,
                    }))
                  }
                  placeholder="Flash Sale 50%"
                />
              </div>
              <div className="flex flex-col gap-1">
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={form.description}
                  onChange={(event) =>
                    setForm((previous) => ({
                      ...previous,
                      description: event.target.value,
                    }))
                  }
                  placeholder="Short description"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="flex flex-col gap-1">
                  <Label htmlFor="discount_type">Discount Type</Label>
                  <Select
                    value={form.discount_type}
                    onValueChange={(value) => {
                      if (value === "percentage" || value === "fixed") {
                        setForm((previous) => ({
                          ...previous,
                          discount_type: value,
                        }));
                      }
                    }}
                  >
                    <SelectTrigger id="discount_type">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="percentage">Percentage (%)</SelectItem>
                      <SelectItem value="fixed">Fixed (IDR)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex flex-col gap-1">
                  <Label htmlFor="discount_value">
                    {form.discount_type === "percentage"
                      ? "Discount %"
                      : "Discount (IDR)"}
                  </Label>
                  <Input
                    id="discount_value"
                    type="number"
                    min={1}
                    value={form.discount_value}
                    onChange={(event) =>
                      setForm((previous) => ({
                        ...previous,
                        discount_value: event.target.value,
                      }))
                    }
                    placeholder={
                      form.discount_type === "percentage" ? "50" : "10000"
                    }
                  />
                </div>
              </div>
              <div className="flex flex-col gap-1">
                <Label htmlFor="min_quantity">Min Quantity (optional)</Label>
                <Input
                  id="min_quantity"
                  type="number"
                  min={1}
                  value={form.min_quantity}
                  onChange={(event) =>
                    setForm((previous) => ({
                      ...previous,
                      min_quantity: event.target.value,
                    }))
                  }
                  placeholder="2"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="flex flex-col gap-1">
                  <Label htmlFor="start_at">Start Date</Label>
                  <Input
                    id="start_at"
                    type="date"
                    value={form.start_at}
                    onChange={(event) =>
                      setForm((previous) => ({
                        ...previous,
                        start_at: event.target.value,
                      }))
                    }
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <Label htmlFor="end_at">End Date</Label>
                  <Input
                    id="end_at"
                    type="date"
                    value={form.end_at}
                    onChange={(event) =>
                      setForm((previous) => ({
                        ...previous,
                        end_at: event.target.value,
                      }))
                    }
                  />
                </div>
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
                Create promotion
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="flex flex-col gap-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="text-primary size-6 animate-spin" />
            </div>
          ) : promotions.length === 0 ? (
            <Card className="rounded-3xl border">
              <CardContent className="flex flex-col items-center justify-center gap-3 py-12">
                <Percent className="text-muted-foreground size-10" />
                <p className="text-muted-foreground">No promotions yet.</p>
              </CardContent>
            </Card>
          ) : (
            promotions.map((promotion, index) => (
              <motion.div
                key={promotion.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className="rounded-3xl border">
                  <CardContent className="flex items-start justify-between gap-4 p-4">
                    <div className="min-w-0">
                      <p className="truncate font-semibold">{promotion.name}</p>
                      <p className="text-muted-foreground text-xs">
                        {promotion.discount_type === "percentage"
                          ? `${promotion.discount_value}% off`
                          : `Rp ${promotion.discount_value.toLocaleString("id-ID")} off`}
                        {promotion.min_quantity &&
                          ` • Min: ${promotion.min_quantity} items`}
                      </p>
                      <p className="text-muted-foreground mt-1 flex items-center gap-1 text-xs">
                        <Calendar className="size-3" />
                        {formatDate(promotion.start_at)} →{" "}
                        {formatDate(promotion.end_at)}
                      </p>
                    </div>
                    <Button
                      size="icon-xs"
                      variant="ghost"
                      onClick={() => handleDelete(promotion.id)}
                      aria-label="Delete promotion"
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
