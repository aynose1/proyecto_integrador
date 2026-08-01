"""Agregar peso_actual a contenedores y tabla registros_peso.

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-01

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # server_default="0" para que las filas ya existentes queden en 0
    # (equivalente a "sin lectura todavía") en vez de fallar el ALTER
    # por ser NOT NULL sobre una tabla con datos.
    op.add_column(
        "contenedores",
        sa.Column("peso_actual", sa.Numeric(7, 2), nullable=False, server_default="0"),
    )

    op.create_table(
        "registros_peso",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_contenedor", sa.Integer(), nullable=False),
        sa.Column("fecha_hora", sa.DateTime(), nullable=False),
        sa.Column("peso_kg", sa.Numeric(7, 2), nullable=False),
        sa.Column("origen", sa.Enum("sensor", "manual", name="origenregistro"), nullable=False),
        sa.ForeignKeyConstraint(["id_contenedor"], ["contenedores.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_registros_peso_fecha_hora"), "registros_peso", ["fecha_hora"], unique=False
    )
    op.create_index(
        op.f("ix_registros_peso_id_contenedor"), "registros_peso", ["id_contenedor"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_registros_peso_id_contenedor"), table_name="registros_peso")
    op.drop_index(op.f("ix_registros_peso_fecha_hora"), table_name="registros_peso")
    op.drop_table("registros_peso")
    op.drop_column("contenedores", "peso_actual")
