from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.api_client import APIError, api_request
from app.decorators import admin_required

bp = Blueprint("ubicaciones", __name__, url_prefix="/ubicaciones")


def _load_form_data():
    sectores = api_request("get", "/sectores")
    zonas = api_request("get", "/zonas")
    return {"sectores": sectores, "zonas": zonas}


def _sector_label(sector: dict) -> str:
    zona = sector.get("zona", {})
    return f"{zona.get('nombre', '?')} / {sector.get('nombre', '?')}"


@bp.route("")
@admin_required
def listar():
    try:
        ubicaciones = api_request("get", "/ubicaciones")
    except APIError as exc:
        flash(exc.message, "danger")
        ubicaciones = []
    return render_template("ubicaciones/list.html", ubicaciones=ubicaciones)


@bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def crear():
    form_data = _load_form_data()

    if request.method == "POST":
        payload = {"id_sector": int(request.form["id_sector"])}
        try:
            api_request("post", "/ubicaciones", data=payload)
            flash("Ubicación creada.", "success")
            return redirect(url_for("ubicaciones.listar"))
        except APIError as exc:
            flash(exc.message, "danger")

    return render_template(
        "ubicaciones/form.html",
        ubicacion=None,
        sector_label=_sector_label,
        **form_data,
    )


@bp.route("/<int:ubicacion_id>/editar", methods=["GET", "POST"])
@admin_required
def editar(ubicacion_id: int):
    form_data = _load_form_data()

    try:
        ubicaciones = api_request("get", "/ubicaciones")
        ubicacion = next((u for u in ubicaciones if u["id"] == ubicacion_id), None)
        if not ubicacion:
            flash("Ubicación no encontrada.", "danger")
            return redirect(url_for("ubicaciones.listar"))
    except APIError as exc:
        flash(exc.message, "danger")
        return redirect(url_for("ubicaciones.listar"))

    if request.method == "POST":
        payload = {"id_sector": int(request.form["id_sector"])}
        try:
            api_request("put", f"/ubicaciones/{ubicacion_id}", data=payload)
            flash("Ubicación actualizada.", "success")
            return redirect(url_for("ubicaciones.listar"))
        except APIError as exc:
            flash(exc.message, "danger")

    return render_template(
        "ubicaciones/form.html",
        ubicacion=ubicacion,
        sector_label=_sector_label,
        **form_data,
    )


@bp.route("/<int:ubicacion_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(ubicacion_id: int):
    try:
        api_request("delete", f"/ubicaciones/{ubicacion_id}")
        flash("Ubicación eliminada.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("ubicaciones.listar"))
