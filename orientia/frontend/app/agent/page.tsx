"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { Loader2, Wrench } from "lucide-react";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

// Placeholder until real auth wiring — replace with supabase.auth session user id.
const DEMO_USER_ID = "00000000-0000-0000-0000-000000000000";

export default function AgentPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Bonjour ! Je suis l'assistant OrientIA. Dis-moi sur quel programme tu travailles, et je peux vérifier la date limite, ton éligibilité, ou t'aider à rédiger ta lettre de motivation.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastTrace, setLastTrace] = useState<{ tool: string; result: string }[]>([]);

  async function send() {
    if (!input.trim() || loading) return;
    const next = [...messages, { role: "user" as const, content: input }];
    setMessages(next);
    setInput("");
    setLoading(true);
    try {
      const res = await api.chatWithAgent(DEMO_USER_ID, next);
      setMessages([...next, { role: "assistant", content: res.reply }]);
      setLastTrace(res.tool_trace);
    } catch (err) {
      setMessages([
        ...next,
        {
          role: "assistant",
          content: "Désolé, une erreur est survenue côté serveur. Réessaie dans un instant.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-12 flex flex-col h-[calc(100vh-73px)]">
      <span className="stamp-badge text-zellige mb-4 self-start">Assistant agent</span>
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`max-w-[85%] rounded-sm px-4 py-3 text-sm leading-relaxed ${
              m.role === "user"
                ? "bg-ink text-paper ml-auto"
                : "bg-paper-card border border-line text-ink"
            }`}
          >
            {m.content}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-ink-soft text-sm">
            <Loader2 className="animate-spin" size={16} /> L&apos;agent réfléchit et vérifie les faits…
          </div>
        )}
      </div>

      {lastTrace.length > 0 && (
        <div className="mb-4 text-xs font-mono text-ink-soft border border-line rounded-sm p-3 bg-paper-card">
          <div className="flex items-center gap-1 mb-1 text-zellige">
            <Wrench size={12} /> Outils utilisés
          </div>
          {lastTrace.map((t, i) => (
            <p key={i}>→ {t.tool}</p>
          ))}
        </div>
      )}

      <div className="flex gap-2">
        <input
          className="flex-1 border border-line bg-paper-card rounded-stamp px-4 py-3 text-sm"
          placeholder="Écris ton message…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <button
          onClick={send}
          disabled={loading}
          className="bg-ink text-paper rounded-stamp px-6 font-medium hover:bg-ink-soft transition-colors disabled:opacity-60"
        >
          Envoyer
        </button>
      </div>
    </div>
  );
}
