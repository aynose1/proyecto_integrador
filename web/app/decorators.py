from functools import wraps

from flask import flash, redirect, session, url_for

from app.api_client import APIError, get_api_client


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
            profile = get_api_client().get("/usuarios/me")
        except APIError:
            session.clear()
            flash("Tu sesión expiró. Vuelve a iniciar sesión.", "warning")
            return redirect(url_for("auth.login"))

        if profile.get("tipo_usuario", {}).get("tipo") != "administrador":
            flash("Se requiere rol de administrador.", "danger")
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped
