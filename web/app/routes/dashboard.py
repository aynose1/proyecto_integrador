from flask import Blueprint, flash, render_template, request

from app.api_client import APIError, api_request
from app.decorators import admin_required

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@admin_required
def index():
    fecha = request.args.get("fecha")  # opcional: ver recolectores de otro día
    try:
        params = {"fecha": fecha} if fecha else {}
        resumen = api_request("get", "/dashboard/resumen", params=params)
    except APIError as exc:
        flash(exc.message, "danger")
        resumen = None
    return render_template("dashboard/index.html", resumen=resumen, fecha_consultada=fecha)
