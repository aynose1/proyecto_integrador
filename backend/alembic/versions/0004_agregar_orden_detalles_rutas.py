"""Agregar campo orden a detalles_rutas.

Revision ID: 0004
Revises: 0003
Create Date: 2025-01-22

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar columna orden con valor temporal 0
    op.add_column(
        "detalles_rutas",
        sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
    )

    # Actualizar valores de orden basado en el orden de creación (id)
    # Se usa tabla derivada porque MySQL no permite actualizar
    # una tabla leyendo directamente de la misma tabla en una subconsulta.
    op.execute(
        """
        UPDATE detalles_rutas dr
        JOIN (
            SELECT 
                id,
                ROW_NUMBER() OVER (
                    PARTITION BY id_ruta 
                    ORDER BY id
                ) AS nuevo_orden
            FROM detalles_rutas
        ) tmp ON dr.id = tmp.id
        SET dr.orden = tmp.nuevo_orden
        """
    )

    # Quitar el valor por defecto después de poblar datos existentes
    op.alter_column(
        "detalles_rutas",
        "orden",
        existing_type=sa.Integer(),
        server_default=None,
        nullable=False
    )


def downgrade() -> None:
    op.drop_column(
        "detalles_rutas",
        "orden"
    )