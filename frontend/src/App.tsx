import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  text: string;
}

const API_URL = "http://localhost:8000/ask-llm";

const SUGGESTIONS = [
  { label: "Summarize", icon: "◈" },
  { label: "Key Numbers", icon: "◎" },
  { label: "Ask About Data", icon: "▤" },
  { label: "Explain This", icon: "✦" },
];

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  // Global reset — makes the gradient fill the ENTIRE browser viewport,
  // overriding Vite's default index.css (which sets a dark body background
  // in dark-mode browsers) and default html/body margins.
  useEffect(() => {
    const style = document.createElement("style");
    style.textContent = `
      html, body, #root {
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at 30% 20%, #fdf2f8 0%, #f5f3ff 35%, #eff6ff 65%, #ecfeff 100%);
      }
    `;
    document.head.appendChild(style);
    return () => { document.head.removeChild(style); };
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  async function sendQuery(overrideText?: string) {
    const queryText = overrideText ?? input;
    if (!queryText.trim() || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: queryText }]);
    setLoading(true);

    const formData = new FormData();
    formData.append("user_query", queryText);
    if (file) formData.append("file", file);

    try {
      const response = await fetch(API_URL, { method: "POST", body: formData });
      if (!response.ok) throw new Error(`Request failed: ${response.status}`);
      const data = await response.json();
      setMessages((prev) => [...prev, { role: "assistant", text: data.answer }]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
      setInput("");
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendQuery();
    }
  }

  const hasMessages = messages.length > 0;

  return (
    <div style={styles.page}>
      {/* sidebar */}
      <div style={styles.sidebar}>
        <div style={styles.logo}>Q</div>
        <div style={styles.sidebarIcons}>
          <div style={{ ...styles.sidebarIcon, ...styles.sidebarIconActive }}>✦</div>
          <div style={styles.sidebarIcon}>◈</div>
          <div style={styles.sidebarIcon}>⚙</div>
        </div>
        <div style={styles.sidebarIcon}>⏻</div>
      </div>

      {/* main */}
      <div style={styles.main}>
        <div style={styles.topBar}>
          <div style={styles.pill}>+ &nbsp;Attach Document</div>
        </div>

        {!hasMessages ? (
          <div style={styles.hero}>
            <h1 style={styles.heroTitle}>
              <span style={styles.heroTitleMuted}>Ask Anything, </span>
              <span style={styles.heroTitleBold}>Get Real Answers</span>
              <br />
              <span style={styles.heroTitleBold}>From Your Data</span>
            </h1>

            <div style={styles.suggestionRow}>
              {SUGGESTIONS.map((s) => (
                <button
                  key={s.label}
                  style={styles.suggestionChip}
                  onClick={() => sendQuery(s.label)}
                >
                  <span style={{ marginRight: 6 }}>{s.icon}</span>
                  {s.label}
                </button>
              ))}
              <button style={styles.moreChip}>•••</button>
            </div>
          </div>
        ) : (
          <div style={styles.messageList} ref={scrollRef}>
            {messages.map((msg, i) => (
              <div
                key={i}
                style={{
                  ...styles.messageRow,
                  justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                }}
              >
                <div
                  style={{
                    ...styles.messageBubble,
                    ...(msg.role === "user" ? styles.userBubble : styles.assistantBubble),
                  }}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            {loading && (
              <div style={{ ...styles.messageRow, justifyContent: "flex-start" }}>
                <div style={{ ...styles.messageBubble, ...styles.assistantBubble }}>
                  <span style={styles.thinkingDots}>Thinking</span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* input bar */}
        <div style={styles.inputBarWrap}>
          <div style={styles.inputBar}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me anything about your document..."
              style={styles.textInput}
              disabled={loading}
            />
            <div style={styles.inputBarActions}>
              <label style={styles.attachChip}>
                🔗 Attach
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                  style={{ display: "none" }}
                />
              </label>
              <button
                style={{ ...styles.sendChip, opacity: loading ? 0.6 : 1 }}
                onClick={() => sendQuery()}
                disabled={loading}
              >
                ➤ Send
              </button>
            </div>
          </div>
          {file && <div style={styles.fileNote}>📎 {file.name}</div>}
        </div>
      </div>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  page: {
    width: "100vw",
    height: "100vh",
    display: "flex",
    background:
      "radial-gradient(circle at 30% 20%, #fdf2f8 0%, #f5f3ff 35%, #eff6ff 65%, #ecfeff 100%)",
    fontFamily:
      "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    boxSizing: "border-box",
  },
  sidebar: {
    width: 76,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "24px 0",
    borderRight: "1px solid rgba(0,0,0,0.05)",
  },
  logo: {
    width: 36,
    height: 36,
    borderRadius: 12,
    background: "linear-gradient(135deg, #f0abfc, #a5b4fc, #67e8f9)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#fff",
    fontWeight: 700,
    fontSize: 16,
  },
  sidebarIcons: { display: "flex", flexDirection: "column", gap: 20 },
  sidebarIcon: {
    width: 40,
    height: 40,
    borderRadius: 12,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#9ca3af",
    fontSize: 16,
    cursor: "pointer",
  },
  sidebarIconActive: {
    background: "linear-gradient(135deg, rgba(240,171,252,0.25), rgba(165,180,252,0.25))",
    color: "#7c3aed",
  },
  main: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    padding: "24px 48px",
    minWidth: 0,
  },
  topBar: { display: "flex", justifyContent: "flex-end" },
  pill: {
    fontSize: 13,
    color: "#6b7280",
    background: "rgba(255,255,255,0.7)",
    border: "1px solid rgba(0,0,0,0.06)",
    borderRadius: 999,
    padding: "8px 16px",
  },
  hero: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    textAlign: "center",
    gap: 40,
  },
  heroTitle: { fontSize: 42, lineHeight: 1.25, margin: 0, fontWeight: 700 },
  heroTitleMuted: { color: "#c4b5fd" },
  heroTitleBold: { color: "#1f2937" },
  suggestionRow: { display: "flex", gap: 10, flexWrap: "wrap", justifyContent: "center" },
  suggestionChip: {
    fontSize: 13,
    color: "#4b5563",
    background: "rgba(255,255,255,0.8)",
    border: "1px solid rgba(0,0,0,0.06)",
    borderRadius: 999,
    padding: "9px 16px",
    cursor: "pointer",
  },
  moreChip: {
    fontSize: 13,
    color: "#9ca3af",
    background: "rgba(255,255,255,0.8)",
    border: "1px solid rgba(0,0,0,0.06)",
    borderRadius: 999,
    width: 38,
    cursor: "pointer",
  },
  messageList: {
    flex: 1,
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: 12,
    padding: "12px 4px",
  },
  messageRow: { display: "flex", width: "100%" },
  messageBubble: {
    maxWidth: "72%",
    padding: "12px 16px",
    borderRadius: 18,
    fontSize: 14.5,
    lineHeight: 1.5,
    whiteSpace: "pre-wrap",
  },
  userBubble: {
    background: "linear-gradient(135deg, #f0abfc, #a5b4fc)",
    color: "#fff",
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    background: "rgba(255,255,255,0.85)",
    color: "#1f2937",
    border: "1px solid rgba(0,0,0,0.05)",
    borderBottomLeftRadius: 4,
  },
  thinkingDots: { color: "#9ca3af", fontStyle: "italic" },
  inputBarWrap: { marginTop: 16 },
  inputBar: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    background: "rgba(255,255,255,0.85)",
    border: "1px solid rgba(165,180,252,0.4)",
    borderRadius: 20,
    padding: "10px 12px 10px 20px",
    boxShadow: "0 8px 30px rgba(165,180,252,0.25)",
  },
  textInput: {
    flex: 1,
    border: "none",
    outline: "none",
    background: "transparent",
    fontSize: 14.5,
    color: "#1f2937",
  },
  inputBarActions: { display: "flex", gap: 8, alignItems: "center" },
  attachChip: {
    fontSize: 13,
    color: "#6b7280",
    background: "rgba(0,0,0,0.03)",
    borderRadius: 999,
    padding: "8px 14px",
    cursor: "pointer",
    whiteSpace: "nowrap",
  },
  sendChip: {
    fontSize: 13,
    fontWeight: 600,
    color: "#fff",
    background: "linear-gradient(135deg, #f0abfc, #a78bfa)",
    border: "none",
    borderRadius: 999,
    padding: "10px 20px",
    cursor: "pointer",
    whiteSpace: "nowrap",
  },
  fileNote: { marginTop: 8, fontSize: 12, color: "#8b5cf6", paddingLeft: 8 },
};