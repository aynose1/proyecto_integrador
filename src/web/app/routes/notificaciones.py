from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.api_client import APIError, api_request
from app.decorators import admin_required

bp = Blueprint("notificaciones", __name__, url_prefix="/notificaciones")


@bp.route("")
@admin_required
def listar():
    tab = request.args.get("tab", "discrepancias")
    if tab not in {"discrepancias", "incidencias"}:
        tab = "discrepancias"
    try:
        discrepancias = api_request("get", "/notificaciones")
        incidencias = api_request("get", "/incidencias")
        contenedores = api_request("get", "/contenedores")
        usuarios = api_request("get", "/usuarios")
        contenedores_por_id = {c["id"]: c for c in contenedores}
        usuarios_por_id = {u["id"]: u for u in usuarios}
    except APIError as exc:
        flash(exc.message, "danger")
        discrepancias = []
        incidencias = []
        contenedores_por_id = {}
        usuarios_por_id = {}
    return render_template(
        "notificaciones/list.html",
        discrepancias=discrepancias,
        incidencias=incidencias,
        contenedores_por_id=contenedores_por_id,
        usuarios_por_id=usuarios_por_id,
        tab=tab,
    )


@bp.route("/<int:notificacion_id>/leida", methods=["POST"])
@admin_required
def marcar_leida(notificacion_id: int):
    try:
        api_request("patch", f"/notificaciones/{notificacion_id}")
        flash("Notificación marcada como leída.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("notificaciones.listar", tab="discrepancias"))


@bp.route("/incidencias/<int:incidencia_id>/atender", methods=["POST"])
@admin_required
def atender_incidencia(incidencia_id: int):
    try:
        estados = api_request("get", "/catalogos/estados")
        estado_atendido = next((e for e in estados if e["estado"].lower() == "atendido"), None)
        if not estado_atendido:
            flash("El catálogo de estados no tiene 'atendido'. Revisa el seeder.", "danger")
            return redirect(url_for("notificaciones.listar", tab="incidencias"))
        api_request("patch", f"/incidencias/{incidencia_id}", data={"id_estado": estado_atendido["id"]})
        flash("Incidencia marcada como atendida.", "success")
    except APIError as exc:
        flash(exc.message, "danger")
    return redirect(url_for("notificaciones.listar", tab="incidencias"))
