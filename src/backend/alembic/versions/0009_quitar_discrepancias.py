"""Quitar deteccion de discrepancias: columnas de detalles_rutas.

Revision ID: 0009
Revises: 0008
Create Date: 2026-08-02

"""

from alembic import op
import sqlalchemy as sa


revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("detalles_rutas", "discrepancia_revisada")
    op.drop_column("detalles_rutas", "fecha_recolectado")


def downgrade() -> None:
    op.add_column("detalles_rutas", sa.Column("fecha_recolectado", sa.DateTime(), nullable=True))
    op.add_column(
        "detalles_rutas",
        sa.Column("discrepancia_revisada", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
