from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.api_client import APIError, api_request
from app.decorators import admin_required

bp = Blueprint("rutas", __name__, url_prefix="/rutas")


def _load_form_data():
    usuarios = api_request("get", "/usuarios")
    recolectores = [u for u in usuarios if u.get("tipo_usuario", {}).get("tipo") == "recolector"]
    contenedores = api_request("get", "/contenedores")
    return {"usuarios": usuarios, "recolectores": recolectores, "contenedores": contenedores}


@bp.route("")
@admin_required
def listar():
    try:
        form_data = _load_form_data()
        resumenes = api_request("get", "/rutas")
        rutas = []
        for resumen in resumenes:
            detalle = api_request("get", f"/rutas/{resumen['id']}")
            detalle["selected_ids"] = [
                d["contenedor"]["id"] for d in detalle.get("detalles", [])
            ]
            rutas.append(detalle)
        usuarios_map = {u["id"]: u for u in form_data["usuarios"]}
    except APIError as exc:
        flash(exc.message, "danger")
        rutas = []
        usuarios_map = {}
        form_data = {"recolectores": [], "contenedores": []}

    return render_template(
        "rutas/list.html",
        rutas=rutas,
        usuarios=usuarios_map,
        recolectores=form_data["recolectores"],
        contenedores=form_data["contenedores"],
    )


@bp.route("/nuevo", methods=["POST"])
@admin_required
def crear():
    ids_contenedores = [int(x) for x in request.form.getlist("ids_contenedores")]
    if not ids_contenedores:
        flash("Selecciona al menos un contenedor para la ruta.", "warning")
        return redirect(url_for("rutas.listar"))

    payload = {
        "nombre": request.form["nombre"].strip(),
        "id_usuario": int(request.form["id_usuario"]),
        "fecha": request.form["fecha"],
        "hora_inicio": request.form.get("hora_inicio") or None,
        "hora_fin": request.form.get("hora_fin") or None,
        "ids_contenedores": ids_contenedores,
    }
    try:
        api_request("post", "/rutas", data=payload)
        flash("Ruta creada.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("rutas.listar"))


@bp.route("/<int:ruta_id>/editar", methods=["POST"])
@admin_required
def editar(ruta_id: int):
    ids_contenedores = [int(x) for x in request.form.getlist("ids_contenedores")]
    if not ids_contenedores:
        flash("Selecciona al menos un contenedor para la ruta.", "warning")
        return redirect(url_for("rutas.listar"))

    payload = {
        "nombre": request.form["nombre"].strip(),
        "id_usuario": int(request.form["id_usuario"]),
        "fecha": request.form["fecha"],
        "hora_inicio": request.form.get("hora_inicio") or None,
        "hora_fin": request.form.get("hora_fin") or None,
        "ids_contenedores": ids_contenedores,
    }
    try:
        api_request("put", f"/rutas/{ruta_id}", data=payload)
        flash("Ruta actualizada.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("rutas.listar"))


@bp.route("/<int:ruta_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(ruta_id: int):
    try:
        api_request("delete", f"/rutas/{ruta_id}")
        flash("Ruta eliminada.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("rutas.listar"))
