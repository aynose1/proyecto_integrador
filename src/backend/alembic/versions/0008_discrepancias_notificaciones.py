"""Deteccion de discrepancias: campos en detalles_rutas y notificaciones.

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-01

"""

from alembic import op
import sqlalchemy as sa


revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("detalles_rutas", sa.Column("fecha_recolectado", sa.DateTime(), nullable=True))
    op.add_column(
        "detalles_rutas",
        sa.Column("discrepancia_revisada", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.add_column(
        "notificaciones", sa.Column("leida", sa.Boolean(), nullable=False, server_default=sa.false())
    )
    op.alter_column("notificaciones", "id_usuario", existing_type=sa.Integer(), nullable=True)

    tipos_notificacion = sa.table(
        "tipos_notificacion", sa.column("id", sa.Integer), sa.column("tipo", sa.String)
    )
    op.bulk_insert(tipos_notificacion, [{"id": 3, "tipo": "Posible recolección no confirmada"}])


def downgrade() -> None:
    op.execute("DELETE FROM tipos_notificacion WHERE id = 3")
    op.alter_column("notificaciones", "id_usuario", existing_type=sa.Integer(), nullable=False)
    op.drop_column("notificaciones", "leida")
    op.drop_column("detalles_rutas", "discrepancia_revisada")
    op.drop_column("detalles_rutas", "fecha_recolectado")
