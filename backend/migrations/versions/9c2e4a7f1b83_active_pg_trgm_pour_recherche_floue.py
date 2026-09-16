"""active pg_trgm pour la recherche floue (increment B)

Revision ID: 9c2e4a7f1b83
Revises: 7a1f9c3d5e21
Create Date: 2026-09-16
"""
from alembic import op

revision = "9c2e4a7f1b83"
down_revision = "7a1f9c3d5e21"
branch_labels = None
depends_on = None


def upgrade():
    # pg_trgm : découpe les chaînes en trigrammes (groupes de 3 caractères)
    # et permet de comparer leur similarité — c'est ce qui rend la
    # recherche tolérante aux fautes de frappe (ex. "algoritme" reste
    # proche d'"algorithme" même mal orthographié), contrairement à la
    # recherche par mot entier exact déjà en place.
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    # Index trigramme sur le titre : accélère la recherche floue. Peu
    # utile sur le volume actuel de notions, mais une bonne pratique à
    # poser dès maintenant plutôt qu'une fois la table devenue grosse.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_notion_titre_trgm "
        "ON notion USING gin (titre gin_trgm_ops)"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_notion_titre_trgm")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")