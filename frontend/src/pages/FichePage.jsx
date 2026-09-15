import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { obtenirFiche } from "../services/api";
import AssistantIA from "../components/AssistantIA";

export default function FichePage() {
  const { id } = useParams();

  // undefined = chargement en cours
  // null = fiche introuvable (404)
  const [fiche, setFiche] = useState(undefined);

  useEffect(() => {
    obtenirFiche(id).then(setFiche);
  }, [id]);

  if (fiche === undefined) {
    return (
      <p className="p-8 text-center text-slate-400 dark:text-slate-500">
        Chargement...
      </p>
    );
  }

  if (fiche === null) {
    return (
      <div className="animate-fade-in-up p-8 text-center">
        <p className="text-slate-500 dark:text-slate-400">
          Cette fiche n'existe pas.
        </p>

        <Link
          to="/"
          className="mt-4 inline-block text-brand-600 hover:underline dark:text-brand-500"
        >
          Retour à la recherche
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl animate-fade-in-up px-4 py-12">
      <Link
        to="/"
        className="text-sm text-brand-600 hover:underline dark:text-brand-500"
      >
        ← Nouvelle recherche
      </Link>

      <h1 className="mt-4 text-3xl font-bold text-slate-900 dark:text-slate-50">
        {fiche.titre}
      </h1>

      <p className="mt-4 text-lg leading-relaxed text-slate-700 dark:text-slate-300">
        {fiche.definition}
      </p>

      {fiche.concepts_cles?.length > 0 && (
        <section className="mt-8">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
            Concepts clés
          </h2>

          <div className="mt-2 flex flex-wrap gap-2">
            {fiche.concepts_cles.map((c) => (
              <span
                key={c}
                className="rounded-full bg-brand-50 px-3 py-1 text-sm text-brand-700 dark:bg-brand-500/10 dark:text-brand-300"
              >
                {c}
              </span>
            ))}
          </div>
        </section>
      )}

      {fiche.prerequis?.length > 0 && (
        <section className="mt-6">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
            Prérequis
          </h2>

          <ul className="mt-2 list-disc pl-5 text-slate-700 dark:text-slate-300">
            {fiche.prerequis.map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        </section>
      )}

      {fiche.pour_aller_plus_loin && (
        <section className="mt-6">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
            Pour aller plus loin
          </h2>

          <p className="mt-2 leading-relaxed text-slate-700 dark:text-slate-300">
            {fiche.pour_aller_plus_loin}
          </p>
        </section>
      )}

      {fiche.ressources?.length > 0 && (
        <section className="mt-6">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
            Ressources
          </h2>

          <ul className="mt-2 space-y-1">
            {fiche.ressources.map((r) => (
              <li key={r.url}>
                <a
                  href={r.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-brand-600 hover:underline dark:text-brand-500"
                >
                  {r.libelle}
                </a>
              </li>
            ))}
          </ul>
        </section>
      )}
      <AssistantIA ficheId={fiche.id} />
    </div>
  );
}