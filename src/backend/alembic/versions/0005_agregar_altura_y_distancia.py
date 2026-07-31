"""Agregar altura_cm a contenedores y distancia_cm a registros_nivel.

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-24

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Nullable: los contenedores ya existentes no tienen este dato hasta
    # que el administrador lo capture desde la web. El endpoint del
    # sensor rechaza la lectura (con un mensaje claro) si intenta
    # calcular el nivel de un contenedor sin altura_cm configurada.
    op.add_column(
        "contenedores",
        sa.Column("altura_cm", sa.Numeric(6, 2), nullable=True),
    )

    # Guarda la distancia cruda que mandó el sensor, para poder revisar
    # el cálculo después. NULL en lecturas manuales (no vienen de sensor).
    op.add_column(
        "registros_nivel",
        sa.Column("distancia_cm", sa.Numeric(6, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("registros_nivel", "distancia_cm")
    op.drop_column("contenedores", "altura_cm")
