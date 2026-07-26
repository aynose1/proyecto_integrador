from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.api_client import APIClient, APIError

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("access_token"):
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        codigo = request.form.get("codigo_usuario", "").strip()
        contrasena = request.form.get("contrasena", "")

        if not codigo or not contrasena:
            flash("Ingresa código de usuario y contraseña.", "warning")
            return render_template("login.html")

        client = APIClient()
        try:
            tokens = client.login(codigo, contrasena)
            session["access_token"] = tokens["access_token"]
            session["refresh_token"] = tokens["refresh_token"]

            profile = APIClient(token=tokens["access_token"]).get("/usuarios/me")
            if profile.get("tipo_usuario", {}).get("tipo") != "administrador":
                session.clear()
                flash("Solo administradores pueden acceder a esta plataforma.", "danger")
                return render_template("login.html")

            session["user_name"] = f"{profile['nombre']} {profile['apellido_paterno']}"
            flash("Sesión iniciada correctamente.", "success")
            return redirect(url_for("dashboard.index"))
        except APIError as exc:
            flash(exc.message, "danger")

    return render_template("login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("access_token"):
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        codigo = request.form.get("codigo_usuario", "").strip()
        nombre = request.form.get("nombre", "").strip()
        apellido_paterno = request.form.get("apellido_paterno", "").strip()
        apellido_materno = request.form.get("apellido_materno", "").strip() or None
        contrasena = request.form.get("contrasena", "")
        contrasena_confirm = request.form.get("contrasena_confirm", "")

        if not all([codigo, nombre, apellido_paterno, contrasena, contrasena_confirm]):
            flash("Completa todos los campos obligatorios.", "warning")
            return render_template("register.html")

        if len(contrasena) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "warning")
            return render_template("register.html")

        if contrasena != contrasena_confirm:
            flash("Las contraseñas no coinciden.", "warning")
            return render_template("register.html")

        client = APIClient()
        try:
            client.post(
                "/auth/register",
                data={
                    "codigo_usuario": codigo,
                    "nombre": nombre,
                    "apellido_paterno": apellido_paterno,
                    "apellido_materno": apellido_materno,
                    "contrasena": contrasena,
                },
            )
            flash("Cuenta creada. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("auth.login"))
        except APIError as exc:
            flash(exc.message, "danger")

    return render_template("register.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))
