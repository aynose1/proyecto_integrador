from functools import wraps

from flask import flash, redirect, session, url_for

from app.api_client import APIError, api_request


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("access_token"):
            flash("Inicia sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        try:
            # api_request() (no get_api_client() directo) es importante
            # aquí: si el access_token de 15 min ya expiró pero el
            # refresh_token (7 días) sigue vigente, api_request() lo
            # renueva solo y esta llamada de todos modos funciona. Antes
            # esto llamaba al cliente directo, que no reintenta con el
            # refresh_token, así que cualquier usuario que llevara más
            # de 15 minutos en la página se iba a login aunque su sesión
            # de verdad siguiera siendo válida por días.
            profile = api_request("get", "/usuarios/me")
        except APIError:
            session.clear()
            flash("Tu sesión expiró. Vuelve a iniciar sesión.", "warning")
            return redirect(url_for("auth.login"))

        if profile.get("tipo_usuario", {}).get("tipo") != "administrador":
            flash("Se requiere rol de administrador.", "danger")
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped
