from app.clients import ia_client
from app.clients.ia_client import AssistantIndisponible
from app.extensions import db
from app.models.notion import Ressource
from app.repositories import notion_repository


def rechercher(terme: str) -> dict:
    """Logique métier de la recherche (US01/US02), étendue en 3 paliers
    (increment B) avant de se rabattre sur la génération IA complète :

    1. Mots entiers exacts (notion_repository.rechercher) — rapide, pas
       d'appel IA.
    2. Recherche floue par similarité de trigrammes
       (notion_repository.rechercher_flou) — tolère les fautes de frappe,
       toujours sans appel IA.
    3. Correspondance IA (ia_client.trouver_correspondance) — un terme
       reformulé différemment ("POO") peut correspondre à une notion déjà
       existante ("Programmation orientée objet") sans lui ressembler ni
       par mot exact ni par similarité de caractères ; un appel IA court
       tranche ce cas avant de dupliquer du contenu déjà généré.

    Si les 3 paliers échouent, une nouvelle notion est générée à la volée
    et conservée en base, plutôt que de renvoyer une simple absence de
    résultat. Le visiteur n'arrive donc (quasiment) plus jamais sur une
    impasse — seulement si l'IA est indisponible, ce qu'on signale via
    "generation_echouee" plutôt que de faire échouer la recherche
    elle-même.
    """
    terme_nettoye = terme.strip()
    if not terme_nettoye:
        return {"resultats": [], "generation_echouee": False}

    resultats = notion_repository.rechercher(terme_nettoye)
    if not resultats:
        resultats = notion_repository.rechercher_flou(terme_nettoye)
    if resultats:
        return {"resultats": resultats, "generation_echouee": False}

    try:
        notion = _trouver_via_correspondance_ia(terme_nettoye)
        if notion is None:
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


def _trouver_via_correspondance_ia(terme: str):
    """Palier 3 : demande à l'IA si le terme correspond à une notion
    existante formulée différemment. Renvoie None si l'IA ne trouve rien
    — y compris si elle indique par erreur un slug qui n'existe plus,
    auquel cas on se rabat simplement sur la génération, sans planter."""
    notions_existantes = notion_repository.lister_titres_slugs()
    slug = ia_client.trouver_correspondance(terme, notions_existantes)
    if slug is None:
        return None
    return notion_repository.obtenir_par_slug(slug)


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