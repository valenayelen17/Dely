from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from estados import EstadoEntrega
from models import Entrega
from schemas import EntregaDetalle, EntregaEstado, EntregaUbicacion
from services import entregas as servicio

router = APIRouter(prefix="/api/entregas", tags=["Entregas"])


@router.get("/", response_model=list[EntregaDetalle])
def listar_entregas(
    repartidor_id: int | None = None,
    estado: EstadoEntrega | None = None,
    limit: int = Query(100, gt=0, le=500),
    db: Session = Depends(get_db),
):
    consulta = select(Entrega).options(*servicio.CARGA_ENTREGA).order_by(Entrega.id_entrega.desc()).limit(limit)
    if repartidor_id is not None:
        consulta = consulta.where(Entrega.repartidor_id == repartidor_id)
    if estado is not None:
        consulta = consulta.where(Entrega.estado == estado)
    return list(db.scalars(consulta).all())


@router.get("/{entrega_id}", response_model=EntregaDetalle)
def obtener_entrega(entrega_id: int, db: Session = Depends(get_db)):
    return servicio.obtener_entrega(db, entrega_id)


@router.patch("/{entrega_id}/estado", response_model=EntregaDetalle)
def cambiar_estado(entrega_id: int, datos: EntregaEstado, db: Session = Depends(get_db)):
    return servicio.cambiar_estado(db, entrega_id, datos.estado, datos.ubicacion_actual)


@router.patch("/{entrega_id}/ubicacion", response_model=EntregaDetalle)
def actualizar_ubicacion(entrega_id: int, datos: EntregaUbicacion, db: Session = Depends(get_db)):
    return servicio.actualizar_ubicacion(db, entrega_id, datos.ubicacion_actual)
