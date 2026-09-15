from flask import Blueprint, jsonify, request

from app.schemas.fiche_schema import vers_resultat_recherche
from app.services import recherche_service

bp = Blueprint("recherche", __name__, url_prefix="/api")


@bp.get("/recherche")
def rechercher():
    terme = request.args.get("q", "")
    resultats = recherche_service.rechercher_fiches(terme)
    return jsonify([vers_resultat_recherche(r) for r in resultats])