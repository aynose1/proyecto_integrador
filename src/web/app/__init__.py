from flask import Flask, session

from app.config import Config


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.routes.auth import bp as auth_bp
    from app.routes.contenedores import bp as contenedores_bp
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.notificaciones import bp as notificaciones_bp
    from app.routes.notificaciones import contar_pendientes
    from app.routes.reportes import bp as reportes_bp
    from app.routes.rutas import bp as rutas_bp
    from app.routes.ubicaciones import bp as ubicaciones_bp
    from app.routes.usuarios import bp as usuarios_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(rutas_bp)
    app.register_blueprint(contenedores_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(ubicaciones_bp)
    app.register_blueprint(notificaciones_bp)
    app.register_blueprint(reportes_bp)

    @app.context_processor
    def inject_globals():
        # Badge del sidebar: solo se consulta si ya hay sesión iniciada,
        # para no gastar una llamada a la API en cada vista de login/registro.
        pendientes = contar_pendientes() if session.get("access_token") else 0
        return {"app_name": "Echo-Bin", "notificaciones_pendientes_count": pendientes}

    return app
