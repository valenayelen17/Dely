from api import app
from database import get_db
from models import Usuario
from seed import PASSWORD_DEMO, cargar, cargar_usuarios


def test_seed_carga_un_escenario_completo_una_sola_vez(client):
    db = next(app.dependency_overrides[get_db]())

    assert cargar(db) is True
    assert cargar(db) is False

    estados = sorted(p["estado"] for p in client.get("/api/pedidos/").json())
    assert estados == ["Asignado", "Cancelado", "En camino", "En camino", "Entregado", "Pendiente", "Pendiente"]
    assert len(client.get("/api/pedidos/pendientes").json()) == 5


def test_seed_crea_cuentas_de_demo_para_cada_rol(client):
    db = next(app.dependency_overrides[get_db]())
    cargar(db)
    db.query(Usuario).delete()  # el fixture crea un encargado de prueba; el seed sólo actúa sobre una base sin cuentas
    db.commit()

    assert cargar_usuarios(db) is True
    assert cargar_usuarios(db) is False

    for email, rol in [("encargado@dely.com", "encargado"), ("lucia.fernandez@dely.com", "repartidor"), ("ana.perez@ejemplo.com", "cliente")]:
        respuesta = client.post("/api/auth/login", json={"email": email, "password": PASSWORD_DEMO})
        assert respuesta.status_code == 200, email
        assert respuesta.json()["usuario"]["rol"] == rol
