import { redirect } from "next/navigation";

import { Button } from "@chat-kasir/ui/components/button";
import { Card, CardContent, CardHeader, CardTitle } from "@chat-kasir/ui/components/card";
import { getMe, removeToken } from "@/lib/auth";

export default async function DashboardPage() {
  const user = await getMe();
  if (!user) {
    redirect("/login");
  }

  async function handleLogout() {
    "use server";
    await removeToken();
    redirect("/");
  }

  return (
    <main className="container mx-auto max-w-7xl px-4 py-12">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Welcome back, {user.full_name ?? user.username}
          </p>
        </div>
        <form action={handleLogout}>
          <Button variant="outline" type="submit">Log out</Button>
        </form>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="rounded-3xl border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Store</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground text-sm">
              Your WhatsApp storefront and catalog settings will appear here.
            </p>
          </CardContent>
        </Card>

        <Card className="rounded-3xl border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Orders</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground text-sm">
              Recent customer orders and payment confirmations.
            </p>
          </CardContent>
        </Card>

        <Card className="rounded-3xl border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Analytics</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground text-sm">
              Sales summary and conversation metrics.
            </p>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
