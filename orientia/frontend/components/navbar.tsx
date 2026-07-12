import Link from "next/link";

export default function Navbar() {
  const links = [
    { href: "/programs", label: "Programmes" },
    { href: "/transcript", label: "Relevé de notes" },
    { href: "/agent", label: "Assistant" },
    { href: "/dashboard", label: "Mon suivi" },
  ];

  return (
    <header className="border-b border-line bg-paper/95 backdrop-blur sticky top-0 z-30">
      <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="font-display text-xl tracking-tight text-ink">OrientIA</span>
          <span className="stamp-badge text-zellige">Dossier</span>
        </Link>
        <nav className="hidden md:flex items-center gap-8 font-mono text-xs uppercase tracking-wider text-ink-soft">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className="hover:text-stamp transition-colors">
              {l.label}
            </Link>
          ))}
        </nav>
        <Link
          href="/login"
          className="border border-ink text-ink text-sm px-4 py-1.5 rounded-stamp hover:bg-ink hover:text-paper transition-colors"
        >
          Se connecter
        </Link>
      </div>
    </header>
  );
}
