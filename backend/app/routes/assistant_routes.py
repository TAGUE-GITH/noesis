from flask import Blueprint, abort, jsonify, request

from app.clients.ia_client import AssistantIndisponible
from app.repositories import notion_repository
from app.services import assistant_service

assistant_bp = Blueprint("assistant", __name__)


@assistant_bp.route("/api/notions/<slug>/assistant", methods=["POST"])
def poser_question(slug):
    donnees = request.get_json(silent=True) or {}
    question = (donnees.get("question") or "").strip()
    if not question:
        abort(400, description="La question ne peut pas être vide.")

    notion = notion_repository.obtenir_par_slug(slug)
    if notion is None:
        abort(404, description="Cette notion n'existe pas.")

    try:
        resultat = assistant_service.repondre_question(notion, question)
    except AssistantIndisponible:
        # On ne renvoie jamais le détail technique de l'erreur au visiteur
        # (clé API absente, erreur réseau...) — juste un message compréhensible,
        # avec un code 503 (service temporairement indisponible), pas un 500.
        return (
            jsonify({"erreur": "L'assistant IA est momentanément indisponible."}),
            503,
        )

    return jsonify(resultat)


@assistant_bp.route("/api/notions/<slug>/quiz", methods=["POST"])
def generer_quiz(slug):
    notion = notion_repository.obtenir_par_slug(slug)
    if notion is None:
        abort(404, description="Cette notion n'existe pas.")

    try:
        resultat = assistant_service.generer_quiz(notion)
    except AssistantIndisponible:
        return (
            jsonify({"erreur": "L'assistant IA est momentanément indisponible."}),
            503,
        )

    return jsonify(resultat)