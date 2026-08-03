"""
Configuración central de la aplicación.
Todos los valores sensibles se leen de variables de entorno (.env),
nunca se hardcodean aquí.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Base de datos (MySQL / MariaDB vía PyMySQL) ---
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int = 3306
    DB_NAME: str

    # --- Autenticación JWT ---
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- API Key para el sistema embebido (sensores) ---
    DEVICE_API_KEY: str

    # --- API Key de plataforma: capa EXTRA junto al JWT (defensa en
    # profundidad), obligatoria en TODOS los endpoints salvo los de
    # sensores (esos ya tienen su propia llave, DEVICE_API_KEY, para un
    # actor distinto). La misma llave la comparten la web y la app
    # móvil -- ver web/app/config.py y pi_movil/config/api.js.
    PLATFORM_API_KEY: str

    # --- Rate limiting ---
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_DEFAULT: str = "100/minute"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
