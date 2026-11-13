from .src import services


class TokenApiMiddleware:
    """Pone el JWT de la sesión a disposición de services.py durante cada request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with services.usando_token(request.session.get("token")):
            return self.get_response(request)
