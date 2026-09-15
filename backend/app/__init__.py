from flask import Flask
from flask_migrate import Migrate

from config import Config
from app.extensions import db


migrate = Migrate()


def create_app():
    """
    Factory qui construit et configure l'application Flask.
    """
    app = Flask(__name__)

    # Chargement de la configuration
    app.config.from_object(Config)

    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import des modèles pour les enregistrer dans les métadonnées SQLAlchemy.
    # Cet import doit être effectué après l'initialisation de db.
    from app.models import Fiche, Ressource  # noqa: F401

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app