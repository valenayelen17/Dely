from django.conf import settings


def dely(request):
    """Datos comunes a todas las pantallas del panel."""
    match = getattr(request, "resolver_match", None)
    return {
        "seccion": match.url_name if match else "",
        "frontend_url": settings.FRONTEND_URL.rstrip("/"),
    }
