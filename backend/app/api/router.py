from fastapi import APIRouter

from app.api.routes import (
    auth,
    catalogos,
    contenedores,
    incidencias,
    notificaciones,
    registros_nivel,
    rutas,
    sectores,
    usuarios,
    zonas,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(usuarios.router)
api_router.include_router(contenedores.router)
api_router.include_router(rutas.router)
api_router.include_router(registros_nivel.router)
api_router.include_router(incidencias.router)
api_router.include_router(notificaciones.router)
api_router.include_router(zonas.router)
api_router.include_router(sectores.router)
api_router.include_router(catalogos.router)
