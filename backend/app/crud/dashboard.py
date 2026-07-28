from datetime import date as date_type
from datetime import datetime, time

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.catalogos import Estado
from app.models.contenedor import Contenedor
from app.models.registro_nivel import RegistroNivel
from app.models.ruta import DetalleRuta, Ruta
from app.models.usuario import Usuario
from app.models.zona_sector import Sector, Zona

UMBRAL_MEDIO = 50
UMBRAL_ALTO = 80

# date.weekday(): lunes=0 ... domingo=6
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def _niveles_a_fecha(db: Session, fecha: date_type) -> dict[int, float]:
    """
    Para cada contenedor, reconstruye cuál era su nivel al final del día
    dado: la lectura más reciente (RegistroNivel) con fecha_hora <= fin
    de ese día. Un contenedor que todavía no tenía NINGUNA lectura hasta
    esa fecha simplemente no aparece en el resultado — no se puede saber
    su nivel en un momento anterior a su primera lectura.

    Nota: para 'hoy' esto da exactamente lo mismo que nivel_actual,
    porque nivel_actual siempre es la lectura más reciente que existe,
    y no puede haber lecturas 'del futuro'.
    """
    cutoff = datetime.combine(fecha, time.max)

    fila_mas_reciente = (
        func.row_number()
        .over(
            partition_by=RegistroNivel.id_contenedor,
            order_by=(RegistroNivel.fecha_hora.desc(), RegistroNivel.id.desc()),
        )
        .label("posicion")
    )
    subq = (
        db.query(RegistroNivel.id_contenedor, RegistroNivel.nivel_porcentaje, fila_mas_reciente)
        .filter(RegistroNivel.fecha_hora <= cutoff)
        .subquery()
    )
    filas = db.query(subq.c.id_contenedor, subq.c.nivel_porcentaje).filter(subq.c.posicion == 1).all()
    return {id_contenedor: float(nivel) for id_contenedor, nivel in filas}


def _distribucion_nivel(niveles: list[float]) -> dict:
    total = len(niveles)
    bajo = medio = alto = 0
    for nivel in niveles:
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


def _promedio_por_zona(contenedores: list[Contenedor], niveles: dict[int, float]) -> list[dict]:
    por_zona: dict[str, list[float]] = {}
    for c in contenedores:
        nivel = niveles.get(c.id)
        if nivel is None:
            continue
        por_zona.setdefault(c.sector.zona.nombre, []).append(nivel)

    return [
        {
            "zona": zona_nombre,
            "promedio_nivel": round(sum(valores) / len(valores), 1),
            "total_contenedores": len(valores),
        }
        for zona_nombre, valores in sorted(por_zona.items())
    ]


def _recolecciones_por_dia_semana(db: Session) -> list[dict]:
    """
    Cuenta, sobre TODO el histórico de rutas (no depende del filtro de
    fecha del dashboard — un solo día no alcanza para mostrar un patrón
    semanal), cuántos contenedores se marcaron 'recolectado', agrupados
    por el día de la semana de la fecha de la ruta a la que pertenecen.
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


def _contenedores_criticos(contenedores: list[Contenedor], niveles: dict[int, float]) -> list[dict]:
    criticos = []
    for c in contenedores:
        nivel = niveles.get(c.id)
        if nivel is not None and nivel >= UMBRAL_ALTO:
            criticos.append(
                {
                    "id": c.id,
                    "nombre": c.nombre,
                    "codigo_contenedor": c.codigo_contenedor,
                    "nivel_actual": nivel,
                    "zona": c.sector.zona.nombre,
                    "sector": c.sector.nombre,
                }
            )
    criticos.sort(key=lambda c: c["nivel_actual"], reverse=True)
    return criticos


def resumen(db: Session, fecha: date_type) -> dict:
    """
    total_contenedores siempre es el total ACTUAL (no hay fecha de
    registro guardada por contenedor, así que no puede variar por día).
    Todo lo demás que depende del nivel de llenado (KPI de llenado alto,
    distribución, promedio por zona, críticos) se reconstruye a partir
    del historial de lecturas hasta el final del día consultado — para
    'hoy' esto coincide exactamente con nivel_actual.
    """
    contenedores = db.query(Contenedor).options(joinedload(Contenedor.sector).joinedload(Sector.zona)).all()
    niveles = _niveles_a_fecha(db, fecha)

    contenedores_sin_datos = sum(1 for c in contenedores if c.id not in niveles)
    niveles_lista = list(niveles.values())

    return {
        "fecha": fecha,
        "total_contenedores": len(contenedores),
        "contenedores_sin_datos_a_fecha": contenedores_sin_datos,
        "contenedores_llenado_alto": sum(1 for n in niveles_lista if n >= UMBRAL_ALTO),
        "distribucion_nivel": _distribucion_nivel(niveles_lista),
        "promedio_por_zona": _promedio_por_zona(contenedores, niveles),
        "recolecciones_por_dia_semana": _recolecciones_por_dia_semana(db),
        "recolectores_hoy": _recolectores_hoy(db, fecha),
        "contenedores_criticos": _contenedores_criticos(contenedores, niveles),
    }
