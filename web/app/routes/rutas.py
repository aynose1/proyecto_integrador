from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.api_client import APIError, api_request
from app.decorators import admin_required

bp = Blueprint("rutas", __name__, url_prefix="/rutas")


def _load_form_data():
    usuarios = api_request("get", "/usuarios")
    recolectores = [u for u in usuarios if u.get("tipo_usuario", {}).get("tipo") == "recolector"]
    contenedores = api_request("get", "/contenedores")
    return {"recolectores": recolectores, "contenedores": contenedores}


@bp.route("")
@admin_required
def listar():
    try:
        rutas = api_request("get", "/rutas")
        usuarios = {u["id"]: u for u in api_request("get", "/usuarios")}
    except APIError as exc:
        flash(exc.message, "danger")
        rutas = []
        usuarios = {}

    return render_template("rutas/list.html", rutas=rutas, usuarios=usuarios)


@bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def crear():
    form_data = _load_form_data()

    if request.method == "POST":
        ids_contenedores = [int(x) for x in request.form.getlist("ids_contenedores")]
        payload = {
            "nombre": request.form["nombre"].strip(),
            "id_usuario": int(request.form["id_usuario"]),
            "fecha": request.form["fecha"],
            "hora_inicio": request.form.get("hora_inicio") or None,
            "hora_fin": request.form.get("hora_fin") or None,
            "ids_contenedores": ids_contenedores,
        }
        if not ids_contenedores:
            flash("Selecciona al menos un contenedor para la ruta.", "warning")
            return render_template("rutas/form.html", ruta=None, selected_ids=[], **form_data)

        try:
            api_request("post", "/rutas", data=payload)
            flash("Ruta creada.", "success")
            return redirect(url_for("rutas.listar"))
        except APIError as exc:
            flash(exc.message, "danger")

    return render_template("rutas/form.html", ruta=None, selected_ids=[], **form_data)


@bp.route("/<int:ruta_id>")
@admin_required
def detalle(ruta_id: int):
    try:
        ruta = api_request("get", f"/rutas/{ruta_id}")
    except APIError as exc:
        flash(exc.message, "danger")
        return redirect(url_for("rutas.listar"))
    return render_template("rutas/detail.html", ruta=ruta)


@bp.route("/<int:ruta_id>/editar", methods=["GET", "POST"])
@admin_required
def editar(ruta_id: int):
    form_data = _load_form_data()

    try:
        ruta = api_request("get", f"/rutas/{ruta_id}")
    except APIError as exc:
        flash(exc.message, "danger")
        return redirect(url_for("rutas.listar"))

    if request.method == "POST":
        ids_contenedores = [int(x) for x in request.form.getlist("ids_contenedores")]
        payload = {
            "nombre": request.form["nombre"].strip(),
            "id_usuario": int(request.form["id_usuario"]),
            "fecha": request.form["fecha"],
            "hora_inicio": request.form.get("hora_inicio") or None,
            "hora_fin": request.form.get("hora_fin") or None,
            "ids_contenedores": ids_contenedores,
        }
        if not ids_contenedores:
            flash("Selecciona al menos un contenedor para la ruta.", "warning")
            selected_ids = [d["contenedor"]["id"] for d in ruta.get("detalles", [])]
            return render_template("rutas/form.html", ruta=ruta, selected_ids=selected_ids, **form_data)

        try:
            api_request("put", f"/rutas/{ruta_id}", data=payload)
            flash("Ruta actualizada.", "success")
            return redirect(url_for("rutas.listar"))
        except APIError as exc:
            flash(exc.message, "danger")

    selected_ids = [d["contenedor"]["id"] for d in ruta.get("detalles", [])]
    return render_template("rutas/form.html", ruta=ruta, selected_ids=selected_ids, **form_data)


@bp.route("/<int:ruta_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(ruta_id: int):
    try:
        api_request("delete", f"/rutas/{ruta_id}")
        flash("Ruta eliminada.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("rutas.listar"))
