"use client";

import { useEffect, useState, useTransition } from "react";
import { motion } from "framer-motion";
import { Building2, Loader2, Plus, Trash2 } from "lucide-react";
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
  createBankAccount,
  deleteBankAccount,
  listBankAccounts,
  type BankAccount,
} from "@/lib/store";

export default function BankPage() {
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [isPending, startTransition] = useTransition();
  const [form, setForm] = useState({
    bank_name: "",
    account_number: "",
    account_holder_name: "",
    is_primary: false,
  });

  const load = async () => {
    try {
      const data = await listBankAccounts();
      setAccounts(data);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to load accounts");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.bank_name.trim() || !form.account_number.trim() || !form.account_holder_name.trim()) {
      toast.error("All bank fields are required");
      return;
    }

    startTransition(async () => {
      try {
        await createBankAccount(form);
        toast.success("Bank account added");
        setForm({
          bank_name: "",
          account_number: "",
          account_holder_name: "",
          is_primary: false,
        });
        await load();
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "Failed to add account");
      }
    });
  };

  const handleDelete = (id: string) => {
    startTransition(async () => {
      try {
        await deleteBankAccount(id);
        toast.success("Account removed");
        await load();
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "Failed to remove account");
      }
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Bank Account</h1>
        <p className="text-muted-foreground mt-1">
          Customers will transfer to this account.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="rounded-3xl border">
          <CardHeader>
            <CardTitle className="text-sm font-medium">Add bank account</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div className="space-y-1">
                <Label htmlFor="bank_name">Bank name</Label>
                <Input
                  id="bank_name"
                  value={form.bank_name}
                  onChange={(event) =>
                    setForm((previous) => ({ ...previous, bank_name: event.target.value }))
                  }
                  placeholder="BCA"
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="account_number">Account number</Label>
                <Input
                  id="account_number"
                  value={form.account_number}
                  onChange={(event) =>
                    setForm((previous) => ({
                      ...previous,
                      account_number: event.target.value,
                    }))
                  }
                  placeholder="1234567890"
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="account_holder_name">Account holder name</Label>
                <Input
                  id="account_holder_name"
                  value={form.account_holder_name}
                  onChange={(event) =>
                    setForm((previous) => ({
                      ...previous,
                      account_holder_name: event.target.value,
                    }))
                  }
                  placeholder="Budi Santoso"
                />
              </div>
              <Button type="submit" className="w-full rounded-full" disabled={isPending}>
                {isPending ? (
                  <Loader2 className="mr-2 size-4 animate-spin" />
                ) : (
                  <Plus className="mr-2 size-4" />
                )}
                Add account
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="text-primary size-6 animate-spin" />
            </div>
          ) : accounts.length === 0 ? (
            <Card className="rounded-3xl border">
              <CardContent className="flex flex-col items-center justify-center gap-3 py-12">
                <Building2 className="text-muted-foreground size-10" />
                <p className="text-muted-foreground">No bank accounts yet.</p>
              </CardContent>
            </Card>
          ) : (
            accounts.map((account, index) => (
              <motion.div
                key={account.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className="rounded-3xl border">
                  <CardContent className="flex items-start justify-between gap-4 p-4">
                    <div className="min-w-0">
                      <p className="truncate font-semibold">
                        {account.bank_name}
                        {account.is_primary && (
                          <span className="bg-primary/10 text-primary ml-2 rounded-full px-2 py-0.5 text-[10px]">
                            Primary
                          </span>
                        )}
                      </p>
                      <p className="text-muted-foreground text-xs">
                        {account.account_number}
                      </p>
                      <p className="text-muted-foreground text-xs">
                        {account.account_holder_name}
                      </p>
                    </div>
                    <Button
                      size="icon-xs"
                      variant="ghost"
                      onClick={() => handleDelete(account.id)}
                      aria-label="Delete account"
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
