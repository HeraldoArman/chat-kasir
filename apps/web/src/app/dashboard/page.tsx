import Link from "next/link";
import { redirect } from "next/navigation";
import {
  Package,
  Building2,
  Receipt,
  BarChart3,
  BookOpen,
  TrendingUp,
  Clock,
} from "lucide-react";

import { Button } from "@chat-kasir/ui/components/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@chat-kasir/ui/components/card";
import { getMe } from "@/lib/auth";
import { getDashboardSummary } from "@/lib/store";

const nav = [
  { href: "/dashboard/products" as const, label: "Products", icon: Package },
  { href: "/dashboard/bank" as const, label: "Bank Account", icon: Building2 },
  { href: "/dashboard/orders" as const, label: "Orders", icon: Receipt },
  { href: "/dashboard/analytics" as const, label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/knowledge" as const, label: "Knowledge", icon: BookOpen },
] as const;

export default async function DashboardPage() {
  const user = await getMe();
  if (!user) {
    redirect("/login");
  }

  let summary;
  try {
    summary = await getDashboardSummary();
  } catch {
    redirect("/onboarding");
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Welcome back, {user.full_name || user.username}
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="rounded-3xl border">
          <CardHeader className="pb-2">
            <CardDescription>Total Revenue</CardDescription>
            <CardTitle className="text-2xl font-bold">
              Rp {summary.total_revenue.toLocaleString("id-ID")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-muted-foreground flex items-center gap-1 text-xs">
              <TrendingUp className="size-3" />
              Paid & confirmed orders
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-3xl border">
          <CardHeader className="pb-2">
            <CardDescription>Pending Orders</CardDescription>
            <CardTitle className="text-2xl font-bold">
              {summary.pending_orders}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-muted-foreground flex items-center gap-1 text-xs">
              <Clock className="size-3" />
              Awaiting payment verification
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-3xl border">
          <CardHeader className="pb-2">
            <CardDescription>Products</CardDescription>
            <CardTitle className="text-2xl font-bold">
              {summary.product_count}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-muted-foreground text-xs">In your catalog</div>
          </CardContent>
        </Card>

        <Card className="rounded-3xl border">
          <CardHeader className="pb-2">
            <CardDescription>Total Orders</CardDescription>
            <CardTitle className="text-2xl font-bold">
              {summary.order_count}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-muted-foreground text-xs">All time</div>
          </CardContent>
        </Card>
      </div>

      {summary.bestseller && (
        <Card className="rounded-3xl border">
          <CardHeader className="pb-2">
            <CardDescription>Bestseller</CardDescription>
            <CardTitle className="text-lg font-semibold">
              {String(summary.bestseller.name ?? "-")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground text-xs">
              {String(summary.bestseller.quantity ?? 0)} sold
            </p>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {nav.map(({ href, label, icon: Icon }) => (
          <Link key={href} href={href}>
            <Card className="hover:bg-muted/50 rounded-3xl border transition-colors">
              <CardContent className="flex items-center gap-4 p-6">
                <div className="bg-primary/10 text-primary flex size-10 items-center justify-center rounded-xl">
                  <Icon className="size-5" />
                </div>
                <div>
                  <p className="font-semibold">{label}</p>
                  <p className="text-muted-foreground text-xs">
                    Manage {label.toLowerCase()}
                  </p>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>


    </div>
  );
}
