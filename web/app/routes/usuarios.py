from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.api_client import APIError, api_request
from app.decorators import admin_required

bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


def _load_form_data():
    tipos = api_request("get", "/catalogos/tipos-usuario")
    return {"tipos_usuario": tipos}


@bp.route("")
@admin_required
def listar():
    try:
        usuarios = api_request("get", "/usuarios")
    except APIError as exc:
        flash(exc.message, "danger")
        usuarios = []
    return render_template("usuarios/list.html", usuarios=usuarios)


@bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def crear():
    if request.method == "POST":
        payload = {
            "codigo_usuario": request.form["codigo_usuario"].strip(),
            "nombre": request.form["nombre"].strip(),
            "apellido_paterno": request.form["apellido_paterno"].strip(),
            "apellido_materno": request.form.get("apellido_materno", "").strip() or None,
            "contrasena": request.form["contrasena"],
            "id_tipo_usuario": int(request.form["id_tipo_usuario"]),
        }
        try:
            api_request("post", "/usuarios", data=payload)
            flash("Usuario creado correctamente.", "success")
            return redirect(url_for("usuarios.listar"))
        except APIError as exc:
            flash(exc.message, "danger")

    return render_template("usuarios/form.html", usuario=None, **_load_form_data())


@bp.route("/<int:usuario_id>/editar", methods=["GET", "POST"])
@admin_required
def editar(usuario_id: int):
    try:
        usuario = api_request("get", f"/usuarios/{usuario_id}")
    except APIError as exc:
        flash(exc.message, "danger")
        return redirect(url_for("usuarios.listar"))

    if request.method == "POST":
        payload = {
            "nombre": request.form["nombre"].strip(),
            "apellido_paterno": request.form["apellido_paterno"].strip(),
            "apellido_materno": request.form.get("apellido_materno", "").strip() or None,
            "id_tipo_usuario": int(request.form["id_tipo_usuario"]),
        }
        contrasena = request.form.get("contrasena", "").strip()
        if contrasena:
            payload["contrasena"] = contrasena

        try:
            api_request("put", f"/usuarios/{usuario_id}", data=payload)
            flash("Usuario actualizado.", "success")
            return redirect(url_for("usuarios.listar"))
        except APIError as exc:
            flash(exc.message, "danger")

    return render_template("usuarios/form.html", usuario=usuario, **_load_form_data())


@bp.route("/<int:usuario_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(usuario_id: int):
    try:
        api_request("delete", f"/usuarios/{usuario_id}")
        flash("Usuario eliminado.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("usuarios.listar"))
