from datetime import date, datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.api_client import APIError, api_request
from app.decorators import admin_required

bp = Blueprint("notificaciones", __name__, url_prefix="/notificaciones")

# Un ícono distinto por motivo, para que se distingan de un vistazo en
# el centro de notificaciones (igual que Gmail/Slack usan íconos por
# tipo de evento). Si aparece un motivo nuevo que no está en este mapa,
# se usa el genérico de "Otro".
ICONOS_MOTIVO = {
    "sensor dañado": "bi-cpu",
    "contenedor dañado": "bi-trash3",
    "lectura errónea": "bi-exclamation-triangle",
    "otro": "bi-info-circle",
}


def _icono_motivo(motivo: str) -> str:
    return ICONOS_MOTIVO.get((motivo or "").lower(), "bi-info-circle")


def _tiempo_relativo(fecha_hora_str: str | None) -> str:
    """
    "Hace 5 min", "Hace 3 h", "Ayer", "Hace 4 días" -- mucho más legible
    de un vistazo que una fecha ISO cruda, como ya hace cualquier centro
    de notificaciones (Gmail, Slack, etc.).
    """
    if not fecha_hora_str:
        return "—"
    try:
        momento = datetime.fromisoformat(fecha_hora_str)
    except ValueError:
        return fecha_hora_str

    segundos = (datetime.now() - momento).total_seconds()
    if segundos < 0:
        segundos = 0

    if segundos < 60:
        return "Justo ahora"
    minutos = int(segundos // 60)
    if minutos < 60:
        return f"Hace {minutos} min"
    horas = int(minutos // 60)
    if horas < 24:
        return f"Hace {horas} h"
    dias = int(horas // 24)
    if dias == 1:
        return "Ayer"
    if dias < 7:
        return f"Hace {dias} días"
    return momento.strftime("%d/%m/%Y")


def _agrupar_por_fecha(incidencias: list[dict]) -> list[dict]:
    """
    Agrupa en las mismas franjas que ya usan Gmail/Slack/Classroom:
    Hoy, Ayer, Esta semana, Más antiguo -- en vez de una tabla plana
    donde hay que leer la fecha de cada fila para ubicarte en el tiempo.
    """
    hoy = date.today()
    ayer = hoy - timedelta(days=1)
    limite_semana = hoy - timedelta(days=7)

    franjas = {"Hoy": [], "Ayer": [], "Esta semana": [], "Más antiguo": []}
    for inc in incidencias:
        try:
            fecha_item = datetime.fromisoformat(inc["fecha_hora"]).date()
        except (ValueError, KeyError, TypeError):
            fecha_item = None

        if fecha_item == hoy:
            franjas["Hoy"].append(inc)
        elif fecha_item == ayer:
            franjas["Ayer"].append(inc)
        elif fecha_item is not None and fecha_item > limite_semana:
            franjas["Esta semana"].append(inc)
        else:
            franjas["Más antiguo"].append(inc)

    return [{"titulo": titulo, "notificaciones": items} for titulo, items in franjas.items() if items]


def _preparar_incidencias(incidencias: list[dict]) -> list[dict]:
    # Más reciente primero, dentro de cada franja y en general.
    ordenadas = sorted(incidencias, key=lambda i: i.get("fecha_hora") or "", reverse=True)
    for inc in ordenadas:
        inc["tiempo_relativo"] = _tiempo_relativo(inc.get("fecha_hora"))
        inc["icono"] = _icono_motivo(inc.get("motivo", {}).get("motivo"))
    return ordenadas


def contar_pendientes() -> int:
    """
    Usado también por el context_processor (ver web/app/__init__.py)
    para el contador del sidebar -- una sola fuente de verdad para "qué
    cuenta como pendiente", sin duplicar el criterio en dos lugares.
    """
    try:
        incidencias = api_request("get", "/incidencias")
    except APIError:
        return 0
    return sum(1 for i in incidencias if i.get("estado", {}).get("estado") != "atendido")


@bp.route("")
@admin_required
def listar():
    estado_filtro = request.args.get("estado") or None
    motivo_filtro = request.args.get("motivo") or None

    try:
        incidencias = api_request("get", "/incidencias")
        contenedores = api_request("get", "/contenedores")
        usuarios = api_request("get", "/usuarios")
        contenedores_por_id = {c["id"]: c for c in contenedores}
        usuarios_por_id = {u["id"]: u for u in usuarios}
    except APIError as exc:
        flash(exc.message, "danger")
        incidencias = []
        contenedores_por_id = {}
        usuarios_por_id = {}

    motivos_disponibles = sorted({i["motivo"]["motivo"] for i in incidencias if i.get("motivo")})

    if estado_filtro:
        incidencias = [i for i in incidencias if i.get("estado", {}).get("estado") == estado_filtro]
    if motivo_filtro:
        incidencias = [i for i in incidencias if i.get("motivo", {}).get("motivo") == motivo_filtro]

    incidencias = _preparar_incidencias(incidencias)

    return render_template(
        "notificaciones/list.html",
        grupos=_agrupar_por_fecha(incidencias),
        total=len(incidencias),
        contenedores_por_id=contenedores_por_id,
        usuarios_por_id=usuarios_por_id,
        motivos_disponibles=motivos_disponibles,
        estado_filtro=estado_filtro,
        motivo_filtro=motivo_filtro,
    )


@bp.route("/incidencias/<int:incidencia_id>/atender", methods=["POST"])
@admin_required
def atender_incidencia(incidencia_id: int):
    try:
        estados = api_request("get", "/catalogos/estados")
        estado_atendido = next((e for e in estados if e["estado"].lower() == "atendido"), None)
        if not estado_atendido:
            flash("El catálogo de estados no tiene 'atendido'. Revisa el seeder.", "danger")
            return redirect(url_for("notificaciones.listar"))
        api_request("patch", f"/incidencias/{incidencia_id}", data={"id_estado": estado_atendido["id"]})
        flash("Incidencia marcada como atendida.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("notificaciones.listar", **request.args))
