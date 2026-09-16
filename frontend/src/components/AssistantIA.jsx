import { useState } from "react";
import { poserQuestionAssistant } from "../services/api";

export default function AssistantIA({ slug }) {
  const [question, setQuestion] = useState("");
  const [reponse, setReponse] = useState(null);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState(null);

  async function poserQuestion(e) {
    e.preventDefault();
    if (!question.trim()) return;
    setEnCours(true);
    setErreur(null);
    setReponse(null);
    try {
      const resultat = await poserQuestionAssistant(slug, question);
      setReponse(resultat);
    } catch (err) {
      setErreur(err.message);
    } finally {
      setEnCours(false);
    }
  }

  return (
    <section className="mt-8 rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
        Une question sur cette notion ?
      </h2>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
        L'assistant répond uniquement à partir du contenu de cette notion —
        pas de connaissances externes.
      </p>

      <form onSubmit={poserQuestion} className="mt-3 flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ex. : pourquoi c'est plus léger qu'une VM ?"
          className="w-full rounded-lg border border-slate-200 bg-transparent px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none dark:border-slate-600 dark:text-slate-100 dark:placeholder:text-slate-500"
        />
        <button
          type="submit"
          disabled={enCours}
          className="shrink-0 rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
        >
          {enCours ? "..." : "Demander"}
        </button>
      </form>

      {erreur && (
        <p className="mt-3 animate-fade-in-up text-sm text-red-500 dark:text-red-400">
          {erreur}
        </p>
      )}

      {reponse && (
        <div className="mt-3 animate-fade-in-up rounded-lg bg-brand-50 p-3 dark:bg-brand-500/10">
          <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-200">
            {reponse.reponse}
          </p>
          <p className="mt-2 text-xs text-slate-400 dark:text-slate-500">
            Réponse basée sur : {reponse.source.titre}
          </p>
        </div>
      )}
    </section>
  );
}