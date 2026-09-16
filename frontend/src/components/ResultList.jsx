import { Link } from "react-router-dom";

// resultats/generationEchouee viennent tous les deux de GET /api/recherche.
// Depuis la fusion fiche/cours en une seule notion, TOUTE recherche sur un
// terme réel finit par renvoyer une notion — vérifiée si elle existait déjà,
// générée à la volée par l'IA sinon (et alors conservée en base). Il n'y a
// donc plus de branche séparée "réponse IA sans fiche" : un seul type de
// résultat, un seul type de page (NotionPage) vers laquelle il pointe.
export default function ResultList({ resultats, generationEchouee, terme }) {
  // resultats === null : aucune recherche n'a encore été lancée — on
  // n'affiche rien, ni message ni liste vide.
  if (resultats === null) return null;

  if (resultats.length === 0) {
    if (generationEchouee) {
      return (
        <p className="mt-8 animate-fade-in-up text-center text-slate-500 dark:text-slate-400">
          Le moteur n'a pas pu générer de contenu pour «&nbsp;{terme}&nbsp;»
          pour le moment. Réessaie dans un instant.
        </p>
      );
    }
    return (
      <p className="mt-8 animate-fade-in-up text-center text-slate-500 dark:text-slate-400">
        Aucun résultat trouvé pour «&nbsp;{terme}&nbsp;».
      </p>
    );
  }

  return (
    <ul className="mt-8 w-full max-w-2xl space-y-3">
      {resultats.map((notion, index) => (
        <li
          key={notion.id}
          className="animate-fade-in-up"
          style={{ animationDelay: `${index * 60}ms` }}
        >
          <Link
            to={`/notions/${notion.slug}`}
            className="block rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-md dark:border-slate-700 dark:bg-slate-800 dark:shadow-none dark:hover:border-brand-500"
          >
            <h3 className="font-semibold text-slate-900 dark:text-slate-100">{notion.titre}</h3>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{notion.extrait}</p>
          </Link>
        </li>
      ))}
    </ul>
  );
}