from api import app
from database import get_db
from seed import cargar


def test_seed_carga_un_escenario_completo_una_sola_vez(client):
    db = next(app.dependency_overrides[get_db]())

    assert cargar(db) is True
    assert cargar(db) is False

    estados = sorted(p["estado"] for p in client.get("/api/pedidos/").json())
    assert estados == ["Asignado", "Cancelado", "En camino", "En camino", "Entregado", "Pendiente", "Pendiente"]
    assert len(client.get("/api/pedidos/pendientes").json()) == 5
