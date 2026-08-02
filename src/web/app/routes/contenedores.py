from io import BytesIO

import qrcode
from flask import Blueprint, Response, abort, flash, redirect, render_template, request, url_for

from app.api_client import APIError, api_request
from app.decorators import admin_required

bp = Blueprint("contenedores", __name__, url_prefix="/contenedores")


def _sector_label(sector: dict) -> str:
    zona = sector.get("zona", {})
    return f"ID {sector['id']} — {zona.get('nombre', '?')} / {sector.get('nombre', '?')}"


def _estados_contenedor(todos_los_estados: list[dict]) -> list[dict]:
    """
    Un contenedor solo admite 'activo'/'inactivo'. El catálogo de
    estados es compartido con DetalleRuta (pendiente/recolectado) e
    Incidencia (pendiente/atendido) — por eso se filtra aquí en vez de
    tocar /catalogos/estados, que otras pantallas sí necesitan completo.
    """
    return [e for e in todos_los_estados if e["estado"].lower() in ("activo", "inactivo")]


@bp.route("")
@admin_required
def listar():
    try:
        contenedores = api_request("get", "/contenedores")
        sectores = api_request("get", "/sectores")
        zonas = api_request("get", "/zonas")
        estados = _estados_contenedor(api_request("get", "/catalogos/estados"))
    except APIError as exc:
        flash(exc.message, "danger")
        contenedores = []
        sectores = []
        zonas = []
        estados = []

    estado_activo = next((e for e in estados if e["estado"].lower() == "activo"), None)
    estado_inactivo = next((e for e in estados if e["estado"].lower() == "inactivo"), None)

    return render_template(
        "contenedores/list.html",
        contenedores=contenedores,
        sectores=sectores,
        zonas=zonas,
        estados=estados,
        estado_activo_id=estado_activo["id"] if estado_activo else None,
        estado_inactivo_id=estado_inactivo["id"] if estado_inactivo else None,
        sector_label=_sector_label,
    )


@bp.route("/nuevo", methods=["POST"])
@admin_required
def crear():
    payload = {
        "nombre": request.form["nombre"].strip(),
        "codigo_contenedor": request.form["codigo_contenedor"].strip(),
        "capacidad_max": float(request.form["capacidad_max"]),
        "altura_cm": float(request.form["altura_cm"]),
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
    # OJO: id_estado NO va aquí — el modal "Editar contenedor" nunca
    # tuvo ese campo a propósito, porque el estado activo/inactivo ya se
    # controla con el switch de la tabla (ver cambiar_estado() abajo).
    # ContenedorUpdate lo tiene como opcional en la API, así que
    # simplemente no enviarlo deja el estado actual intacto.
    payload = {
        "nombre": request.form["nombre"].strip(),
        "capacidad_max": float(request.form["capacidad_max"]),
        "altura_cm": float(request.form["altura_cm"]),
        "id_sector": int(request.form["id_sector"]),
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


@bp.route("/<int:contenedor_id>/estado", methods=["POST"])
@admin_required
def cambiar_estado(contenedor_id: int):
    """Switch rápido activo/inactivo desde la tarjeta, sin abrir el modal de edición."""
    id_estado = request.form.get("id_estado", type=int)
    if not id_estado:
        flash("No se pudo determinar el nuevo estado.", "danger")
        return redirect(url_for("contenedores.listar"))
    try:
        api_request("put", f"/contenedores/{contenedor_id}", data={"id_estado": id_estado})
        flash("Estado del contenedor actualizado.", "success")
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
