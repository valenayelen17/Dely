def test_pendientes_excluye_entregados_y_cancelados_y_ordena_por_horario(client, base, crear_pedido):
    tarde = crear_pedido()
    client.put(
        f"/api/pedidos/{tarde['id_pedido']}",
        json={"direccion_entrega": tarde["direccion_entrega"], "zona": "Centro", "horario_estimado": "22:30:00"},
    )
    temprano = crear_pedido()
    client.put(
        f"/api/pedidos/{temprano['id_pedido']}",
        json={"direccion_entrega": temprano["direccion_entrega"], "zona": "Centro", "horario_estimado": "20:00:00"},
    )

    pendientes = client.get("/api/pedidos/pendientes", params={"comercio_id": base["comercio"]["id_comercio"]}).json()

    assert [p["id_pedido"] for p in pendientes] == [temprano["id_pedido"], tarde["id_pedido"]]


def test_pedido_incluye_datos_principales(client, base, crear_pedido):
    pedido = crear_pedido(cantidad_pizzas=2)

    assert pedido["cliente"]["nombre"] == "Ana"
    assert pedido["detalles"][0]["producto_nombre"] == "Pizza muzzarella"
    assert pedido["total"] == "24000.00"


def test_pedido_asignado_muestra_al_repartidor(client, base, crear_pedido):
    pedido = crear_pedido()
    asignado = client.patch(
        f"/api/pedidos/{pedido['id_pedido']}/asignar", json={"repartidor_id": base["repartidor_centro"]["id_repartidor"]}
    ).json()

    assert asignado["entrega"]["repartidor"]["nombre"] == "Juan"
    pendientes = client.get("/api/pedidos/pendientes").json()
    assert pendientes[0]["estado"] == "Asignado"
