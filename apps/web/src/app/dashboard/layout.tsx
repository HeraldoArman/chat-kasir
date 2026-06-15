import Link from "next/link";
import { redirect } from "next/navigation";
import {
  LayoutDashboard,
  Package,
  Building2,
  Receipt,
  BarChart3,
  BookOpen,
} from "lucide-react";

import { getMe } from "@/lib/auth";

const nav = [
  { href: "/dashboard" as const, label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/products" as const, label: "Products", icon: Package },
  { href: "/dashboard/bank" as const, label: "Bank Account", icon: Building2 },
  { href: "/dashboard/orders" as const, label: "Orders", icon: Receipt },
  { href: "/dashboard/analytics" as const, label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/knowledge" as const, label: "Knowledge", icon: BookOpen },
] as const;

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
