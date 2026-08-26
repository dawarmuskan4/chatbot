// src/auth.ts
// Small helper module: talks to /signup and /login, and manages the token
// in sessionStorage (cleared when the tab closes — swap for localStorage
// if you want login to persist across browser restarts).

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

export async function signup(username: string, password: string): Promise<string> {
  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);

  const res = await fetch(`${API_BASE}/signup`, { method: "POST", body: formData });
  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail ?? "Signup failed");
  }
  return data.token;
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