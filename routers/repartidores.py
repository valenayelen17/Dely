from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import Repartidor
from schemas import RepartidorCreate, RepartidorOut, RepartidorUpdate

router = APIRouter(prefix="/api/repartidores", tags=["Repartidores"])


@router.get("/", response_model=list[RepartidorOut])
def listar_repartidores(limit: int = Query(100, gt=0, le=500), db: Session = Depends(get_db)):
    consulta = select(Repartidor).order_by(Repartidor.id_repartidor).limit(limit)
    return list(db.scalars(consulta).all())


@router.get("/{repartidor_id}", response_model=RepartidorOut)
def obtener_repartidor(repartidor_id: int, db: Session = Depends(get_db)):
    repartidor = db.get(Repartidor, repartidor_id)
    if repartidor is None:
        raise HTTPException(404, "Repartidor no encontrado.")
    return repartidor


@router.post("/", response_model=RepartidorOut, status_code=status.HTTP_201_CREATED)
def crear_repartidor(datos: RepartidorCreate, db: Session = Depends(get_db)):
    repartidor = Repartidor(**datos.model_dump())
    db.add(repartidor)
    db.commit()
    db.refresh(repartidor)
    return repartidor


@router.put("/{repartidor_id}", response_model=RepartidorOut)
def actualizar_repartidor(repartidor_id: int, datos: RepartidorUpdate, db: Session = Depends(get_db)):
    repartidor = db.get(Repartidor, repartidor_id)
    if repartidor is None:
        raise HTTPException(404, "Repartidor no encontrado.")
    for campo, valor in datos.model_dump().items():
        setattr(repartidor, campo, valor)
    db.commit()
    db.refresh(repartidor)
    return repartidor


@router.delete("/{repartidor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_repartidor(repartidor_id: int, db: Session = Depends(get_db)):
    repartidor = db.get(Repartidor, repartidor_id)
    if repartidor is None:
        raise HTTPException(404, "Repartidor no encontrado.")
    db.delete(repartidor)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, "No se puede eliminar: el repartidor tiene pedidos asociados.") from error
