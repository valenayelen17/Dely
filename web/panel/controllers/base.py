from django.shortcuts import render
from django.views import View

from ..src.services import ErrorApi


class ControladorDely(View):
    """Controlador base: si la API falla, muestra una página de error amigable."""

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except ErrorApi as error:
            # 404 si la API no encontró el recurso; 502 si la API falló o no respondió.
            status = 404 if error.status == 404 else 502
            return render(request, "error.html", {"mensaje": str(error)}, status=status)
