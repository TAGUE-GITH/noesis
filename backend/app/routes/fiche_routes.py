from flask import Blueprint, abort, jsonify

from app.schemas.fiche_schema import vers_detail_fiche
from app.services import fiche_service

bp = Blueprint("fiche", __name__, url_prefix="/api")


@bp.get("/fiches/<int:fiche_id>")
def detail(fiche_id):
    fiche = fiche_service.obtenir_detail(fiche_id)
    if fiche is None:
        abort(404, description="Fiche introuvable.")
    return jsonify(vers_detail_fiche(fiche))