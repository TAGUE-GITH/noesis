from flask import Blueprint, jsonify, request

from app.schemas.notion_schema import vers_resultat_recherche
from app.services import notion_service

bp = Blueprint("recherche", __name__, url_prefix="/api")


@bp.get("/recherche")
def rechercher():
    """US01/US02, étendue : si aucune notion ne correspond déjà au terme
    recherché, une nouvelle notion est générée par l'IA (recherche web +
    structuration) et renvoyée directement dans les résultats — plus de
    branche séparée "réponse IA sans fiche" : un seul chemin, pour toute
    recherche. Renvoie toujours 200 ; "generation_echouee" ne passe à vrai
    que si l'IA est indisponible ET qu'aucune notion existante ne
    correspondait déjà (donc rien à montrer).
    """
    terme = request.args.get("q", "").strip()
    resultat = notion_service.rechercher(terme)

    return jsonify(
        {
            "resultats": [vers_resultat_recherche(r) for r in resultat["resultats"]],
            "generation_echouee": resultat["generation_echouee"],
        }
    )