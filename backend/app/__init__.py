from flask import Flask


def create_app():
    """Factory qui construit et configure l'application Flask.

    On utilise une factory (plutôt qu'une instance globale de Flask créée
    directement dans un fichier) pour pouvoir créer plusieurs instances de
    l'app avec des configurations différentes — utile notamment pour les
    tests automatisés (étape 26), qui ont besoin d'une app isolée.
    """
    app = Flask(__name__)

    @app.get("/api/health")
    def health():
        """Endpoint minimal pour vérifier que le serveur tourne."""
        return {"status": "ok"}

    return app