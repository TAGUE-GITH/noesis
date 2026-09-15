from flask import Flask, jsonify
from flask_migrate import Migrate

from app.config import Config
from app.extensions import db

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.models import fiche  # noqa: F401

    from app.routes.recherche_routes import bp as recherche_bp
    from app.routes.fiche_routes import bp as fiche_bp
    app.register_blueprint(recherche_bp)
    app.register_blueprint(fiche_bp)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(404)
    def non_trouve(e):
        message = getattr(e, "description", "Ressource introuvable.")
        return jsonify({"erreur": message}), 404

    return app