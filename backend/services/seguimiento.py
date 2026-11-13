from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from errores import NoEncontrado
from models import DetallePedido, Entrega, Pedido
from schemas import ProductoSeguimiento, SeguimientoOut


CARGA_SEGUIMIENTO = (
    selectinload(Pedido.comercio),
    selectinload(Pedido.entrega).selectinload(Entrega.repartidor),
    selectinload(Pedido.detalles).selectinload(DetallePedido.producto),
    selectinload(Pedido.notificaciones),
)


def buscar_por_codigo(db: Session, codigo: str, cliente_id: int | None = None) -> Pedido:
    """Busca el pedido por código. Con `cliente_id`, sólo lo encuentra si es de ese cliente."""
    consulta = select(Pedido).options(*CARGA_SEGUIMIENTO).where(Pedido.codigo_seguimiento == codigo.strip().upper())
    if cliente_id is not None:
        consulta = consulta.where(Pedido.cliente_id == cliente_id)
    pedido = db.scalars(consulta).first()
    if pedido is None:
        raise NoEncontrado("No encontramos un pedido con ese código de seguimiento.")
    return pedido


def armar_seguimiento(pedido: Pedido) -> SeguimientoOut:
    entrega = pedido.entrega
    return SeguimientoOut(
        codigo_seguimiento=pedido.codigo_seguimiento,
        estado=pedido.estado,
        estado_entrega=entrega.estado if entrega else None,
        fecha_pedido=pedido.fecha_pedido,
        horario_estimado=pedido.horario_estimado,
        direccion_entrega=pedido.direccion_entrega,
        comercio=pedido.comercio.nombre,
        comercio_telefono=pedido.comercio.telefono,
        repartidor=entrega.repartidor.nombre if entrega else None,
        ubicacion_actual=entrega.ubicacion_actual if entrega else None,
        hora_entrega=entrega.hora_entrega if entrega else None,
        productos=[
            ProductoSeguimiento(nombre=d.producto_nombre, cantidad=d.cantidad, subtotal=d.subtotal)
            for d in pedido.detalles
        ],
        total=pedido.total,
        notificaciones=pedido.notificaciones,
    )


def consultar(db: Session, codigo: str, cliente_id: int | None = None) -> SeguimientoOut:
    return armar_seguimiento(buscar_por_codigo(db, codigo, cliente_id))


def pedidos_del_cliente(db: Session, cliente_id: int) -> list[SeguimientoOut]:
    consulta = (
        select(Pedido)
        .options(*CARGA_SEGUIMIENTO)
        .where(Pedido.cliente_id == cliente_id)
        .order_by(Pedido.fecha_pedido.desc(), Pedido.id_pedido.desc())
    )
    return [armar_seguimiento(pedido) for pedido in db.scalars(consulta).all()]


def marcar_notificaciones_leidas(db: Session, codigo: str, cliente_id: int | None = None) -> SeguimientoOut:
    pedido = buscar_por_codigo(db, codigo, cliente_id)
    for notificacion in pedido.notificaciones:
        notificacion.leida = True
    db.commit()
    return consultar(db, codigo, cliente_id)
