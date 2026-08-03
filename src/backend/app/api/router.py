from fastapi import APIRouter, Depends

from app.api.deps import verify_platform_api_key
from app.api.routes import (
    auth,
    catalogos,
    contenedores,
    dashboard,
    incidencias,
    notificaciones,
    registros_nivel,
    registros_peso,
    rutas,
    sectores,
    usuarios,
    zonas,
)

api_router = APIRouter()

# Todos estos requieren la API Key de plataforma JUNTO con el JWT (donde
# aplique) -- capa extra de defensa en profundidad para web/app móvil.
_dep_platform = [Depends(verify_platform_api_key)]
api_router.include_router(auth.router, dependencies=_dep_platform)
api_router.include_router(usuarios.router, dependencies=_dep_platform)
api_router.include_router(contenedores.router, dependencies=_dep_platform)
api_router.include_router(rutas.router, dependencies=_dep_platform)
api_router.include_router(incidencias.router, dependencies=_dep_platform)
api_router.include_router(notificaciones.router, dependencies=_dep_platform)
api_router.include_router(zonas.router, dependencies=_dep_platform)
api_router.include_router(sectores.router, dependencies=_dep_platform)
api_router.include_router(catalogos.router, dependencies=_dep_platform)
api_router.include_router(dashboard.router, dependencies=_dep_platform)

# registros_nivel y registros_peso NO llevan la API Key de plataforma a
# propósito: los consume el sistema embebido (sensores), un actor
# totalmente distinto a la web/app móvil, que ya se autentica con su
# propia llave (DEVICE_API_KEY, ver verify_device_api_key). Exigirle
# también la de plataforma no tendría sentido -- el firmware del sensor
# no tiene por qué conocer esa llave.
api_router.include_router(registros_nivel.router)
api_router.include_router(registros_peso.router)
