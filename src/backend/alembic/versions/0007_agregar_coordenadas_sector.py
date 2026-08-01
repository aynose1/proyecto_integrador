"""Agregar latitud y longitud a sectores.

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-01

"""

from alembic import op
import sqlalchemy as sa


revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sectores", sa.Column("latitud", sa.Numeric(10, 7), nullable=True))
    op.add_column("sectores", sa.Column("longitud", sa.Numeric(10, 7), nullable=True))


def downgrade() -> None:
    op.drop_column("sectores", "longitud")
    op.drop_column("sectores", "latitud")
