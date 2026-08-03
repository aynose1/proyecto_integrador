from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.router import api_router
from app.core.rate_limit import limiter

# root_path="/api": HAProxy expone la API pública detrás del prefijo
# /api (ver acl path_api + http-request replace-path en
# haproxy.cfg.template), quitándolo antes de reenviar la petición --
# así que FastAPI, por dentro, nunca ve ese prefijo en la ruta real.
# Sin root_path, Swagger UI (/docs) genera su HTML pidiendo
# /openapi.json a secas; el navegador entonces pide
# http://localhost/openapi.json (sin /api), que HAProxy manda a Flask
# en vez de a la API -> 404 "Failed to load API definition". Con
# root_path="/api", FastAPI arma esa URL como /api/openapi.json,
# quedando correcta.
#
# Trade-off consciente: la API también se puede consultar directo por
# el puerto 8080 (api_internal_front en HAProxy, sin prefijo /api, para
# que Flask/el server de desarrollo de la app móvil le hablen sin
# lidiar con el certificado autofirmado). Por ese puerto, /docs con
# Swagger UI no cargará bien sus assets (asumirá el prefijo /api que
# ahí no existe) -- pero por ese puerto nadie necesita explorar Swagger
# a mano, solo consumir la API programáticamente, así que no afecta el
# uso real que se le da.
app = FastAPI(title="Sistema de Gestión de Residuos Sólidos - API", root_path="/api")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(api_router)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}
