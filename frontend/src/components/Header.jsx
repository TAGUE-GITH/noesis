import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import LogoIcon from "./LogoIcon";

export default function Header() {
  // Préférence système par défaut, puis mémorisée dans le navigateur
  // (localStorage) une fois que l'utilisateur choisit explicitement.
  const [sombre, setSombre] = useState(() => {
    const stocke = window.localStorage.getItem("theme");
    if (stocke) return stocke === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", sombre);
    window.localStorage.setItem("theme", sombre ? "dark" : "light");
  }, [sombre]);

  return (
    <header className="flex items-center justify-between px-6 py-4">
      <Link to="/" className="flex items-center gap-2">
        <LogoIcon className="h-9 w-9" />
        <span className="text-lg font-bold text-slate-900 dark:text-slate-100">Yamia</span>
      </Link>
      <button
        onClick={() => setSombre((v) => !v)}
        aria-label="Basculer le mode sombre"
        className="rounded-full p-2 text-lg text-slate-500 transition hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
      >
        {sombre ? "☀️" : "🌙"}
      </button>
    </header>
  );
}