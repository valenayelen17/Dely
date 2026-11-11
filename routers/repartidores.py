from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from models import Repartidor
from routers.comercios import buscar_comercio
from schemas import RepartidorCreate, RepartidorDisponibilidad, RepartidorOut, RepartidorUpdate

router = APIRouter(prefix="/api/repartidores", tags=["Repartidores"])


def buscar_repartidor(db: Session, repartidor_id: int) -> Repartidor:
    repartidor = db.get(Repartidor, repartidor_id)
    if repartidor is None:
        raise HTTPException(404, "Repartidor no encontrado.")
    return repartidor


@router.get("/", response_model=list[RepartidorOut])
def listar_repartidores(
    comercio_id: int | None = None,
    zona: str | None = None,
    disponible: bool | None = None,
    limit: int = Query(100, gt=0, le=500),
    db: Session = Depends(get_db),
):
    consulta = select(Repartidor).order_by(Repartidor.id_repartidor).limit(limit)
    if comercio_id is not None:
        consulta = consulta.where(Repartidor.comercio_id == comercio_id)
    if zona:
        consulta = consulta.where(func.lower(Repartidor.zona) == zona.strip().lower())
    if disponible is not None:
        consulta = consulta.where(Repartidor.disponible == disponible)
    return list(db.scalars(consulta).all())


@router.get("/{repartidor_id}", response_model=RepartidorOut)
def obtener_repartidor(repartidor_id: int, db: Session = Depends(get_db)):
    return buscar_repartidor(db, repartidor_id)


@router.post("/", response_model=RepartidorOut, status_code=status.HTTP_201_CREATED)
def crear_repartidor(datos: RepartidorCreate, db: Session = Depends(get_db)):
    buscar_comercio(db, datos.comercio_id)
    repartidor = Repartidor(**datos.model_dump())
    db.add(repartidor)
    db.commit()
    db.refresh(repartidor)
    return repartidor


@router.put("/{repartidor_id}", response_model=RepartidorOut)
def actualizar_repartidor(repartidor_id: int, datos: RepartidorUpdate, db: Session = Depends(get_db)):
    repartidor = buscar_repartidor(db, repartidor_id)
    buscar_comercio(db, datos.comercio_id)
    for campo, valor in datos.model_dump().items():
        setattr(repartidor, campo, valor)
    db.commit()
    db.refresh(repartidor)
    return repartidor


@router.patch("/{repartidor_id}/disponibilidad", response_model=RepartidorOut)
def cambiar_disponibilidad(
    repartidor_id: int, datos: RepartidorDisponibilidad, db: Session = Depends(get_db)
):
    repartidor = buscar_repartidor(db, repartidor_id)
    repartidor.disponible = datos.disponible
    db.commit()
    db.refresh(repartidor)
    return repartidor


@router.delete("/{repartidor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_repartidor(repartidor_id: int, db: Session = Depends(get_db)):
    repartidor = buscar_repartidor(db, repartidor_id)
    if repartidor.entregas:
        raise HTTPException(409, "No se puede eliminar: el repartidor tiene entregas registradas.")
    db.delete(repartidor)
    db.commit()
