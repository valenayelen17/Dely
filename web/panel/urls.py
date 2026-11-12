"""Rutas del panel web del encargado."""

from django.urls import path
from django.views.generic import RedirectView

from panel.controllers.historial_controller import HistorialController
from panel.controllers.pedidos_controller import (
    AsignarRepartidorController,
    CancelarPedidoController,
    NuevoPedidoController,
    PedidoDetalleController,
    PendientesController,
)
from panel.controllers.repartidores_controller import DisponibilidadController, RepartidoresController

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="pendientes", permanent=False)),
    path("pedidos/", PendientesController.as_view(), name="pendientes"),
    path("pedidos/nuevo/", NuevoPedidoController.as_view(), name="nuevo_pedido"),
    path("pedidos/<int:pedido_id>/", PedidoDetalleController.as_view(), name="pedido_detalle"),
    path("pedidos/<int:pedido_id>/asignar/", AsignarRepartidorController.as_view(), name="asignar_repartidor"),
    path("pedidos/<int:pedido_id>/cancelar/", CancelarPedidoController.as_view(), name="cancelar_pedido"),
    path("repartidores/", RepartidoresController.as_view(), name="repartidores"),
    path(
        "repartidores/<int:repartidor_id>/disponibilidad/",
        DisponibilidadController.as_view(),
        name="disponibilidad",
    ),
    path("historial/", HistorialController.as_view(), name="historial"),
]
