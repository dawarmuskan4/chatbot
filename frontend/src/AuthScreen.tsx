// src/AuthScreen.tsx
import { useState } from "react";
import { login, signup, verifyCode, resendCode } from "./auth";

interface AuthScreenProps {
  onAuthenticated: (token: string, username: string) => void;
}

type Mode = "login" | "signup" | "verify";

export default function AuthScreen({ onAuthenticated }: AuthScreenProps) {
  const [mode, setMode] = useState<Mode>("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  async function handleLoginOrSignup(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setInfo("");
    setLoading(true);

    try {
      if (mode === "login") {
        const token = await login(username, password);
        onAuthenticated(token, username);
      } else {
        await signup(username, password);
        setInfo(`We sent a verification code to ${username}. Enter it below.`);
        setMode("verify");
        startResendCooldown();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function handleVerify(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const token = await verifyCode(username, code);
      onAuthenticated(token, username);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Verification failed");
    } finally {
      setLoading(false);
    }
  }

  function startResendCooldown() {
    setResendCooldown(30);
    const interval = setInterval(() => {
      setResendCooldown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }

  async function handleResend() {
    if (resendCooldown > 0 || resending) return;
    setError("");
    setResending(true);

    try {
      await resendCode(username);
      setInfo(`A new code was sent to ${username}.`);
      setCode("");
      startResendCooldown();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not resend code");
    } finally {
      setResending(false);
    }
  }

  function switchMode(newMode: Mode) {
    setMode(newMode);
    setError("");
    setInfo("");
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logo}>Q</div>

        {mode !== "verify" ? (
          <form onSubmit={handleLoginOrSignup} style={styles.form}>
            <h1 style={styles.title}>
              {mode === "login" ? "Welcome back" : "Create your account"}
            </h1>

            <input
              type="text"
              placeholder="Username or email"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={styles.input}
              autoComplete="username"
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={styles.input}
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              required
            />

            {error && <div style={styles.error}>{error}</div>}

            <button type="submit" disabled={loading} style={styles.submitButton}>
              {loading ? "Please wait..." : mode === "login" ? "Log In" : "Sign Up"}
            </button>

            <div style={styles.switchRow}>
              {mode === "login" ? "Don't have an account?" : "Already have an account?"}{" "}
              <span
                style={styles.switchLink}
                onClick={() => switchMode(mode === "login" ? "signup" : "login")}
              >
                {mode === "login" ? "Sign up" : "Log in"}
              </span>
            </div>
          </form>
        ) : (
          <form onSubmit={handleVerify} style={styles.form}>
            <h1 style={styles.title}>Check your email</h1>
            {info && <div style={styles.info}>{info}</div>}

            <input
              type="text"
              placeholder="6-digit code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              style={{ ...styles.input, textAlign: "center", letterSpacing: 4, fontSize: 18 }}
              maxLength={6}
              inputMode="numeric"
              autoFocus
              required
            />

            {error && <div style={styles.error}>{error}</div>}

            <button type="submit" disabled={loading} style={styles.submitButton}>
              {loading ? "Verifying..." : "Verify & Continue"}
            </button>

            <div style={styles.switchRow}>
              Didn't get it?{" "}
              <span
                style={{
                  ...styles.switchLink,
                  ...(resendCooldown > 0 || resending ? styles.switchLinkDisabled : {}),
                }}
                onClick={handleResend}
              >
                {resending
                  ? "Sending..."
                  : resendCooldown > 0
                    ? `Resend in ${resendCooldown}s`
                    : "Resend code"}
              </span>
            </div>

            <div style={styles.switchRow}>
              Wrong email?{" "}
              <span style={styles.switchLink} onClick={() => switchMode("signup")}>
                Go back
              </span>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  page: {
    width: "100vw",
    height: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background:
      "radial-gradient(circle at 30% 20%, #fdf2f8 0%, #f5f3ff 35%, #eff6ff 65%, #ecfeff 100%)",
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  card: {
    width: 340,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 14,
    background: "rgba(255,255,255,0.85)",
    border: "1px solid rgba(165,180,252,0.4)",
    borderRadius: 24,
    padding: "36px 32px",
    boxShadow: "0 20px 60px rgba(165,180,252,0.25)",
  },
  form: { width: "100%", display: "flex", flexDirection: "column", alignItems: "center", gap: 14 },
  logo: {
    width: 44,
    height: 44,
    borderRadius: 14,
    background: "linear-gradient(135deg, #f0abfc, #a5b4fc, #67e8f9)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#fff",
    fontWeight: 700,
    fontSize: 18,
  },
  title: { fontSize: 20, fontWeight: 700, color: "#1f2937", margin: 0, textAlign: "center" },
  input: {
    width: "100%",
    padding: "11px 14px",
    borderRadius: 12,
    border: "1px solid rgba(0,0,0,0.1)",
    fontSize: 14,
    outline: "none",
    boxSizing: "border-box",
  },
  info: {
    fontSize: 13,
    color: "#4b5563",
    background: "rgba(165,180,252,0.12)",
    borderRadius: 8,
    padding: "10px 12px",
    width: "100%",
    boxSizing: "border-box",
    textAlign: "center",
    lineHeight: 1.4,
  },
  error: {
    fontSize: 13,
    color: "#dc2626",
    background: "rgba(220,38,38,0.08)",
    borderRadius: 8,
    padding: "8px 12px",
    width: "100%",
    boxSizing: "border-box",
    textAlign: "center",
  },
  submitButton: {
    width: "100%",
    padding: "11px 0",
    borderRadius: 999,
    border: "none",
    background: "linear-gradient(135deg, #f0abfc, #a78bfa)",
    color: "#fff",
    fontWeight: 600,
    fontSize: 14,
    cursor: "pointer",
  },
  switchRow: { fontSize: 13, color: "#6b7280" },
  switchLink: { color: "#7c3aed", fontWeight: 600, cursor: "pointer" },
  switchLinkDisabled: { color: "#c4b5fd", cursor: "default" },
};