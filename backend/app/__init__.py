from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from app.config import Config
from app.extensions import db

migrate = Migrate()


def create_app():
    """Factory qui construit et configure l'application Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

    from app.models import fiche  # noqa: F401  — nécessaire pour Flask-Migrate

    from app.routes.recherche_routes import bp as recherche_bp
    from app.routes.fiche_routes import bp as fiche_bp
    from app.routes.assistant_routes import assistant_bp

    app.register_blueprint(recherche_bp)
    app.register_blueprint(fiche_bp)
    app.register_blueprint(assistant_bp)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(404)
    def non_trouve(e):
        message = getattr(e, "description", "Ressource introuvable.")
        return jsonify({"erreur": message}), 404

    @app.errorhandler(400)
    def requete_invalide(e):
        """Même principe que le 404 ci-dessus, pour les requêtes mal
        formées (ex. question vide envoyée à l'assistant IA)."""
        message = getattr(e, "description", "Requête invalide.")
        return jsonify({"erreur": message}), 400

    return app