from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.api_client import APIError, api_request
from app.decorators import admin_required

bp = Blueprint("contenedores", __name__, url_prefix="/contenedores")


def _load_form_data():
    ubicaciones = api_request("get", "/ubicaciones")
    estados = api_request("get", "/catalogos/estados")
    return {"ubicaciones": ubicaciones, "estados": estados}


def _ubicacion_label(ubicacion: dict) -> str:
    sector = ubicacion.get("sector", {})
    zona = sector.get("zona", {})
    return f"ID {ubicacion['id']} — {zona.get('nombre', '?')} / {sector.get('nombre', '?')}"


@bp.route("")
@admin_required
def listar():
    try:
        contenedores = api_request("get", "/contenedores")
    except APIError as exc:
        flash(exc.message, "danger")
        contenedores = []
    return render_template("contenedores/list.html", contenedores=contenedores)


@bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def crear():
    form_data = _load_form_data()

    if request.method == "POST":
        payload = {
            "nombre": request.form["nombre"].strip(),
            "codigo_contenedor": request.form["codigo_contenedor"].strip(),
            "capacidad_max": float(request.form["capacidad_max"]),
            "id_ubicacion": int(request.form["id_ubicacion"]),
            "id_estado": int(request.form["id_estado"]),
        }
        try:
            api_request("post", "/contenedores", data=payload)
            flash("Contenedor registrado.", "success")
            return redirect(url_for("contenedores.listar"))
        except APIError as exc:
            flash(exc.message, "danger")

    return render_template(
        "contenedores/form.html",
        contenedor=None,
        ubicacion_label=_ubicacion_label,
        **form_data,
    )


@bp.route("/<int:contenedor_id>/editar", methods=["GET", "POST"])
@admin_required
def editar(contenedor_id: int):
    form_data = _load_form_data()

    try:
        contenedor = api_request("get", f"/contenedores/{contenedor_id}")
    except APIError as exc:
        flash(exc.message, "danger")
        return redirect(url_for("contenedores.listar"))

    if request.method == "POST":
        payload = {
            "nombre": request.form["nombre"].strip(),
            "capacidad_max": float(request.form["capacidad_max"]),
            "id_ubicacion": int(request.form["id_ubicacion"]),
            "id_estado": int(request.form["id_estado"]),
        }
        try:
            api_request("put", f"/contenedores/{contenedor_id}", data=payload)
            flash("Contenedor actualizado.", "success")
            return redirect(url_for("contenedores.listar"))
        except APIError as exc:
            flash(exc.message, "danger")

    return render_template(
        "contenedores/form.html",
        contenedor=contenedor,
        ubicacion_label=_ubicacion_label,
        **form_data,
    )


@bp.route("/<int:contenedor_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(contenedor_id: int):
    try:
        api_request("delete", f"/contenedores/{contenedor_id}")
        flash("Contenedor eliminado.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("contenedores.listar"))
