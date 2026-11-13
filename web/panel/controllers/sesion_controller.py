from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from ..forms import LoginForm
from ..src import services
from ..src.services import ErrorApi


class LoginController(View):
    """Inicia sesión contra la API y guarda el JWT en la sesión. Sólo entra el encargado."""

    template = "login.html"

    def destino(self, request) -> str:
        siguiente = request.POST.get("next") or request.GET.get("next") or ""
        if url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
            return siguiente
        return "pendientes"

    def get(self, request):
        if request.session.get("token"):
            return redirect("pendientes")
        return render(request, self.template, {"form": LoginForm(), "next": request.GET.get("next", "")})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                sesion = services.login(form.cleaned_data["email"], form.cleaned_data["password"])
            except ErrorApi as error:
                form.add_error(None, str(error))
            else:
                if sesion["usuario"]["rol"] != "encargado":
                    form.add_error(None, "Esta cuenta no es de encargado: el panel es sólo para el comercio.")
                else:
                    request.session.cycle_key()
                    request.session["token"] = sesion["access_token"]
                    request.session["usuario"] = sesion["usuario"]
                    return redirect(self.destino(request))
        contexto = {"form": form, "next": request.POST.get("next", "")}
        return render(request, self.template, contexto, status=400)


class LogoutController(View):
    def post(self, request):
        request.session.flush()
        messages.success(request, "Cerraste sesión.")
        return redirect("login")
