// src/AuthScreen.tsx
import { useState } from "react";
import { login, signup } from "./auth";

interface AuthScreenProps {
    onAuthenticated: (token: string, username: string) => void;
}

export default function AuthScreen({ onAuthenticated }: AuthScreenProps) {
    const [mode, setMode] = useState<"login" | "signup">("login");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            const token = mode === "login"
                ? await login(username, password)
                : await signup(username, password);
            onAuthenticated(token, username);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Something went wrong");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div style={styles.page}>
            <form onSubmit={handleSubmit} style={styles.card}>
                <div style={styles.logo}>Q</div>
                <h1 style={styles.title}>
                    {mode === "login" ? "Welcome back" : "Create your account"}
                </h1>

                <input
                    type="text"
                    placeholder="Username"
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
                        onClick={() => {
                            setMode(mode === "login" ? "signup" : "login");
                            setError("");
                        }}
                    >
                        {mode === "login" ? "Sign up" : "Log in"}
                    </span>
                </div>
            </form>
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
        marginBottom: 4,
    },
    title: { fontSize: 20, fontWeight: 700, color: "#1f2937", margin: 0 },
    input: {
        width: "100%",
        padding: "11px 14px",
        borderRadius: 12,
        border: "1px solid rgba(0,0,0,0.1)",
        fontSize: 14,
        outline: "none",
        boxSizing: "border-box",
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
};