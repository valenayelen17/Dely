from django.contrib import messages
from django.shortcuts import redirect, render

from ..src import services
from ..src.services import ErrorApi
from .base import ControladorDely


class RepartidoresController(ControladorDely):
    def get(self, request):
        comercio = services.obtener_comercio()
        repartidores = services.listar_repartidores(comercio["id_comercio"])
        contexto = {
            "comercio": comercio,
            "repartidores": sorted(repartidores, key=lambda r: (r["zona"], r["nombre"])),
            "en_turno": sum(1 for r in repartidores if r["disponible"]),
        }
        return render(request, "repartidores.html", contexto)


class DisponibilidadController(ControladorDely):
    """Pone al repartidor en turno o fuera de turno."""

    def post(self, request, repartidor_id):
        disponible = request.POST.get("disponible") == "true"
        try:
            repartidor = services.cambiar_disponibilidad(repartidor_id, disponible)
        except ErrorApi as error:
            messages.error(request, str(error))
        else:
            estado = "en turno" if repartidor["disponible"] else "fuera de turno"
            messages.success(request, f"{repartidor['nombre']} {repartidor['apellido']} quedó {estado}.")
        return redirect("repartidores")
