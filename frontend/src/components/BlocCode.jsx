import { useEffect, useRef, useState } from "react";
import hljs from "highlight.js/lib/core";
import java from "highlight.js/lib/languages/java";
import python from "highlight.js/lib/languages/python";
import javascript from "highlight.js/lib/languages/javascript";
import xml from "highlight.js/lib/languages/xml"; // couvre aussi le HTML
import css from "highlight.js/lib/languages/css";
import sql from "highlight.js/lib/languages/sql";
import bash from "highlight.js/lib/languages/bash";
import json from "highlight.js/lib/languages/json";
import "highlight.js/styles/atom-one-dark.css";

// On n'enregistre que les langages réellement utilisés dans le projet
// (plutôt que "highlight.js" complet, ~35 Ko compressé pour ce sous-
// ensemble contre plusieurs centaines pour la totalité des langages).
// Facile à étendre : une ligne d'import + un enregistrement ci-dessous.
hljs.registerLanguage("java", java);
hljs.registerLanguage("kotlin", java); // pas de grammaire Kotlin dédiée ici, Java s'en approche suffisamment
hljs.registerLanguage("python", python);
hljs.registerLanguage("javascript", javascript);
hljs.registerLanguage("html", xml);
hljs.registerLanguage("xml", xml);
hljs.registerLanguage("css", css);
hljs.registerLanguage("sql", sql);
hljs.registerLanguage("bash", bash);
hljs.registerLanguage("shell", bash);
hljs.registerLanguage("json", json);

// Bloc de code avec coloration syntaxique et bouton "copier" — remplace le
// <pre><code> brut utilisé jusqu'ici. Le thème sombre (atom-one-dark)
// s'applique quel que soit le thème clair/sombre du site : le bloc garde
// toujours un fond terminal foncé, donc pas besoin d'un second thème pour
// le mode clair.
export default function BlocCode({ code, langage }) {
  const refCode = useRef(null);
  const [copie, setCopie] = useState(false);

  useEffect(() => {
    if (refCode.current) {
      // On retire le marquage précédent avant de re-highlighter : sinon
      // highlight.js peut refuser de re-traiter un noeud déjà marqué
      // "hljs" lors d'un changement de code (navigation entre notions).
      delete refCode.current.dataset.highlighted;
      hljs.highlightElement(refCode.current);
    }
  }, [code, langage]);

  async function copier() {
    try {
      await navigator.clipboard.writeText(code);
      setCopie(true);
      setTimeout(() => setCopie(false), 1500);
    } catch {
      // Le presse-papiers peut être inaccessible (permissions du
      // navigateur) — on échoue silencieusement plutôt que de casser
      // l'affichage pour un simple confort.
    }
  }

  const langageConnu = langage && hljs.getLanguage(langage) ? langage : undefined;

  return (
    <div className="mt-4 overflow-hidden rounded-xl border border-slate-800 shadow-sm">
      <div className="flex items-center gap-1.5 bg-slate-800 px-4 py-2">
        <span className="h-2.5 w-2.5 rounded-full bg-red-400/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-amber-400/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-emerald-400/70" />
        {langage && (
          <span className="ml-2 text-xs font-medium uppercase tracking-wide text-slate-400">
            {langage}
          </span>
        )}
        <button
          type="button"
          onClick={copier}
          className="ml-auto rounded px-2 py-0.5 text-xs font-medium text-slate-400 transition hover:bg-slate-700 hover:text-slate-200"
        >
          {copie ? "Copié !" : "Copier"}
        </button>
      </div>
      <pre className="overflow-x-auto bg-slate-900 p-4 text-sm leading-relaxed dark:bg-slate-950">
        <code ref={refCode} className={langageConnu ? `language-${langageConnu}` : undefined}>
          {code}
        </code>
      </pre>
    </div>
  );
}