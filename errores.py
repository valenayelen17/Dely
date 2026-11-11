"""Errores de negocio y su traducción a respuestas HTTP.

Los servicios lanzan estas excepciones sin conocer HTTP; api.py las convierte
en respuestas JSON con el código de estado correspondiente.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ErrorDely(Exception):
    status_code = 400

    def __init__(self, detalle: str):
        super().__init__(detalle)
        self.detalle = detalle


class NoEncontrado(ErrorDely):
    """El recurso pedido no existe (404)."""

    status_code = 404


class Conflicto(ErrorDely):
    """La operación choca con el estado actual de los datos (409)."""

    status_code = 409


class DatoInvalido(ErrorDely):
    """Los datos son válidos en forma pero no cumplen una regla de negocio (422)."""

    status_code = 422


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(ErrorDely)
    async def manejar_error_dely(_: Request, error: ErrorDely) -> JSONResponse:
        return JSONResponse(status_code=error.status_code, content={"detail": error.detalle})
