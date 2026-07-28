from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import require_admin
from app.db.session import get_db
from app.schemas.dashboard import DashboardResumen

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/resumen", response_model=DashboardResumen, dependencies=[Depends(require_admin)])
def obtener_resumen(
    fecha: date | None = Query(
        default=None,
        description="Fecha del corte del dashboard (KPIs, gráficas y listas); por defecto la fecha de hoy",
    ),
    db: Session = Depends(get_db),
):
    return crud.dashboard.resumen(db, fecha or date.today())
