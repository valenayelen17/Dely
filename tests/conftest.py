import os

os.environ["DATABASE_URL"] = "sqlite://"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

import models  # noqa: E402, F401
from api import app  # noqa: E402
from database import Base, crear_engine, get_db  # noqa: E402


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
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()


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
