def stock_pizza(client, base):
    return client.get(f"/api/productos/{base['pizza']['id_producto']}").json()["stock"]


def test_cancelar_devuelve_stock_y_cancela_la_entrega(client, base, crear_pedido):
    pedido = crear_pedido(cantidad_pizzas=4)
    client.patch(f"/api/pedidos/{pedido['id_pedido']}/asignar", json={"repartidor_id": base["repartidor_centro"]["id_repartidor"]})
    assert stock_pizza(client, base) == 6

    cancelado = client.patch(f"/api/pedidos/{pedido['id_pedido']}/cancelar").json()

    assert cancelado["estado"] == "Cancelado"
    assert cancelado["entrega"]["estado"] == "Cancelada"
    assert stock_pizza(client, base) == 10


def test_no_cancela_dos_veces(client, crear_pedido):
    pedido = crear_pedido()
    client.patch(f"/api/pedidos/{pedido['id_pedido']}/cancelar")
    assert client.patch(f"/api/pedidos/{pedido['id_pedido']}/cancelar").status_code == 409


def test_eliminar_cancelado_no_devuelve_stock_otra_vez(client, base, crear_pedido):
    pedido = crear_pedido(cantidad_pizzas=4)
    client.patch(f"/api/pedidos/{pedido['id_pedido']}/cancelar")

    assert client.delete(f"/api/pedidos/{pedido['id_pedido']}").status_code == 204
    assert stock_pizza(client, base) == 10


def test_no_elimina_pedidos_entregados(client, base, crear_pedido):
    pedido = crear_pedido()
    entrega = client.patch(
        f"/api/pedidos/{pedido['id_pedido']}/asignar", json={"repartidor_id": base["repartidor_centro"]["id_repartidor"]}
    ).json()["entrega"]
    for estado in ("En camino", "Entregada"):
        client.patch(f"/api/entregas/{entrega['id_entrega']}/estado", json={"estado": estado})

    assert client.delete(f"/api/pedidos/{pedido['id_pedido']}").status_code == 409
    assert client.patch(f"/api/pedidos/{pedido['id_pedido']}/cancelar").status_code == 409


def test_solo_edita_pedidos_pendientes(client, base, crear_pedido):
    pedido = crear_pedido()
    client.patch(f"/api/pedidos/{pedido['id_pedido']}/asignar", json={"repartidor_id": base["repartidor_centro"]["id_repartidor"]})
    respuesta = client.put(
        f"/api/pedidos/{pedido['id_pedido']}",
        json={"direccion_entrega": "Otra 456", "zona": "Norte", "horario_estimado": "22:00:00"},
    )
    assert respuesta.status_code == 409
