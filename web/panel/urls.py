"""Rutas del panel web del encargado."""

from django.urls import path
from django.views.generic import RedirectView

from panel.controllers.clientes_controller import ClienteFormularioController, ClientesController
from panel.controllers.historial_controller import HistorialController
from panel.controllers.pedidos_controller import (
    AsignarRepartidorController,
    CancelarPedidoController,
    EditarPedidoController,
    NuevoPedidoController,
    PedidoDetalleController,
    PendientesController,
)
from panel.controllers.productos_controller import ProductoFormularioController, ProductosController
from panel.controllers.repartidores_controller import (
    DisponibilidadController,
    RepartidoresController,
    RepartidorFormularioController,
)

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="pendientes", permanent=False)),
    # Pedidos
    path("pedidos/", PendientesController.as_view(), name="pendientes"),
    path("pedidos/nuevo/", NuevoPedidoController.as_view(), name="nuevo_pedido"),
    path("pedidos/<int:pedido_id>/", PedidoDetalleController.as_view(), name="pedido_detalle"),
    path("pedidos/<int:pk>/editar/", EditarPedidoController.as_view(), name="pedido_editar"),
    path("pedidos/<int:pedido_id>/asignar/", AsignarRepartidorController.as_view(), name="asignar_repartidor"),
    path("pedidos/<int:pedido_id>/cancelar/", CancelarPedidoController.as_view(), name="cancelar_pedido"),
    path("historial/", HistorialController.as_view(), name="historial"),
    # Repartidores
    path("repartidores/", RepartidoresController.as_view(), name="repartidores"),
    path("repartidores/nuevo/", RepartidorFormularioController.as_view(), name="repartidor_nuevo"),
    path("repartidores/<int:pk>/editar/", RepartidorFormularioController.as_view(), name="repartidor_editar"),
    path(
        "repartidores/<int:repartidor_id>/disponibilidad/",
        DisponibilidadController.as_view(),
        name="disponibilidad",
    ),
    # Productos
    path("productos/", ProductosController.as_view(), name="productos"),
    path("productos/nuevo/", ProductoFormularioController.as_view(), name="producto_nuevo"),
    path("productos/<int:pk>/editar/", ProductoFormularioController.as_view(), name="producto_editar"),
    # Clientes
    path("clientes/", ClientesController.as_view(), name="clientes"),
    path("clientes/nuevo/", ClienteFormularioController.as_view(), name="cliente_nuevo"),
    path("clientes/<int:pk>/editar/", ClienteFormularioController.as_view(), name="cliente_editar"),
]
