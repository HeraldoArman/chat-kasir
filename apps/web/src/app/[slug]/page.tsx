import { notFound, redirect } from "next/navigation";

import { getPublicStore } from "@/lib/store";

export default async function PublicStorePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;

  let store;
  try {
    store = await getPublicStore(slug);
  } catch {
    notFound();
  }

  if (!store.whatsapp_number) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6 text-center">
        <div className="max-w-md space-y-2">
          <h1 className="text-2xl font-bold">{store.name}</h1>
          <p className="text-muted-foreground">
            Toko ini belum mengatur nomor WhatsApp. Silakan hubungi merchant.
          </p>
        </div>
      </div>
    );
  }

  const phone = store.whatsapp_number.replace(/\D/g, "").replace(/^0/, "62");
  const text = encodeURIComponent(`Halo, saya ingin pesan dari ${store.name}`);
  redirect(`https://wa.me/${phone}?text=${text}`);
}
