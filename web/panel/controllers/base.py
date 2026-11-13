from urllib.parse import urlencode

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from ..src.services import ErrorApi


def ir_al_login(request):
    destino = reverse("login")
    if request.method == "GET":
        destino += "?" + urlencode({"next": request.get_full_path()})
    return redirect(destino)


class ControladorDely(View):
    """Controlador base del panel.

    - Exige que el encargado haya iniciado sesión (hay un JWT en la sesión).
    - Si la API responde 401 (token vencido o inválido), cierra la sesión y vuelve al login.
    - Cualquier otro error de la API se muestra en una página de error amigable.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("token"):
            return ir_al_login(request)
        try:
            return super().dispatch(request, *args, **kwargs)
        except ErrorApi as error:
            if error.status == 401:
                request.session.flush()
                messages.warning(request, "Tu sesión venció. Volvé a iniciar sesión.")
                return ir_al_login(request)
            # 404 si la API no encontró el recurso; 502 si la API falló o no respondió.
            status = {404: 404, 403: 403}.get(error.status, 502)
            return render(request, "error.html", {"mensaje": str(error)}, status=status)
