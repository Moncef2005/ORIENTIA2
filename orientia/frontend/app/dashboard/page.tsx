import KanbanBoard from "@/components/kanban-board";

// Replace with the authenticated user's id (supabase.auth.getSession()) once
// auth is wired up in a client component wrapper.
const DEMO_USER_ID = "00000000-0000-0000-0000-000000000000";

export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      <span className="stamp-badge text-zellige">Suivi</span>
      <h1 className="font-display text-3xl text-ink mt-4 mb-8">Mes candidatures</h1>
      <KanbanBoard userId={DEMO_USER_ID} />
    </div>
  );
}
