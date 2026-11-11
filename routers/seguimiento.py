from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import SeguimientoOut
from services import seguimiento as servicio

router = APIRouter(prefix="/api/seguimiento", tags=["Seguimiento"])


@router.get("/{codigo}", response_model=SeguimientoOut)
def consultar_seguimiento(codigo: str, db: Session = Depends(get_db)):
    return servicio.consultar(db, codigo)


@router.patch("/{codigo}/notificaciones/leidas", response_model=SeguimientoOut)
def marcar_leidas(codigo: str, db: Session = Depends(get_db)):
    return servicio.marcar_notificaciones_leidas(db, codigo)
