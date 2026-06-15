"use server";

import { apiDelete, apiFetch, apiPatch, apiPost } from "./api";

export interface Store {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  category: string | null;
  whatsapp_number: string | null;
  ai_personality: string;
  custom_prompt: string | null;
  owner_id: string;
  created_at: string;
}

export interface Product {
  id: string;
  store_id: string;
  name: string;
  description: string | null;
  price: number;
  stock: number | null;
  weight: number | null;
  image_url: string | null;
  is_active: boolean;
  created_at: string;
}

export interface BankAccount {
  id: string;
  store_id: string;
  bank_name: string;
  account_number: string;
  account_holder_name: string;
  is_primary: boolean;
  created_at: string;
}

export interface Order {
  id: string;
  store_id: string;
  customer_phone: string;
  customer_name: string | null;
  total: number;
  status: string;
  items: Array<Record<string, unknown>>;
  note: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface KnowledgeEntry {
  id: string;
  store_id: string;
  category: string;
  question: string | null;
  answer: string;
  created_at: string;
}

export interface DashboardSummary {
  store_id: string;
  store_name: string;
  total_revenue: number;
  order_count: number;
  pending_orders: number;
  product_count: number;
  bestseller: Record<string, unknown> | null;
}

export async function createStore(data: {
  name: string;
  description?: string;
  category?: string;
  whatsapp_number?: string;
}): Promise<Store> {
  return apiPost<Store>("/stores", data);
}

export async function getMyStore(): Promise<Store | null> {
  try {
    return await apiFetch<Store>("/stores/me");
  } catch (error) {
    if (error instanceof Error && error.message.includes("not found")) {
      return null;
    }
    throw error;
  }
}

export async function updateStore(data: Partial<Omit<Store, "id" | "slug" | "owner_id" | "created_at">>): Promise<Store> {
  return apiPatch<Store>("/stores/me", data);
}

export async function createProduct(data: {
  name: string;
  description?: string;
  price: number;
  stock?: number;
  weight?: number;
  image_url?: string;
}): Promise<Product> {
  return apiPost<Product>("/stores/me/products", data);
}

export async function listProducts(): Promise<Product[]> {
  return apiFetch<Product[]>("/stores/me/products");
}

export async function updateProduct(
  productId: string,
  data: Partial<Omit<Product, "id" | "store_id" | "created_at">>
): Promise<Product> {
  return apiPatch<Product>(`/stores/me/products/${productId}`, data);
}

export async function deleteProduct(productId: string): Promise<void> {
  return apiDelete(`/stores/me/products/${productId}`);
}

export async function createBankAccount(data: {
  bank_name: string;
  account_number: string;
  account_holder_name: string;
  is_primary?: boolean;
}): Promise<BankAccount> {
  return apiPost<BankAccount>("/stores/me/bank-accounts", data);
}

export async function listBankAccounts(): Promise<BankAccount[]> {
  return apiFetch<BankAccount[]>("/stores/me/bank-accounts");
}

export async function updateBankAccount(
  accountId: string,
  data: Partial<Omit<BankAccount, "id" | "store_id" | "created_at">>
): Promise<BankAccount> {
  return apiPatch<BankAccount>(`/stores/me/bank-accounts/${accountId}`, data);
}

export async function deleteBankAccount(accountId: string): Promise<void> {
  return apiDelete(`/stores/me/bank-accounts/${accountId}`);
}

export async function listOrders(): Promise<Order[]> {
  return apiFetch<Order[]>("/orders/stores/me");
}

export async function verifyOrder(orderId: string): Promise<Order> {
  return apiPost<Order>(`/orders/${orderId}/verify`, {});
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return apiFetch<DashboardSummary>("/stores/me/dashboard");
}

export async function createKnowledgeEntry(data: {
  category: string;
  question?: string;
  answer: string;
}): Promise<KnowledgeEntry> {
  return apiPost<KnowledgeEntry>("/stores/me/knowledge", data);
}

export async function listKnowledge(): Promise<KnowledgeEntry[]> {
  return apiFetch<KnowledgeEntry[]>("/stores/me/knowledge");
}

export async function deleteKnowledge(entryId: string): Promise<void> {
  return apiDelete(`/stores/me/knowledge/${entryId}`);
}
