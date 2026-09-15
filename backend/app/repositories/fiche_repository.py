from sqlalchemy import text

from app.extensions import db
from app.models.fiche import Fiche

# SQL brut plutôt que pur ORM : dès qu'on mélange une recherche floue
# (unaccent/ILIKE) et une recherche à l'intérieur d'un tableau (mots_cles),
# le SQL direct reste plus lisible. Le reste de l'application n'a pas à
# savoir comment cette requête est écrite — c'est le rôle du repository
# de cacher ce détail.
_REQUETE_RECHERCHE = text(
    """
    SELECT id, titre, definition, resume, mots_cles,
           CASE
               WHEN unaccent(titre) ILIKE unaccent(:motif) THEN 3
               WHEN EXISTS (
                   SELECT 1 FROM unnest(mots_cles) AS mc
                   WHERE unaccent(mc) ILIKE unaccent(:motif)
               ) THEN 2
               WHEN unaccent(definition) ILIKE unaccent(:motif) THEN 1
               ELSE 0
           END AS score
    FROM fiche
    WHERE unaccent(titre) ILIKE unaccent(:motif)
       OR EXISTS (
           SELECT 1 FROM unnest(mots_cles) AS mc
           WHERE unaccent(mc) ILIKE unaccent(:motif)
       )
       OR unaccent(definition) ILIKE unaccent(:motif)
    ORDER BY score DESC, titre ASC
    """
)


def rechercher(terme: str) -> list[dict]:
    """Recherche les fiches par titre/mots-clés/définition — insensible à
    la casse et aux accents (US01), triée par pertinence (US02)."""
    motif = f"%{terme}%"
    resultat = db.session.execute(_REQUETE_RECHERCHE, {"motif": motif})
    return [dict(ligne._mapping) for ligne in resultat]

def obtenir_par_id(fiche_id: int) -> Fiche | None:
    """Récupère une fiche complète (avec ses ressources) par son id (US03).
    Ici, l'ORM classique suffit largement — pas besoin de SQL brut."""
    return db.session.get(Fiche, fiche_id)