from datetime import UTC, datetime, timedelta

import jwt
import pytest

from seguridad import JWT_ALGORITMO, JWT_SECRET
from tests.conftest import PASSWORD


@pytest.fixture
def cuentas(client, base):
    """Da acceso a los dos repartidores y al cliente de la base."""
    for repartidor, email in [("repartidor_centro", "juan@dely.com"), ("repartidor_norte", "luz@dely.com")]:
        r = client.put(
            f"/api/usuarios/repartidores/{base[repartidor]['id_repartidor']}/acceso",
            json={"email": email, "password": PASSWORD},
        )
        assert r.status_code == 200, r.text
    r = client.put(
        f"/api/usuarios/clientes/{base['cliente']['id_cliente']}/acceso", json={"email": "ana@mail.com", "password": PASSWORD}
    )
    assert r.status_code == 200, r.text


def test_login_devuelve_token_y_datos_del_usuario(client):
    respuesta = client.post("/api/auth/login", json={"email": "ENCARGADO@dely.com", "password": PASSWORD})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["token_type"] == "bearer"
    assert cuerpo["usuario"]["rol"] == "encargado"
    datos = jwt.decode(cuerpo["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITMO])
    assert datos["rol"] == "encargado"


@pytest.mark.parametrize("email, password", [("encargado@dely.com", "otra-clave"), ("nadie@dely.com", PASSWORD)])
def test_login_rechaza_credenciales_invalidas_con_el_mismo_mensaje(client, email, password):
    respuesta = client.post("/api/auth/login", json={"email": email, "password": password})

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "Email o contraseña incorrectos."


def test_sin_token_no_se_puede_usar_la_api(como):
    assert como(None).get("/api/pedidos/").status_code == 401


def test_token_vencido_o_adulterado(client, como):
    vencido = jwt.encode({"sub": "1", "rol": "encargado", "exp": datetime.now(UTC) - timedelta(minutes=1)}, JWT_SECRET)
    otro = como(None)

    otro.headers["Authorization"] = f"Bearer {vencido}"
    assert otro.get("/api/pedidos/").json()["detail"] == "La sesión venció. Volvé a iniciar sesión."

    otro.headers["Authorization"] = "Bearer no-es-un-jwt"
    assert otro.get("/api/pedidos/").status_code == 401


def test_quien_soy(client, cuentas, como):
    yo = como("juan@dely.com").get("/api/auth/yo").json()

    assert yo["rol"] == "repartidor"
    assert yo["nombre"] == "Juan Gómez"


def test_repartidor_y_cliente_no_acceden_a_la_gestion(cuentas, como):
    for email in ("juan@dely.com", "ana@mail.com"):
        sesion = como(email)
        assert sesion.get("/api/pedidos/").status_code == 403
        assert sesion.get("/api/clientes/").status_code == 403
        assert sesion.get("/api/usuarios/").status_code == 403


def test_repartidor_solo_ve_y_mueve_sus_entregas(client, base, cuentas, crear_pedido, como):
    pedido = crear_pedido()
    entrega = client.patch(
        f"/api/pedidos/{pedido['id_pedido']}/asignar", json={"repartidor_id": base["repartidor_centro"]["id_repartidor"]}
    ).json()["entrega"]
    juan, luz = como("juan@dely.com"), como("luz@dely.com")
    id_juan = base["repartidor_centro"]["id_repartidor"]

    assert len(juan.get(f"/api/repartidores/{id_juan}/entregas").json()) == 1
    assert luz.get(f"/api/repartidores/{id_juan}/entregas").status_code == 403
    assert luz.get(f"/api/entregas/{entrega['id_entrega']}").status_code == 403
    assert luz.patch(f"/api/entregas/{entrega['id_entrega']}/estado", json={"estado": "En camino"}).status_code == 403

    respuesta = juan.patch(f"/api/entregas/{entrega['id_entrega']}/estado", json={"estado": "En camino"})
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "En camino"


def test_cliente_ve_solo_sus_pedidos(client, base, cuentas, crear_pedido, como):
    pedido = crear_pedido()
    otro_cliente = client.post(
        "/api/clientes/",
        json={"nombre": "Beto", "apellido": "Ruiz", "telefono": "1190000000", "email": "beto@mail.com", "direccion": "Calle 2"},
    ).json()
    client.put(f"/api/usuarios/clientes/{otro_cliente['id_cliente']}/acceso", json={"email": "beto@mail.com", "password": PASSWORD})
    ana, beto = como("ana@mail.com"), como("beto@mail.com")
    codigo = pedido["codigo_seguimiento"]

    assert [p["codigo_seguimiento"] for p in ana.get("/api/seguimiento/").json()] == [codigo]
    assert beto.get("/api/seguimiento/").json() == []
    assert ana.get(f"/api/seguimiento/{codigo}").status_code == 200
    # A otro cliente el pedido "no existe": no se revela que el código es válido.
    assert beto.get(f"/api/seguimiento/{codigo}").status_code == 404
    assert beto.patch(f"/api/seguimiento/{codigo}/notificaciones/leidas").status_code == 404


def test_el_encargado_cambia_la_contrasena_de_un_acceso(client, base, cuentas, como):
    id_juan = base["repartidor_centro"]["id_repartidor"]

    r = client.put(f"/api/usuarios/repartidores/{id_juan}/acceso", json={"email": "juan@dely.com", "password": "nueva-clave"})

    assert r.status_code == 200
    assert como(None).post("/api/auth/login", json={"email": "juan@dely.com", "password": PASSWORD}).status_code == 401
    assert como(None).post("/api/auth/login", json={"email": "juan@dely.com", "password": "nueva-clave"}).status_code == 200
    assert len(client.get("/api/usuarios/?rol=repartidor").json()) == 2


def test_no_se_repite_el_email_entre_cuentas(client, base, cuentas):
    id_luz = base["repartidor_norte"]["id_repartidor"]

    r = client.put(f"/api/usuarios/repartidores/{id_luz}/acceso", json={"email": "juan@dely.com", "password": PASSWORD})

    assert r.status_code == 409
