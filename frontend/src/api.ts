// src/api.ts
// Calls for conversation history — separate from auth.ts since this is a
// distinct concern (chat data vs. identity/session management).

const API_BASE = "http://localhost:8000";

export interface ConversationSummary {
    session_id: string;
    started_at: string;
    preview: string;
}

export interface StoredMessage {
    role: "user" | "assistant";
    content: string;
}

export async function fetchConversations(token: string): Promise<ConversationSummary[]> {
    const res = await fetch(`${API_BASE}/conversations`, {
        headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Failed to load conversations");
    return res.json();
}

export async function fetchConversationMessages(
    token: string,
    sessionId: string
): Promise<StoredMessage[]> {
    const res = await fetch(`${API_BASE}/conversations/${sessionId}/messages`, {
        headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Failed to load conversation");
    return res.json();
}