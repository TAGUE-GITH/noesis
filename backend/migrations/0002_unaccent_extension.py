"""active l'extension unaccent

Revision ID: 0002_unaccent
Revises: b9f0104e165c
Create Date: 2026-09-15
"""
from alembic import op

revision = "0002_unaccent"
down_revision = "b9f0104e165c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")


def downgrade():
    op.execute("DROP EXTENSION IF EXISTS unaccent;")