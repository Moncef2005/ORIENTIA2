import type { Config } from "tailwindcss";

// Design direction: French administrative dossier meets travel/visa —
// grounded in the actual object at the center of this product: the
// "dossier Études en France" and the stamped visa that follows it.
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#EDE6D6", // dossier paper background
        "paper-card": "#F7F1E3", // slightly lighter card surface
        ink: "#1B2A4A", // passport-cover navy — primary text & chrome
        "ink-soft": "#3B4A6B",
        stamp: "#B23A2F", // stamp-ink red — the one accent, used sparingly
        zellige: "#3F6B5E", // muted teal, secondary accent
        line: "#C9BFA5", // hairline rules on paper
      },
      fontFamily: {
        display: ["var(--font-fraunces)", "serif"],
        mono: ["var(--font-ibm-plex-mono)", "monospace"],
        sans: ["var(--font-inter)", "sans-serif"],
      },
      borderRadius: {
        stamp: "2px",
      },
    },
  },
  plugins: [],
};
export default config;
