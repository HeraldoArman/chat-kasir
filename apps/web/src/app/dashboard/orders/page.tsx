"use client";

import { useEffect, useState, useTransition } from "react";
import { motion } from "framer-motion";
import { CheckCircle2, Loader2, Receipt } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@chat-kasir/ui/components/button";
import { Card, CardContent } from "@chat-kasir/ui/components/card";
import { listOrders, verifyOrder, type Order } from "@/lib/store";

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [isPending, startTransition] = useTransition();

  const load = async () => {
    try {
      const data = await listOrders();
      setOrders(data);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to load orders"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const handleVerify = (id: string) => {
    startTransition(async () => {
      try {
        await verifyOrder(id);
        toast.success("Payment verified");
        await load();
      } catch (error) {
        toast.error(
          error instanceof Error ? error.message : "Failed to verify"
        );
      }
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Orders</h1>
        <p className="text-muted-foreground mt-1">
          Review and verify customer payments.
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="text-primary size-6 animate-spin" />
        </div>
      ) : orders.length === 0 ? (
        <Card className="rounded-3xl border">
          <CardContent className="flex flex-col items-center justify-center gap-3 py-12">
            <Receipt className="text-muted-foreground size-10" />
            <p className="text-muted-foreground">No orders yet.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {orders.map((order, index) => (
            <motion.div
              key={order.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card className="rounded-3xl border">
                <CardContent className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold">
                        Order #{order.id.slice(0, 8)}
                      </p>
                      <span
                        className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                          order.status === "confirmed"
                            ? "bg-green-100 text-green-700"
                            : order.status === "pending_payment"
                              ? "bg-amber-100 text-amber-700"
                              : "bg-muted text-muted-foreground"
                        }`}
                      >
                        {order.status}
                      </span>
                    </div>
                    <p className="text-muted-foreground text-sm">
                      {order.customer_name || order.customer_phone}
                    </p>
                    <p className="text-muted-foreground text-xs">
                      {order.items.length} item(s) • Rp{" "}
                      {order.total.toLocaleString("id-ID")}
                    </p>
                  </div>
                  <div className="flex shrink-0 items-center gap-3">
                    {order.status === "pending_payment" && (
                      <Button
                        size="sm"
                        className="rounded-full"
                        disabled={isPending}
                        onClick={() => handleVerify(order.id)}
                      >
                        <CheckCircle2 className="mr-1.5 size-3.5" />
                        Verify payment
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
