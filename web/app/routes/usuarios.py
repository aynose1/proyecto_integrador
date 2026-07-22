from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.api_client import APIError, api_request
from app.decorators import admin_required

bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@bp.route("")
@admin_required
def listar():
    try:
        usuarios = api_request("get", "/usuarios")
        tipos_usuario = api_request("get", "/catalogos/tipos-usuario")
    except APIError as exc:
        flash(exc.message, "danger")
        usuarios = []
        tipos_usuario = []
    return render_template("usuarios/list.html", usuarios=usuarios, tipos_usuario=tipos_usuario)


@bp.route("/nuevo", methods=["POST"])
@admin_required
def crear():
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
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("usuarios.listar"))


@bp.route("/<int:usuario_id>/editar", methods=["POST"])
@admin_required
def editar(usuario_id: int):
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
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("usuarios.listar"))


@bp.route("/<int:usuario_id>/eliminar", methods=["POST"])
@admin_required
def eliminar(usuario_id: int):
    try:
        api_request("delete", f"/usuarios/{usuario_id}")
        flash("Usuario eliminado.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("usuarios.listar"))
