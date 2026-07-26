from datetime import date as date_type

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.catalogos import Estado
from app.models.contenedor import Contenedor
from app.models.ruta import DetalleRuta, Ruta
from app.models.usuario import Usuario
from app.models.zona_sector import Sector, Zona

UMBRAL_MEDIO = 50
UMBRAL_ALTO = 80

# date.weekday(): lunes=0 ... domingo=6
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def _distribucion_nivel(contenedores: list[Contenedor]) -> dict:
    total = len(contenedores)
    bajo = medio = alto = 0
    for c in contenedores:
        nivel = float(c.nivel_actual)
        if nivel >= UMBRAL_ALTO:
            alto += 1
        elif nivel >= UMBRAL_MEDIO:
            medio += 1
        else:
            bajo += 1

    def pct(n: int) -> float:
        return round(n / total * 100, 1) if total else 0.0

    return {
        "bajo": bajo,
        "medio": medio,
        "alto": alto,
        "bajo_pct": pct(bajo),
        "medio_pct": pct(medio),
        "alto_pct": pct(alto),
    }


def _promedio_por_zona(db: Session) -> list[dict]:
    filas = (
        db.query(Zona.nombre, func.avg(Contenedor.nivel_actual), func.count(Contenedor.id))
        .select_from(Zona)
        .join(Sector, Sector.id_zona == Zona.id)
        .join(Contenedor, Contenedor.id_sector == Sector.id)
        .group_by(Zona.id, Zona.nombre)
        .order_by(Zona.nombre)
        .all()
    )
    return [
        {
            "zona": nombre,
            "promedio_nivel": round(float(promedio), 1) if promedio is not None else 0.0,
            "total_contenedores": total,
        }
        for nombre, promedio, total in filas
    ]


def _recolecciones_por_dia_semana(db: Session) -> list[dict]:
    """
    Cuenta, sobre TODO el histórico de rutas (no solo hoy — un día no
    alcanza para mostrar un patrón semanal), cuántos contenedores se
    marcaron 'recolectado', agrupados por el día de la semana de la
    fecha de la ruta a la que pertenecen. No se agregó ninguna columna
    nueva: Ruta.fecha ya alcanza para saber el día de la semana.
    """
    fechas = (
        db.query(Ruta.fecha)
        .join(DetalleRuta, DetalleRuta.id_ruta == Ruta.id)
        .join(Estado, DetalleRuta.id_estado == Estado.id)
        .filter(Estado.estado == "recolectado")
        .all()
    )
    conteo = {dia: 0 for dia in DIAS_SEMANA}
    for (fecha,) in fechas:
        conteo[DIAS_SEMANA[fecha.weekday()]] += 1
    return [{"dia": dia, "total": conteo[dia]} for dia in DIAS_SEMANA]


def _recolectores_hoy(db: Session, fecha: date_type) -> list[dict]:
    rutas_hoy = (
        db.query(Ruta)
        .options(selectinload(Ruta.detalles).joinedload(DetalleRuta.estado))
        .filter(Ruta.fecha == fecha)
        .all()
    )
    if not rutas_hoy:
        return []

    por_usuario: dict[int, list[Ruta]] = {}
    for r in rutas_hoy:
        por_usuario.setdefault(r.id_usuario, []).append(r)

    usuarios = db.query(Usuario).filter(Usuario.id.in_(por_usuario.keys())).all()
    resultado = []
    for u in usuarios:
        rutas_u = por_usuario[u.id]
        resultado.append(
            {
                "id": u.id,
                "nombre": f"{u.nombre} {u.apellido_paterno}",
                "codigo_usuario": u.codigo_usuario,
                "rutas_hoy": len(rutas_u),
                "rutas_completadas_hoy": sum(1 for r in rutas_u if r.completada),
            }
        )
    resultado.sort(key=lambda r: r["nombre"])
    return resultado


def _contenedores_criticos(contenedores: list[Contenedor]) -> list[dict]:
    criticos = [c for c in contenedores if float(c.nivel_actual) >= UMBRAL_ALTO]
    criticos.sort(key=lambda c: float(c.nivel_actual), reverse=True)
    return [
        {
            "id": c.id,
            "nombre": c.nombre,
            "codigo_contenedor": c.codigo_contenedor,
            "nivel_actual": float(c.nivel_actual),
            "zona": c.sector.zona.nombre,
            "sector": c.sector.nombre,
        }
        for c in criticos
    ]


def resumen(db: Session, fecha: date_type) -> dict:
    """
    Todo lo referente a CONTENEDORES (total, distribución, promedio por
    zona, críticos) es en tiempo real: nivel_actual siempre refleja
    'ahora', no tiene sentido pedirlo 'a una fecha pasada'. Lo único que
    sí depende de la fecha es la lista de recolectores con ruta
    asignada ESE día — por defecto hoy, pero el parámetro `fecha`
    permite consultar otro día si se necesita.
    """
    contenedores = (
        db.query(Contenedor).options(joinedload(Contenedor.sector).joinedload(Sector.zona)).all()
    )

    return {
        "fecha": fecha,
        "total_contenedores": len(contenedores),
        "contenedores_llenado_alto": sum(1 for c in contenedores if float(c.nivel_actual) >= UMBRAL_ALTO),
        "distribucion_nivel": _distribucion_nivel(contenedores),
        "promedio_por_zona": _promedio_por_zona(db),
        "recolecciones_por_dia_semana": _recolecciones_por_dia_semana(db),
        "recolectores_hoy": _recolectores_hoy(db, fecha),
        "contenedores_criticos": _contenedores_criticos(contenedores),
    }
