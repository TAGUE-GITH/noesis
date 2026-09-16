import { Link } from "react-router-dom";

// Navigation "Cours" / "Exercices" partagée entre NotionPage et
// ExercicesPage : matérialise la séparation entre lire le contenu et
// s'exercer dessus, comme sur une vraie plateforme d'apprentissage — plutôt
// que tout empiler sur une seule page.
export default function OngletsNotion({ slug, actif }) {
  const onglets = [
    { cle: "cours", libelle: "Cours", chemin: `/notions/${slug}` },
    { cle: "exercices", libelle: "Exercices", chemin: `/notions/${slug}/exercices` },
  ];

  return (
    <nav className="mt-6 flex gap-1 border-b border-slate-200 dark:border-slate-700">
      {onglets.map((onglet) => (
        <Link
          key={onglet.cle}
          to={onglet.chemin}
          className={`px-4 py-2 text-sm font-medium transition ${
            actif === onglet.cle
              ? "border-b-2 border-brand-500 text-brand-600 dark:text-brand-400"
              : "border-b-2 border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
          }`}
        >
          {onglet.libelle}
        </Link>
      ))}
    </nav>
  );
}