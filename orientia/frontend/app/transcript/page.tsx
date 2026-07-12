"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { Loader2, UploadCloud, AlertTriangle } from "lucide-react";

const DEMO_USER_ID = "00000000-0000-0000-0000-000000000000";

interface Grade {
  subject: string;
  grade: number;
  coefficient: number | null;
  year: string | null;
}
interface WeakSpot {
  subject: string;
  issue: string;
  suggestion: string;
}

export default function TranscriptPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [grades, setGrades] = useState<Grade[] | null>(null);
  const [weakSpots, setWeakSpots] = useState<WeakSpot[] | null>(null);

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.uploadTranscript(DEMO_USER_ID, file);
      setGrades(res.grades);
      setWeakSpots(res.weak_spots);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec de l'analyse du document.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-12">
      <span className="stamp-badge text-zellige">Étape 2</span>
      <h1 className="font-display text-3xl text-ink mt-4 mb-2">Analyse ton relevé de notes</h1>
      <p className="text-ink-soft mb-8">
        Dépose ton relevé en PDF. L&apos;IA extrait tes notes et repère ce qui pourrait
        inquiéter un jury d&apos;admission — avec une suggestion concrète pour ta lettre.
      </p>

      <label className="flex flex-col items-center justify-center gap-3 border-2 border-dashed border-line rounded-sm p-10 cursor-pointer bg-paper-card hover:bg-paper transition-colors">
        <UploadCloud size={28} className="text-zellige" />
        <span className="text-sm text-ink-soft">
          {loading ? "Analyse en cours…" : "Clique pour choisir un fichier PDF"}
        </span>
        <input type="file" accept="application/pdf" className="hidden" onChange={handleFile} />
      </label>

      {loading && (
        <div className="flex items-center gap-2 text-ink-soft text-sm mt-6">
          <Loader2 className="animate-spin" size={16} /> Extraction et analyse en cours…
        </div>
      )}

      {error && (
        <div className="flex items-start gap-2 text-stamp border border-stamp rounded-stamp px-4 py-3 mt-6 text-sm">
          <AlertTriangle size={16} className="shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      {grades && (
        <div className="mt-10">
          <h2 className="font-display text-xl text-ink mb-4">Notes extraites</h2>
          <table className="w-full text-sm border border-line rounded-sm overflow-hidden">
            <thead className="bg-paper-card font-mono text-xs uppercase tracking-wider text-ink-soft">
              <tr>
                <th className="text-left px-4 py-2">Matière</th>
                <th className="text-left px-4 py-2">Note</th>
                <th className="text-left px-4 py-2">Coefficient</th>
                <th className="text-left px-4 py-2">Année</th>
              </tr>
            </thead>
            <tbody>
              {grades.map((g, i) => (
                <tr key={i} className="border-t border-line">
                  <td className="px-4 py-2">{g.subject}</td>
                  <td className="px-4 py-2">{g.grade}/20</td>
                  <td className="px-4 py-2">{g.coefficient ?? "—"}</td>
                  <td className="px-4 py-2">{g.year ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {weakSpots && weakSpots.length > 0 && (
        <div className="mt-10">
          <h2 className="font-display text-xl text-ink mb-4">Points à recontextualiser</h2>
          <div className="space-y-4">
            {weakSpots.map((w, i) => (
              <div key={i} className="bg-paper-card border border-line rounded-sm p-4">
                <p className="font-medium text-stamp text-sm">{w.subject} — {w.issue}</p>
                <p className="text-sm text-ink-soft mt-1">{w.suggestion}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
