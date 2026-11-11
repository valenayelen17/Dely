from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ErrorDely(Exception):
    status_code = 400

    def __init__(self, detalle: str):
        super().__init__(detalle)
        self.detalle = detalle


class NoEncontrado(ErrorDely):
    status_code = 404


class Conflicto(ErrorDely):
    status_code = 409


class DatoInvalido(ErrorDely):
    status_code = 422


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(ErrorDely)
    async def manejar_error_dely(_: Request, error: ErrorDely) -> JSONResponse:
        return JSONResponse(status_code=error.status_code, content={"detail": error.detalle})
