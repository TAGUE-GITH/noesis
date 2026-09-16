const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

export async function rechercherFiches(terme) {
  const reponse = await fetch(`${BASE_URL}/recherche?q=${encodeURIComponent(terme)}`);
  if (!reponse.ok) {
    throw new Error("Erreur lors de la recherche.");
  }
  return reponse.json();
}

export async function obtenirNotion(slug) {
  const reponse = await fetch(`${BASE_URL}/notions/${encodeURIComponent(slug)}`);
  if (reponse.status === 404) {
    return null;
  }
  if (!reponse.ok) {
    throw new Error("Erreur lors de la récupération de la notion.");
  }
  return reponse.json();
}

export async function poserQuestionAssistant(slug, question) {
  const reponse = await fetch(`${BASE_URL}/notions/${encodeURIComponent(slug)}/assistant`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  // Le backend renvoie toujours du JSON, même en cas d'erreur (400/404/503),
  // donc on peut toujours lire son champ "erreur" pour afficher un message
  // utile plutôt qu'un message générique.
  const donnees = await reponse.json().catch(() => null);
  if (!reponse.ok) {
    throw new Error(donnees?.erreur || "L'assistant IA est momentanément indisponible.");
  }
  return donnees;
}

export async function genererQuiz(slug) {
  const reponse = await fetch(`${BASE_URL}/notions/${encodeURIComponent(slug)}/quiz`, {
    method: "POST",
  });
  const donnees = await reponse.json().catch(() => null);
  if (!reponse.ok) {
    throw new Error(donnees?.erreur || "L'assistant IA est momentanément indisponible.");
  }
  return donnees;
}