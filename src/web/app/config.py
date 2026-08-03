import os


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
    INSTITUTION_NAME = os.getenv("INSTITUTION_NAME", "Nombre de la Institución")
    # Debe coincidir EXACTO con PLATFORM_API_KEY en src/backend/.env --
    # es la misma llave compartida, ver core/config.py del backend.
    PLATFORM_API_KEY = os.getenv("PLATFORM_API_KEY", "")
