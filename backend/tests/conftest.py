import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "clave-de-prueba-con-largo-suficiente-para-hs256"
os.environ["BCRYPT_ROUNDS"] = "4"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

import models  # noqa: E402, F401
from api import app  # noqa: E402
from database import Base, crear_engine, get_db  # noqa: E402
from estados import Rol  # noqa: E402
from seguridad import hashear  # noqa: E402

PASSWORD = "clave123"


@pytest.fixture
def client():
    engine = crear_engine("sqlite://")
    Base.metadata.create_all(engine)
    Sesion = sessionmaker(bind=engine, autoflush=False)

    def get_db_de_prueba():
        db = Sesion()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_de_prueba

    with Sesion() as db:
        db.add(models.Usuario(email="encargado@dely.com", password_hash=hashear(PASSWORD), rol=Rol.ENCARGADO))
        db.commit()

    # Por defecto los tests actúan como encargado; los de permisos arman sus propios clientes.
    cliente_http = TestClient(app)
    cliente_http.headers["Authorization"] = f"Bearer {iniciar_sesion(cliente_http, 'encargado@dely.com')}"
    yield cliente_http
    app.dependency_overrides.clear()
    engine.dispose()


def iniciar_sesion(cliente_http: TestClient, email: str, password: str = PASSWORD) -> str:
    respuesta = cliente_http.post("/api/auth/login", json={"email": email, "password": password})
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["access_token"]


@pytest.fixture
def como():
    """Devuelve un TestClient autenticado con el email dado (o sin token si email es None)."""

    def _como(email: str | None) -> TestClient:
        otro = TestClient(app)
        if email is not None:
            otro.headers["Authorization"] = f"Bearer {iniciar_sesion(otro, email)}"
        return otro

    return _como


@pytest.fixture
def base(client):
    comercio = client.post(
        "/api/comercios/",
        json={"nombre": "Pizzería Dely", "direccion": "Av. Corrientes 1000", "telefono": "1140000000", "email": "pizzeria@dely.com"},
    ).json()
    cliente = client.post(
        "/api/clientes/",
        json={"nombre": "Ana", "apellido": "Pérez", "telefono": "1150000000", "email": "ana@mail.com", "direccion": "Calle Falsa 123"},
    ).json()
    pizza = client.post(
        "/api/productos/",
        json={"nombre": "Pizza muzzarella", "precio": "12000.00", "categoria": "Pizzas", "stock": 10, "comercio_id": comercio["id_comercio"]},
    ).json()
    empanada = client.post(
        "/api/productos/",
        json={"nombre": "Empanada", "precio": "1500.00", "categoria": "Empanadas", "stock": 24, "comercio_id": comercio["id_comercio"]},
    ).json()
    repartidor_centro = client.post(
        "/api/repartidores/",
        json={"nombre": "Juan", "apellido": "Gómez", "telefono": "1160000000", "zona": "Centro", "comercio_id": comercio["id_comercio"]},
    ).json()
    repartidor_norte = client.post(
        "/api/repartidores/",
        json={"nombre": "Luz", "apellido": "Díaz", "telefono": "1170000000", "zona": "Norte", "comercio_id": comercio["id_comercio"]},
    ).json()
    return {
        "comercio": comercio,
        "cliente": cliente,
        "pizza": pizza,
        "empanada": empanada,
        "repartidor_centro": repartidor_centro,
        "repartidor_norte": repartidor_norte,
    }


@pytest.fixture
def crear_pedido(client, base):
    def _crear(cantidad_pizzas: int = 2, zona: str = "Centro"):
        respuesta = client.post(
            "/api/pedidos/",
            json={
                "zona": zona,
                "horario_estimado": "21:00:00",
                "cliente_id": base["cliente"]["id_cliente"],
                "comercio_id": base["comercio"]["id_comercio"],
                "detalles": [{"producto_id": base["pizza"]["id_producto"], "cantidad": cantidad_pizzas}],
            },
        )
        assert respuesta.status_code == 201, respuesta.text
        return respuesta.json()

    return _crear
