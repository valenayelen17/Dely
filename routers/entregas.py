from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Entrega, Pedido
from schemas import EntregaCreate, EntregaOut, EntregaUpdate

router = APIRouter(prefix="/api/entregas", tags=["Entregas"])
ESTADOS = {"Pendiente", "Preparando", "Listo para retirar", "En camino", "Entregado", "Cancelado"}


@router.get("/", response_model=list[EntregaOut])
def listar_entregas(limit: int = Query(100, gt=0, le=500), db: Session = Depends(get_db)):
    consulta = select(Entrega).order_by(Entrega.id_entrega.desc()).limit(limit)
    return list(db.scalars(consulta).all())


@router.get("/{entrega_id}", response_model=EntregaOut)
def obtener_entrega(entrega_id: int, db: Session = Depends(get_db)):
    entrega = db.get(Entrega, entrega_id)
    if entrega is None:
        raise HTTPException(404, "Entrega no encontrada.")
    return entrega


@router.post("/", response_model=EntregaOut, status_code=status.HTTP_201_CREATED)
def crear_entrega(datos: EntregaCreate, db: Session = Depends(get_db)):
    pedido = db.get(Pedido, datos.pedido_id)
    if pedido is None:
        raise HTTPException(404, "Pedido no encontrado.")
    if pedido.entrega is not None:
        raise HTTPException(409, "El pedido ya tiene una entrega registrada.")
    entrega = Entrega(**datos.model_dump(), estado="Pendiente")
    db.add(entrega)
    db.commit()
    db.refresh(entrega)
    return entrega


@router.put("/{entrega_id}", response_model=EntregaOut)
def actualizar_entrega(entrega_id: int, datos: EntregaUpdate, db: Session = Depends(get_db)):
    entrega = db.get(Entrega, entrega_id)
    if entrega is None:
        raise HTTPException(404, "Entrega no encontrada.")
    if datos.estado not in ESTADOS:
        raise HTTPException(422, f"Estado inválido. Usá: {', '.join(sorted(ESTADOS))}.")
    if datos.estado == "En camino" and entrega.pedido.repartidor_id is None:
        raise HTTPException(409, "Asigná un repartidor al pedido antes de iniciar la entrega.")
    for campo, valor in datos.model_dump().items():
        setattr(entrega, campo, valor)
    entrega.pedido.estado = entrega.estado
    db.commit()
    db.refresh(entrega)
    return entrega


@router.delete("/{entrega_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_entrega(entrega_id: int, db: Session = Depends(get_db)):
    entrega = db.get(Entrega, entrega_id)
    if entrega is None:
        raise HTTPException(404, "Entrega no encontrada.")
    db.delete(entrega)
    db.commit()
