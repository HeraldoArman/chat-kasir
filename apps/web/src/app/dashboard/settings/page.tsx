"use client";

import { Loader2, Save } from "lucide-react";
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
import { Textarea } from "@chat-kasir/ui/components/textarea";

import { Button } from "@chat-kasir/ui/components/button";
import { getGowaPhone, getMyStore, updateStore, type Store } from "@/lib/store";
import { getMe, updateMe, type User } from "@/lib/auth";

export default function SettingsPage() {
  const router = useRouter();
  const [store, setStore] = useState<Store | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [gowaPhone, setGowaPhone] = useState<string | null>(null);

  const [form, setForm] = useState({
    name: "",
    description: "",
    category: "",
    whatsapp_number: "",
    ai_personality: "",
    custom_prompt: "",
  });
  const [userPhone, setUserPhone] = useState("");

  useEffect(() => {
    Promise.all([getMyStore(), getGowaPhone(), getMe()])
      .then(([storeResult, phone, userResult]) => {
        if (!storeResult) {
          router.push("/onboarding");
          return;
        }
        setStore(storeResult);
        setGowaPhone(phone);
        setUser(userResult);
        setUserPhone(userResult?.whatsapp_number ?? "");
        setForm({
          name: storeResult.name,
          description: storeResult.description ?? "",
          category: storeResult.category ?? "",
          whatsapp_number: storeResult.whatsapp_number ?? "",
          ai_personality: storeResult.ai_personality,
          custom_prompt: storeResult.custom_prompt ?? "",
        });
      })
      .catch(() => router.push("/onboarding"))
      .finally(() => setLoading(false));
  }, [router]);

  const handleChange = (field: keyof typeof form, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSaveStore = async () => {
    if (!store) return;
    setSaving(true);
    try {
      const payload: Record<string, string | null> = {};
      (Object.keys(form) as (keyof typeof form)[]).forEach((key) => {
        payload[key] = form[key] || null;
      });
      const [updated, updatedUser] = await Promise.all([
        updateStore(payload),
        updateMe({ whatsapp_number: userPhone || null }),
      ]);
      setStore(updated);
      setUser(updatedUser);
      toast.success("Settings saved!");
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to save settings",
      );
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
        <h1 className="text-3xl font-bold tracking-tight">Store Settings</h1>
        <p className="text-muted-foreground mt-1">
          Update your store information and preferences
        </p>
      </div>

      {gowaPhone && (
        <Card className="rounded-3xl border border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950">
          <CardContent className="p-4">
            <p className="text-sm font-medium text-green-800 dark:text-green-200">
              GoWA connected phone: {gowaPhone}
            </p>
            <p className="text-xs text-green-700 dark:text-green-300">
              Set your store's WhatsApp number below to match this for the bot
              to work
            </p>
          </CardContent>
        </Card>
      )}

      <Card className="rounded-3xl border">
        <CardHeader>
          <CardTitle>General</CardTitle>
          <CardDescription>
            Basic store details shown to customers
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Store Name</Label>
            <Input
              id="name"
              value={form.name}
              onChange={(e) => handleChange("name", e.target.value)}
              className="rounded-xl"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={form.description}
              onChange={(e) => handleChange("description", e.target.value)}
              className="rounded-xl"
              rows={3}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="category">Category</Label>
            <Input
              id="category"
              value={form.category}
              onChange={(e) => handleChange("category", e.target.value)}
              placeholder="e.g. Food, Fashion, Electronics"
              className="rounded-xl"
            />
          </div>
        </CardContent>
      </Card>

      <Card className="rounded-3xl border">
        <CardHeader>
          <CardTitle>WhatsApp Integration</CardTitle>
          <CardDescription>
            Set your store and personal WhatsApp numbers for the bot to work
            correctly
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {gowaPhone && (
            <div className="bg-muted rounded-2xl border p-3 text-sm">
              <span className="font-medium">GoWA device phone:</span>{" "}
              {gowaPhone}
            </div>
          )}
          <div className="space-y-2">
            <Label htmlFor="whatsapp">Store WhatsApp Number (GoWA)</Label>
            <Input
              id="whatsapp"
              value={form.whatsapp_number}
              onChange={(e) => handleChange("whatsapp_number", e.target.value)}
              placeholder={gowaPhone ?? "+62 812 3456 7890"}
              className="rounded-xl"
            />
            <p className="text-muted-foreground text-xs">
              Must match the GoWA device phone above. Customers send messages
              to this number. Set to: <strong>{gowaPhone}</strong>
            </p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="userPhone">
              Your Personal WhatsApp Number
            </Label>
            <Input
              id="userPhone"
              value={userPhone}
              onChange={(e) => setUserPhone(e.target.value)}
              placeholder="+62 812 3456 7890"
              className="rounded-xl"
            />
            <p className="text-muted-foreground text-xs">
              This is YOUR personal number. The bot will recognize you as the
              store owner when you message from this number, giving you access
              to data and admin commands.
            </p>
          </div>
        </CardContent>
      </Card>

      <Card className="rounded-3xl border">
        <CardHeader>
          <CardTitle>AI Assistant</CardTitle>
          <CardDescription>
            Configure how the AI bot interacts with your customers
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="ai_personality">AI Personality</Label>
            <Input
              id="ai_personality"
              value={form.ai_personality}
              onChange={(e) => handleChange("ai_personality", e.target.value)}
              placeholder="friendly, professional, casual"
              className="rounded-xl"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="custom_prompt">Custom Prompt</Label>
            <Textarea
              id="custom_prompt"
              value={form.custom_prompt}
              onChange={(e) => handleChange("custom_prompt", e.target.value)}
              className="rounded-xl"
              rows={4}
              placeholder="Instructions for how the AI should respond to customers..."
            />
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button
          className="rounded-full"
          onClick={handleSaveStore}
          disabled={saving}
        >
          {saving ? (
            <Loader2 className="mr-2 size-4 animate-spin" />
          ) : (
            <Save className="mr-2 size-4" />
          )}
          Save Settings
        </Button>
      </div>
    </div>
  );
}
