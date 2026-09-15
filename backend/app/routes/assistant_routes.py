from flask import Blueprint, abort, jsonify, request

from app.clients.ia_client import AssistantIndisponible
from app.repositories import fiche_repository
from app.services import assistant_service

assistant_bp = Blueprint("assistant", __name__)


@assistant_bp.route("/api/fiches/<int:fiche_id>/assistant", methods=["POST"])
def poser_question(fiche_id):
    donnees = request.get_json(silent=True) or {}
    question = (donnees.get("question") or "").strip()
    if not question:
        abort(400, description="La question ne peut pas être vide.")

    fiche = fiche_repository.obtenir_par_id(fiche_id)
    if fiche is None:
        abort(404, description="Cette fiche n'existe pas.")

    try:
        resultat = assistant_service.repondre_question(fiche, question)
    except AssistantIndisponible:
        # On ne renvoie jamais le détail technique de l'erreur au visiteur
        # (clé API absente, erreur réseau...) — juste un message compréhensible,
        # avec un code 503 (service temporairement indisponible), pas un 500.
        return (
            jsonify({"erreur": "L'assistant IA est momentanément indisponible."}),
            503,
        )

    return jsonify(resultat)