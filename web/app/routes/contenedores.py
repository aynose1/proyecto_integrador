from io import BytesIO

import qrcode
from flask import Blueprint, Response, abort, flash, redirect, render_template, request, url_for

from app.api_client import APIError, api_request
from app.decorators import admin_required

bp = Blueprint("contenedores", __name__, url_prefix="/contenedores")


def _sector_label(sector: dict) -> str:
    zona = sector.get("zona", {})
    return f"ID {sector['id']} — {zona.get('nombre', '?')} / {sector.get('nombre', '?')}"


@bp.route("")
@admin_required
def listar():
    try:
        contenedores = api_request("get", "/contenedores")
        sectores = api_request("get", "/sectores")
        estados = api_request("get", "/catalogos/estados")
    except APIError as exc:
        flash(exc.message, "danger")
        contenedores = []
        sectores = []
        estados = []
    return render_template(
        "contenedores/list.html",
        contenedores=contenedores,
        sectores=sectores,
        estados=estados,
        sector_label=_sector_label,
    )


@bp.route("/nuevo", methods=["POST"])
@admin_required
def crear():
    payload = {
        "nombre": request.form["nombre"].strip(),
        "codigo_contenedor": request.form["codigo_contenedor"].strip(),
        "capacidad_max": float(request.form["capacidad_max"]),
        "id_sector": int(request.form["id_sector"]),
        "id_estado": int(request.form["id_estado"]),
    }
    try:
        api_request("post", "/contenedores", data=payload)
        flash("Contenedor registrado.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("contenedores.listar"))


@bp.route("/<int:contenedor_id>/editar", methods=["POST"])
@admin_required
def editar(contenedor_id: int):
    payload = {
        "nombre": request.form["nombre"].strip(),
        "capacidad_max": float(request.form["capacidad_max"]),
        "id_sector": int(request.form["id_sector"]),
        "id_estado": int(request.form["id_estado"]),
    }
    try:
        api_request("put", f"/contenedores/{contenedor_id}", data=payload)
        flash("Contenedor actualizado.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("contenedores.listar"))


@bp.route("/<int:contenedor_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(contenedor_id: int):
    try:
        api_request("delete", f"/contenedores/{contenedor_id}")
        flash("Contenedor eliminado.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("contenedores.listar"))


@bp.route("/<int:contenedor_id>/qr.png")
@admin_required
def qr_png(contenedor_id: int):
    """
    Genera la imagen del código QR de un contenedor. Codifica únicamente
    codigo_contenedor (el mismo identificador que ya usa el contenedor
    como dispositivo y que la app móvil mandará a
    POST /rutas/{id}/recolectar al escanearlo).
    """
    try:
        contenedor = api_request("get", f"/contenedores/{contenedor_id}")
    except APIError:
        abort(404)

    img = qrcode.make(contenedor["codigo_contenedor"], border=2)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    response = Response(buffer.getvalue(), mimetype="image/png")
    if request.args.get("download"):
        filename = f"qr-{contenedor['codigo_contenedor']}.png"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response
