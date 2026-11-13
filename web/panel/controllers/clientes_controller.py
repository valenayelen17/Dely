from django.shortcuts import render

from ..forms import ClienteForm
from ..src import services
from .accesos_controller import accesos_por_persona
from .base import ControladorDely
from .formulario_controller import FormularioController


class ClientesController(ControladorDely):
    def get(self, request):
        comercio = services.obtener_comercio()
        busqueda = request.GET.get("q", "").strip()
        clientes = sorted(services.listar_clientes(), key=lambda c: (c["apellido"], c["nombre"]))
        if busqueda:
            texto = busqueda.lower()
            clientes = [
                c for c in clientes
                if texto in f"{c['nombre']} {c['apellido']} {c['telefono']} {c['email']}".lower()
            ]
        contexto = {
            "comercio": comercio,
            "clientes": clientes,
            "busqueda": busqueda,
            "accesos": accesos_por_persona("cliente"),
        }
        return render(request, "clientes.html", contexto)


class ClienteFormularioController(FormularioController):
    form_class = ClienteForm
    entidad = "cliente"
    url_volver = "clientes"

    def obtener(self, pk):
        return services.obtener_cliente(pk)

    def crear(self, datos):
        return services.crear_cliente(datos)

    def editar(self, pk, datos):
        return services.editar_cliente(pk, datos)

    def nombre(self, objeto):
        return f"{objeto['nombre']} {objeto['apellido']}"
