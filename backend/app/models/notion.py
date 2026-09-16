from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import ARRAY

from app.extensions import db


class Notion(db.Model):
    """Une notion informatique (ex. "Docker", "Java", "Héritage") : le coeur
    unifié du moteur Yamia.

    Remplace les anciennes tables séparées `fiche` (rédigée à la main,
    vérifiée) et `cours` (générée par l'IA) : les deux étaient deux versions
    incomplètes du même besoin (expliquer une notion en profondeur), et leur
    séparation empêchait d'offrir la même profondeur pédagogique partout,
    quelle que soit l'origine du contenu. Une seule table, une seule origine
    de vérité ; `origine` distingue seulement si le contenu a été vérifié
    par Franck ou généré par l'IA — pour garder la transparence envers le
    visiteur, pas pour dupliquer la structure.
    """

    __tablename__ = "notion"

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.Text, nullable=False)
    # Clé de recherche/URL normalisée (minuscules, tirets, sans accents) —
    # unique, utilisée dans /api/notions/<slug> et dans l'URL frontend.
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    # Courte description utilisée comme extrait dans la liste de résultats
    # de recherche (US02) — distincte du contenu complet (US03).
    resume = db.Column(db.Text, nullable=False)
    mots_cles = db.Column(ARRAY(db.Text), nullable=False, default=list)
    # Variantes/termes proches (ex. "POO" pour "Programmation orientée
    # objet") : élargit la recherche sans dépendre d'un appel IA à chaque
    # requête.
    synonymes = db.Column(ARRAY(db.Text), nullable=False, default=list)
    # Slugs d'autres notions à suggérer ensuite (ex. "classe" -> ["objet",
    # "encapsulation", "heritage"]) — alimente le parcours d'apprentissage.
    notions_liees = db.Column(ARRAY(db.Text), nullable=False, default=list)
    # "verifiee" (rédigée/relue par Franck) ou "generee_ia" (générée
    # automatiquement) — affiché au visiteur pour la transparence.
    origine = db.Column(db.String(20), nullable=False)
    date_verification = db.Column(db.DateTime, nullable=True)
    # Contenu structuré : liste ORDONNÉE de blocs typés, par ex.
    # [{"type": "texte", "titre": "Définition", "texte": "...", "code": "",
    #   "langage": ""},
    #  {"type": "analogie", "titre": "...", "texte": "...", "code": "", "langage": ""},
    #  {"type": "code", "titre": "Exemple", "texte": "explication du code",
    #   "code": "...", "langage": "java"},
    #  {"type": "a_retenir", ...}, {"type": "erreur_frequente", ...}]
    # JSON plutôt que des colonnes fixes : le nombre, l'ordre et les types de
    # blocs varient d'une notion à l'autre (une notion simple comme "Tableau"
    # n'a pas besoin des mêmes sections qu'un framework comme "Spring Boot").
    contenu = db.Column(db.JSON, nullable=False)
    # Quiz de base stocké une fois (même format que ia_client.generer_quiz) ;
    # None tant qu'aucun quiz n'a encore été généré pour cette notion.
    quiz = db.Column(db.JSON, nullable=True)
    date_creation = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    date_modification = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    ressources = db.relationship(
        "Ressource", backref="notion", cascade="all, delete-orphan"
    )


class Ressource(db.Model):
    """Une ressource liée à une notion (ex. un lien vers la documentation
    officielle). Inchangé dans son principe par rapport à l'ancienne version
    liée à `Fiche` — seule la clé étrangère change de cible."""

    __tablename__ = "ressource"

    id = db.Column(db.Integer, primary_key=True)
    notion_id = db.Column(db.Integer, db.ForeignKey("notion.id"), nullable=False)
    libelle = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)