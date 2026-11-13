from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from seguridad import solo_encargado
from estados import PEDIDOS_ACTIVOS, EstadoPedido
from models import Pedido
from schemas import NotificacionOut, PedidoAsignacion, PedidoCreate, PedidoOut, PedidoUpdate
from services import pedidos as servicio

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos"], dependencies=[Depends(solo_encargado)])


@router.get("/", response_model=list[PedidoOut])
def listar_pedidos(
    comercio_id: int | None = None,
    estado: EstadoPedido | None = None,
    limit: int = Query(100, gt=0, le=500),
    db: Session = Depends(get_db),
):
    consulta = select(Pedido).options(*servicio.CARGA_PEDIDO).order_by(Pedido.id_pedido.desc()).limit(limit)
    if comercio_id is not None:
        consulta = consulta.where(Pedido.comercio_id == comercio_id)
    if estado is not None:
        consulta = consulta.where(Pedido.estado == estado)
    return list(db.scalars(consulta).all())


@router.get("/pendientes", response_model=list[PedidoOut])
def listar_pendientes(
    comercio_id: int | None = None,
    zona: str | None = None,
    db: Session = Depends(get_db),
):
    consulta = (
        select(Pedido)
        .options(*servicio.CARGA_PEDIDO)
        .where(Pedido.estado.in_(PEDIDOS_ACTIVOS))
        .order_by(Pedido.fecha_pedido, Pedido.horario_estimado, Pedido.id_pedido)
    )
    if comercio_id is not None:
        consulta = consulta.where(Pedido.comercio_id == comercio_id)
    if zona:
        consulta = consulta.where(func.lower(Pedido.zona) == zona.strip().lower())
    return list(db.scalars(consulta).all())


@router.get("/{pedido_id}", response_model=PedidoOut)
def obtener_pedido(pedido_id: int, db: Session = Depends(get_db)):
    return servicio.obtener_pedido(db, pedido_id)


@router.get("/{pedido_id}/notificaciones", response_model=list[NotificacionOut])
def notificaciones_del_pedido(pedido_id: int, db: Session = Depends(get_db)):
    return servicio.obtener_pedido(db, pedido_id).notificaciones


@router.post("/", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
def crear_pedido(datos: PedidoCreate, db: Session = Depends(get_db)):
    return servicio.crear_pedido(db, datos)


@router.put("/{pedido_id}", response_model=PedidoOut)
def actualizar_pedido(pedido_id: int, datos: PedidoUpdate, db: Session = Depends(get_db)):
    return servicio.actualizar_pedido(db, pedido_id, datos)


@router.patch("/{pedido_id}/asignar", response_model=PedidoOut)
def asignar_repartidor(pedido_id: int, datos: PedidoAsignacion, db: Session = Depends(get_db)):
    return servicio.asignar_repartidor(db, pedido_id, datos.repartidor_id)


@router.patch("/{pedido_id}/cancelar", response_model=PedidoOut)
def cancelar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    return servicio.cancelar_pedido(db, pedido_id)


@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    servicio.eliminar_pedido(db, pedido_id)
