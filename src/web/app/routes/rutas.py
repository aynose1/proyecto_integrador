from datetime import date, timedelta

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
    # Por defecto se muestran las rutas de HOY. ?fecha=todas quita el
    # filtro; ?fecha=YYYY-MM-DD muestra un día específico (para navegar
    # a otros días con los botones de la plantilla).
    fecha_param = request.args.get("fecha", date.today().isoformat())
    fecha_filtro = None if fecha_param == "todas" else fecha_param

    try:
        form_data = _load_form_data()
        params = {"fecha": fecha_filtro} if fecha_filtro else {}
        resumenes = api_request("get", "/rutas", params=params)
        rutas = []
        for resumen in resumenes:
            detalle = api_request("get", f"/rutas/{resumen['id']}")
            detalle["selected_ids"] = [
                d["contenedor"]["id"] for d in detalle.get("detalles", [])
            ]
            rutas.append(detalle)
        usuarios_map = {u["id"]: u for u in form_data["usuarios"]}
        todos_los_estados = api_request("get", "/catalogos/estados")
        estados_detalle = [e for e in todos_los_estados if e["estado"].lower() in ("pendiente", "recolectado")]
    except APIError as exc:
        flash(exc.message, "danger")
        rutas = []
        usuarios_map = {}
        form_data = {"recolectores": [], "contenedores": []}
        estados_detalle = []

    dia_actual = date.fromisoformat(fecha_filtro) if fecha_filtro else None

    return render_template(
        "rutas/list.html",
        rutas=rutas,
        usuarios=usuarios_map,
        recolectores=form_data["recolectores"],
        contenedores=form_data["contenedores"],
        estados_detalle=estados_detalle,
        fecha_filtro=fecha_filtro,
        dia_actual=dia_actual,
        dia_anterior=(dia_actual - timedelta(days=1)).isoformat() if dia_actual else None,
        dia_siguiente=(dia_actual + timedelta(days=1)).isoformat() if dia_actual else None,
        hoy=date.today().isoformat(),
    )


@bp.route("/nuevo", methods=["POST"])
@admin_required
def crear():
    # Parse comma-separated IDs from hidden input field
    ids_raw = request.form.get("ids_contenedores", "").strip()
    ids_contenedores = [int(x.strip()) for x in ids_raw.split(",") if x.strip()] if ids_raw else []
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
    # Parse comma-separated IDs from hidden input field
    ids_raw = request.form.get("ids_contenedores", "").strip()
    ids_contenedores = [int(x.strip()) for x in ids_raw.split(",") if x.strip()] if ids_raw else []
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


@bp.route("/<int:ruta_id>/detalles/estados", methods=["POST"])
@admin_required
def confirmar_estados_detalle(ruta_id: int):
    """
    Aplica de un solo clic los cambios de estado (pendiente/recolectado)
    de todos los contenedores de la ruta que se hayan modificado en el
    modal 'Ver ruta' — sin depender del escaneo de QR, para pruebas o
    correcciones. Cada campo del formulario viene nombrado
    'estado_detalle_<detalle_id>'.
    """
    errores = 0
    actualizados = 0
    for campo, valor in request.form.items():
        if not campo.startswith("estado_detalle_"):
            continue
        detalle_id = int(campo.removeprefix("estado_detalle_"))
        id_estado = int(valor)
        try:
            api_request("patch", f"/rutas/{ruta_id}/detalles/{detalle_id}", data={"id_estado": id_estado})
            actualizados += 1
        except APIError as exc:
            errores += 1
            flash(f"Contenedor (detalle {detalle_id}): {exc.message}", "danger")

    if actualizados and not errores:
        flash(f"Estatus actualizado ({actualizados} contenedor{'es' if actualizados != 1 else ''}).", "success")
    elif actualizados and errores:
        flash(f"Se actualizó el estatus de {actualizados}, pero {errores} fallaron (ver arriba).", "warning")
    elif errores:
        flash("No se pudo cambiar el estatus (ver errores arriba).", "danger")
    else:
        flash("Esta ruta no tiene contenedores.", "info")

    return redirect(url_for("rutas.listar"))
