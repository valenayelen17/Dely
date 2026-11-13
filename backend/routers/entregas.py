from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from estados import EstadoEntrega
from models import Entrega, Usuario
from schemas import EntregaDetalle, EntregaEstado, EntregaUbicacion
from seguridad import puede_ver_repartidor, solo_encargado, usuario_actual
from services import entregas as servicio

router = APIRouter(prefix="/api/entregas", tags=["Entregas"])


def entrega_propia(db: Session, entrega_id: int, usuario: Usuario) -> Entrega:
    """La entrega, si el usuario es el encargado o el repartidor que la tiene asignada."""
    entrega = servicio.obtener_entrega(db, entrega_id)
    puede_ver_repartidor(usuario, entrega.repartidor_id)
    return entrega


@router.get("/", response_model=list[EntregaDetalle], dependencies=[Depends(solo_encargado)])
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
def obtener_entrega(entrega_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_actual)):
    return entrega_propia(db, entrega_id, usuario)


@router.patch("/{entrega_id}/estado", response_model=EntregaDetalle)
def cambiar_estado(
    entrega_id: int, datos: EntregaEstado, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_actual)
):
    entrega_propia(db, entrega_id, usuario)
    return servicio.cambiar_estado(db, entrega_id, datos.estado, datos.ubicacion_actual)


@router.patch("/{entrega_id}/ubicacion", response_model=EntregaDetalle)
def actualizar_ubicacion(
    entrega_id: int, datos: EntregaUbicacion, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_actual)
):
    entrega_propia(db, entrega_id, usuario)
    return servicio.actualizar_ubicacion(db, entrega_id, datos.ubicacion_actual)
