"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const COLUMNS = [
  { key: "considering", label: "À l'étude" },
  { key: "in_progress", label: "En préparation" },
  { key: "submitted", label: "Soumis" },
  { key: "interview", label: "Entretien" },
  { key: "accepted", label: "Accepté" },
  { key: "rejected", label: "Refusé" },
] as const;

interface Application {
  id: number;
  status: string;
  programs: { university: string; program_name: string; application_deadline: string | null };
}

export default function KanbanBoard({ userId }: { userId: string }) {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listApplications(userId)
      .then((data) => setApplications(data as Application[]))
      .finally(() => setLoading(false));
  }, [userId]);

  async function moveCard(applicationId: number, newStatus: string) {
    // Optimistic update
    setApplications((prev) =>
      prev.map((a) => (a.id === applicationId ? { ...a, status: newStatus } : a))
    );
    try {
      await api.updateApplicationStatus(applicationId, newStatus);
    } catch {
      // revert on failure
      setApplications((prev) => [...prev]);
    }
  }

  if (loading) return <p className="text-ink-soft">Chargement du suivi…</p>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {COLUMNS.map((col) => {
        const items = applications.filter((a) => a.status === col.key);
        return (
          <div key={col.key} className="bg-paper-card border border-line rounded-sm p-3 min-h-[200px]">
            <p className="font-mono text-xs uppercase tracking-wider text-ink-soft mb-3">
              {col.label} · {items.length}
            </p>
            <div className="space-y-2">
              {items.map((app) => (
                <div key={app.id} className="bg-paper border border-line rounded-stamp p-3 text-sm">
                  <p className="font-medium text-ink">{app.programs.program_name}</p>
                  <p className="text-ink-soft text-xs">{app.programs.university}</p>
                  {app.programs.application_deadline && (
                    <p className="font-mono text-[11px] text-stamp mt-1">
                      Limite : {app.programs.application_deadline}
                    </p>
                  )}
                  <select
                    value={app.status}
                    onChange={(e) => moveCard(app.id, e.target.value)}
                    className="mt-2 w-full text-xs border border-line rounded-stamp px-2 py-1 bg-paper-card"
                  >
                    {COLUMNS.map((c) => (
                      <option key={c.key} value={c.key}>
                        {c.label}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
