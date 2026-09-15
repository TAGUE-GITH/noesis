from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import ARRAY

from app.extensions import db


class Fiche(db.Model):
    """Une fiche de connaissance (ex. "Docker"), au coeur du moteur Noesis."""

    __tablename__ = "fiche"

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.Text, nullable=False)
    definition = db.Column(db.Text, nullable=False)
    resume = db.Column(db.Text, nullable=False)
    mots_cles = db.Column(ARRAY(db.Text), nullable=False, default=list)
    concepts_cles = db.Column(ARRAY(db.Text), nullable=False, default=list)
    prerequis = db.Column(ARRAY(db.Text), nullable=False, default=list)
    pour_aller_plus_loin = db.Column(db.Text, nullable=True)
    date_creation = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    date_modification = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    ressources = db.relationship(
        "Ressource", backref="fiche", cascade="all, delete-orphan"
    )


class Ressource(db.Model):
    """Une ressource liée à une fiche (ex. lien vers la doc officielle)."""

    __tablename__ = "ressource"

    id = db.Column(db.Integer, primary_key=True)
    fiche_id = db.Column(db.Integer, db.ForeignKey("fiche.id"), nullable=False)
    libelle = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)