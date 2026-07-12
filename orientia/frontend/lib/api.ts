const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Erreur ${res.status}`);
  }
  return res.json();
}

export interface StudentProfile {
  full_name: string;
  filiere: string;
  average_grade: number;
  languages: string[];
  target_intake: string;
  target_field: string;
  target_countries: string[];
  budget_eur_per_year?: number;
  free_text?: string;
}

export interface ProgramMatch {
  program_id: number;
  university: string;
  program_name: string;
  city: string;
  degree_level: string;
  match_score: number;
  reasoning: string;
  application_deadline: string | null;
  eligible: boolean;
  eligibility_notes: string;
}

export const api = {
  matchPrograms: (profile: StudentProfile, top_k = 8) =>
    request<ProgramMatch[]>("/programs/match", {
      method: "POST",
      body: JSON.stringify({ profile, top_k }),
    }),

  chatWithAgent: (userId: string, messages: { role: string; content: string }[], programId?: number) =>
    request<{ reply: string; tool_trace: { tool: string; result: string }[] }>("/agent/chat", {
      method: "POST",
      body: JSON.stringify({ user_id: userId, messages, program_id: programId }),
    }),

  uploadTranscript: (userId: string, file: File) => {
    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("file", file);
    return fetch(`${API_BASE}/documents/transcript`, { method: "POST", body: formData }).then(
      async (res) => {
        if (!res.ok) throw new Error((await res.json()).detail || "Échec de l'analyse.");
        return res.json();
      }
    );
  },

  listApplications: (userId: string) => request(`/applications/${userId}`),

  createApplication: (userId: string, programId: number) =>
    request("/applications", {
      method: "POST",
      body: JSON.stringify({ user_id: userId, program_id: programId }),
    }),

  updateApplicationStatus: (applicationId: number, status: string) =>
    request(`/applications/${applicationId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),
};
