import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { obtenirNotion } from "../services/api";
import AssistantIA from "../components/AssistantIA";
import OngletsNotion from "../components/OngletsNotion";
import BlocCode from "../components/BlocCode";
import BlocDiagramme from "../components/BlocDiagramme";

// Style visuel par type de bloc : chaque type de contenu pédagogique a son
// propre traitement (couleur, libellé) pour que l'oeil distingue tout de
// suite une analogie d'une définition, ou un point à retenir d'une erreur
// fréquente — plutôt que tout afficher de façon identique.
const STYLE_PAR_TYPE = {
  analogie: {
    libelle: "Analogie",
    classe:
      "border-purple-200 bg-purple-50 dark:border-purple-500/30 dark:bg-purple-500/10",
    classeLibelle: "text-purple-700 dark:text-purple-400",
  },
  a_retenir: {
    libelle: "À retenir",
    classe:
      "border-brand-200 bg-brand-50 dark:border-brand-500/30 dark:bg-brand-500/10",
    classeLibelle: "text-brand-700 dark:text-brand-400",
  },
  erreur_frequente: {
    libelle: "Erreur fréquente",
    classe:
      "border-red-200 bg-red-50 dark:border-red-500/30 dark:bg-red-500/10",
    classeLibelle: "text-red-700 dark:text-red-400",
  },

    test: {
    libelle: "Teste-toi",
    classe:
      "border-teal-200 bg-teal-50 dark:border-teal-500/30 dark:bg-teal-500/10",
    classeLibelle: "text-teal-700 dark:text-teal-400",
  },
  amusement: {
    libelle: "Le sais-tu ?",
    classe:
      "border-pink-200 bg-pink-50 dark:border-pink-500/30 dark:bg-pink-500/10",
    classeLibelle: "text-pink-700 dark:text-pink-400",
  },
};

export default function NotionPage() {
  const { slug } = useParams();
  // undefined = chargement en cours, null = notion introuvable (404)
  const [notion, setNotion] = useState(undefined);

  useEffect(() => {
    setNotion(undefined);
    obtenirNotion(slug).then(setNotion);
  }, [slug]);

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

  const verifiee = notion.origine === "verifiee";

  return (
    <div className="animate-fade-in-up">
      {/* Bandeau d'en-tête : dégradé de marque, identité visuelle commune à
          toutes les notions, vérifiées ou générées par l'IA. */}
      <div className="border-b border-slate-200 bg-gradient-to-b from-brand-50 to-slate-50 dark:border-slate-800 dark:from-brand-500/10 dark:to-slate-900">
        <div className="mx-auto max-w-2xl px-4 py-10">
          <Link to="/" className="text-sm text-brand-600 hover:underline dark:text-brand-500">
            ← Nouvelle recherche
          </Link>

          <p
            className={`mt-4 inline-block rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide ${
              verifiee
                ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400"
                : "bg-amber-100 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400"
            }`}
          >
            {verifiee ? "Notion vérifiée par Yamia" : "Générée par l'IA — pas encore vérifiée par Yamia"}
          </p>
          <h1 className="mt-3 text-3xl font-bold text-slate-900 dark:text-slate-50 sm:text-4xl">
            {notion.titre}
          </h1>
          <p className="mt-4 text-lg leading-relaxed text-slate-600 dark:text-slate-300">
            {notion.resume}
          </p>

          {/* Onglets Cours/Exercices : la lecture et l'entraînement sont
              désormais deux pages distinctes, comme sur une vraie
              plateforme d'apprentissage, plutôt qu'un quiz empilé en bas
              du cours. */}
          <OngletsNotion slug={notion.slug} actif="cours" />
        </div>
      </div>

      <div className="mx-auto max-w-2xl px-4 py-10">
        {notion.contenu.length > 1 && (
          <nav className="mb-10 rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
              Au sommaire
            </p>
            <ol className="mt-2 space-y-1">
              {notion.contenu.map((bloc, index) => (
                <li key={index}>
                  
                  <a
                    href={`#bloc-${index}`}
                    className="text-sm text-slate-600 transition hover:text-brand-600 dark:text-slate-300 dark:hover:text-brand-400"
                  >
                    {index + 1}. {bloc.titre}
                  </a>
                </li>
              ))}
            </ol>
          </nav>
        )}

        {notion.contenu.map((bloc, index) => {
          const style = STYLE_PAR_TYPE[bloc.type];
          return (
            <section key={index} id={`bloc-${index}`} className="mt-10 scroll-mt-6 first:mt-0">
              {style ? (
                <div className={`rounded-xl border p-5 ${style.classe}`}>
                  <p className={`text-xs font-semibold uppercase tracking-wide ${style.classeLibelle}`}>
                    {style.libelle}
                  </p>
                  <h2 className="mt-1 text-lg font-semibold text-slate-900 dark:text-slate-100">
                    {bloc.titre}
                  </h2>
                  <p className="mt-2 leading-relaxed text-slate-700 dark:text-slate-200">
                    {bloc.texte}
                  </p>
                </div>
              ) : (
                <>
                  <div className="flex items-baseline gap-3">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-100 text-sm font-semibold text-brand-700 dark:bg-brand-500/20 dark:text-brand-400">
                      {index + 1}
                    </span>
                    <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
                      {bloc.titre}
                    </h2>
                  </div>
                  <p className="mt-3 pl-10 leading-relaxed text-slate-700 dark:text-slate-300">
                    {bloc.texte}
                  </p>
                </>
              )}

              {bloc.code && (
                <div className="ml-10">
                  <BlocCode code={bloc.code} langage={bloc.langage} />
                </div>
              )}
                            {bloc.etapes?.length > 0 && (
                <div className="ml-10">
                  <BlocDiagramme etapes={bloc.etapes} />
                </div>
              )}
            </section>
          );
        })}

        {notion.notions_liees?.length > 0 && (
          <section className="mt-12">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
              Notions liées
            </h2>
            <div className="mt-2 flex flex-wrap gap-2">
              {notion.notions_liees.map((liee) => (
                <Link
                  key={liee.slug}
                  to={`/notions/${liee.slug}`}
                  className="rounded-full border border-slate-200 bg-white px-3 py-1 text-sm text-slate-600 transition hover:border-brand-300 hover:text-brand-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-brand-500 dark:hover:text-brand-400"
                >
                  {liee.titre}
                </Link>
              ))}
            </div>
          </section>
        )}

        {notion.ressources?.length > 0 && (
          <section className="mt-12">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
              Ressources
            </h2>
            <ul className="mt-2 space-y-1">
              {notion.ressources.map((r) => (
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

        <AssistantIA slug={notion.slug} />
      </div>
    </div>
  );
}