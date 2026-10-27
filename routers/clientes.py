from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import Cliente
from schemas import ClienteCreate, ClienteOut, ClienteUpdate

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])


@router.get("/", response_model=list[ClienteOut])
def listar_clientes(limit: int = Query(100, gt=0, le=500), db: Session = Depends(get_db)):
    consulta = select(Cliente).order_by(Cliente.id_cliente).limit(limit)
    return list(db.scalars(consulta).all())


@router.get("/{cliente_id}", response_model=ClienteOut)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(404, "Cliente no encontrado.")
    return cliente


@router.post("/", response_model=ClienteOut, status_code=status.HTTP_201_CREATED)
def crear_cliente(datos: ClienteCreate, db: Session = Depends(get_db)):
    cliente = Cliente(**datos.model_dump())
    db.add(cliente)
    try:
        db.commit()
        db.refresh(cliente)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, "Ya existe un cliente con ese email.") from error
    return cliente


@router.put("/{cliente_id}", response_model=ClienteOut)
def actualizar_cliente(cliente_id: int, datos: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(404, "Cliente no encontrado.")
    for campo, valor in datos.model_dump().items():
        setattr(cliente, campo, valor)
    try:
        db.commit()
        db.refresh(cliente)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, "Ya existe un cliente con ese email.") from error
    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(404, "Cliente no encontrado.")
    db.delete(cliente)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, "No se puede eliminar: el cliente tiene pedidos asociados.") from error
