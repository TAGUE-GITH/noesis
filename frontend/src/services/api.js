const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

export async function rechercherFiches(terme) {
  const reponse = await fetch(`${BASE_URL}/recherche?q=${encodeURIComponent(terme)}`);
  if (!reponse.ok) throw new Error("Erreur lors de la recherche.");
  return reponse.json();
}

export async function obtenirFiche(id) {
  const reponse = await fetch(`${BASE_URL}/fiches/${id}`);
  if (reponse.status === 404) return null;
  if (!reponse.ok) throw new Error("Erreur lors de la récupération de la fiche.");
  return reponse.json();
}

export async function poserQuestionAssistant(ficheId, question) {
  const reponse = await fetch(`${BASE_URL}/fiches/${ficheId}/assistant`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  const donnees = await reponse.json().catch(() => null);
  if (!reponse.ok) {
    throw new Error(donnees?.erreur || "L'assistant IA est momentanément indisponible.");
  }
  return donnees;
}

export async function genererQuiz(ficheId) {
  const reponse = await fetch(`${BASE_URL}/fiches/${ficheId}/quiz`, {
    method: "POST",
  });
  const donnees = await reponse.json().catch(() => null);
  if (!reponse.ok) {
    throw new Error(donnees?.erreur || "L'assistant IA est momentanément indisponible.");
  }
  return donnees;
}