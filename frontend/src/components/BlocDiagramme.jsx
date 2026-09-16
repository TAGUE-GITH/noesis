// Diagramme de flux : une séquence d'étapes reliées par des flèches.
// Rendu en CSS pur (flex-wrap), pas en SVG généré : ça reste toujours net
// et lisible quelle que soit la longueur du texte de chaque étape ou la
// largeur de l'écran, contrairement à des coordonnées dessinées par l'IA
// qui peuvent se chevaucher ou déborder.
export default function BlocDiagramme({ etapes }) {
  if (!etapes || etapes.length === 0) return null;

  return (
    <div className="mt-4 flex flex-wrap items-center gap-y-3">
      {etapes.map((etape, index) => (
        <div key={index} className="flex items-center">
          <div className="rounded-xl border border-brand-200 bg-brand-50 px-4 py-2.5 text-sm font-medium text-brand-700 dark:border-brand-500/30 dark:bg-brand-500/10 dark:text-brand-400">
            {etape}
          </div>
          {index < etapes.length - 1 && (
            <span
              className="mx-2 text-lg text-slate-300 dark:text-slate-600"
              aria-hidden="true"
            >
              →
            </span>
          )}
        </div>
      ))}
    </div>
  );
}