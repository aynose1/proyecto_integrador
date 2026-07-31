"""seed catalogos y primer administrador

Revision ID: 0002_seed_catalogos
Revises: 0001_esquema_inicial
Create Date: 2026-07-13

IMPORTANTE: down_revision debe apuntar al id real que Alembic generó
para tu migración de esquema inicial (la que sale de
`alembic revision --autogenerate -m "esquema inicial"`).
Reemplaza "0001_esquema_inicial" abajo por ese id si es distinto.
"""
from datetime import datetime

import sqlalchemy as sa
from alembic import op
from passlib.context import CryptContext

revision = "0002_seed_catalogos"
down_revision = "bb05c596672e"
branch_labels = None
depends_on = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def upgrade() -> None:
    tipos_usuarios = sa.table(
        "tipos_usuarios", sa.column("id", sa.Integer), sa.column("tipo", sa.String)
    )
    op.bulk_insert(
        tipos_usuarios,
        [
            {"id": 1, "tipo": "administrador"},
            {"id": 2, "tipo": "recolector"},
        ],
    )

    estados = sa.table("estados", sa.column("id", sa.Integer), sa.column("estado", sa.String))
    op.bulk_insert(
        estados,
        [
            {"id": 1, "estado": "activo"},
            {"id": 2, "estado": "inactivo"},
            {"id": 3, "estado": "mantenimiento"},
            {"id": 4, "estado": "pendiente"},
            {"id": 5, "estado": "recolectado"},
            {"id": 6, "estado": "atendido"},
        ],
    )

    zonas = sa.table("zonas", sa.column("id", sa.Integer), sa.column("nombre", sa.String))
    op.bulk_insert(
        zonas,
        [
            {"id": 1, "nombre": "Edificio A"},
            {"id": 2, "nombre": "Edificio B"},
            {"id": 3, "nombre": "Edificio C"},
        ],
    )
    # Los sectores NO se siembran: el administrador los da de alta desde la
    # web, eligiendo a cuál de las 3 zonas pertenece cada uno.

    motivos_incidencia = sa.table(
        "motivos_incidencia", sa.column("id", sa.Integer), sa.column("motivo", sa.String)
    )
    op.bulk_insert(
        motivos_incidencia,
        [
            {"id": 1, "motivo": "Lectura errónea"},
            {"id": 2, "motivo": "Sensor dañado"},
            {"id": 3, "motivo": "Contenedor dañado"},
            {"id": 4, "motivo": "Otro"},
        ],
    )

    tipos_notificacion = sa.table(
        "tipos_notificacion", sa.column("id", sa.Integer), sa.column("tipo", sa.String)
    )
    op.bulk_insert(
        tipos_notificacion,
        [
            {"id": 1, "tipo": "Nivel alto"},
            {"id": 2, "tipo": "Incidencia reportada"},
        ],
    )

    # Primer administrador, para poder iniciar sesión y crear al resto de
    # usuarios desde la web. CAMBIA la contraseña inmediatamente después
    # del primer despliegue.
    usuarios = sa.table(
        "usuarios",
        sa.column("id", sa.Integer),
        sa.column("codigo_usuario", sa.String),
        sa.column("nombre", sa.String),
        sa.column("apellido_paterno", sa.String),
        sa.column("apellido_materno", sa.String),
        sa.column("contrasena_hash", sa.String),
        sa.column("id_tipo_usuario", sa.Integer),
    )
    op.bulk_insert(
        usuarios,
        [
            {
                "id": 1,
                "codigo_usuario": "ADMIN001",
                "nombre": "Administrador",
                "apellido_paterno": "Inicial",
                "apellido_materno": None,
                "contrasena_hash": pwd_context.hash("CambiaEstaClave123!"),
                "id_tipo_usuario": 1,
            }
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM usuarios WHERE id = 1")
    op.execute("DELETE FROM tipos_notificacion")
    op.execute("DELETE FROM motivos_incidencia")
    op.execute("DELETE FROM zonas")
    op.execute("DELETE FROM estados")
    op.execute("DELETE FROM tipos_usuarios")
