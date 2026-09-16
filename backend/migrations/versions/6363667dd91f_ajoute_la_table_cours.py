"""ajoute la table cours

Revision ID: 6363667dd91f
Revises: 0002_unaccent
Create Date: 2026-09-15 23:20:29.676931

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6363667dd91f'
down_revision = '0002_unaccent'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('cours',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('terme', sa.String(length=255), nullable=False),
    sa.Column('titre', sa.Text(), nullable=False),
    sa.Column('introduction', sa.Text(), nullable=False),
    sa.Column('sections', sa.JSON(), nullable=False),
    sa.Column('conclusion', sa.Text(), nullable=True),
    sa.Column('date_creation', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('cours', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_cours_terme'), ['terme'], unique=True)


def downgrade():
    with op.batch_alter_table('cours', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_cours_terme'))

    op.drop_table('cours')