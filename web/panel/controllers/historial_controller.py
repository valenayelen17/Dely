from decimal import Decimal

from django.shortcuts import render

from ..src import services
from .base import ControladorDely

FILTROS = {"entregados": "Entregado", "cancelados": "Cancelado"}


class HistorialController(ControladorDely):
    """Pedidos cerrados: entregados y cancelados."""

    def get(self, request):
        comercio = services.obtener_comercio()
        filtro = request.GET.get("estado")
        pedidos = services.listar_pedidos(comercio["id_comercio"])

        cerrados = [p for p in pedidos if p["estado"] in FILTROS.values()]
        if filtro in FILTROS:
            cerrados = [p for p in cerrados if p["estado"] == FILTROS[filtro]]
        entregados = [p for p in pedidos if p["estado"] == "Entregado"]

        contexto = {
            "comercio": comercio,
            "pedidos": cerrados,
            "filtro": filtro if filtro in FILTROS else None,
            "cantidad_entregados": len(entregados),
            "facturado": sum((Decimal(str(p["total"])) for p in entregados), Decimal(0)),
        }
        return render(request, "historial.html", contexto)
