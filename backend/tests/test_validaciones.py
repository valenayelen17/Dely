"""Reglas de negocio, validaciones de datos y seguridad que surgieron del relevamiento."""

from datetime import date, timedelta

import pytest

from tests.conftest import PASSWORD


def asignar(client, pedido, repartidor):
    respuesta = client.patch(f"/api/pedidos/{pedido['id_pedido']}/asignar", json={"repartidor_id": repartidor["id_repartidor"]})
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["entrega"]


def datos_de(repartidor, **cambios):
    base = {k: repartidor[k] for k in ("nombre", "apellido", "telefono", "zona", "disponible", "comercio_id")}
    return {**base, **cambios}


# --- Repartidores con entregas activas ----------------------------------------------

def test_no_saca_de_turno_a_un_repartidor_con_entregas_activas(client, base, crear_pedido):
    juan = base["repartidor_centro"]
    asignar(client, crear_pedido(), juan)

    respuesta = client.patch(f"/api/repartidores/{juan['id_repartidor']}/disponibilidad", json={"disponible": False})

    assert respuesta.status_code == 409
    assert "1 entrega activa" in respuesta.json()["detail"]
    assert client.get(f"/api/repartidores/{juan['id_repartidor']}").json()["disponible"] is True


def test_la_edicion_completa_respeta_la_misma_regla(client, base, crear_pedido):
    juan = base["repartidor_centro"]
    asignar(client, crear_pedido(), juan)

    fuera_de_turno = client.put(f"/api/repartidores/{juan['id_repartidor']}", json=datos_de(juan, disponible=False))
    otra_zona = client.put(f"/api/repartidores/{juan['id_repartidor']}", json=datos_de(juan, zona="Norte"))
    mismo_nombre_otra_grafia = client.put(f"/api/repartidores/{juan['id_repartidor']}", json=datos_de(juan, zona="centro"))

    assert fuera_de_turno.status_code == 409
    assert otra_zona.status_code == 409
    assert mismo_nombre_otra_grafia.status_code == 200


def test_puede_salir_de_turno_cuando_termina_sus_entregas(client, base, crear_pedido):
    juan = base["repartidor_centro"]
    entrega = asignar(client, crear_pedido(), juan)
    for estado in ("En camino", "Llegando", "Entregada"):
        client.patch(f"/api/entregas/{entrega['id_entrega']}/estado", json={"estado": estado})

    respuesta = client.patch(f"/api/repartidores/{juan['id_repartidor']}/disponibilidad", json={"disponible": False})

    assert respuesta.status_code == 200
    assert respuesta.json()["disponible"] is False


def test_no_cambia_de_comercio_a_un_repartidor_ni_a_un_producto_con_historial(client, base, crear_pedido):
    juan = base["repartidor_centro"]
    asignar(client, crear_pedido(), juan)
    otro = client.post("/api/comercios/", json={"nombre": "Otro", "direccion": "Av. 2", "telefono": "1140000001", "email": "otro@dely.com"}).json()

    repartidor = client.put(f"/api/repartidores/{juan['id_repartidor']}", json=datos_de(juan, comercio_id=otro["id_comercio"]))
    pizza = base["pizza"]
    producto = client.put(
        f"/api/productos/{pizza['id_producto']}",
        json={"nombre": pizza["nombre"], "precio": pizza["precio"], "categoria": pizza["categoria"], "stock": 5, "comercio_id": otro["id_comercio"]},
    )

    assert repartidor.status_code == 409
    assert producto.status_code == 409


# --- Recorrido y asignación ---------------------------------------------------------

def test_no_se_entrega_sin_avisar_que_esta_llegando(client, base, crear_pedido):
    entrega = asignar(client, crear_pedido(), base["repartidor_centro"])
    client.patch(f"/api/entregas/{entrega['id_entrega']}/estado", json={"estado": "En camino"})

    respuesta = client.patch(f"/api/entregas/{entrega['id_entrega']}/estado", json={"estado": "Entregada"})

    assert respuesta.status_code == 409
    assert "En camino a Entregada" in respuesta.json()["detail"]


def test_no_reasigna_al_mismo_repartidor(client, base, crear_pedido):
    pedido = crear_pedido()
    juan = base["repartidor_centro"]
    asignar(client, pedido, juan)

    respuesta = client.patch(f"/api/pedidos/{pedido['id_pedido']}/asignar", json={"repartidor_id": juan["id_repartidor"]})

    assert respuesta.status_code == 409
    tipos = [n["tipo"] for n in client.get(f"/api/pedidos/{pedido['id_pedido']}/notificaciones").json()]
    assert tipos.count("Asignada") == 1


# --- Pedidos ----------------------------------------------------------------------

def test_rechaza_pedidos_en_zonas_sin_repartidores(client, base):
    respuesta = client.post(
        "/api/pedidos/",
        json={
            "zona": "Marte", "horario_estimado": "21:00:00", "cliente_id": base["cliente"]["id_cliente"],
            "comercio_id": base["comercio"]["id_comercio"], "detalles": [{"producto_id": base["pizza"]["id_producto"], "cantidad": 1}],
        },
    )

    assert respuesta.status_code == 422
    assert "Centro, Norte" in respuesta.json()["detail"]


def test_la_zona_del_pedido_toma_la_grafia_del_repartidor(client, crear_pedido):
    pedido = crear_pedido(zona="  CENTRO ")

    assert pedido["zona"] == "Centro"


