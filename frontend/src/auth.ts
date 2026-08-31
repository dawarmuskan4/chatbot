// src/auth.ts
const API_BASE = "http://localhost:8000";
const TOKEN_KEY = "chat_auth_token";
const USERNAME_KEY = "chat_username";

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function getUsername(): string | null {
  return sessionStorage.getItem(USERNAME_KEY);
}

export function setSession(token: string, username: string) {
  sessionStorage.setItem(TOKEN_KEY, token);
  sessionStorage.setItem(USERNAME_KEY, username);
}

export function clearSession() {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USERNAME_KEY);
}

export async function login(username: string, password: string): Promise<string> {
  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);

  const res = await fetch(`${API_BASE}/login`, { method: "POST", body: formData });
  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail ?? "Login failed");
  }
  return data.token;
}

// signup no longer returns a token directly — it triggers an email with a
// verification code, and the caller must then call verifyCode() to finish.
export async function signup(username: string, password: string): Promise<void> {
  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);

  const res = await fetch(`${API_BASE}/signup`, { method: "POST", body: formData });
  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail ?? "Signup failed");
  }
}

export async function verifyCode(username: string, code: string): Promise<string> {
  const formData = new FormData();
  formData.append("username", username);
  formData.append("code", code);

  const res = await fetch(`${API_BASE}/verify`, { method: "POST", body: formData });
  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail ?? "Verification failed");
  }
  return data.token;
}