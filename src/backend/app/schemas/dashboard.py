from datetime import date

from pydantic import BaseModel


class DistribucionNivel(BaseModel):
    """
    Cuenta y porcentaje de contenedores en cada franja (bajo/medio/alto).
    Se reutiliza para nivel Y para peso (ambos se reducen a un porcentaje
    0-100 antes de llegar aquí) — mismos umbrales, mismo significado.
    """
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


class TendenciaDia(BaseModel):
    """
    Un punto de comparación nivel vs peso para un día -- ambos
    normalizados 0-1 (fracción, no porcentaje) para poder comparar las
    dos variables en la misma escala. None cuando ese día no tenía
    ninguna lectura todavía (para que la gráfica muestre un hueco, no
    un 0 falso).
    """
    fecha: date
    etiqueta: str
    promedio_nivel: float | None
    promedio_peso: float | None


class DashboardResumen(BaseModel):
    fecha: date
    total_contenedores: int
    contenedores_sin_datos_a_fecha: int
    contenedores_llenado_alto: int
    contenedores_peso_alto: int
    distribucion_nivel: DistribucionNivel
    distribucion_peso: DistribucionNivel
    promedio_por_zona: list[PromedioZona]
    recolecciones_por_dia_semana: list[RecoleccionDia]
    tendencia_7_dias: list[TendenciaDia]
    recolectores_hoy: list[RecolectorHoy]
    contenedores_criticos: list[ContenedorCritico]
