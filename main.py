from cliente import Cliente
from repartidor import Repartidor
from pedido import Pedido
from entrega import Entrega
from producto import Producto
from detalle_pedido import DetallePedido


cliente = Cliente(
    1,
    "Valentina",
    "De Jesús",
    "1123456789",
    "valentina@gmail.com",
    "Av. Siempre Viva 123"
)

repartidor = Repartidor(
    1,
    "Juan",
    "Gómez",
    "1198765432",
    "Zona Centro"
)

pedido = Pedido(
    1,
    "15/09/2026",
    cliente.direccion,
    "Pendiente",
    "20:00 - 21:00"
)

producto = Producto(
    1,
    "Pizza",
    "Pizza muzzarella",
    12000,
    "Comida",
    10
)

detalle = DetallePedido(
    1,
    2,
    producto.precio
)

entrega = Entrega(
    1,
    "15/09/2026",
    "20:30",
    "Pendiente",
    "Comercio"
)

entrega.iniciar_entrega()
entrega.actualizar_ubicacion("Av. Siempre Viva 100")

pedido.agregar_detalle(detalle)
pedido.asignar_repartidor(repartidor)

print("=================================")
print("             DELY")
print("=================================")

print("\nCliente:", cliente.nombre, cliente.apellido)
print("Pedido:", pedido.id_pedido)
print("Dirección:", pedido.direccion_entrega)
print("Estado:", pedido.estado)
print("Repartidor:", pedido.repartidor.nombre, pedido.repartidor.apellido)
print("Estado de entrega:", entrega.estado)
print("Ubicación actual:", entrega.ubicacion_actual)
print("Producto:", producto.nombre)
print("Cantidad:", detalle.cantidad)
print("Subtotal: $", detalle.calcular_subtotal())