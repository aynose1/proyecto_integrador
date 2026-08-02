from datetime import date as date_type
from datetime import datetime, time, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.catalogos import Estado
from app.models.contenedor import Contenedor
from app.models.registro_nivel import RegistroNivel
from app.models.registro_peso import RegistroPeso
from app.models.ruta import DetalleRuta, Ruta
from app.models.usuario import Usuario
from app.models.zona_sector import Sector, Zona

UMBRAL_MEDIO = 50
UMBRAL_ALTO = 80

# date.weekday(): lunes=0 ... domingo=6
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
DIAS_SEMANA_CORTO = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


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


def _pesos_pct_a_fecha(db: Session, fecha: date_type, contenedores: list[Contenedor]) -> dict[int, float]:
    """
    Análogo a _niveles_a_fecha pero para el sensor de peso: reconstruye
    el peso (Kg) más reciente de cada contenedor hasta el final del día
    dado, y lo convierte a porcentaje contra capacidad_max (mismo
    criterio que la barra de peso en Contenedores/Ver) para poder
    aplicarle los mismos umbrales de color que a nivel.
    """
    cutoff = datetime.combine(fecha, time.max)

    fila_mas_reciente = (
        func.row_number()
        .over(
            partition_by=RegistroPeso.id_contenedor,
            order_by=(RegistroPeso.fecha_hora.desc(), RegistroPeso.id.desc()),
        )
        .label("posicion")
    )
    subq = (
        db.query(RegistroPeso.id_contenedor, RegistroPeso.peso_kg, fila_mas_reciente)
        .filter(RegistroPeso.fecha_hora <= cutoff)
        .subquery()
    )
    filas = db.query(subq.c.id_contenedor, subq.c.peso_kg).filter(subq.c.posicion == 1).all()
    pesos_kg = {id_contenedor: float(peso) for id_contenedor, peso in filas}

    capacidades = {c.id: float(c.capacidad_max) for c in contenedores if c.capacidad_max}
    return {
        id_contenedor: min(100.0, peso / capacidades[id_contenedor] * 100)
        for id_contenedor, peso in pesos_kg.items()
        if id_contenedor in capacidades
    }


def _distribucion(valores_pct: list[float]) -> dict:
    """
    Genérica a propósito: recibe una lista de porcentajes 0-100 (de
    nivel O de peso, no le importa cuál) y los reparte en las 3 franjas.
    """
    total = len(valores_pct)
    bajo = medio = alto = 0
    for valor in valores_pct:
        if valor >= UMBRAL_ALTO:
            alto += 1
        elif valor >= UMBRAL_MEDIO:
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


