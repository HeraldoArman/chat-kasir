import Link from "next/link";
import { redirect } from "next/navigation";
import type { Route } from "next";
import {
  LayoutDashboard,
  Package,
  Building2,
  Receipt,
  BarChart3,
  BookOpen,
  Percent,
  TrendingUp,
  Share2,
} from "lucide-react";

import { getMe } from "@/lib/auth";

const nav = [
  { href: "/dashboard" as Route, label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/products" as Route, label: "Products", icon: Package },
  {
    href: "/dashboard/promotions" as Route,
    label: "Promotions",
    icon: Percent,
  },
  { href: "/dashboard/insights" as Route, label: "Insights", icon: TrendingUp },
  { href: "/dashboard/bank" as Route, label: "Bank Account", icon: Building2 },
  { href: "/dashboard/orders" as Route, label: "Orders", icon: Receipt },
  {
    href: "/dashboard/analytics" as Route,
    label: "Analytics",
    icon: BarChart3,
  },
  { href: "/dashboard/knowledge" as Route, label: "Knowledge", icon: BookOpen },
  { href: "/dashboard/share" as Route, label: "Share", icon: Share2 },
];

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getMe();
  if (!user) {
    redirect("/login");
  }

  return (
    <div className="container mx-auto flex max-w-7xl flex-col gap-6 px-4 py-6 md:flex-row md:py-12">
      <aside className="w-full shrink-0 md:w-60">
        <nav className="bg-card rounded-3xl border p-3">
          <ul className="flex flex-row gap-1 overflow-x-auto md:flex-col">
            {nav.map(({ href, label, icon: Icon }) => (
              <li key={href}>
                <Link
                  href={href}
                  className="text-muted-foreground hover:text-foreground hover:bg-muted flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-medium whitespace-nowrap transition-colors"
                >
                  <Icon className="size-4" />
                  {label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </aside>
      <div className="min-w-0 flex-1">{children}</div>
    </div>
  );
}
