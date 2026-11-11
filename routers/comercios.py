from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import Comercio
from schemas import ComercioCreate, ComercioOut, ComercioUpdate

router = APIRouter(prefix="/api/comercios", tags=["Comercios"])


def buscar_comercio(db: Session, comercio_id: int) -> Comercio:
    comercio = db.get(Comercio, comercio_id)
    if comercio is None:
        raise HTTPException(404, "Comercio no encontrado.")
    return comercio


@router.get("/", response_model=list[ComercioOut])
def listar_comercios(limit: int = Query(100, gt=0, le=500), db: Session = Depends(get_db)):
    consulta = select(Comercio).order_by(Comercio.id_comercio).limit(limit)
    return list(db.scalars(consulta).all())


@router.get("/{comercio_id}", response_model=ComercioOut)
def obtener_comercio(comercio_id: int, db: Session = Depends(get_db)):
    return buscar_comercio(db, comercio_id)


@router.post("/", response_model=ComercioOut, status_code=status.HTTP_201_CREATED)
def crear_comercio(datos: ComercioCreate, db: Session = Depends(get_db)):
    comercio = Comercio(**datos.model_dump())
    db.add(comercio)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, "Ya existe un comercio con ese email.") from error
    db.refresh(comercio)
    return comercio


@router.put("/{comercio_id}", response_model=ComercioOut)
def actualizar_comercio(comercio_id: int, datos: ComercioUpdate, db: Session = Depends(get_db)):
    comercio = buscar_comercio(db, comercio_id)
    for campo, valor in datos.model_dump().items():
        setattr(comercio, campo, valor)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, "Ya existe un comercio con ese email.") from error
    db.refresh(comercio)
    return comercio


@router.delete("/{comercio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_comercio(comercio_id: int, db: Session = Depends(get_db)):
    comercio = buscar_comercio(db, comercio_id)
    if comercio.pedidos or comercio.productos or comercio.repartidores:
        raise HTTPException(409, "No se puede eliminar: el comercio tiene pedidos, productos o repartidores.")
    db.delete(comercio)
    db.commit()
