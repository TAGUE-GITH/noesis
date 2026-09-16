from app.clients import ia_client
from app.clients.ia_client import AssistantIndisponible
from app.extensions import db
from app.models.notion import Ressource
from app.repositories import notion_repository


def rechercher(terme: str) -> dict:
    """Logique métier de la recherche (US01/US02), étendue : si aucune
    notion existante ne correspond au terme, on en génère une nouvelle à la
    volée (recherche web + structuration IA) et on la conserve en base,
    plutôt que de renvoyer une simple absence de résultat. Le visiteur
    n'arrive donc (quasiment) plus jamais sur une impasse — seulement si
    l'IA est indisponible, ce qu'on signale via "generation_echouee" plutôt
    que de faire échouer la recherche elle-même.

    C'est ce qui remplace l'ancienne branche séparée "réponse IA en direct
    si aucune fiche" : plus de distinction entre chemin "fiche vérifiée" et
    chemin "IA" côté recherche — toute notion, vérifiée ou générée, vit
    dans la même table et suit le même chemin ensuite.
    """
    terme_nettoye = terme.strip()
    if not terme_nettoye:
        return {"resultats": [], "generation_echouee": False}

    resultats = notion_repository.rechercher(terme_nettoye)
    if resultats:
        return {"resultats": resultats, "generation_echouee": False}

    try:
        notion = generer_et_creer(terme_nettoye)
    except AssistantIndisponible:
        return {"resultats": [], "generation_echouee": True}

    return {
        "resultats": [
            {
                "id": notion.id,
                "titre": notion.titre,
                "slug": notion.slug,
                "resume": notion.resume,
            }
        ],
        "generation_echouee": False,
    }


def generer_et_creer(terme: str):
    """Génère une nouvelle notion via l'IA et la stocke en base (origine
    "generee_ia"). Les pages consultées pendant la recherche web
    deviennent les ressources affichées sur la notion — même principe de
    transparence des sources qu'une notion vérifiée à la main."""
    resultat = ia_client.generer_notion(terme)
    notion = notion_repository.creer(
        titre=resultat["titre"],
        resume=resultat["resume"],
        mots_cles=resultat.get("mots_cles", []),
        synonymes=[],
        origine="generee_ia",
        contenu=resultat["blocs"],
    )
    for source in resultat.get("sources", []):
        notion.ressources.append(
            Ressource(libelle=source["libelle"], url=source["url"])
        )
    db.session.commit()
    return notion


def obtenir_detail(slug: str):
    return notion_repository.obtenir_par_slug(slug)