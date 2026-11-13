from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from ..forms import AccesoForm
from ..src import services
from ..src.services import ErrorApi
from .base import ControladorDely


def accesos_por_persona(rol: str) -> dict[int, dict]:
    """{id de repartidor o cliente: cuenta}, para mostrar quién tiene acceso en los listados."""
    campo = f"{rol}_id"
    return {u[campo]: u for u in services.listar_usuarios(rol) if u.get(campo)}


class AccesoController(ControladorDely):
    """Crea o actualiza el email y la contraseña con los que un repartidor o un cliente inicia sesión."""

    template = "acceso.html"
    rol = ""             # "repartidor" o "cliente"
    url_volver = ""

    def obtener(self, pk) -> dict:
        raise NotImplementedError

    def renderizar(self, request, form, persona, cuenta, pk, status=200):
        contexto = {
            "form": form,
            "persona": persona,
            "cuenta": cuenta,
            "rol": self.rol,
            "persona_id": pk,
            "volver": reverse(self.url_volver),
        }
        return render(request, self.template, contexto, status=status)

    def get(self, request, pk):
        persona = self.obtener(pk)
        cuenta = accesos_por_persona(self.rol).get(pk)
        inicial = {"email": cuenta["email"] if cuenta else persona.get("email", "")}
        return self.renderizar(request, AccesoForm(initial=inicial), persona, cuenta, pk)

    def post(self, request, pk):
        persona = self.obtener(pk)
        form = AccesoForm(request.POST)
        if form.is_valid():
            try:
                services.dar_acceso(self.rol, pk, form.cleaned_data["email"], form.cleaned_data["password"])
            except ErrorApi as error:
                form.add_error(None, str(error))
            else:
                messages.success(request, f"{persona['nombre']} {persona['apellido']} ya puede iniciar sesión con {form.cleaned_data['email']}.")
                return redirect(self.url_volver)
        cuenta = accesos_por_persona(self.rol).get(pk)
        return self.renderizar(request, form, persona, cuenta, pk, status=400)


class QuitarAccesoController(ControladorDely):
    """Desactiva la cuenta de un repartidor o un cliente."""

    rol = ""
    url_volver = ""

    def post(self, request, pk):
        try:
            services.quitar_acceso(self.rol, pk)
        except ErrorApi as error:
            messages.error(request, str(error))
        else:
            messages.success(request, "Acceso desactivado. Para volver a habilitarlo, asignale credenciales de nuevo.")
        return redirect(self.url_volver)


class AccesoRepartidorController(AccesoController):
    rol = "repartidor"
    url_volver = "repartidores"

    def obtener(self, pk):
        return services.obtener_repartidor(pk)


class QuitarAccesoRepartidorController(QuitarAccesoController):
    rol = "repartidor"
    url_volver = "repartidores"


class AccesoClienteController(AccesoController):
    rol = "cliente"
    url_volver = "clientes"

    def obtener(self, pk):
        return services.obtener_cliente(pk)


class QuitarAccesoClienteController(QuitarAccesoController):
    rol = "cliente"
    url_volver = "clientes"
