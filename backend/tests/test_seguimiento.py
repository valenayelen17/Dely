def test_cliente_consulta_estado_y_horario_con_su_codigo(client, base, crear_pedido):
    pedido = crear_pedido()

    respuesta = client.get(f"/api/seguimiento/{pedido['codigo_seguimiento'].lower()}")

    assert respuesta.status_code == 200
    seguimiento = respuesta.json()
    assert seguimiento["estado"] == "Pendiente"
    assert seguimiento["horario_estimado"] == "21:00:00"
    assert seguimiento["comercio"] == "Pizzería Dely"
    assert seguimiento["productos"] == [{"nombre": "Pizza muzzarella", "cantidad": 2, "subtotal": "24000.00"}]
    assert "cliente" not in seguimiento and "id_pedido" not in seguimiento


def test_seguimiento_muestra_repartidor_y_ubicacion(client, base, crear_pedido):
    pedido = crear_pedido()
    entrega = client.patch(
        f"/api/pedidos/{pedido['id_pedido']}/asignar", json={"repartidor_id": base["repartidor_centro"]["id_repartidor"]}
    ).json()["entrega"]
    client.patch(f"/api/entregas/{entrega['id_entrega']}/estado", json={"estado": "En camino", "ubicacion_actual": "Av. Callao 200"})

    seguimiento = client.get(f"/api/seguimiento/{pedido['codigo_seguimiento']}").json()

    assert seguimiento["estado"] == "En camino"
    assert seguimiento["repartidor"] == "Juan"
    assert seguimiento["ubicacion_actual"] == "Av. Callao 200"


def test_marcar_notificaciones_leidas(client, crear_pedido):
    pedido = crear_pedido()

    seguimiento = client.patch(f"/api/seguimiento/{pedido['codigo_seguimiento']}/notificaciones/leidas").json()

    assert all(n["leida"] for n in seguimiento["notificaciones"])


def test_codigo_inexistente(client):
    assert client.get("/api/seguimiento/NOEXISTE").status_code == 404
