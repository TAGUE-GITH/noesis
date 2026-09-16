"""fusionne fiche et cours en une seule table notion

Revision ID: 7a1f9c3d5e21
Revises: 6363667dd91f
Create Date: 2026-09-16
"""
import re
import unicodedata

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY

revision = "7a1f9c3d5e21"
down_revision = "6363667dd91f"
branch_labels = None
depends_on = None


def _slugifier(titre: str) -> str:
    sans_accents = unicodedata.normalize("NFKD", titre).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", sans_accents.lower()).strip("-")
    return slug or "notion"


def upgrade():
    bind = op.get_bind()

    # 1. On met les anciennes tables de côté (renommées, PAS supprimées) :
    #    si quelque chose se passe mal, les données d'origine restent
    #    consultables et rien n'est perdu.
    op.rename_table("fiche", "fiche_backup_migration_notion")
    op.rename_table("cours", "cours_backup_migration_notion")
    op.rename_table("ressource", "ressource_backup_migration_notion")

    # 2. Nouvelle table unifiée + sa table de ressources (même principe
    #    qu'avant, la clé étrangère pointe juste sur "notion" désormais).
    op.create_table(
        "notion",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("titre", sa.Text, nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("resume", sa.Text, nullable=False),
        sa.Column("mots_cles", ARRAY(sa.Text), nullable=False),
        sa.Column("synonymes", ARRAY(sa.Text), nullable=False),
        sa.Column("notions_liees", ARRAY(sa.Text), nullable=False),
        sa.Column("origine", sa.String(20), nullable=False),
        sa.Column("date_verification", sa.DateTime, nullable=True),
        sa.Column("contenu", sa.JSON, nullable=False),
        sa.Column("quiz", sa.JSON, nullable=True),
        sa.Column("date_creation", sa.DateTime, nullable=True),
        sa.Column("date_modification", sa.DateTime, nullable=True),
    )
    op.create_index("ix_notion_slug", "notion", ["slug"], unique=True)

    op.create_table(
        "ressource",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("notion_id", sa.Integer, sa.ForeignKey("notion.id"), nullable=False),
        sa.Column("libelle", sa.Text, nullable=False),
        sa.Column("url", sa.Text, nullable=False),
    )

    notion_table = sa.table(
        "notion",
        sa.column("id", sa.Integer),
        sa.column("titre", sa.Text),
        sa.column("slug", sa.String),
        sa.column("resume", sa.Text),
        sa.column("mots_cles", ARRAY(sa.Text)),
        sa.column("synonymes", ARRAY(sa.Text)),
        sa.column("notions_liees", ARRAY(sa.Text)),
        sa.column("origine", sa.String),
        sa.column("date_verification", sa.DateTime),
        sa.column("contenu", sa.JSON),
        sa.column("quiz", sa.JSON),
        sa.column("date_creation", sa.DateTime),
    )
    ressource_table = sa.table(
        "ressource",
        sa.column("id", sa.Integer),
        sa.column("notion_id", sa.Integer),
        sa.column("libelle", sa.Text),
        sa.column("url", sa.Text),
    )

    slugs_utilises = set()

    def slug_unique(titre: str) -> str:
        base = _slugifier(titre)
        slug = base
        compteur = 2
        while slug in slugs_utilises:
            slug = f"{base}-{compteur}"
            compteur += 1
        slugs_utilises.add(slug)
        return slug

    # 3. Fiches vérifiées -> notion (origine="verifiee"). Chaque champ texte
    #    devient un bloc "texte" ; "pour_aller_plus_loin" devient un bloc
    #    "a_retenir" (même esprit : l'essentiel à retenir/creuser ensuite).
    fiches = bind.execute(
        sa.text(
            "SELECT id, titre, definition, resume, mots_cles, concepts_cles, "
            "prerequis, pour_aller_plus_loin, date_creation, date_modification "
            "FROM fiche_backup_migration_notion ORDER BY id"
        )
    ).mappings().all()

    correspondance_fiche_id = {}

    for fiche in fiches:
        blocs = [
            {
                "type": "texte",
                "titre": "Définition",
                "texte": fiche["definition"],
                "code": "",
                "langage": "",
            }
        ]
        if fiche["concepts_cles"]:
            blocs.append(
                {
                    "type": "texte",
                    "titre": "Concepts clés",
                    "texte": ", ".join(fiche["concepts_cles"]),
                    "code": "",
                    "langage": "",
                }
            )
        if fiche["prerequis"]:
            blocs.append(
                {
                    "type": "texte",
                    "titre": "Prérequis",
                    "texte": ", ".join(fiche["prerequis"]),
                    "code": "",
                    "langage": "",
                }
            )
        if fiche["pour_aller_plus_loin"]:
            blocs.append(
                {
                    "type": "a_retenir",
                    "titre": "Pour aller plus loin",
                    "texte": fiche["pour_aller_plus_loin"],
                    "code": "",
                    "langage": "",
                }
            )

        slug = slug_unique(fiche["titre"])
        resultat = bind.execute(
            notion_table.insert()
            .values(
                titre=fiche["titre"],
                slug=slug,
                resume=fiche["resume"],
                mots_cles=list(fiche["mots_cles"] or []),
                synonymes=[],
                notions_liees=[],
                origine="verifiee",
                date_verification=fiche["date_creation"],
                contenu=blocs,
                quiz=None,
                date_creation=fiche["date_creation"],
            )
            .returning(notion_table.c.id)
        )
        correspondance_fiche_id[fiche["id"]] = resultat.scalar_one()

    # 4. Ressources -> repointées sur le nouvel id notion (via la
    #    correspondance construite juste au-dessus).
    ressources = bind.execute(
        sa.text(
            "SELECT fiche_id, libelle, url FROM ressource_backup_migration_notion ORDER BY id"
        )
    ).mappings().all()
    for ressource in ressources:
        nouveau_id = correspondance_fiche_id.get(ressource["fiche_id"])
        if nouveau_id is None:
            continue
        bind.execute(
            ressource_table.insert().values(
                notion_id=nouveau_id,
                libelle=ressource["libelle"],
                url=ressource["url"],
            )
        )

    # 5. Cours générés par l'IA -> notion (origine="generee_ia").
    #    L'introduction devient un bloc "texte", chaque section devient un
    #    bloc "code" (si elle a un exemple) ou "texte" sinon, et la
    #    conclusion devient un bloc "a_retenir".
    cours_liste = bind.execute(
        sa.text(
            "SELECT terme, titre, introduction, sections, conclusion, date_creation "
            "FROM cours_backup_migration_notion ORDER BY id"
        )
    ).mappings().all()

    for cours in cours_liste:
        blocs = [
            {
                "type": "texte",
                "titre": "Introduction",
                "texte": cours["introduction"],
                "code": "",
                "langage": "",
            }
        ]
        sections = cours["sections"] or []
        for section in sections:
            if section.get("code"):
                blocs.append(
                    {
                        "type": "code",
                        "titre": section.get("sous_titre", ""),
                        "texte": section.get("texte", ""),
                        "code": section.get("code", ""),
                        "langage": section.get("langage", ""),
                    }
                )
            else:
                blocs.append(
                    {
                        "type": "texte",
                        "titre": section.get("sous_titre", ""),
                        "texte": section.get("texte", ""),
                        "code": "",
                        "langage": "",
                    }
                )
        if cours["conclusion"]:
            blocs.append(
                {
                    "type": "a_retenir",
                    "titre": "Pour aller plus loin",
                    "texte": cours["conclusion"],
                    "code": "",
                    "langage": "",
                }
            )

        introduction = cours["introduction"] or ""
        resume = introduction[:180].strip()
        if len(introduction) > 180:
            resume += "…"

        titre = cours["titre"] or cours["terme"]
        slug = slug_unique(titre)
        bind.execute(
            notion_table.insert().values(
                titre=titre,
                slug=slug,
                resume=resume,
                mots_cles=[cours["terme"]],
                synonymes=[],
                notions_liees=[],
                origine="generee_ia",
                date_verification=None,
                contenu=blocs,
                quiz=None,
                date_creation=cours["date_creation"],
            )
        )


def downgrade():
    op.drop_table("ressource")
    op.drop_table("notion")
    op.rename_table("ressource_backup_migration_notion", "ressource")
    op.rename_table("cours_backup_migration_notion", "cours")
    op.rename_table("fiche_backup_migration_notion", "fiche")