def _recolecciones_por_dia_semana(db: Session, fecha: date_type) -> list[dict]:
    """
    Cuenta cuántos contenedores se marcaron 'recolectado', agrupados por
    día de la semana, SOLO dentro de la semana actual (lunes a domingo
    que contiene 'fecha' — por defecto hoy). Antes esto usaba TODO el
    histórico de rutas; ahora se acota a la semana en curso.
    """
    inicio_semana = fecha - timedelta(days=fecha.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    fechas = (
        db.query(Ruta.fecha)
        .join(DetalleRuta, DetalleRuta.id_ruta == Ruta.id)
        .join(Estado, DetalleRuta.id_estado == Estado.id)
        .filter(Estado.estado == "recolectado")
        .filter(Ruta.fecha >= inicio_semana, Ruta.fecha <= fin_semana)
        .all()
    )
    conteo = {dia: 0 for dia in DIAS_SEMANA}
    for (fecha_ruta,) in fechas:
        conteo[DIAS_SEMANA[fecha_ruta.weekday()]] += 1
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


def _tendencia_7_dias(db: Session, fecha: date_type, contenedores: list[Contenedor]) -> list[dict]:
    """
    Últimos 7 días (rolling, terminando en 'fecha' -- hoy), un punto por
    día: promedio de nivel y promedio de peso de todos los contenedores
    activos, AMBOS normalizados 0-1 (no 0-100) para poder comparar las
    dos variables en la misma escala en una sola gráfica de líneas.
    Reutiliza exactamente el mismo criterio histórico que ya usa el
    resto del dashboard (_niveles_a_fecha / _pesos_pct_a_fecha), solo
    que aplicado a 7 fechas en vez de una.

    Nota de rendimiento: esto repite las consultas de nivel/peso 7
    veces (una por día) -- aceptable para el volumen de contenedores de
    este proyecto, pero si el catálogo creciera mucho valdría la pena
    una consulta agregada por rango en vez de 7 consultas puntuales.
    """
    resultado = []
    for delta in range(6, -1, -1):
        dia = fecha - timedelta(days=delta)

        niveles_dia = _niveles_a_fecha(db, dia)
        pesos_dia = _pesos_pct_a_fecha(db, dia, contenedores)

        niveles_lista = [niveles_dia[c.id] for c in contenedores if c.id in niveles_dia]
        pesos_lista = [pesos_dia[c.id] for c in contenedores if c.id in pesos_dia]

        promedio_nivel = round((sum(niveles_lista) / len(niveles_lista)) / 100, 3) if niveles_lista else None
        promedio_peso = round((sum(pesos_lista) / len(pesos_lista)) / 100, 3) if pesos_lista else None

        resultado.append(
            {
                "fecha": dia,
                "etiqueta": f"{DIAS_SEMANA_CORTO[dia.weekday()]} {dia.strftime('%d/%m')}",
                "promedio_nivel": promedio_nivel,
                "promedio_peso": promedio_peso,
            }
        )
    return resultado


def _rutas_hoy_progreso(db: Session, fecha: date_type) -> dict:
    """Total de rutas creadas para 'fecha' vs cuántas ya quedaron completadas (todos sus detalles en 'recolectado')."""
    rutas_hoy = (
        db.query(Ruta)
        .options(selectinload(Ruta.detalles).joinedload(DetalleRuta.estado))
        .filter(Ruta.fecha == fecha)
        .all()
    )
    return {
        "total": len(rutas_hoy),
        "completadas": sum(1 for r in rutas_hoy if r.completada),
    }


def resumen(db: Session, fecha: date_type) -> dict:
    """
    total_contenedores siempre es el total ACTUAL (no hay fecha de
    registro guardada por contenedor, así que no puede variar por día).
    Todo lo demás que depende del nivel de llenado (KPI de llenado alto,
    distribución, promedio por zona, críticos) se reconstruye a partir
    del historial de lecturas hasta el final del día consultado — para
    'hoy' esto coincide exactamente con nivel_actual. Lo mismo aplica a
    distribucion_peso, con el historial de RegistroPeso.

    Solo se consideran contenedores en estado 'activo': uno inactivo no
    está en operación, así que no debería contar en ningún KPI ni
    gráfica del dashboard (llenado alto, distribución, promedio por
    zona, críticos, ni en el total).
    """
    contenedores = (
        db.query(Contenedor)
        .join(Estado, Contenedor.id_estado == Estado.id)
        .filter(Estado.estado == "activo")
        .options(joinedload(Contenedor.sector).joinedload(Sector.zona))
        .all()
    )
    niveles = _niveles_a_fecha(db, fecha)
    pesos_pct = _pesos_pct_a_fecha(db, fecha, contenedores)

    contenedores_sin_datos = sum(1 for c in contenedores if c.id not in niveles)
    # niveles/pesos_pct traen lecturas de TODOS los contenedores (las
    # consultas no saben de estados); hay que quedarnos solo con las de
    # los contenedores activos que ya filtramos arriba.
    niveles_lista = [niveles[c.id] for c in contenedores if c.id in niveles]
    pesos_pct_lista = [pesos_pct[c.id] for c in contenedores if c.id in pesos_pct]

    rutas_progreso = _rutas_hoy_progreso(db, fecha)

    return {
        "fecha": fecha,
        "total_contenedores": len(contenedores),
        "contenedores_sin_datos_a_fecha": contenedores_sin_datos,
        "contenedores_llenado_alto": sum(1 for n in niveles_lista if n >= UMBRAL_ALTO),
        "contenedores_peso_alto": sum(1 for p in pesos_pct_lista if p >= UMBRAL_ALTO),
        # "Desbordado": el sensor está midiendo el tope (100%) de lo que
        # puede reportar -- el clamp de /registros-nivel deja nivel_porcentaje
        # en exactamente 100.0 cuando la distancia medida es 0 o negativa.
        "contenedores_nivel_desbordado": sum(1 for n in niveles_lista if n >= 100),
        # "Excede su límite": el peso medido ya alcanzó o superó su
        # capacidad_max (mismo umbral que "crítico" en la barra de peso
        # de Contenedores/Ver).
        "contenedores_peso_excedido": sum(1 for p in pesos_pct_lista if p >= 100),
        "rutas_totales_hoy": rutas_progreso["total"],
        "rutas_completadas_hoy": rutas_progreso["completadas"],
        "distribucion_nivel": _distribucion(niveles_lista),
        "distribucion_peso": _distribucion(pesos_pct_lista),
        "promedio_por_zona": _promedio_por_zona(contenedores, niveles),
        "recolecciones_por_dia_semana": _recolecciones_por_dia_semana(db, fecha),
        "tendencia_7_dias": _tendencia_7_dias(db, fecha, contenedores),
        "recolectores_hoy": _recolectores_hoy(db, fecha),
        "contenedores_criticos": _contenedores_criticos(contenedores, niveles),
    }
