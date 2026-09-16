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

    # Le frontend (port 5173, serveur Vite) et le backend (port 5000) sont
    # deux origines différentes du point de vue du navigateur : sans ça,
    # le navigateur bloque les requêtes du frontend par sécurité (CORS).
    # En v1, on autorise seulement l'origine du frontend en développement ;
    # à adapter à l'étape 29 (déploiement) avec le vrai domaine du frontend.
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

    from app.models import notion  # noqa: F401  — nécessaire pour Flask-Migrate

    from app.routes.recherche_routes import bp as recherche_bp
    from app.routes.notion_routes import notion_bp
    from app.routes.assistant_routes import assistant_bp

    app.register_blueprint(recherche_bp)
    app.register_blueprint(notion_bp)
    app.register_blueprint(assistant_bp)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(404)
    def non_trouve(e):
        """Gestionnaire d'erreur centralisé : garantit que même une erreur
        renvoie du JSON (jamais la page HTML par défaut de Flask), pour que
        le frontend puisse toujours l'interpréter de la même façon. Version
        volontairement minimale — sera enrichie à l'étape 25."""
        message = getattr(e, "description", "Ressource introuvable.")
        return jsonify({"erreur": message}), 404

    @app.errorhandler(400)
    def requete_invalide(e):
        """Même principe que le 404 ci-dessus, pour les requêtes mal
        formées (ex. question vide envoyée à l'assistant IA)."""
        message = getattr(e, "description", "Requête invalide.")
        return jsonify({"erreur": message}), 400

    return app