import pytest


@pytest.fixture
def entrega(client, base, crear_pedido):
    pedido = crear_pedido()
    asignado = client.patch(
        f"/api/pedidos/{pedido['id_pedido']}/asignar", json={"repartidor_id": base["repartidor_centro"]["id_repartidor"]}
    ).json()
    return asignado["entrega"]


def cambiar(client, entrega, estado, **extra):
    return client.patch(f"/api/entregas/{entrega['id_entrega']}/estado", json={"estado": estado, **extra})


def test_repartidor_ve_sus_entregas_activas_con_datos_del_cliente(client, base, entrega):
    entregas = client.get(f"/api/repartidores/{base['repartidor_centro']['id_repartidor']}/entregas").json()

    assert [e["id_entrega"] for e in entregas] == [entrega["id_entrega"]]
    assert entregas[0]["pedido"]["cliente"]["telefono"] == base["cliente"]["telefono"]
    assert entregas[0]["pedido"]["direccion_entrega"] == base["cliente"]["direccion"]


def test_repartidor_marca_en_camino_y_el_pedido_se_actualiza(client, entrega):
    respuesta = cambiar(client, entrega, "En camino", ubicacion_actual="Saliendo del local")

    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["estado"] == "En camino"
    assert respuesta.json()["ubicacion_actual"] == "Saliendo del local"
    assert client.get(f"/api/pedidos/{entrega['pedido_id']}").json()["estado"] == "En camino"


def test_recorrido_completo_registra_fecha_y_hora_de_entrega(client, base, entrega):
    cambiar(client, entrega, "En camino")
    client.patch(f"/api/entregas/{entrega['id_entrega']}/ubicacion", json={"ubicacion_actual": "Av. Rivadavia 500"})
    cambiar(client, entrega, "Llegando")
    final = cambiar(client, entrega, "Entregada").json()

    assert final["estado"] == "Entregada"
    assert final["fecha_entrega"] is not None and final["hora_entrega"] is not None
    assert final["pedido"]["estado"] == "Entregado"
    activas = client.get(f"/api/repartidores/{base['repartidor_centro']['id_repartidor']}/entregas").json()
    assert activas == []


def test_no_permite_saltear_estados(client, entrega):
    respuesta = cambiar(client, entrega, "Entregada")
    assert respuesta.status_code == 409


def test_no_actualiza_ubicacion_antes_de_salir(client, entrega):
    respuesta = client.patch(f"/api/entregas/{entrega['id_entrega']}/ubicacion", json={"ubicacion_actual": "Esquina"})
    assert respuesta.status_code == 409


def test_no_reasigna_un_pedido_en_camino(client, base, entrega):
    cambiar(client, entrega, "En camino")
    respuesta = client.patch(
        f"/api/pedidos/{entrega['pedido_id']}/asignar", json={"repartidor_id": base["repartidor_centro"]["id_repartidor"]}
    )
    assert respuesta.status_code == 409
