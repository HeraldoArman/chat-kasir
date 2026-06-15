"use server";

import { cookies } from "next/headers";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export interface LoginInput {
  username: string;
  password: string;
}

export interface RegisterInput {
  username: string;
  full_name: string;
  whatsapp_number?: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  username: string;
  full_name: string;
  whatsapp_number: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export async function storeToken(token: string): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.set("access_token", token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24, // 1 day
  });
}

export async function getToken(): Promise<string | null> {
  const cookieStore = await cookies();
  return cookieStore.get("access_token")?.value ?? null;
}

export async function removeToken(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete("access_token");
}

export async function login(input: LoginInput): Promise<AuthResponse> {
  const formData = new URLSearchParams();
  formData.append("username", input.username);
  formData.append("password", input.password);

  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData.toString(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Login failed" }));
    throw new Error(error.detail ?? "Login failed");
  }

  const data = (await response.json()) as AuthResponse;
  await storeToken(data.access_token);
  return data;
}

export async function register(input: RegisterInput): Promise<User> {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Registration failed" }));
    throw new Error(error.detail ?? "Registration failed");
  }

  return (await response.json()) as User;
}

export async function getMe(): Promise<User | null> {
  const token = await getToken();
  if (!token) return null;

  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    await removeToken();
    return null;
  }

  return (await response.json()) as User;
}
