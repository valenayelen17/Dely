"""Acceso a la API de DELY con requests.

Es la capa de Modelo del panel: los controladores nunca arman URLs ni hacen
requests directamente, sólo llaman a estas funciones.
"""

from contextlib import contextmanager
from contextvars import ContextVar

import requests
from django.conf import settings

TIMEOUT = 10

# JWT del encargado logueado. Lo carga TokenApiMiddleware desde la sesión en cada request.
_token: ContextVar[str | None] = ContextVar("token_api", default=None)


@contextmanager
def usando_token(token: str | None):
    marca = _token.set(token)
    try:
        yield
    finally:
        _token.reset(marca)


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
    token = _token.get()
    if token:
        kwargs["headers"] = {**kwargs.get("headers", {}), "Authorization": f"Bearer {token}"}
    try:
        respuesta = requests.request(metodo, _url(ruta), timeout=TIMEOUT, **kwargs)
    except requests.exceptions.RequestException as error:
        raise ErrorApi("No se pudo conectar con la API de DELY. ¿Está corriendo en el puerto 8000?") from error
    if respuesta.status_code >= 400:
        raise ErrorApi(_mensaje_de_error(respuesta), respuesta.status_code)
    if respuesta.status_code == 204 or not respuesta.content:
        return None
    return respuesta.json()


# --- Autenticación ------------------------------------------------------------

def login(email: str, password: str) -> dict:
    """Devuelve {access_token, expira, usuario} o lanza ErrorApi (401 si las credenciales no son válidas)."""
    return _pedir("POST", "auth/login", json={"email": email, "password": password})


def listar_usuarios(rol: str) -> list[dict]:
    return _pedir("GET", "usuarios/", params={"rol": rol})


def dar_acceso(rol: str, id_persona: int, email: str, password: str) -> dict:
    """Crea o actualiza las credenciales de un repartidor o un cliente."""
    recurso = {"repartidor": "repartidores", "cliente": "clientes"}[rol]
    return _pedir("PUT", f"usuarios/{recurso}/{id_persona}/acceso", json={"email": email, "password": password})


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


def editar_pedido(pedido_id: int, datos: dict) -> dict:
    """Sólo para pedidos Pendientes: dirección, zona y horario."""
    return _pedir("PUT", f"pedidos/{pedido_id}", json=datos)


# --- Repartidores -------------------------------------------------------------

def listar_repartidores(comercio_id: int, zona: str | None = None, disponible: bool | None = None) -> list[dict]:
    params = {"comercio_id": comercio_id, "limit": 500}
    if zona:
        params["zona"] = zona
    if disponible is not None:
        params["disponible"] = str(disponible).lower()
    return _pedir("GET", "repartidores/", params=params)


def obtener_repartidor(repartidor_id: int) -> dict:
    return _pedir("GET", f"repartidores/{repartidor_id}")


def crear_repartidor(datos: dict) -> dict:
    return _pedir("POST", "repartidores/", json=datos)


def editar_repartidor(repartidor_id: int, datos: dict) -> dict:
    return _pedir("PUT", f"repartidores/{repartidor_id}", json=datos)


def cambiar_disponibilidad(repartidor_id: int, disponible: bool) -> dict:
    return _pedir("PATCH", f"repartidores/{repartidor_id}/disponibilidad", json={"disponible": disponible})


# --- Clientes -----------------------------------------------------------------

def listar_clientes() -> list[dict]:
    return _pedir("GET", "clientes/", params={"limit": 500})


def obtener_cliente(cliente_id: int) -> dict:
    return _pedir("GET", f"clientes/{cliente_id}")


def crear_cliente(datos: dict) -> dict:
    return _pedir("POST", "clientes/", json=datos)


def editar_cliente(cliente_id: int, datos: dict) -> dict:
    return _pedir("PUT", f"clientes/{cliente_id}", json=datos)


# --- Productos ----------------------------------------------------------------

def listar_productos(comercio_id: int) -> list[dict]:
    return _pedir("GET", "productos/", params={"comercio_id": comercio_id, "limit": 500})


def obtener_producto(producto_id: int) -> dict:
    return _pedir("GET", f"productos/{producto_id}")


def crear_producto(datos: dict) -> dict:
    return _pedir("POST", "productos/", json=datos)


def editar_producto(producto_id: int, datos: dict) -> dict:
    return _pedir("PUT", f"productos/{producto_id}", json=datos)
