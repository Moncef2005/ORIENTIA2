"use client";

import { useState } from "react";
import { api, ProgramMatch, StudentProfile } from "@/lib/api";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";

const emptyProfile: StudentProfile = {
  full_name: "",
  filiere: "",
  average_grade: 14,
  languages: ["Français"],
  target_intake: "2027-09",
  target_field: "Computer Science",
  target_countries: ["France"],
  free_text: "",
};

export default function ProgramsPage() {
  const [profile, setProfile] = useState<StudentProfile>(emptyProfile);
  const [results, setResults] = useState<ProgramMatch[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const matches = await api.matchPrograms(profile);
      setResults(matches);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Une erreur est survenue.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-12">
      <span className="stamp-badge text-zellige">Étape 1</span>
      <h1 className="font-display text-3xl text-ink mt-4 mb-2">Trouve tes programmes</h1>
      <p className="text-ink-soft mb-8 max-w-2xl">
        Décris ton profil. L&apos;IA compare tes réponses aux exigences réelles des
        programmes indexés (Campus France, Parcoursup, sites universitaires) et
        explique pourquoi chaque programme te correspond — ou pas.
      </p>

      <form onSubmit={handleSubmit} className="grid md:grid-cols-2 gap-6 bg-paper-card border border-line rounded-sm p-6 mb-10">
        <label className="flex flex-col gap-1 text-sm">
          Nom complet
          <input
            required
            className="border border-line bg-paper rounded-stamp px-3 py-2"
            value={profile.full_name}
            onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Filière actuelle
          <input
            required
            placeholder="ex: Bac SM, Prépa ECG, L2 Informatique"
            className="border border-line bg-paper rounded-stamp px-3 py-2"
            value={profile.filiere}
            onChange={(e) => setProfile({ ...profile, filiere: e.target.value })}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Moyenne générale (/20)
          <input
            required
            type="number"
            step="0.01"
            min={0}
            max={20}
            className="border border-line bg-paper rounded-stamp px-3 py-2"
            value={profile.average_grade}
            onChange={(e) => setProfile({ ...profile, average_grade: Number(e.target.value) })}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Domaine visé
          <input
            required
            className="border border-line bg-paper rounded-stamp px-3 py-2"
            value={profile.target_field}
            onChange={(e) => setProfile({ ...profile, target_field: e.target.value })}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Rentrée visée
          <input
            required
            placeholder="2027-09"
            className="border border-line bg-paper rounded-stamp px-3 py-2"
            value={profile.target_intake}
            onChange={(e) => setProfile({ ...profile, target_intake: e.target.value })}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm md:col-span-2">
          Précisions (projets, contexte, contraintes)
          <textarea
            rows={3}
            className="border border-line bg-paper rounded-stamp px-3 py-2"
            value={profile.free_text}
            onChange={(e) => setProfile({ ...profile, free_text: e.target.value })}
          />
        </label>
        <button
          type="submit"
          disabled={loading}
          className="md:col-span-2 bg-ink text-paper rounded-stamp px-6 py-3 font-medium hover:bg-ink-soft transition-colors flex items-center justify-center gap-2 disabled:opacity-60"
        >
          {loading && <Loader2 className="animate-spin" size={18} />}
          {loading ? "Analyse en cours…" : "Comparer les programmes"}
        </button>
      </form>

      {error && (
        <p className="text-stamp border border-stamp rounded-stamp px-4 py-3 mb-8">{error}</p>
      )}

      {results && (
        <div className="grid gap-5">
          {results.length === 0 && (
            <p className="text-ink-soft">Aucun programme correspondant trouvé pour ce profil.</p>
          )}
          {results.map((r) => (
            <div key={r.program_id} className="bg-paper-card border border-line rounded-sm p-6 relative">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-mono text-xs uppercase tracking-wider text-ink-soft">
                    {r.city} · {r.degree_level}
                  </p>
                  <h3 className="font-display text-xl text-ink mt-1">{r.program_name}</h3>
                  <p className="text-ink-soft text-sm">{r.university}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="font-display text-3xl text-zellige">{Math.round(r.match_score)}%</p>
                  <p className="text-xs text-ink-soft">compatibilité</p>
                </div>
              </div>
              <div className="dossier-rule my-4" />
              <p className="text-sm text-ink-soft mb-3">{r.reasoning}</p>
              <div className="flex items-center gap-2 text-sm">
                {r.eligible ? (
                  <CheckCircle2 size={16} className="text-zellige" />
                ) : (
                  <XCircle size={16} className="text-stamp" />
                )}
                <span className={r.eligible ? "text-zellige" : "text-stamp"}>
                  {r.eligibility_notes}
                </span>
              </div>
              {r.application_deadline && (
                <p className="mt-2 text-xs font-mono text-ink-soft">
                  Date limite : {r.application_deadline}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
