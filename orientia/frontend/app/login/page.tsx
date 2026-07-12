"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const { error } =
      mode === "signin"
        ? await supabase.auth.signInWithPassword({ email, password })
        : await supabase.auth.signUp({ email, password });
    setLoading(false);
    if (error) {
      setError(error.message);
      return;
    }
    router.push("/dashboard");
  }

  return (
    <div className="mx-auto max-w-md px-6 py-20">
      <span className="stamp-badge text-zellige">
        {mode === "signin" ? "Connexion" : "Créer un compte"}
      </span>
      <h1 className="font-display text-3xl text-ink mt-4 mb-8">
        {mode === "signin" ? "Content de te revoir" : "Ouvre ton dossier"}
      </h1>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm">
          Email
          <input
            required
            type="email"
            className="border border-line bg-paper-card rounded-stamp px-3 py-2"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Mot de passe
          <input
            required
            type="password"
            minLength={6}
            className="border border-line bg-paper-card rounded-stamp px-3 py-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        {error && <p className="text-stamp text-sm">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="bg-ink text-paper rounded-stamp px-6 py-3 font-medium hover:bg-ink-soft transition-colors disabled:opacity-60"
        >
          {loading ? "…" : mode === "signin" ? "Se connecter" : "Créer mon compte"}
        </button>
      </form>

      <button
        onClick={() => setMode(mode === "signin" ? "signup" : "signin")}
        className="mt-6 text-sm text-ink-soft underline"
      >
        {mode === "signin" ? "Pas encore de compte ? Inscris-toi" : "Déjà un compte ? Connecte-toi"}
      </button>
    </div>
  );
}
