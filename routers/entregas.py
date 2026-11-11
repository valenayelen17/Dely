from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from estados import EstadoEntrega
from models import Entrega
from schemas import EntregaOut

router = APIRouter(prefix="/api/entregas", tags=["Entregas"])


@router.get("/", response_model=list[EntregaOut])
def listar_entregas(
    repartidor_id: int | None = None,
    estado: EstadoEntrega | None = None,
    limit: int = Query(100, gt=0, le=500),
    db: Session = Depends(get_db),
):
    consulta = select(Entrega).order_by(Entrega.id_entrega.desc()).limit(limit)
    if repartidor_id is not None:
        consulta = consulta.where(Entrega.repartidor_id == repartidor_id)
    if estado is not None:
        consulta = consulta.where(Entrega.estado == estado)
    return list(db.scalars(consulta).all())


@router.get("/{entrega_id}", response_model=EntregaOut)
def obtener_entrega(entrega_id: int, db: Session = Depends(get_db)):
    entrega = db.get(Entrega, entrega_id)
    if entrega is None:
        raise HTTPException(404, "Entrega no encontrada.")
    return entrega
