from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.api_client import APIError, api_request
from app.decorators import admin_required

bp = Blueprint("ubicaciones", __name__, url_prefix="/ubicaciones")


@bp.route("")
@admin_required
def listar():
    tab = request.args.get("tab", "zonas")
    if tab not in {"zonas", "sectores"}:
        tab = "zonas"
    try:
        sectores = api_request("get", "/sectores")
        zonas = api_request("get", "/zonas")
    except APIError as exc:
        flash(exc.message, "danger")
        sectores = []
        zonas = []
    return render_template(
        "ubicaciones/list.html",
        sectores=sectores,
        zonas=zonas,
        tab=tab,
    )


@bp.route("/zonas/nuevo", methods=["POST"])
@admin_required
def crear_zona():
    payload = {"nombre": request.form["nombre"].strip()}
    try:
        api_request("post", "/zonas", data=payload)
        flash("Zona creada.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("ubicaciones.listar", tab="zonas"))


@bp.route("/zonas/<int:zona_id>/editar", methods=["POST"])
@admin_required
def editar_zona(zona_id: int):
    payload = {"nombre": request.form["nombre"].strip()}
    try:
        api_request("put", f"/zonas/{zona_id}", data=payload)
        flash("Zona actualizada.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("ubicaciones.listar", tab="zonas"))


@bp.route("/zonas/<int:zona_id>/eliminar", methods=["POST"])
@admin_required
def eliminar_zona(zona_id: int):
    try:
        api_request("delete", f"/zonas/{zona_id}")
        flash("Zona eliminada.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("ubicaciones.listar", tab="zonas"))


@bp.route("/sectores/nuevo", methods=["POST"])
@admin_required
def crear_sector():
    payload = {
        "nombre": request.form["nombre"].strip(),
        "id_zona": int(request.form["id_zona"]),
    }
    try:
        api_request("post", "/sectores", data=payload)
        flash("Sector creado.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("ubicaciones.listar", tab="sectores"))


@bp.route("/sectores/<int:sector_id>/editar", methods=["POST"])
@admin_required
def editar_sector(sector_id: int):
    payload = {
        "nombre": request.form["nombre"].strip(),
        "id_zona": int(request.form["id_zona"]),
    }
    try:
        api_request("put", f"/sectores/{sector_id}", data=payload)
        flash("Sector actualizado.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("ubicaciones.listar", tab="sectores"))


@bp.route("/sectores/<int:sector_id>/eliminar", methods=["POST"])
@admin_required
def eliminar_sector(sector_id: int):
    try:
        api_request("delete", f"/sectores/{sector_id}")
        flash("Sector eliminado.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("ubicaciones.listar", tab="sectores"))