@pytest.mark.parametrize("fecha", [date.today() - timedelta(days=1), date.today() + timedelta(days=8)])
def test_rechaza_fechas_de_pedido_fuera_de_rango(client, base, fecha):
    respuesta = client.post(
        "/api/pedidos/",
        json={
            "fecha_pedido": fecha.isoformat(), "zona": "Centro", "horario_estimado": "21:00:00",
            "cliente_id": base["cliente"]["id_cliente"], "comercio_id": base["comercio"]["id_comercio"],
            "detalles": [{"producto_id": base["pizza"]["id_producto"], "cantidad": 1}],
        },
    )

    assert respuesta.status_code == 422


# --- Datos de personas y productos --------------------------------------------------

CLIENTE = {"nombre": "Beto", "apellido": "Ruiz", "telefono": "11 5555-0000", "email": "Beto@Mail.com", "direccion": "Calle 3"}


@pytest.mark.parametrize("campo, valor", [("telefono", "abcdefg"), ("telefono", "12-34"), ("nombre", "R2D2"), ("apellido", "Ruiz!")])
def test_rechaza_telefonos_y_nombres_invalidos(client, campo, valor):
    respuesta = client.post("/api/clientes/", json={**CLIENTE, campo: valor})

    assert respuesta.status_code == 422


def test_el_email_se_guarda_en_minusculas_y_no_se_repite_con_otra_grafia(client):
    creado = client.post("/api/clientes/", json=CLIENTE)
    repetido = client.post("/api/clientes/", json={**CLIENTE, "telefono": "1190000001", "email": "BETO@mail.com"})

    assert creado.status_code == 201
    assert creado.json()["email"] == "beto@mail.com"
    assert repetido.status_code == 409


def test_no_repite_el_telefono_entre_repartidores(client, base):
    comercio_id = base["comercio"]["id_comercio"]
    repartidor = {"nombre": "Otra", "apellido": "Persona", "zona": "Centro", "comercio_id": comercio_id}

    con_formato_distinto = client.post("/api/repartidores/", json={**repartidor, "telefono": "11 6000-0000"})
    distinto = client.post("/api/repartidores/", json={**repartidor, "telefono": "1180000000"})

    assert con_formato_distinto.status_code == 409  # el de Juan es 1160000000
    assert distinto.status_code == 201


def test_no_repite_el_nombre_de_un_producto_en_el_comercio(client, base):
    comercio_id = base["comercio"]["id_comercio"]

    repetido = client.post("/api/productos/", json={"nombre": "pizza MUZZARELLA", "precio": "1", "categoria": "Pizzas", "stock": 1, "comercio_id": comercio_id})
    editado = client.put(
        f"/api/productos/{base['empanada']['id_producto']}",
        json={"nombre": "Pizza muzzarella", "precio": "1", "categoria": "Pizzas", "stock": 1, "comercio_id": comercio_id},
    )

    assert repetido.status_code == 409
    assert editado.status_code == 409


# --- Seguridad --------------------------------------------------------------------

@pytest.fixture
def juan_con_acceso(client, base):
    id_juan = base["repartidor_centro"]["id_repartidor"]
    client.put(f"/api/usuarios/repartidores/{id_juan}/acceso", json={"email": "juan@dely.com", "password": PASSWORD})
    return id_juan


def test_el_token_deja_de_valer_al_cambiar_la_contrasena(client, juan_con_acceso, como):
    sesion = como("juan@dely.com")
    assert sesion.get("/api/auth/yo").status_code == 200

    client.put(f"/api/usuarios/repartidores/{juan_con_acceso}/acceso", json={"email": "juan@dely.com", "password": "otra-clave1"})

    respuesta = sesion.get("/api/auth/yo")
    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "La contraseña cambió. Volvé a iniciar sesión."


def test_el_encargado_puede_quitar_un_acceso_y_volver_a_darlo(client, juan_con_acceso, como):
    sesion = como("juan@dely.com")

    assert client.delete(f"/api/usuarios/repartidores/{juan_con_acceso}/acceso").status_code == 204
    assert sesion.get("/api/auth/yo").status_code == 401
    assert como(None).post("/api/auth/login", json={"email": "juan@dely.com", "password": PASSWORD}).status_code == 401
    assert client.get("/api/usuarios/?rol=repartidor").json()[0]["activo"] is False

    client.put(f"/api/usuarios/repartidores/{juan_con_acceso}/acceso", json={"email": "juan@dely.com", "password": PASSWORD})
    assert como(None).post("/api/auth/login", json={"email": "juan@dely.com", "password": PASSWORD}).status_code == 200


def test_quitar_acceso_a_quien_no_tiene_cuenta(client, base):
    assert client.delete(f"/api/usuarios/clientes/{base['cliente']['id_cliente']}/acceso").status_code == 404


@pytest.mark.parametrize("password", ["123456", "soloLetras", "12345678", "corta1"])
def test_rechaza_contrasenas_debiles(client, base, password):
    id_juan = base["repartidor_centro"]["id_repartidor"]

    respuesta = client.put(f"/api/usuarios/repartidores/{id_juan}/acceso", json={"email": "juan@dely.com", "password": password})

    assert respuesta.status_code == 422


def test_bloquea_el_login_despues_de_varios_intentos_fallidos(client, juan_con_acceso, como):
    anonimo = como(None)
    for _ in range(5):
        assert anonimo.post("/api/auth/login", json={"email": "juan@dely.com", "password": "mala1234"}).status_code == 401

    bloqueado = anonimo.post("/api/auth/login", json={"email": "juan@dely.com", "password": PASSWORD})

    assert bloqueado.status_code == 429
    assert "Retry-After" in bloqueado.headers
    # Otro usuario no se ve afectado.
    assert anonimo.post("/api/auth/login", json={"email": "encargado@dely.com", "password": PASSWORD}).status_code == 200
