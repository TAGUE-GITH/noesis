from flask_sqlalchemy import SQLAlchemy  # type: ignore[import-not-found]

# Instance unique de SQLAlchemy, partagée par toute l'application.
# On la crée ici, séparément de create_app(), pour éviter les imports
# circulaires : les modèles (models/fiche.py) ont besoin d'importer `db`,
# et app/__init__.py a besoin d'importer les modèles.
db = SQLAlchemy()