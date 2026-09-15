from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models.fiche import Fiche
from app.services import recherche_service

app = create_app()
with app.app_context():
    Fiche.query.delete()
    db.session.commit()

    db.session.add_all([
        Fiche(titre="Docker", definition="Docker est un outil de conteneurisation.",
              resume="Conteneurisation d'applications.", mots_cles=["conteneur", "devops"]),
        Fiche(titre="Modélisation UML", definition="La modélisation permet de représenter un système.",
              resume="Représentation d'un système.", mots_cles=["UML", "conception"]),
    ])
    db.session.commit()

    print(recherche_service.rechercher_fiches("docker"))
    print(recherche_service.rechercher_fiches("modelisation"))