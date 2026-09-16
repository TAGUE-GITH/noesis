from flask import Blueprint, abort, jsonify

from app.schemas.notion_schema import vers_detail_notion
from app.services import notion_service

notion_bp = Blueprint("notion", __name__, url_prefix="/api")


@notion_bp.get("/notions/<slug>")
def detail(slug):
    """US03, étendue : détail complet d'une notion — qu'elle soit vérifiée
    par Franck ou générée par l'IA, c'est la même page et la même route.

    404 si le slug ne correspond à aucune notion.
    """
    notion = notion_service.obtenir_detail(slug)
    if notion is None:
        abort(404, description="Cette notion n'existe pas.")
    notions_liees = notion_service.obtenir_notions_liees(notion)
    return jsonify(vers_detail_notion(notion, notions_liees))