"""active l'extension unaccent

Revision ID: 0002_unaccent
Revises: 8ef55fc8b660
Create Date: 2026-09-15
"""
from alembic import op

revision = "0002_unaccent"
down_revision = "8ef55fc8b660"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")


def downgrade():
    op.execute("DROP EXTENSION IF EXISTS unaccent;")