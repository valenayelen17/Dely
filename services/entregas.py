from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from errores import Conflicto, NoEncontrado
from estados import ENTREGAS_ACTIVAS, PEDIDO_SEGUN_ENTREGA, TRANSICIONES_ENTREGA, EstadoEntrega
from models import DetallePedido, Entrega, Pedido, Repartidor
from services.notificaciones import notificar_estado

CARGA_ENTREGA = (
    selectinload(Entrega.repartidor),
    selectinload(Entrega.pedido).selectinload(Pedido.cliente),
    selectinload(Entrega.pedido).selectinload(Pedido.detalles).selectinload(DetallePedido.producto),
)


def obtener_entrega(db: Session, entrega_id: int) -> Entrega:
    entrega = db.scalars(
        select(Entrega).options(*CARGA_ENTREGA).where(Entrega.id_entrega == entrega_id)
    ).first()
    if entrega is None:
        raise NoEncontrado("Entrega no encontrada.")
    return entrega


def entregas_de_repartidor(db: Session, repartidor_id: int, solo_activas: bool) -> list[Entrega]:
    if db.get(Repartidor, repartidor_id) is None:
        raise NoEncontrado("Repartidor no encontrado.")
    consulta = (
        select(Entrega)
        .options(*CARGA_ENTREGA)
        .join(Entrega.pedido)
        .where(Entrega.repartidor_id == repartidor_id)
        .order_by(Pedido.fecha_pedido, Pedido.horario_estimado)
    )
    if solo_activas:
        consulta = consulta.where(Entrega.estado.in_(ENTREGAS_ACTIVAS))
    return list(db.scalars(consulta).all())


def cambiar_estado(
    db: Session, entrega_id: int, nuevo: EstadoEntrega, ubicacion: str | None = None
) -> Entrega:
    entrega = obtener_entrega(db, entrega_id)
    actual = EstadoEntrega(entrega.estado)
    if nuevo not in TRANSICIONES_ENTREGA[actual]:
        raise Conflicto(f"La entrega no puede pasar de {actual} a {nuevo}.")

    entrega.estado = nuevo
    if ubicacion:
        entrega.ubicacion_actual = ubicacion
    if nuevo == EstadoEntrega.ENTREGADA:
        ahora = datetime.now()
        entrega.fecha_entrega = ahora.date()
        entrega.hora_entrega = ahora.time().replace(microsecond=0)
        entrega.ubicacion_actual = entrega.pedido.direccion_entrega
    entrega.pedido.estado = PEDIDO_SEGUN_ENTREGA[nuevo]
    notificar_estado(entrega.pedido, nuevo)
    db.commit()
    return obtener_entrega(db, entrega_id)


def actualizar_ubicacion(db: Session, entrega_id: int, ubicacion: str) -> Entrega:
    entrega = obtener_entrega(db, entrega_id)
    if entrega.estado not in {EstadoEntrega.EN_CAMINO, EstadoEntrega.LLEGANDO}:
        raise Conflicto("Solo se actualiza la ubicación de entregas en camino.")
    entrega.ubicacion_actual = ubicacion
    db.commit()
    return obtener_entrega(db, entrega_id)
