import { Link } from "react-router-dom";

export default function ResultList({ resultats, terme }) {
  // resultats === null : aucune recherche n'a encore été lancée (US01 pas
  // encore déclenchée) — on n'affiche rien, ni message ni liste vide.
  if (resultats === null) return null;

  // resultats === [] après une vraie recherche : c'est US04, un état
  // fonctionnel normal, pas une erreur.
  if (resultats.length === 0) {
    return (
      <p className="mt-8 animate-fade-in-up text-center text-slate-500 dark:text-slate-400">
        Aucun résultat trouvé pour «&nbsp;{terme}&nbsp;».
      </p>
    );
  }

  return (
    <ul className="mt-8 w-full max-w-2xl space-y-3">
      {resultats.map((fiche, index) => (
        <li
          key={fiche.id}
          className="animate-fade-in-up"
          style={{ animationDelay: `${index * 60}ms` }}
        >
          <Link
            to={`/fiches/${fiche.id}`}
            className="block rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-md dark:border-slate-700 dark:bg-slate-800 dark:shadow-none dark:hover:border-brand-500"
          >
            <h3 className="font-semibold text-slate-900 dark:text-slate-100">{fiche.titre}</h3>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{fiche.extrait}</p>
          </Link>
        </li>
      ))}
    </ul>
  );
}