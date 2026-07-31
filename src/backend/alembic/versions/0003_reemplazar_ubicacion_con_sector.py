"""Reemplazar ubicación con sector directamente en contenedor.

Revision ID: 0003
Revises: 0002_seed_catalogos
Create Date: 2025-01-22

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002_seed_catalogos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar nueva columna id_sector
    op.add_column(
        "contenedores",
        sa.Column("id_sector", sa.Integer(), nullable=True)
    )

    # Crear FK hacia sectores
    op.create_foreign_key(
        "fk_contenedores_id_sector",
        "contenedores",
        "sectores",
        ["id_sector"],
        ["id"],
    )

    # Migrar datos desde ubicaciones hacia sectores
    op.execute(
        """
        UPDATE contenedores
        SET id_sector = (
            SELECT ubicaciones.id_sector
            FROM ubicaciones
            WHERE ubicaciones.id = contenedores.id_ubicacion
        )
        WHERE id_ubicacion IS NOT NULL
        """
    )

    # Convertir id_sector a NOT NULL
    op.alter_column(
        "contenedores",
        "id_sector",
        existing_type=sa.Integer(),
        nullable=False
    )

    # Eliminar FK antigua
    # Nombre real generado por MySQL:
    # contenedores_ibfk_2
    op.drop_constraint(
        "contenedores_ibfk_2",
        "contenedores",
        type_="foreignkey"
    )

    # Eliminar columna antigua
    op.drop_column(
        "contenedores",
        "id_ubicacion"
    )

    # Eliminar tabla ubicaciones
    op.drop_table("ubicaciones")


def downgrade() -> None:
    # Recrear tabla ubicaciones
    op.create_table(
        "ubicaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("id_sector", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_sector"],
            ["sectores.id"],
            name="fk_ubicaciones_id_sector"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Agregar columna id_ubicacion nuevamente
    op.add_column(
        "contenedores",
        sa.Column("id_ubicacion", sa.Integer(), nullable=True)
    )

    # Crear ubicaciones desde sectores existentes
    op.execute(
        """
        INSERT INTO ubicaciones (id_sector)
        SELECT DISTINCT id_sector
        FROM contenedores
        """
    )

    # Restaurar relaciones
    op.execute(
        """
        UPDATE contenedores
        SET id_ubicacion = (
            SELECT ubicaciones.id
            FROM ubicaciones
            WHERE ubicaciones.id_sector = contenedores.id_sector
        )
        """
    )

    # Convertir id_ubicacion a NOT NULL
    op.alter_column(
        "contenedores",
        "id_ubicacion",
        existing_type=sa.Integer(),
        nullable=False
    )

    # Crear FK antigua
    op.create_foreign_key(
        "fk_contenedores_id_ubicacion",
        "contenedores",
        "ubicaciones",
        ["id_ubicacion"],
        ["id"],
    )

    # Eliminar FK nueva
    op.drop_constraint(
        "fk_contenedores_id_sector",
        "contenedores",
        type_="foreignkey"
    )

    # Eliminar id_sector
    op.drop_column(
        "contenedores",
        "id_sector"
    )