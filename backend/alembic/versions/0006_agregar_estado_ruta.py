"""Agregar estado propio a rutas (pendiente/en progreso/completada/cancelada).

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-25

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Nullable primero: se rellena en el mismo script antes de dejarla
    # como referencia obligatoria de aquí en adelante en el código de
    # la app (a nivel de BD se deja nullable por simplicidad, la app
    # siempre manda un valor al crear una ruta).
    op.add_column("rutas", sa.Column("id_estado", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_rutas_id_estado", "rutas", "estados", ["id_estado"], ["id"]
    )

    conn = op.get_bind()
    estados = sa.table("estados", sa.column("id", sa.Integer), sa.column("estado", sa.String))

    # Este es un estado NUEVO e independiente de si sus contenedores ya
    # se recolectaron (eso lo sigue calculando 'completada'). Se
    # siembran solo los que todavía no existían en el catálogo.
    existentes = {row[0] for row in conn.execute(sa.select(estados.c.estado))}
    faltantes = [e for e in ["en progreso", "completada", "cancelada"] if e not in existentes]
    if faltantes:
        op.bulk_insert(estados, [{"estado": e} for e in faltantes])

    # Backfill de las rutas ya existentes: 'completada' si TODOS sus
    # detalles ya están en 'recolectado', si no 'pendiente'. Es solo un
    # punto de partida razonable — el admin puede ajustarlo a mano
    # (ej. a 'cancelada') donde no aplique.
    conn.execute(sa.text("""
        UPDATE rutas r
        SET id_estado = (
            CASE WHEN NOT EXISTS (
                    SELECT 1 FROM detalles_rutas dr
                    JOIN estados e ON e.id = dr.id_estado
                    WHERE dr.id_ruta = r.id AND e.estado <> 'recolectado'
                 )
                 AND EXISTS (SELECT 1 FROM detalles_rutas dr2 WHERE dr2.id_ruta = r.id)
                THEN (SELECT id FROM estados WHERE estado = 'completada')
                ELSE (SELECT id FROM estados WHERE estado = 'pendiente')
            END
        )
        WHERE r.id_estado IS NULL
    """))


def downgrade() -> None:
    op.drop_constraint("fk_rutas_id_estado", "rutas", type_="foreignkey")
    op.drop_column("rutas", "id_estado")
    op.execute("DELETE FROM estados WHERE estado IN ('en progreso', 'completada', 'cancelada')")
