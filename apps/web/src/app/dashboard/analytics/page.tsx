"use client";

import { useEffect, useState } from "react";
import { Loader2, TrendingUp, Package, Clock } from "lucide-react";
import { toast } from "sonner";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@chat-kasir/ui/components/card";
import { getDashboardSummary, type DashboardSummary } from "@/lib/store";

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void getDashboardSummary()
      .then((data) => setSummary(data))
      .catch((error) => {
        toast.error(error instanceof Error ? error.message : "Failed to load analytics");
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="text-primary size-6 animate-spin" />
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="text-muted-foreground py-12 text-center">
        Failed to load analytics.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground mt-1">
          Revenue, bestseller, and pending orders at a glance.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card className="rounded-3xl border">
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <TrendingUp className="size-3.5" />
              Total Revenue
            </CardDescription>
            <CardTitle className="text-3xl font-bold">
              Rp {summary.total_revenue.toLocaleString("id-ID")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground text-xs">
              From paid & confirmed orders
            </p>
          </CardContent>
        </Card>

        <Card className="rounded-3xl border">
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <Clock className="size-3.5" />
              Pending Orders
            </CardDescription>
            <CardTitle className="text-3xl font-bold">
              {summary.pending_orders}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground text-xs">
              Awaiting verification
            </p>
          </CardContent>
        </Card>

        <Card className="rounded-3xl border">
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-2">
              <Package className="size-3.5" />
              Products
            </CardDescription>
            <CardTitle className="text-3xl font-bold">
              {summary.product_count}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground text-xs">In catalog</p>
          </CardContent>
        </Card>
      </div>

      {summary.bestseller && (
        <Card className="rounded-3xl border">
          <CardHeader>
            <CardDescription>Bestseller</CardDescription>
            <CardTitle className="text-xl font-semibold">
              {String(summary.bestseller.name ?? "-")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground text-sm">
              {String(summary.bestseller.quantity ?? 0)} sold
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
