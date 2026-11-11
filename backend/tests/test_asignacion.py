def asignar(client, pedido_id, repartidor_id):
    return client.patch(f"/api/pedidos/{pedido_id}/asignar", json={"repartidor_id": repartidor_id})


def test_crear_pedido_descuenta_stock_y_usa_direccion_del_cliente(client, base, crear_pedido):
    pedido = crear_pedido(cantidad_pizzas=3)

    assert pedido["estado"] == "Pendiente"
    assert pedido["direccion_entrega"] == base["cliente"]["direccion"]
    assert pedido["entrega"] is None
    producto = client.get(f"/api/productos/{base['pizza']['id_producto']}").json()
    assert producto["stock"] == 7


def test_crear_pedido_sin_stock_suficiente_falla(client, crear_pedido, base):
    respuesta = client.post(
        "/api/pedidos/",
        json={
            "zona": "Centro",
            "horario_estimado": "21:00:00",
            "cliente_id": base["cliente"]["id_cliente"],
            "comercio_id": base["comercio"]["id_comercio"],
            "detalles": [{"producto_id": base["pizza"]["id_producto"], "cantidad": 99}],
        },
    )
    assert respuesta.status_code == 409


def test_asignar_repartidor_disponible_de_la_zona_genera_la_entrega(client, base, crear_pedido):
    pedido = crear_pedido()
    repartidor = base["repartidor_centro"]

    respuesta = asignar(client, pedido["id_pedido"], repartidor["id_repartidor"])

    assert respuesta.status_code == 200, respuesta.text
    asignado = respuesta.json()
    assert asignado["estado"] == "Asignado"
    assert asignado["entrega"]["estado"] == "Asignada"
    assert asignado["entrega"]["repartidor_id"] == repartidor["id_repartidor"]


def test_no_asigna_repartidor_de_otra_zona(client, base, crear_pedido):
    pedido = crear_pedido(zona="Centro")
    respuesta = asignar(client, pedido["id_pedido"], base["repartidor_norte"]["id_repartidor"])
    assert respuesta.status_code == 409
    assert "zona" in respuesta.json()["detail"]


def test_no_asigna_repartidor_no_disponible(client, base, crear_pedido):
    repartidor = base["repartidor_centro"]
    client.put(
        f"/api/repartidores/{repartidor['id_repartidor']}",
        json={**{k: v for k, v in repartidor.items() if k != "id_repartidor"}, "disponible": False},
    )
    pedido = crear_pedido()
    respuesta = asignar(client, pedido["id_pedido"], repartidor["id_repartidor"])
    assert respuesta.status_code == 409


def test_reasignar_mientras_no_salio_actualiza_la_misma_entrega(client, base, crear_pedido):
    otro = client.post(
        "/api/repartidores/",
        json={"nombre": "Leo", "apellido": "Ruiz", "telefono": "1180000000", "zona": "centro", "comercio_id": base["comercio"]["id_comercio"]},
    ).json()
    pedido = crear_pedido()
    primera = asignar(client, pedido["id_pedido"], base["repartidor_centro"]["id_repartidor"]).json()
    segunda = asignar(client, pedido["id_pedido"], otro["id_repartidor"]).json()

    assert segunda["entrega"]["id_entrega"] == primera["entrega"]["id_entrega"]
    assert segunda["entrega"]["repartidor_id"] == otro["id_repartidor"]


def test_no_acepta_productos_de_otro_comercio(client, base):
    otro_comercio = client.post(
        "/api/comercios/",
        json={"nombre": "Otro", "direccion": "Calle 1", "telefono": "1190000000", "email": "otro@dely.com"},
    ).json()
    respuesta = client.post(
        "/api/pedidos/",
        json={
            "zona": "Centro",
            "horario_estimado": "21:00:00",
            "cliente_id": base["cliente"]["id_cliente"],
            "comercio_id": otro_comercio["id_comercio"],
            "detalles": [{"producto_id": base["pizza"]["id_producto"], "cantidad": 1}],
        },
    )
    assert respuesta.status_code == 422
