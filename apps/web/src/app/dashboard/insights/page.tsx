"use client";

import { useEffect, useState, useTransition } from "react";
import { motion } from "framer-motion";
import {
  AlertCircle,
  ArrowUpRight,
  Calendar,
  Clock,
  Loader2,
  Package,
  Receipt,
  TrendingUp,
} from "lucide-react";
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
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@chat-kasir/ui/components/tabs";

import {
  getAbandonedPayments,
  getDailySummary,
  getLowStockInventory,
  getOrders,
  getRecommendations,
  type DailySummary,
  type Order,
  type Product,
  type Recommendation,
} from "@/lib/store";

export default function InsightsPage() {
  const [activeTab, setActiveTab] = useState("orders");
  const [isPending, startTransition] = useTransition();

  // Orders state
  const [orders, setOrders] = useState<Order[]>([]);
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [customerPhone, setCustomerPhone] = useState("");

  // Abandoned state
  const [abandoned, setAbandoned] = useState<Order[]>([]);
  const [abandonedLoading, setAbandonedLoading] = useState(false);
  const [abandonedHours, setAbandonedHours] = useState("24");

  // Daily summary state
  const [dailySummary, setDailySummary] = useState<DailySummary | null>(null);
  const [dailyLoading, setDailyLoading] = useState(false);
  const [targetDate, setTargetDate] = useState(
    new Date().toISOString().split("T")[0]
  );

  // Inventory state
  const [lowStock, setLowStock] = useState<Product[]>([]);
  const [inventoryLoading, setInventoryLoading] = useState(false);
  const [threshold, setThreshold] = useState("5");

  // Recommendations state
  const [recommendation, setRecommendation] = useState<Recommendation | null>(
    null
  );
  const [recommendationLoading, setRecommendationLoading] = useState(false);
  const [recCustomerPhone, setRecCustomerPhone] = useState("");

  const loadOrders = async () => {
    setOrdersLoading(true);
    try {
      const data = await getOrders(customerPhone || undefined);
      setOrders(data);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to load orders"
      );
    } finally {
      setOrdersLoading(false);
    }
  };

  const loadAbandoned = async () => {
    setAbandonedLoading(true);
    try {
      const data = await getAbandonedPayments(Number(abandonedHours));
      setAbandoned(data);
    } catch (error) {
      toast.error(
        error instanceof Error
          ? error.message
          : "Failed to load abandoned payments"
      );
    } finally {
      setAbandonedLoading(false);
    }
  };

  const loadDailySummary = async () => {
    setDailyLoading(true);
    try {
      const data = await getDailySummary(targetDate);
      setDailySummary(data);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to load daily summary"
      );
    } finally {
      setDailyLoading(false);
    }
  };

  const loadInventory = async () => {
    setInventoryLoading(true);
    try {
      const data = await getLowStockInventory(Number(threshold));
      setLowStock(data);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to load inventory"
      );
    } finally {
      setInventoryLoading(false);
    }
  };

  const loadRecommendations = async () => {
    setRecommendationLoading(true);
    try {
      const data = await getRecommendations(recCustomerPhone || undefined);
      setRecommendation(data);
    } catch (error) {
      toast.error(
        error instanceof Error
          ? error.message
          : "Failed to load recommendations"
      );
    } finally {
      setRecommendationLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === "orders") void loadOrders();
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === "abandoned") void loadAbandoned();
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === "daily") void loadDailySummary();
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === "inventory") void loadInventory();
  }, [activeTab]);

  useEffect(() => {
    if (activeTab === "recommendations") void loadRecommendations();
  }, [activeTab]);

  const formatCurrency = (value: number) =>
    `Rp ${value.toLocaleString("id-ID")}`;

  const formatDate = (dateStr: string) =>
    new Date(dateStr).toLocaleDateString("id-ID", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Insights</h1>
        <p className="text-muted-foreground mt-1">
          Analytics and recommendations for your store.
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5 rounded-2xl">
          <TabsTrigger value="orders">Orders</TabsTrigger>
          <TabsTrigger value="abandoned">Abandoned</TabsTrigger>
          <TabsTrigger value="daily">Daily</TabsTrigger>
          <TabsTrigger value="inventory">Inventory</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
        </TabsList>

        {/* Orders Tab */}
        <TabsContent value="orders" className="mt-6">
          <Card className="rounded-3xl border">
            <CardHeader>
              <CardTitle className="text-sm font-medium">
                Filter by Customer
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-3">
                <div className="flex flex-col gap-1">
                  <Label htmlFor="customer-phone">Phone Number</Label>
                  <div className="flex gap-2">
                    <Input
                      id="customer-phone"
                      value={customerPhone}
                      onChange={(e) => setCustomerPhone(e.target.value)}
                      placeholder="+62..."
                      className="flex-1"
                    />
                    <Button
                      onClick={() =>
                        startTransition(async () => await loadOrders())
                      }
                      disabled={isPending}
                    >
                      {isPending ? (
                        <Loader2 className="size-4 animate-spin" />
                      ) : (
                        <ArrowUpRight className="size-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="mt-4 flex flex-col gap-4">
            {ordersLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="text-primary size-6 animate-spin" />
              </div>
            ) : orders.length === 0 ? (
              <Card className="rounded-3xl border">
                <CardContent className="flex flex-col items-center justify-center gap-3 py-12">
                  <Receipt className="text-muted-foreground size-10" />
                  <p className="text-muted-foreground">No orders found.</p>
                </CardContent>
              </Card>
            ) : (
              orders.map((order, index) => (
                <motion.div
                  key={order.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card className="rounded-3xl border">
                    <CardContent className="flex items-start justify-between gap-4 p-4">
                      <div className="min-w-0">
                        <p className="truncate font-semibold">
                          {order.customer_name || order.customer_phone}
                        </p>
                        <p className="text-muted-foreground text-xs">
                          {formatCurrency(order.total)} • {order.status}
                        </p>
                        <p className="text-muted-foreground mt-1 flex items-center gap-1 text-xs">
                          <Calendar className="size-3" />
                          {formatDate(order.created_at)}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))
            )}
          </div>
        </TabsContent>

        {/* Abandoned Payments Tab */}
        <TabsContent value="abandoned" className="mt-6">
          <Card className="rounded-3xl border">
            <CardHeader>
              <CardTitle className="text-sm font-medium">Time Range</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-3">
                <div className="flex flex-col gap-1">
                  <Label htmlFor="abandoned-hours">Hours</Label>
                  <div className="flex gap-2">
                    <Input
                      id="abandoned-hours"
                      type="number"
                      min={1}
                      max={168}
                      value={abandonedHours}
                      onChange={(e) => setAbandonedHours(e.target.value)}
                      className="flex-1"
                    />
                    <Button
                      onClick={() =>
                        startTransition(async () => await loadAbandoned())
                      }
                      disabled={isPending}
                    >
                      {isPending ? (
                        <Loader2 className="size-4 animate-spin" />
                      ) : (
                        <Clock className="size-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="mt-4 flex flex-col gap-4">
            {abandonedLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="text-primary size-6 animate-spin" />
              </div>
            ) : abandoned.length === 0 ? (
              <Card className="rounded-3xl border">
                <CardContent className="flex flex-col items-center justify-center gap-3 py-12">
                  <AlertCircle className="text-muted-foreground size-10" />
                  <p className="text-muted-foreground">
                    No abandoned payments.
                  </p>
                </CardContent>
              </Card>
            ) : (
              abandoned.map((order, index) => (
                <motion.div
                  key={order.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card className="rounded-3xl border">
                    <CardContent className="flex items-start justify-between gap-4 p-4">
                      <div className="min-w-0">
                        <p className="truncate font-semibold">
                          {order.customer_name || order.customer_phone}
                        </p>
                        <p className="text-muted-foreground text-xs">
                          {formatCurrency(order.total)} • Pending payment
                        </p>
                        <p className="text-muted-foreground mt-1 flex items-center gap-1 text-xs">
                          <Calendar className="size-3" />
                          {formatDate(order.created_at)}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))
            )}
          </div>
        </TabsContent>

        {/* Daily Summary Tab */}
        <TabsContent value="daily" className="mt-6">
          <Card className="rounded-3xl border">
            <CardHeader>
              <CardTitle className="text-sm font-medium">Select Date</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-3">
                <div className="flex flex-col gap-1">
                  <Label htmlFor="target-date">Date</Label>
                  <div className="flex gap-2">
                    <Input
                      id="target-date"
                      type="date"
                      value={targetDate}
                      onChange={(e) => setTargetDate(e.target.value)}
                      className="flex-1"
                    />
                    <Button
                      onClick={() =>
                        startTransition(async () => await loadDailySummary())
                      }
                      disabled={isPending}
                    >
                      {isPending ? (
                        <Loader2 className="size-4 animate-spin" />
                      ) : (
                        <Calendar className="size-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {dailyLoading ? (
            <div className="mt-4 flex items-center justify-center py-12">
              <Loader2 className="text-primary size-6 animate-spin" />
            </div>
          ) : dailySummary ? (
            <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <Card className="rounded-3xl border">
                <CardHeader className="pb-2">
                  <CardDescription>Revenue</CardDescription>
                  <CardTitle className="text-2xl font-bold">
                    {formatCurrency(dailySummary.revenue)}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card className="rounded-3xl border">
                <CardHeader className="pb-2">
                  <CardDescription>Orders</CardDescription>
                  <CardTitle className="text-2xl font-bold">
                    {dailySummary.order_count}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card className="rounded-3xl border">
                <CardHeader className="pb-2">
                  <CardDescription>Pending</CardDescription>
                  <CardTitle className="text-2xl font-bold">
                    {dailySummary.pending_orders}
                  </CardTitle>
                </CardHeader>
              </Card>
              {dailySummary.bestseller && (
                <Card className="rounded-3xl border">
                  <CardHeader className="pb-2">
                    <CardDescription>Bestseller</CardDescription>
                    <CardTitle className="text-lg font-semibold">
                      {String(dailySummary.bestseller.name ?? "-")}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground text-xs">
                      {String(dailySummary.bestseller.quantity ?? 0)} sold
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : null}
        </TabsContent>

        {/* Inventory Tab */}
        <TabsContent value="inventory" className="mt-6">
          <Card className="rounded-3xl border">
            <CardHeader>
              <CardTitle className="text-sm font-medium">
                Low Stock Threshold
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-3">
                <div className="flex flex-col gap-1">
                  <Label htmlFor="threshold">Max Stock Level</Label>
                  <div className="flex gap-2">
                    <Input
                      id="threshold"
                      type="number"
                      min={0}
                      max={100}
                      value={threshold}
                      onChange={(e) => setThreshold(e.target.value)}
                      className="flex-1"
                    />
                    <Button
                      onClick={() =>
                        startTransition(async () => await loadInventory())
                      }
                      disabled={isPending}
                    >
                      {isPending ? (
                        <Loader2 className="size-4 animate-spin" />
                      ) : (
                        <Package className="size-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="mt-4 flex flex-col gap-4">
            {inventoryLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="text-primary size-6 animate-spin" />
              </div>
            ) : lowStock.length === 0 ? (
              <Card className="rounded-3xl border">
                <CardContent className="flex flex-col items-center justify-center gap-3 py-12">
                  <Package className="text-muted-foreground size-10" />
                  <p className="text-muted-foreground">
                    All products well stocked.
                  </p>
                </CardContent>
              </Card>
            ) : (
              lowStock.map((product, index) => (
                <motion.div
                  key={product.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card className="rounded-3xl border">
                    <CardContent className="flex items-start justify-between gap-4 p-4">
                      <div className="min-w-0">
                        <p className="truncate font-semibold">{product.name}</p>
                        <p className="text-muted-foreground text-xs">
                          {formatCurrency(product.price)} • Stock:{" "}
                          {product.stock ?? 0}
                        </p>
                      </div>
                      <div className="bg-destructive/10 text-destructive rounded-full px-2 py-1 text-xs font-medium">
                        Low Stock
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))
            )}
          </div>
        </TabsContent>

        {/* Recommendations Tab */}
        <TabsContent value="recommendations" className="mt-6">
          <Card className="rounded-3xl border">
            <CardHeader>
              <CardTitle className="text-sm font-medium">
                Get Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-3">
                <div className="flex flex-col gap-1">
                  <Label htmlFor="rec-customer">Customer Phone</Label>
                  <div className="flex gap-2">
                    <Input
                      id="rec-customer"
                      value={recCustomerPhone}
                      onChange={(e) => setRecCustomerPhone(e.target.value)}
                      placeholder="+62..."
                      className="flex-1"
                    />
                    <Button
                      onClick={() =>
                        startTransition(async () => await loadRecommendations())
                      }
                      disabled={isPending}
                    >
                      {isPending ? (
                        <Loader2 className="size-4 animate-spin" />
                      ) : (
                        <TrendingUp className="size-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {recommendationLoading ? (
            <div className="mt-4 flex items-center justify-center py-12">
              <Loader2 className="text-primary size-6 animate-spin" />
            </div>
          ) : recommendation ? (
            <div className="mt-4 flex flex-col gap-4">
              <Card className="rounded-3xl border">
                <CardContent className="p-4">
                  <p className="text-muted-foreground text-sm">
                    {recommendation.reason}
                  </p>
                </CardContent>
              </Card>
              {recommendation.products.map((product, index) => (
                <motion.div
                  key={product.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card className="rounded-3xl border">
                    <CardContent className="flex items-start justify-between gap-4 p-4">
                      <div className="min-w-0">
                        <p className="truncate font-semibold">{product.name}</p>
                        <p className="text-muted-foreground text-xs">
                          {formatCurrency(product.price)}
                          {product.stock !== null &&
                            ` • Stock: ${product.stock}`}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          ) : null}
        </TabsContent>
      </Tabs>
    </div>
  );
}
