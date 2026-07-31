from datetime import date, timedelta

from flask import Blueprint, flash, render_template, request

from app.api_client import APIError, api_request
from app.decorators import admin_required

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@admin_required
def index():
    # Igual que en Rutas: por defecto HOY, navegable a otros días.
    # A diferencia de Rutas, aquí no existe un "ver todas las fechas" —
    # los KPIs/gráficas de nivel siempre necesitan UN día de referencia
    # para reconstruir el nivel histórico de cada contenedor.
    fecha = request.args.get("fecha", date.today().isoformat())
    dia_actual = date.fromisoformat(fecha)

    try:
        resumen = api_request("get", "/dashboard/resumen", params={"fecha": fecha})
    except APIError as exc:
        flash(exc.message, "danger")
        resumen = None

    return render_template(
        "dashboard/index.html",
        resumen=resumen,
        dia_actual=dia_actual,
        dia_anterior=(dia_actual - timedelta(days=1)).isoformat(),
        dia_siguiente=(dia_actual + timedelta(days=1)).isoformat(),
        hoy=date.today().isoformat(),
    )
