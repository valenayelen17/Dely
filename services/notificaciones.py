from datetime import datetime

from estados import EstadoEntrega
from models import Notificacion, Pedido

RECIBIDO = "Recibido"


def mensaje_para(pedido: Pedido, estado: EstadoEntrega) -> str:
    repartidor = pedido.entrega.repartidor.nombre if pedido.entrega else "El repartidor"
    mensajes = {
        EstadoEntrega.ASIGNADA: f"{repartidor} va a llevar tu pedido.",
        EstadoEntrega.EN_CAMINO: f"Tu pedido está en camino con {repartidor}.",
        EstadoEntrega.LLEGANDO: f"{repartidor} está llegando a {pedido.direccion_entrega}. ¡Preparate para recibirlo!",
        EstadoEntrega.ENTREGADA: "Tu pedido fue entregado. ¡Gracias por tu compra!",
        EstadoEntrega.CANCELADA: "Tu pedido fue cancelado.",
    }
    return mensajes[estado]


def notificar(pedido: Pedido, tipo: str, mensaje: str) -> None:
    pedido.notificaciones.append(
        Notificacion(tipo=tipo, mensaje=mensaje, fecha_hora=datetime.now().replace(microsecond=0))
    )


def notificar_recepcion(pedido: Pedido) -> None:
    hora = pedido.horario_estimado.strftime("%H:%M")
    notificar(pedido, RECIBIDO, f"Recibimos tu pedido. Horario estimado de entrega: {hora}.")


def notificar_estado(pedido: Pedido, estado: EstadoEntrega) -> None:
    notificar(pedido, estado, mensaje_para(pedido, estado))
