from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from ..src import services
from ..src.services import ErrorApi
from .base import ControladorDely


class FormularioController(ControladorDely):
    """Alta y edición genérica contra la API.

    Cada subclase indica el formulario, las funciones del servicio y a dónde volver.
    Con `pk` en la URL edita; sin `pk` da de alta.
    """

    template = "formulario.html"
    form_class = None
    entidad = ""             # "cliente", "producto"...
    url_volver = ""          # nombre de la ruta del listado
    usa_comercio = False     # agrega comercio_id al cuerpo que se envía a la API

    def obtener(self, pk):
        raise NotImplementedError

    def crear(self, datos):
        raise NotImplementedError

    def editar(self, pk, datos):
        raise NotImplementedError

    def inicial(self, objeto: dict) -> dict:
        return {campo: objeto.get(campo) for campo in self.form_class.base_fields}

    def nombre(self, objeto: dict) -> str:
        return objeto.get("nombre", "")

    def destino(self, objeto: dict):
        return redirect(self.url_volver)

    def volver(self, pk) -> str:
        """URL del botón Volver / Cancelar."""
        return reverse(self.url_volver)

    def contexto_extra(self, comercio) -> dict:
        return {}

    def renderizar(self, request, form, comercio, pk, status=200):
        accion = "Editar" if pk else "Nuevo"
        contexto = {
            "comercio": comercio,
            "form": form,
            "titulo": f"{accion} {self.entidad}",
            "volver": self.volver(pk),
            "editando": pk is not None,
            **self.contexto_extra(comercio),
        }
        return render(request, self.template, contexto, status=status)

    def get(self, request, pk=None):
        comercio = services.obtener_comercio()
        form = self.form_class(initial=self.inicial(self.obtener(pk))) if pk else self.form_class()
        return self.renderizar(request, form, comercio, pk)

    def post(self, request, pk=None):
        comercio = services.obtener_comercio()
        form = self.form_class(request.POST)
        if form.is_valid():
            datos = form.datos_api()
            if self.usa_comercio:
                datos["comercio_id"] = comercio["id_comercio"]
            try:
                objeto = self.editar(pk, datos) if pk else self.crear(datos)
            except ErrorApi as error:
                form.add_error(None, str(error))
            else:
                verbo = "actualizado" if pk else "creado"
                messages.success(request, f"{self.entidad.capitalize()} {self.nombre(objeto)} {verbo}.")
                return self.destino(objeto)
        return self.renderizar(request, form, comercio, pk, status=400)
