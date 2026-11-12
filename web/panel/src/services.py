"""Acceso a la API de DELY con requests.

Es la capa de Modelo del panel: los controladores nunca arman URLs ni hacen
requests directamente, sólo llaman a estas funciones.
"""

import requests
from django.conf import settings

TIMEOUT = 10


class ErrorApi(Exception):
    """Error de negocio o de conexión, con un mensaje listo para mostrar.

    `status` es el código HTTP que devolvió la API (None si no se pudo conectar).
    """

    def __init__(self, mensaje: str, status: int | None = None):
        super().__init__(mensaje)
        self.status = status


def _url(ruta: str) -> str:
    return settings.API_URL.rstrip("/") + "/" + ruta.lstrip("/")


def _mensaje_de_error(respuesta: requests.Response) -> str:
    try:
        detalle = respuesta.json().get("detail")
    except ValueError:
        return f"La API respondió {respuesta.status_code}."
    if isinstance(detalle, list):  # errores de validación de FastAPI
        return " ".join(str(error.get("msg", error)) for error in detalle)
    return str(detalle or f"La API respondió {respuesta.status_code}.")


def _pedir(metodo: str, ruta: str, **kwargs):
    try:
        respuesta = requests.request(metodo, _url(ruta), timeout=TIMEOUT, **kwargs)
    except requests.exceptions.RequestException as error:
        raise ErrorApi("No se pudo conectar con la API de DELY. ¿Está corriendo en el puerto 8000?") from error
    if respuesta.status_code >= 400:
        raise ErrorApi(_mensaje_de_error(respuesta), respuesta.status_code)
    if respuesta.status_code == 204 or not respuesta.content:
        return None
    return respuesta.json()


# --- Comercio -----------------------------------------------------------------

def obtener_comercio() -> dict:
    comercios = _pedir("GET", "comercios/", params={"limit": 1})
    if not comercios:
        raise ErrorApi("No hay comercios cargados. Corré backend/seed.py para cargar los datos de demo.")
    return comercios[0]


# --- Pedidos ------------------------------------------------------------------

def listar_pendientes(comercio_id: int, zona: str | None = None) -> list[dict]:
    params = {"comercio_id": comercio_id}
    if zona:
        params["zona"] = zona
    return _pedir("GET", "pedidos/pendientes", params=params)


def listar_pedidos(comercio_id: int, estado: str | None = None) -> list[dict]:
    params = {"comercio_id": comercio_id, "limit": 500}
    if estado:
        params["estado"] = estado
    return _pedir("GET", "pedidos/", params=params)


def obtener_pedido(pedido_id: int) -> dict:
    return _pedir("GET", f"pedidos/{pedido_id}")


def notificaciones_del_pedido(pedido_id: int) -> list[dict]:
    return _pedir("GET", f"pedidos/{pedido_id}/notificaciones")


def crear_pedido(datos: dict) -> dict:
    return _pedir("POST", "pedidos/", json=datos)


def asignar_repartidor(pedido_id: int, repartidor_id: int) -> dict:
    return _pedir("PATCH", f"pedidos/{pedido_id}/asignar", json={"repartidor_id": repartidor_id})


def cancelar_pedido(pedido_id: int) -> dict:
    return _pedir("PATCH", f"pedidos/{pedido_id}/cancelar")


# --- Repartidores, clientes y productos ---------------------------------------

def listar_repartidores(comercio_id: int, zona: str | None = None, disponible: bool | None = None) -> list[dict]:
    params = {"comercio_id": comercio_id}
    if zona:
        params["zona"] = zona
    if disponible is not None:
        params["disponible"] = str(disponible).lower()
    return _pedir("GET", "repartidores/", params=params)


def cambiar_disponibilidad(repartidor_id: int, disponible: bool) -> dict:
    return _pedir("PATCH", f"repartidores/{repartidor_id}/disponibilidad", json={"disponible": disponible})


def listar_clientes() -> list[dict]:
    return _pedir("GET", "clientes/", params={"limit": 500})


def listar_productos(comercio_id: int) -> list[dict]:
    return _pedir("GET", "productos/", params={"comercio_id": comercio_id, "limit": 500})
