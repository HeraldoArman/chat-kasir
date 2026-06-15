"use client";

import {
  Check,
  Copy,
  ExternalLink,
  Loader2,
  Phone,
  Share2,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@chat-kasir/ui/components/card";
import { Input } from "@chat-kasir/ui/components/input";
import { Label } from "@chat-kasir/ui/components/label";

import { Button } from "@chat-kasir/ui/components/button";
import { getMyStore, updateStore, type Store } from "@/lib/store";

export default function SharePage() {
  const router = useRouter();
  const [store, setStore] = useState<Store | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [whatsapp, setWhatsapp] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getMyStore()
      .then((result) => {
        if (!result) {
          router.push("/onboarding");
          return;
        }
        setStore(result);
        setWhatsapp(result.whatsapp_number ?? "");
      })
      .catch(() => router.push("/onboarding"))
      .finally(() => setLoading(false));
  }, [router]);

  const publicUrl = store ? `${window.location.origin}/${store.slug}` : "";

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(publicUrl);
      setCopied(true);
      toast.success("Link copied!");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Failed to copy link");
    }
  };

  const handleShareWhatsApp = () => {
    if (!store?.whatsapp_number) return;
    const phone = store.whatsapp_number.replace(/\D/g, "").replace(/^0/, "62");
    const text = encodeURIComponent(
      `Halo, saya ingin pesan dari ${store.name}`
    );
    window.open(`https://wa.me/${phone}?text=${text}`, "_blank");
  };

  const handleSaveWhatsApp = async () => {
    if (!store) return;
    setSaving(true);
    try {
      const updated = await updateStore({ whatsapp_number: whatsapp });
      setStore(updated);
      toast.success("WhatsApp number updated!");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to update");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Loader2 className="text-muted-foreground size-6 animate-spin" />
      </div>
    );
  }

  if (!store) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Share Store</h1>
        <p className="text-muted-foreground mt-1">
          Share your store link with customers
        </p>
      </div>

      {/* Store Link Card */}
      <Card className="rounded-3xl border">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="bg-primary/10 text-primary flex size-10 items-center justify-center rounded-xl">
              <Share2 className="size-5" />
            </div>
            <div>
              <CardTitle>Store Link</CardTitle>
              <CardDescription>
                Customers who visit this link will be redirected to WhatsApp
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-muted flex items-center justify-between gap-2 rounded-2xl border p-3">
            <code className="text-sm break-all">{publicUrl}</code>
            <Button
              size="sm"
              variant="outline"
              className="shrink-0 rounded-full"
              onClick={handleCopy}
            >
              {copied ? (
                <>
                  <Check className="mr-1 size-3.5" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="mr-1 size-3.5" />
                  Copy
                </>
              )}
            </Button>
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              className="rounded-full"
              onClick={() => window.open(publicUrl, "_blank")}
            >
              <ExternalLink className="mr-2 size-4" />
              Open link
            </Button>
            {store.whatsapp_number && (
              <Button
                variant="outline"
                className="rounded-full"
                onClick={handleShareWhatsApp}
              >
                <Phone className="mr-2 size-4" />
                Share to WhatsApp
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* WhatsApp Number Card */}
      <Card className="rounded-3xl border">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="bg-primary/10 text-primary flex size-10 items-center justify-center rounded-xl">
              <Phone className="size-5" />
            </div>
            <div>
              <CardTitle>WhatsApp Number</CardTitle>
              <CardDescription>
                The number customers will chat with
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="whatsapp">Phone number</Label>
            <div className="flex gap-2">
              <Input
                id="whatsapp"
                placeholder="+62 812 3456 7890"
                value={whatsapp}
                onChange={(event) => setWhatsapp(event.target.value)}
                className="rounded-xl"
              />
              <Button
                className="shrink-0 rounded-full"
                onClick={handleSaveWhatsApp}
                disabled={saving}
              >
                {saving ? <Loader2 className="size-4 animate-spin" /> : "Save"}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
