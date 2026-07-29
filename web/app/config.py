import os


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
    # Se muestra en el encabezado del "Reporte General de Recolección de
    # Rutas" (PDF/Excel). Cámbialo en tu .env con el nombre real.
    INSTITUTION_NAME = os.getenv("INSTITUTION_NAME", "Nombre de la Institución")
