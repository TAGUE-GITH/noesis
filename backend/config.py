import os

from dotenv import load_dotenv


# Charge les variables définies dans le fichier .env
load_dotenv()


class Config:
    """
    Configuration de l'application.

    Les informations sensibles, comme l'URL de connexion PostgreSQL,
    sont récupérées depuis le fichier .env et ne sont jamais écrites
    directement dans le code source.
    """

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False