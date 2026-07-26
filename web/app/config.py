import os


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
