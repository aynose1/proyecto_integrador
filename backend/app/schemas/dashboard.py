from datetime import date

from pydantic import BaseModel


class DistribucionNivel(BaseModel):
    """Cuenta y porcentaje de contenedores en cada franja de llenado."""
    bajo: int
    medio: int
    alto: int
    bajo_pct: float
    medio_pct: float
    alto_pct: float


class PromedioZona(BaseModel):
    zona: str
    promedio_nivel: float
    total_contenedores: int


class RecolectorHoy(BaseModel):
    id: int
    nombre: str
    codigo_usuario: str
    rutas_hoy: int
    rutas_completadas_hoy: int


class ContenedorCritico(BaseModel):
    id: int
    nombre: str
    codigo_contenedor: str
    nivel_actual: float
    zona: str
    sector: str


class RecoleccionDia(BaseModel):
    dia: str
    total: int


class DashboardResumen(BaseModel):
    fecha: date
    total_contenedores: int
    contenedores_sin_datos_a_fecha: int
    contenedores_llenado_alto: int
    distribucion_nivel: DistribucionNivel
    promedio_por_zona: list[PromedioZona]
    recolecciones_por_dia_semana: list[RecoleccionDia]
    recolectores_hoy: list[RecolectorHoy]
    contenedores_criticos: list[ContenedorCritico]
