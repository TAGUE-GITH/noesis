import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { obtenirNotion, genererQuiz } from "../services/api";
import OngletsNotion from "../components/OngletsNotion";

// Temps accordé par question, en secondes. Un vrai exercice chronométré,
// pas un quiz sans limite : si le temps s'écoule, on passe à la question
// suivante (elle reste sans réponse, donc comptée comme fausse) — c'est ce
// qui recrée la pression d'un examen plutôt qu'un simple questionnaire.
const DUREE_QUESTION = 20;

// Seuil de réussite : un choix technique raisonnable en l'absence de
// consigne précise (ajustable facilement si besoin).
const SEUIL_REUSSITE = 0.7;

export default function ExercicesPage() {
  const { slug } = useParams();
  // undefined = chargement en cours, null = notion introuvable (404)
  const [notion, setNotion] = useState(undefined);

  // "intro" -> "chargement" -> "quiz" -> "resultat"
  const [etape, setEtape] = useState("intro");
  const [quiz, setQuiz] = useState(null);
  const [indexActuel, setIndexActuel] = useState(0);
  const [reponses, setReponses] = useState({});
  const [tempsRestant, setTempsRestant] = useState(DUREE_QUESTION);
  const [erreur, setErreur] = useState(null);

  useEffect(() => {
    obtenirNotion(slug).then(setNotion);
  }, [slug]);

  function passerQuestionSuivante() {
    setIndexActuel((i) => {
      const suivant = i + 1;
      if (!quiz || suivant >= quiz.questions.length) {
        setEtape("resultat");
        return i;
      }
      setTempsRestant(DUREE_QUESTION);
      return suivant;
    });
  }

  // Minuteur : décompte chaque seconde pendant une question ; à zéro, on
  // avance automatiquement, comme le ferait un vrai chronomètre d'examen.
  useEffect(() => {
    if (etape !== "quiz") return;
    if (tempsRestant <= 0) {
      passerQuestionSuivante();
      return;
    }
    const identifiant = setTimeout(() => setTempsRestant((t) => t - 1), 1000);
    return () => clearTimeout(identifiant);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [etape, tempsRestant, indexActuel]);

  async function demarrer() {
    setEtape("chargement");
    setErreur(null);
    try {
      const resultat = await genererQuiz(slug);
      setQuiz(resultat);
      setIndexActuel(0);
      setReponses({});
      setTempsRestant(DUREE_QUESTION);
      setEtape("quiz");
    } catch (err) {
      setErreur(err.message);
      setEtape("intro");
    }
  }

  function choisir(indexChoix) {
    setReponses((prev) => ({ ...prev, [indexActuel]: indexChoix }));
  }

  if (notion === undefined) {
    return (
      <p className="p-8 text-center text-slate-400 dark:text-slate-500">
        Chargement...
      </p>
    );
  }

  if (notion === null) {
    return (
      <div className="animate-fade-in-up p-8 text-center">
        <p className="text-slate-500 dark:text-slate-400">Cette notion n'existe pas.</p>
        <Link to="/" className="mt-4 inline-block text-brand-600 hover:underline dark:text-brand-500">
          Retour à la recherche
        </Link>
      </div>
    );
  }

  const score = quiz
    ? quiz.questions.filter((q, i) => reponses[i] === q.reponse_correcte).length
    : 0;
  const total = quiz ? quiz.questions.length : 0;
  const reussi = total > 0 && score / total >= SEUIL_REUSSITE;

  return (
    <div className="animate-fade-in-up">
      <div className="border-b border-slate-200 bg-gradient-to-b from-brand-50 to-slate-50 dark:border-slate-800 dark:from-brand-500/10 dark:to-slate-900">
        <div className="mx-auto max-w-2xl px-4 py-10">
          <Link
            to={`/notions/${slug}`}
            className="text-sm text-brand-600 hover:underline dark:text-brand-500"
          >
            ← Retour au cours
          </Link>
          <h1 className="mt-3 text-3xl font-bold text-slate-900 dark:text-slate-50 sm:text-4xl">
            Exercices — {notion.titre}
          </h1>
          <p className="mt-4 text-lg leading-relaxed text-slate-600 dark:text-slate-300">
            Teste ce que tu as retenu, dans les conditions d'un vrai exercice :
            questions chronométrées et résultat détaillé à la fin.
          </p>

          <OngletsNotion slug={slug} actif="exercices" />
        </div>
      </div>

      <div className="mx-auto max-w-2xl px-4 py-10">
        {etape === "intro" && (
          <div className="rounded-xl border border-slate-200 bg-white p-8 text-center dark:border-slate-700 dark:bg-slate-800">
            <p className="text-slate-600 dark:text-slate-300">
              {`${DUREE_QUESTION} secondes par question. Prêt·e ?`}
            </p>
            {erreur && (
              <p className="mt-3 text-sm text-red-500 dark:text-red-400">{erreur}</p>
            )}
            <button
              onClick={demarrer}
              className="mt-5 rounded-lg bg-brand-500 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600"
            >
              Commencer l'exercice
            </button>
          </div>
        )}

        {etape === "chargement" && (
          <p className="text-center text-slate-400 dark:text-slate-500">
            Préparation des questions...
          </p>
        )}

        {etape === "quiz" && quiz && (
          <div className="animate-fade-in-up">
            <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
              <span>
                Question {indexActuel + 1} / {quiz.questions.length}
              </span>
              <span
                className={`font-semibold tabular-nums ${
                  tempsRestant <= 5 ? "text-red-500 dark:text-red-400" : ""
                }`}
              >
                {tempsRestant}s
              </span>
            </div>
            {/* Barre de progression du temps restant, purement visuelle. */}
            <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
              <div
                className={`h-full rounded-full transition-all duration-1000 ease-linear ${
                  tempsRestant <= 5 ? "bg-red-500" : "bg-brand-500"
                }`}
                style={{ width: `${(tempsRestant / DUREE_QUESTION) * 100}%` }}
              />
            </div>

            <div className="mt-6 rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
              <p className="font-medium text-slate-800 dark:text-slate-100">
                {quiz.questions[indexActuel].enonce}
              </p>
              <div className="mt-4 space-y-2">
                {quiz.questions[indexActuel].choix.map((option, iChoix) => {
                  const selectionne = reponses[indexActuel] === iChoix;
                  return (
                    <button
                      key={iChoix}
                      type="button"
                      onClick={() => choisir(iChoix)}
                      className={`block w-full rounded-lg border px-4 py-2.5 text-left text-sm text-slate-700 transition dark:text-slate-200 ${
                        selectionne
                          ? "border-brand-500 bg-brand-50 dark:bg-brand-500/10"
                          : "border-slate-200 dark:border-slate-600"
                      }`}
                    >
                      {option}
                    </button>
                  );
                })}
              </div>
            </div>

            <button
              onClick={passerQuestionSuivante}
              className="mt-4 rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-600"
            >
              {indexActuel + 1 < quiz.questions.length ? "Question suivante" : "Terminer"}
            </button>
          </div>
        )}

        {etape === "resultat" && quiz && (
          <div className="animate-fade-in-up">
            <div
              className={`rounded-xl border p-6 text-center ${
                reussi
                  ? "border-emerald-200 bg-emerald-50 dark:border-emerald-500/30 dark:bg-emerald-500/10"
                  : "border-amber-200 bg-amber-50 dark:border-amber-500/30 dark:bg-amber-500/10"
              }`}
            >
              <p
                className={`text-sm font-semibold uppercase tracking-wide ${
                  reussi
                    ? "text-emerald-700 dark:text-emerald-400"
                    : "text-amber-700 dark:text-amber-400"
                }`}
              >
                {reussi ? "Réussi" : "À retravailler"}
              </p>
              <p className="mt-1 text-3xl font-bold text-slate-900 dark:text-slate-50">
                {score} / {total}
              </p>
            </div>

            <div className="mt-8 space-y-5">
              {quiz.questions.map((q, i) => {
                const bonneReponse = reponses[i] === q.reponse_correcte;
                return (
                  <div key={i}>
                    <p className="font-medium text-slate-800 dark:text-slate-100">
                      {i + 1}. {q.enonce}
                    </p>
                    <div className="mt-2 space-y-1.5">
                      {q.choix.map((option, iChoix) => {
                        let style = "border-slate-200 dark:border-slate-600";
                        if (iChoix === q.reponse_correcte) {
                          style = "border-green-500 bg-green-50 dark:bg-green-500/10";
                        } else if (iChoix === reponses[i]) {
                          style = "border-red-400 bg-red-50 dark:bg-red-500/10";
                        }
                        return (
                          <div
                            key={iChoix}
                            className={`rounded-lg border px-3 py-2 text-sm text-slate-700 dark:text-slate-200 ${style}`}
                          >
                            {option}
                          </div>
                        );
                      })}
                    </div>
                    <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-400">
                      {bonneReponse ? "✓ " : "✗ "}
                      {q.explication}
                    </p>
                  </div>
                );
              })}
            </div>

            <div className="mt-8 flex gap-3">
              <button
                onClick={demarrer}
                className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-600"
              >
                Recommencer
              </button>
              <Link
                to={`/notions/${slug}`}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-slate-300 dark:border-slate-600 dark:text-slate-300"
              >
                Retour au cours
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}