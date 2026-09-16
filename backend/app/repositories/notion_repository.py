import re
import unicodedata

from sqlalchemy import text

from app.extensions import db
from app.models.notion import Notion

# Recherche par mot entier (\y = limite de mot en regex PostgreSQL), sur
# titre, mots_cles ET synonymes désormais — c'est l'ajout des synonymes qui
# permet de retrouver une notion même avec une formulation différente de
# son titre (ex. "POO" pour "Programmation orientée objet"), sans appel IA.
# insensible à la casse et aux accents (unaccent), comme avant.
_CORRESPOND = """(
    unaccent(titre) ~* unaccent(:{cle})
    OR EXISTS (
        SELECT 1 FROM unnest(mots_cles) AS mc
        WHERE unaccent(mc) ~* unaccent(:{cle})
    )
    OR EXISTS (
        SELECT 1 FROM unnest(synonymes) AS syn
        WHERE unaccent(syn) ~* unaccent(:{cle})
    )
    OR unaccent(resume) ~* unaccent(:{cle})
)"""

_SCORE_MOT = """CASE
    WHEN unaccent(titre) ~* unaccent(:{cle}) THEN 4
    WHEN EXISTS (
        SELECT 1 FROM unnest(mots_cles) AS mc
        WHERE unaccent(mc) ~* unaccent(:{cle})
    ) THEN 3
    WHEN EXISTS (
        SELECT 1 FROM unnest(synonymes) AS syn
        WHERE unaccent(syn) ~* unaccent(:{cle})
    ) THEN 2
    WHEN unaccent(resume) ~* unaccent(:{cle}) THEN 1
    ELSE 0
END"""


def rechercher(terme: str) -> list[dict]:
    """Recherche les notions dont le titre, les mots-clés, les synonymes ou
    le résumé contiennent CHAQUE mot du terme recherché (peu importe l'ordre
    ou le champ). Insensible à la casse et aux accents. Résultats triés par
    pertinence cumulée : titre > mots-clés > synonymes > résumé."""
    mots = [mot for mot in terme.strip().split() if mot]
    if not mots:
        return []

    conditions = []
    scores = []
    params = {}
    for index, mot in enumerate(mots):
        cle = f"motif{index}"
        params[cle] = rf"\y{re.escape(mot)}\y"
        conditions.append(_CORRESPOND.format(cle=cle))
        scores.append(_SCORE_MOT.format(cle=cle))

    requete = text(
        f"""
        SELECT id, titre, slug, resume,
               ({" + ".join(scores)}) AS score
        FROM notion
        WHERE {" AND ".join(conditions)}
        ORDER BY score DESC, titre ASC
        """
    )
    resultat = db.session.execute(requete, params)
    return [dict(ligne._mapping) for ligne in resultat]


def obtenir_par_slug(slug: str) -> Notion | None:
    """Récupère une notion complète (avec ses ressources) par son slug."""
    return Notion.query.filter_by(slug=slug).first()


def slugifier(titre: str) -> str:
    """Transforme un titre en clé d'URL : minuscules, sans accents, mots
    séparés par des tirets (ex. "Clé primaire et clé étrangère" ->
    "cle-primaire-et-cle-etrangere")."""
    sans_accents = unicodedata.normalize("NFKD", titre).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", sans_accents.lower()).strip("-")
    return slug or "notion"


def slug_disponible(slug: str, exclure_id: int | None = None) -> str:
    """Garantit un slug unique : si "docker" existe déjà, essaie "docker-2",
    "docker-3", etc. Nécessaire car deux notions différentes peuvent avoir
    des titres qui se slugifient à l'identique."""
    candidat = slug
    compteur = 2
    while True:
        requete = Notion.query.filter_by(slug=candidat)
        if exclure_id is not None:
            requete = requete.filter(Notion.id != exclure_id)
        if requete.first() is None:
            return candidat
        candidat = f"{slug}-{compteur}"
        compteur += 1


def creer(*, titre: str, resume: str, mots_cles: list[str], synonymes: list[str],
          origine: str, contenu: list[dict]) -> Notion:
    """Crée une nouvelle notion générée par l'IA (le slug est dérivé du
    titre et garanti unique). Utilisé quand une recherche ne trouve aucune
    notion existante : le résultat de la génération est conservé en base
    pour ne jamais être regénéré à l'identique."""
    slug = slug_disponible(slugifier(titre))
    notion = Notion(
        titre=titre,
        slug=slug,
        resume=resume,
        mots_cles=mots_cles,
        synonymes=synonymes,
        notions_liees=[],
        origine=origine,
        contenu=contenu,
        quiz=None,
    )
    db.session.add(notion)
    db.session.commit()
    return notion