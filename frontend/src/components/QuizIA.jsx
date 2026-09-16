import { useState } from "react";
import { genererQuiz } from "../services/api";

export default function QuizIA({ slug }) {
  const [quiz, setQuiz] = useState(null);
  const [reponses, setReponses] = useState({});
  const [corrige, setCorrige] = useState(false);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState(null);

  async function lancerQuiz() {
    setEnCours(true);
    setErreur(null);
    setQuiz(null);
    setReponses({});
    setCorrige(false);
    try {
      const resultat = await genererQuiz(slug);
      setQuiz(resultat);
    } catch (err) {
      setErreur(err.message);
    } finally {
      setEnCours(false);
    }
  }

  function choisir(indexQuestion, indexChoix) {
    if (corrige) return;
    setReponses((prev) => ({ ...prev, [indexQuestion]: indexChoix }));
  }

  const toutesRepondues =
    quiz && quiz.questions.every((_, i) => reponses[i] !== undefined);
  const score = quiz
    ? quiz.questions.filter((q, i) => reponses[i] === q.reponse_correcte).length
    : 0;

  return (
    <section className="mt-8 rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
        Tester ma compréhension
      </h2>
      <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
        Un petit quiz généré à partir de ce contenu, pour vérifier ce que tu
        as retenu.
      </p>

      {!quiz && (
        <button
          onClick={lancerQuiz}
          disabled={enCours}
          className="mt-3 rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
        >
          {enCours ? "Génération..." : "Générer un quiz"}
        </button>
      )}

      {erreur && (
        <p className="mt-3 animate-fade-in-up text-sm text-red-500 dark:text-red-400">
          {erreur}
        </p>
      )}

      {quiz && (
        <div className="mt-4 animate-fade-in-up space-y-5">
          {quiz.questions.map((q, iQuestion) => {
            const choisi = reponses[iQuestion];
            return (
              <div key={iQuestion}>
                <p className="font-medium text-slate-800 dark:text-slate-100">
                  {iQuestion + 1}. {q.enonce}
                </p>
                <div className="mt-2 space-y-1.5">
                  {q.choix.map((option, iChoix) => {
                    let style = "border-slate-200 dark:border-slate-600";
                    if (corrige) {
                      if (iChoix === q.reponse_correcte) {
                        style =
                          "border-green-500 bg-green-50 dark:bg-green-500/10";
                      } else if (iChoix === choisi) {
                        style = "border-red-400 bg-red-50 dark:bg-red-500/10";
                      }
                    } else if (choisi === iChoix) {
                      style = "border-brand-500 bg-brand-50 dark:bg-brand-500/10";
                    }
                    return (
                      <button
                        key={iChoix}
                        type="button"
                        onClick={() => choisir(iQuestion, iChoix)}
                        disabled={corrige}
                        className={`block w-full rounded-lg border px-3 py-2 text-left text-sm text-slate-700 transition dark:text-slate-200 ${style}`}
                      >
                        {option}
                      </button>
                    );
                  })}
                </div>
                {corrige && (
                  <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-400">
                    {q.explication}
                  </p>
                )}
              </div>
            );
          })}

          {!corrige && (
            <button
              onClick={() => setCorrige(true)}
              disabled={!toutesRepondues}
              className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
            >
              Valider mes réponses
            </button>
          )}

          {corrige && (
            <p className="text-sm font-medium text-slate-700 dark:text-slate-200">
              Score : {score} / {quiz.questions.length}
            </p>
          )}
        </div>
      )}
    </section>
  );
}