import { useState } from "react";
import SearchBar from "../components/SearchBar";
import ResultList from "../components/ResultList";
import LogoIcon from "../components/LogoIcon";
import { rechercherFiches } from "../services/api";

export default function HomePage() {
  const [terme, setTerme] = useState("");
  const [donnees, setDonnees] = useState(null);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState(null);

  async function lancerRecherche() {
    if (!terme.trim()) return;
    setEnCours(true);
    setErreur(null);
    try {
      const data = await rechercherFiches(terme);
      setDonnees(data);
    } catch {
      setErreur("Une erreur est survenue. Réessaie dans un instant.");
    } finally {
      setEnCours(false);
    }
  }

  return (
    <div className="relative flex min-h-[calc(100vh-72px)] flex-col items-center overflow-hidden px-4 pt-16">
      {/* Halo décoratif en dégradé, purement visuel : positionné en absolu, ne
          capte aucun événement (pointer-events-none), flouté (blur-3xl). */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute left-1/2 top-0 h-[420px] w-[420px] -translate-x-1/2 -translate-y-1/3 rounded-full bg-gradient-to-br from-brand-300 via-brand-500 to-brand-700 opacity-20 blur-3xl dark:opacity-30"
      />

      <div className="relative z-10 flex flex-col items-center">
        {/* Grand nom de marque, bien visible en haut du hero (demande explicite
            de Franck) : icône + wordmark en gros caractères, séparé du titre
            d'accroche qui suit en dessous. */}
        <div className="mb-6 flex items-center gap-3">
          <LogoIcon className="h-12 w-12 sm:h-14 sm:w-14" />
          <span className="bg-gradient-to-r from-brand-500 to-brand-700 bg-clip-text text-5xl font-extrabold tracking-tight text-transparent sm:text-6xl">
            Yamia
          </span>
        </div>

        <h1 className="mb-3 max-w-2xl text-center text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl dark:text-slate-50">
          Cherche une notion. Comprends-la vraiment.
        </h1>
        <p className="mb-8 max-w-md text-center text-slate-500 dark:text-slate-400">
          Yamia ne te renvoie pas juste des liens : chaque fiche t'explique une
          notion informatique avec ses concepts clés, ses prérequis et des
          ressources pour aller plus loin.
        </p>
        <SearchBar valeur={terme} onChange={setTerme} onSubmit={lancerRecherche} />
        {enCours && (
          <p className="mt-6 animate-fade-in-up text-slate-400 dark:text-slate-500">
            Recherche en cours...
          </p>
        )}
        {erreur && (
          <p className="mt-6 animate-fade-in-up text-red-500 dark:text-red-400">{erreur}</p>
        )}
        {!enCours && (
          <ResultList
            resultats={donnees ? donnees.resultats : null}
            generationEchouee={donnees ? donnees.generation_echouee : false}
            terme={terme}
          />
        )}
      </div>
    </div>
  );
}