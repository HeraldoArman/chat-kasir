"use client";

import { useEffect, useState, useTransition } from "react";
import { motion } from "framer-motion";
import { Loader2, Package, Plus, Trash2 } from "lucide-react";
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
  createProduct,
  deleteProduct,
  listProducts,
  type Product,
} from "@/lib/store";

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [isPending, startTransition] = useTransition();
  const [form, setForm] = useState({
    name: "",
    description: "",
    price: "",
    stock: "",
    image_url: "",
  });

  const load = async () => {
    try {
      const data = await listProducts();
      setProducts(data);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to load products"
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
    const price = Number(form.price);
    if (!form.name.trim() || Number.isNaN(price) || price <= 0) {
      toast.error("Name and positive price are required");
      return;
    }

    startTransition(async () => {
      try {
        await createProduct({
          name: form.name,
          description: form.description || undefined,
          price,
          stock: form.stock ? Number(form.stock) : undefined,
          image_url: form.image_url || undefined,
        });
        toast.success("Product added");
        setForm({
          name: "",
          description: "",
          price: "",
          stock: "",
          image_url: "",
        });
        await load();
      } catch (error) {
        toast.error(
          error instanceof Error ? error.message : "Failed to add product"
        );
      }
    });
  };

  const handleDelete = (id: string) => {
    startTransition(async () => {
      try {
        await deleteProduct(id);
        toast.success("Product removed");
        await load();
      } catch (error) {
        toast.error(
          error instanceof Error ? error.message : "Failed to remove product"
        );
      }
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Products</h1>
        <p className="text-muted-foreground mt-1">Manage your store catalog.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="rounded-3xl border">
          <CardHeader>
            <CardTitle className="text-sm font-medium">Add product</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div className="space-y-1">
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
                  placeholder="Oli Motor Beat"
                />
              </div>
              <div className="space-y-1">
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
                <div className="space-y-1">
                  <Label htmlFor="price">Price (IDR)</Label>
                  <Input
                    id="price"
                    type="number"
                    min={1}
                    value={form.price}
                    onChange={(event) =>
                      setForm((previous) => ({
                        ...previous,
                        price: event.target.value,
                      }))
                    }
                    placeholder="50000"
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="stock">Stock</Label>
                  <Input
                    id="stock"
                    type="number"
                    min={0}
                    value={form.stock}
                    onChange={(event) =>
                      setForm((previous) => ({
                        ...previous,
                        stock: event.target.value,
                      }))
                    }
                    placeholder="10"
                  />
                </div>
              </div>
              <div className="space-y-1">
                <Label htmlFor="image_url">Image URL</Label>
                <Input
                  id="image_url"
                  value={form.image_url}
                  onChange={(event) =>
                    setForm((previous) => ({
                      ...previous,
                      image_url: event.target.value,
                    }))
                  }
                  placeholder="https://example.com/image.jpg"
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
                Add product
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="text-primary size-6 animate-spin" />
            </div>
          ) : products.length === 0 ? (
            <Card className="rounded-3xl border">
              <CardContent className="flex flex-col items-center justify-center gap-3 py-12">
                <Package className="text-muted-foreground size-10" />
                <p className="text-muted-foreground">No products yet.</p>
              </CardContent>
            </Card>
          ) : (
            products.map((product, index) => (
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
                        Rp {product.price.toLocaleString("id-ID")}
                        {product.stock !== null && ` • Stock: ${product.stock}`}
                      </p>
                    </div>
                    <Button
                      size="icon-xs"
                      variant="ghost"
                      onClick={() => handleDelete(product.id)}
                      aria-label="Delete product"
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
