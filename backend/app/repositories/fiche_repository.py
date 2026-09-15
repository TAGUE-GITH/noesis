from sqlalchemy import text

from app.extensions import db
from app.models.fiche import Fiche

# Un même "champ qui matche un mot" (titre / mots_cles / definition) et son
# score sont réutilisés deux fois par mot (une fois dans le WHERE, une fois
# dans le calcul du score) : on factorise le SQL ici pour ne pas le dupliquer
# à chaque mot de la recherche.
_CORRESPOND = """(
    unaccent(titre) ILIKE unaccent(:{cle})
    OR EXISTS (
        SELECT 1 FROM unnest(mots_cles) AS mc
        WHERE unaccent(mc) ILIKE unaccent(:{cle})
    )
    OR unaccent(definition) ILIKE unaccent(:{cle})
)"""

_SCORE_MOT = """CASE
    WHEN unaccent(titre) ILIKE unaccent(:{cle}) THEN 3
    WHEN EXISTS (
        SELECT 1 FROM unnest(mots_cles) AS mc
        WHERE unaccent(mc) ILIKE unaccent(:{cle})
    ) THEN 2
    WHEN unaccent(definition) ILIKE unaccent(:{cle}) THEN 1
    ELSE 0
END"""


def rechercher(terme: str) -> list[dict]:
    """Recherche les fiches dont le titre, les mots-clés ou la définition
    contiennent CHAQUE mot du terme recherché — pas le terme entier comme une
    seule phrase figée. Ça permet à "clé étrangère primaire" de retrouver la
    fiche "Clé primaire et clé étrangère" même si les mots sont dans un ordre
    différent, ou répartis entre le titre et la définition.

    Recherche insensible à la casse et aux accents (US01). Résultats triés
    par pertinence cumulée sur tous les mots : titre > mots-clés > définition
    (US02, règle actée à l'étape 8) ; en cas d'égalité, ordre alphabétique.
    """
    mots = [mot for mot in terme.strip().split() if mot]
    if not mots:
        return []

    conditions = []
    scores = []
    params = {}
    for index, mot in enumerate(mots):
        cle = f"motif{index}"
        params[cle] = f"%{mot}%"
        conditions.append(_CORRESPOND.format(cle=cle))
        scores.append(_SCORE_MOT.format(cle=cle))

    # Chaque mot doit matcher AU MOINS UN champ (condition jointe par AND
    # entre les mots), mais peu importe lequel — un mot peut matcher le
    # titre et un autre la définition, par exemple.
    requete = text(
        f"""
        SELECT id, titre, definition, resume, mots_cles,
               ({" + ".join(scores)}) AS score
        FROM fiche
        WHERE {" AND ".join(conditions)}
        ORDER BY score DESC, titre ASC
        """
    )
    resultat = db.session.execute(requete, params)
    return [dict(ligne._mapping) for ligne in resultat]


def obtenir_par_id(fiche_id: int) -> Fiche | None:
    """Récupère une fiche complète (avec ses ressources) par son id (US03).
    Ici, l'ORM classique suffit largement — pas besoin de SQL brut."""
    return db.session.get(Fiche, fiche_id)