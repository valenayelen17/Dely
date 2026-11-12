from django.contrib import messages
from django.shortcuts import redirect, render

from ..src import services
from ..src.services import ErrorApi
from .base import ControladorDely

ESTADOS_ACTIVOS = ["Pendiente", "Asignado", "En camino"]
ESTADOS_CERRADOS = ["Entregado", "Cancelado"]


def zonas_del_comercio(comercio_id: int) -> list[str]:
    return sorted({r["zona"] for r in services.listar_repartidores(comercio_id)})


class PendientesController(ControladorDely):
    """HU-01: el encargado ve los pedidos no entregados, agrupados por estado."""

    def get(self, request):
        comercio = services.obtener_comercio()
        zona = request.GET.get("zona") or None
        pedidos = services.listar_pendientes(comercio["id_comercio"], zona)

        columnas = [(estado, [p for p in pedidos if p["estado"] == estado]) for estado in ESTADOS_ACTIVOS]
        contexto = {
            "comercio": comercio,
            "columnas": columnas,
            "zonas": zonas_del_comercio(comercio["id_comercio"]),
            "zona": zona,
            "total_activos": len(pedidos),
            "sin_repartidor": sum(1 for p in pedidos if p["estado"] == "Pendiente"),
        }
        return render(request, "pedidos/pendientes.html", contexto)


class PedidoDetalleController(ControladorDely):
    """Detalle del pedido con la asignación de repartidor (HU-02) y la cancelación."""

    def get(self, request, pedido_id):
        comercio = services.obtener_comercio()
        pedido = services.obtener_pedido(pedido_id)
        entrega = pedido["entrega"]

        # Se puede asignar si está Pendiente, o reasignar mientras el repartidor no salió.
        puede_asignar = pedido["estado"] == "Pendiente" or (entrega is not None and entrega["estado"] == "Asignada")
        repartidores = []
        if puede_asignar:
            repartidores = services.listar_repartidores(comercio["id_comercio"], zona=pedido["zona"], disponible=True)

        contexto = {
            "comercio": comercio,
            "pedido": pedido,
            "entrega": entrega,
            "puede_asignar": puede_asignar,
            "puede_cancelar": pedido["estado"] not in ESTADOS_CERRADOS,
            "repartidores": repartidores,
            "notificaciones": services.notificaciones_del_pedido(pedido_id),
        }
        return render(request, "pedidos/detalle.html", contexto)


class AsignarRepartidorController(ControladorDely):
    def post(self, request, pedido_id):
        repartidor_id = request.POST.get("repartidor_id")
        if not repartidor_id:
            messages.error(request, "Elegí un repartidor.")
            return redirect("pedido_detalle", pedido_id=pedido_id)
        try:
            pedido = services.asignar_repartidor(pedido_id, int(repartidor_id))
        except ErrorApi as error:
            messages.error(request, str(error))
        else:
            repartidor = pedido["entrega"]["repartidor"]
            messages.success(request, f"Pedido asignado a {repartidor['nombre']} {repartidor['apellido']}.")
        return redirect("pedido_detalle", pedido_id=pedido_id)


class CancelarPedidoController(ControladorDely):
    def post(self, request, pedido_id):
        try:
            pedido = services.cancelar_pedido(pedido_id)
        except ErrorApi as error:
            messages.error(request, str(error))
        else:
            messages.success(request, f"Pedido {pedido['codigo_seguimiento']} cancelado. Se devolvió el stock.")
        return redirect("pedido_detalle", pedido_id=pedido_id)


class NuevoPedidoController(ControladorDely):
    """Carga de un pedido: cliente, zona, horario y productos."""

    template = "pedidos/nuevo.html"

    def contexto(self, comercio, datos=None):
        return {
            "comercio": comercio,
            "clientes": services.listar_clientes(),
            "productos": services.listar_productos(comercio["id_comercio"]),
            "zonas": zonas_del_comercio(comercio["id_comercio"]),
            "datos": datos or {},
        }

    def get(self, request):
        return render(request, self.template, self.contexto(services.obtener_comercio()))

    def post(self, request):
        comercio = services.obtener_comercio()
        productos = services.listar_productos(comercio["id_comercio"])

        detalles = []
        for producto in productos:
            cantidad = request.POST.get(f"cantidad_{producto['id_producto']}", "0")
            if cantidad.isdigit() and int(cantidad) > 0:
                detalles.append({"producto_id": producto["id_producto"], "cantidad": int(cantidad)})

        datos = {
            "cliente_id": request.POST.get("cliente_id", ""),
            "zona": request.POST.get("zona", "").strip(),
            "horario_estimado": request.POST.get("horario_estimado", ""),
            "direccion_entrega": request.POST.get("direccion_entrega", "").strip(),
            "cantidades": {str(d["producto_id"]): d["cantidad"] for d in detalles},
        }

        error = None
        if not datos["cliente_id"].isdigit():
            error = "Elegí un cliente."
        elif not datos["zona"] or not datos["horario_estimado"]:
            error = "Completá la zona y el horario estimado."
        elif not detalles:
            error = "Agregá al menos un producto."

        if error is None:
            cuerpo = {
                "cliente_id": int(datos["cliente_id"]),
                "comercio_id": comercio["id_comercio"],
                "zona": datos["zona"],
                "horario_estimado": datos["horario_estimado"],
                "detalles": detalles,
            }
            if datos["direccion_entrega"]:
                cuerpo["direccion_entrega"] = datos["direccion_entrega"]
            try:
                pedido = services.crear_pedido(cuerpo)
            except ErrorApi as error_api:
                error = str(error_api)
            else:
                messages.success(
                    request,
                    f"Pedido creado. Código de seguimiento para el cliente: {pedido['codigo_seguimiento']}.",
                )
                return redirect("pedido_detalle", pedido_id=pedido["id_pedido"])

        messages.error(request, error)
        return render(request, self.template, self.contexto(comercio, datos), status=400)
