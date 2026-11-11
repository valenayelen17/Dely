def notificaciones(client, pedido_id):
    return client.get(f"/api/pedidos/{pedido_id}/notificaciones").json()


def test_cliente_recibe_confirmacion_con_horario_estimado(client, crear_pedido):
    pedido = crear_pedido()

    avisos = notificaciones(client, pedido["id_pedido"])

    assert [a["tipo"] for a in avisos] == ["Recibido"]
    assert "21:00" in avisos[0]["mensaje"]
    assert avisos[0]["leida"] is False


def test_cliente_recibe_aviso_cuando_el_repartidor_esta_llegando(client, base, crear_pedido):
    pedido = crear_pedido()
    entrega = client.patch(
        f"/api/pedidos/{pedido['id_pedido']}/asignar", json={"repartidor_id": base["repartidor_centro"]["id_repartidor"]}
    ).json()["entrega"]
    for estado in ("En camino", "Llegando"):
        client.patch(f"/api/entregas/{entrega['id_entrega']}/estado", json={"estado": estado})

    avisos = notificaciones(client, pedido["id_pedido"])

    assert [a["tipo"] for a in avisos] == ["Recibido", "Asignada", "En camino", "Llegando"]
    assert avisos[-1]["mensaje"].startswith("Juan está llegando a Calle Falsa 123")


def test_cancelar_notifica_al_cliente(client, crear_pedido):
    pedido = crear_pedido()
    client.patch(f"/api/pedidos/{pedido['id_pedido']}/cancelar")

    assert notificaciones(client, pedido["id_pedido"])[-1]["tipo"] == "Cancelada"
