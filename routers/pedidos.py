from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Cliente, DetallePedido, Pedido, Producto, Repartidor
from schemas import PedidoAsignacion, PedidoCreate, PedidoEstado, PedidoOut, PedidoUpdate

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos"])
ESTADOS = {"Pendiente", "Preparando", "Listo para retirar", "En camino", "Entregado", "Cancelado"}


def buscar_pedido(db: Session, pedido_id: int) -> Pedido:
    consulta = select(Pedido).options(joinedload(Pedido.detalles)).where(Pedido.id_pedido == pedido_id)
    pedido = db.scalars(consulta).unique().first()
    if pedido is None:
        raise HTTPException(404, "Pedido no encontrado.")
    return pedido


@router.get("/", response_model=list[PedidoOut])
def listar_pedidos(limit: int = Query(100, gt=0, le=500), db: Session = Depends(get_db)):
    consulta = (
        select(Pedido)
        .options(joinedload(Pedido.detalles))
        .order_by(Pedido.id_pedido.desc())
        .limit(limit)
    )
    return list(db.scalars(consulta).unique().all())


@router.get("/{pedido_id}", response_model=PedidoOut)
def obtener_pedido(pedido_id: int, db: Session = Depends(get_db)):
    return buscar_pedido(db, pedido_id)


@router.post("/", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
def crear_pedido(datos: PedidoCreate, db: Session = Depends(get_db)):
    if db.get(Cliente, datos.cliente_id) is None:
        raise HTTPException(404, "Cliente no encontrado.")
    if len({item.producto_id for item in datos.detalles}) != len(datos.detalles):
        raise HTTPException(422, "Incluí cada producto una sola vez en el pedido.")

    pedido = Pedido(
        fecha_pedido=datos.fecha_pedido,
        direccion_entrega=datos.direccion_entrega,
        zona=datos.zona,
        horario_estimado=datos.horario_estimado,
        cliente_id=datos.cliente_id,
        estado="Pendiente",
    )
    for item in datos.detalles:
        producto = db.get(Producto, item.producto_id)
        if producto is None:
            raise HTTPException(404, f"Producto {item.producto_id} no encontrado.")
        if producto.stock < item.cantidad:
            raise HTTPException(409, f"Stock insuficiente para {producto.nombre}.")
        producto.stock -= item.cantidad
        pedido.detalles.append(
            DetallePedido(
                producto_id=producto.id_producto,
                cantidad=item.cantidad,
                precio_unitario=producto.precio,
            )
        )

    db.add(pedido)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, "No se pudo guardar el pedido por un conflicto de datos.") from error
    return buscar_pedido(db, pedido.id_pedido)


@router.put("/{pedido_id}", response_model=PedidoOut)
def actualizar_pedido(pedido_id: int, datos: PedidoUpdate, db: Session = Depends(get_db)):
    pedido = buscar_pedido(db, pedido_id)
    if datos.estado not in ESTADOS:
        raise HTTPException(422, f"Estado inválido. Usá: {', '.join(sorted(ESTADOS))}.")
    if datos.estado == "En camino" and datos.repartidor_id is None:
        raise HTTPException(409, "Asigná un repartidor antes de iniciar la entrega.")
    if db.get(Cliente, datos.cliente_id) is None:
        raise HTTPException(404, "Cliente no encontrado.")
    repartidor = None
    if datos.repartidor_id is not None:
        repartidor = db.get(Repartidor, datos.repartidor_id)
        if repartidor is None:
            raise HTTPException(404, "Repartidor no encontrado.")
        if not repartidor.disponible or repartidor.zona.casefold() != datos.zona.casefold():
            raise HTTPException(409, "El repartidor debe estar disponible y cubrir la zona del pedido.")

    for campo, valor in datos.model_dump().items():
        setattr(pedido, campo, valor)
    if pedido.entrega is not None:
        pedido.entrega.estado = pedido.estado
    db.commit()
    return buscar_pedido(db, pedido_id)


@router.patch("/{pedido_id}/asignar", response_model=PedidoOut)
def asignar_repartidor(pedido_id: int, datos: PedidoAsignacion, db: Session = Depends(get_db)):
    pedido = buscar_pedido(db, pedido_id)
    if pedido.estado in {"Entregado", "Cancelado"}:
        raise HTTPException(409, "No se puede asignar un pedido finalizado.")
    repartidor = db.get(Repartidor, datos.repartidor_id)
    if repartidor is None:
        raise HTTPException(404, "Repartidor no encontrado.")
    if not repartidor.disponible:
        raise HTTPException(409, "El repartidor no está disponible.")
    if repartidor.zona.casefold() != pedido.zona.casefold():
        raise HTTPException(409, "El repartidor no cubre la zona de entrega del pedido.")
    pedido.repartidor_id = repartidor.id_repartidor
    db.commit()
    return buscar_pedido(db, pedido_id)


@router.patch("/{pedido_id}/estado", response_model=PedidoOut)
def actualizar_estado(pedido_id: int, datos: PedidoEstado, db: Session = Depends(get_db)):
    pedido = buscar_pedido(db, pedido_id)
    if datos.estado not in ESTADOS:
        raise HTTPException(422, f"Estado inválido. Usá: {', '.join(sorted(ESTADOS))}.")
    if datos.estado == "En camino" and pedido.repartidor_id is None:
        raise HTTPException(409, "Asigná un repartidor antes de iniciar la entrega.")
    pedido.estado = datos.estado
    if pedido.entrega is not None:
        pedido.entrega.estado = datos.estado
    db.commit()
    return buscar_pedido(db, pedido_id)


@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    pedido = buscar_pedido(db, pedido_id)
    for detalle in pedido.detalles:
        producto = db.get(Producto, detalle.producto_id)
        if producto is not None:
            producto.stock += detalle.cantidad
    db.delete(pedido)
    db.commit()
