from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from errores import Conflicto, DatoInvalido, NoEncontrado
from estados import PEDIDOS_FINALIZADOS, EstadoEntrega, EstadoPedido
from models import Cliente, Comercio, DetallePedido, Entrega, Pedido, Producto, Repartidor
from schemas import PedidoCreate, PedidoUpdate

CARGA_PEDIDO = (
    selectinload(Pedido.detalles).selectinload(DetallePedido.producto),
    selectinload(Pedido.cliente),
    selectinload(Pedido.entrega).selectinload(Entrega.repartidor),
)


def obtener_pedido(db: Session, pedido_id: int) -> Pedido:
    pedido = db.scalars(
        select(Pedido).options(*CARGA_PEDIDO).where(Pedido.id_pedido == pedido_id)
    ).first()
    if pedido is None:
        raise NoEncontrado("Pedido no encontrado.")
    return pedido


def mismas_zonas(zona_a: str, zona_b: str) -> bool:
    return zona_a.strip().casefold() == zona_b.strip().casefold()


def crear_pedido(db: Session, datos: PedidoCreate) -> Pedido:
    if db.get(Comercio, datos.comercio_id) is None:
        raise NoEncontrado("Comercio no encontrado.")
    cliente = db.get(Cliente, datos.cliente_id)
    if cliente is None:
        raise NoEncontrado("Cliente no encontrado.")
    if len({item.producto_id for item in datos.detalles}) != len(datos.detalles):
        raise DatoInvalido("Incluí cada producto una sola vez en el pedido.")

    pedido = Pedido(
        fecha_pedido=datos.fecha_pedido,
        direccion_entrega=datos.direccion_entrega or cliente.direccion,
        zona=datos.zona,
        horario_estimado=datos.horario_estimado,
        cliente_id=cliente.id_cliente,
        comercio_id=datos.comercio_id,
        estado=EstadoPedido.PENDIENTE,
    )
    for item in datos.detalles:
        producto = db.get(Producto, item.producto_id)
        if producto is None:
            raise NoEncontrado(f"Producto {item.producto_id} no encontrado.")
        if producto.comercio_id != pedido.comercio_id:
            raise DatoInvalido(f"El producto {producto.nombre} no pertenece al comercio del pedido.")
        if producto.stock < item.cantidad:
            raise Conflicto(f"Stock insuficiente para {producto.nombre} (quedan {producto.stock}).")
        producto.stock -= item.cantidad
        pedido.detalles.append(
            DetallePedido(
                producto_id=producto.id_producto,
                cantidad=item.cantidad,
                precio_unitario=producto.precio,
            )
        )

    db.add(pedido)
    db.commit()
    return obtener_pedido(db, pedido.id_pedido)


def actualizar_pedido(db: Session, pedido_id: int, datos: PedidoUpdate) -> Pedido:
    pedido = obtener_pedido(db, pedido_id)
    if pedido.estado != EstadoPedido.PENDIENTE:
        raise Conflicto("Solo se pueden editar pedidos pendientes de asignación.")
    for campo, valor in datos.model_dump().items():
        setattr(pedido, campo, valor)
    db.commit()
    return obtener_pedido(db, pedido_id)


def asignar_repartidor(db: Session, pedido_id: int, repartidor_id: int) -> Pedido:
    pedido = obtener_pedido(db, pedido_id)
    if pedido.estado not in {EstadoPedido.PENDIENTE, EstadoPedido.ASIGNADO}:
        raise Conflicto(f"No se puede asignar un pedido en estado {pedido.estado}.")

    repartidor = db.get(Repartidor, repartidor_id)
    if repartidor is None:
        raise NoEncontrado("Repartidor no encontrado.")
    if repartidor.comercio_id != pedido.comercio_id:
        raise Conflicto("El repartidor no pertenece al comercio del pedido.")
    if not repartidor.disponible:
        raise Conflicto("El repartidor no está disponible.")
    if not mismas_zonas(repartidor.zona, pedido.zona):
        raise Conflicto("El repartidor no cubre la zona de entrega del pedido.")

    if pedido.entrega is None:
        pedido.entrega = Entrega(repartidor_id=repartidor.id_repartidor, estado=EstadoEntrega.ASIGNADA)
    else:
        pedido.entrega.repartidor_id = repartidor.id_repartidor
    pedido.estado = EstadoPedido.ASIGNADO
    db.commit()
    db.expire_all()
    return obtener_pedido(db, pedido_id)


def devolver_stock(pedido: Pedido) -> None:
    for detalle in pedido.detalles:
        detalle.producto.stock += detalle.cantidad


def cancelar_pedido(db: Session, pedido_id: int) -> Pedido:
    pedido = obtener_pedido(db, pedido_id)
    if pedido.estado in PEDIDOS_FINALIZADOS:
        raise Conflicto(f"El pedido ya está {pedido.estado.lower()}.")
    devolver_stock(pedido)
    pedido.estado = EstadoPedido.CANCELADO
    if pedido.entrega is not None:
        pedido.entrega.estado = EstadoEntrega.CANCELADA
    db.commit()
    return obtener_pedido(db, pedido_id)


def eliminar_pedido(db: Session, pedido_id: int) -> None:
    pedido = obtener_pedido(db, pedido_id)
    if pedido.estado not in {EstadoPedido.PENDIENTE, EstadoPedido.CANCELADO}:
        raise Conflicto("Solo se eliminan pedidos pendientes o cancelados; el resto queda como registro.")
    if pedido.estado == EstadoPedido.PENDIENTE:
        devolver_stock(pedido)
    db.delete(pedido)
    db.commit()
