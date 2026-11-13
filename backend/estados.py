from enum import StrEnum


class EstadoPedido(StrEnum):
    PENDIENTE = "Pendiente"
    ASIGNADO = "Asignado"
    EN_CAMINO = "En camino"
    ENTREGADO = "Entregado"
    CANCELADO = "Cancelado"


class EstadoEntrega(StrEnum):
    ASIGNADA = "Asignada"
    EN_CAMINO = "En camino"
    LLEGANDO = "Llegando"
    ENTREGADA = "Entregada"
    CANCELADA = "Cancelada"


class Rol(StrEnum):
    ENCARGADO = "encargado"
    REPARTIDOR = "repartidor"
    CLIENTE = "cliente"


PEDIDOS_ACTIVOS =frozenset({EstadoPedido.PENDIENTE, EstadoPedido.ASIGNADO, EstadoPedido.EN_CAMINO})
PEDIDOS_FINALIZADOS = frozenset({EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO})

ENTREGAS_ACTIVAS = frozenset({EstadoEntrega.ASIGNADA, EstadoEntrega.EN_CAMINO, EstadoEntrega.LLEGANDO})

TRANSICIONES_ENTREGA: dict[EstadoEntrega, frozenset[EstadoEntrega]] = {
    EstadoEntrega.ASIGNADA: frozenset({EstadoEntrega.EN_CAMINO}),
    EstadoEntrega.EN_CAMINO: frozenset({EstadoEntrega.LLEGANDO, EstadoEntrega.ENTREGADA}),
    EstadoEntrega.LLEGANDO: frozenset({EstadoEntrega.ENTREGADA}),
    EstadoEntrega.ENTREGADA: frozenset(),
    EstadoEntrega.CANCELADA: frozenset(),
}

PEDIDO_SEGUN_ENTREGA: dict[EstadoEntrega, EstadoPedido] = {
    EstadoEntrega.ASIGNADA: EstadoPedido.ASIGNADO,
    EstadoEntrega.EN_CAMINO: EstadoPedido.EN_CAMINO,
    EstadoEntrega.LLEGANDO: EstadoPedido.EN_CAMINO,
    EstadoEntrega.ENTREGADA: EstadoPedido.ENTREGADO,
    EstadoEntrega.CANCELADA: EstadoPedido.CANCELADO,
}
