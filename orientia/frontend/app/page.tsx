import Link from "next/link";
import { FileCheck2, Search, MessagesSquare, KanbanSquare } from "lucide-react";

const steps = [
  {
    icon: Search,
    title: "Décris ton profil",
    body: "Filière, moyenne, langues, domaine visé. L'IA cherche parmi les programmes réellement ouverts aux étudiants marocains — pas une liste générique.",
  },
  {
    icon: FileCheck2,
    title: "Dépose ton relevé de notes",
    body: "L'IA extrait tes notes, repère ce qui pourrait inquiéter un jury, et te suggère comment le recontextualiser dans ta lettre.",
  },
  {
    icon: MessagesSquare,
    title: "Discute avec l'assistant",
    body: "Il vérifie les vraies dates limites, calcule ton éligibilité, rédige un premier brouillon de lettre — pas juste une réponse générique.",
  },
  {
    icon: KanbanSquare,
    title: "Suis chaque candidature",
    body: "Un tableau de suivi par université : en cours, soumis, entretien, réponse — pour ne rien perdre de vue entre 6 dossiers en parallèle.",
  },
];

export default function LandingPage() {
  return (
    <div className="mx-auto max-w-6xl px-6">
      {/* Hero */}
      <section className="pt-20 pb-16 grid md:grid-cols-[1.2fr_1fr] gap-12 items-center">
        <div>
          <span className="stamp-badge text-stamp mb-6">Campus France · Parcoursup · 2027</span>
          <h1 className="font-display text-5xl md:text-6xl leading-[1.05] text-ink mt-4">
            Ton dossier d&apos;études en France, tamponné par l&apos;IA avant de partir.
          </h1>
          <p className="mt-6 text-lg text-ink-soft max-w-xl">
            OrientIA lit les vraies exigences des programmes français, compare ton profil,
            repère les points faibles de ton relevé de notes, et t&apos;aide à rédiger un
            dossier qui tient la route — étape par étape, pas en un seul prompt.
          </p>
          <div className="mt-8 flex gap-4">
            <Link
              href="/programs"
              className="bg-ink text-paper px-6 py-3 rounded-stamp font-medium hover:bg-ink-soft transition-colors"
            >
              Trouver mes programmes
            </Link>
            <Link
              href="/agent"
              className="border border-ink text-ink px-6 py-3 rounded-stamp font-medium hover:bg-paper-card transition-colors"
            >
              Parler à l&apos;assistant
            </Link>
          </div>
        </div>

        {/* Signature element: a stamped "visa" card, the visual anchor of the brand */}
        <div className="relative bg-paper-card border border-line rounded-sm p-8 rotate-1 shadow-sm">
          <div className="absolute -top-4 -right-3 stamp-badge text-stamp bg-paper-card rotate-6 text-sm px-3 py-1">
            Éligible
          </div>
          <p className="font-mono text-xs uppercase tracking-wider text-ink-soft">
            Dossier Études en France
          </p>
          <p className="font-display text-2xl text-ink mt-2">
            Licence Informatique — Sorbonne Université
          </p>
          <div className="dossier-rule my-4" />
          <dl className="grid grid-cols-2 gap-y-2 text-sm">
            <dt className="text-ink-soft">Moyenne requise</dt>
            <dd className="text-ink font-medium">14.0/20</dd>
            <dt className="text-ink-soft">Date limite</dt>
            <dd className="text-ink font-medium">15 mars</dd>
            <dt className="text-ink-soft">Score de compatibilité</dt>
            <dd className="text-zellige font-medium">87 %</dd>
          </dl>
        </div>
      </section>

      {/* How it works — a real sequence, so numbering earns its place here */}
      <section className="py-16 dossier-rule">
        <h2 className="font-display text-2xl text-ink mb-10">Comment ça marche</h2>
        <div className="grid md:grid-cols-4 gap-8">
          {steps.map((step, i) => (
            <div key={step.title}>
              <div className="flex items-center gap-3 mb-3">
                <span className="font-mono text-xs text-stamp">0{i + 1}</span>
                <step.icon size={20} className="text-zellige" strokeWidth={1.75} />
              </div>
              <h3 className="font-display text-lg text-ink mb-2">{step.title}</h3>
              <p className="text-sm text-ink-soft leading-relaxed">{step.body}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
