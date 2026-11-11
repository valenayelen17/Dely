def test_lista_repartidores_disponibles_de_una_zona(client, base):
    client.patch(f"/api/repartidores/{base['repartidor_norte']['id_repartidor']}/disponibilidad", json={"disponible": False})

    centro = client.get("/api/repartidores/", params={"zona": "centro", "disponible": True}).json()
    norte = client.get("/api/repartidores/", params={"zona": "Norte", "disponible": True}).json()

    assert [r["id_repartidor"] for r in centro] == [base["repartidor_centro"]["id_repartidor"]]
    assert norte == []


def test_no_elimina_repartidor_con_entregas(client, base, crear_pedido):
    pedido = crear_pedido()
    repartidor_id = base["repartidor_centro"]["id_repartidor"]
    client.patch(f"/api/pedidos/{pedido['id_pedido']}/asignar", json={"repartidor_id": repartidor_id})

    respuesta = client.delete(f"/api/repartidores/{repartidor_id}")

    assert respuesta.status_code == 409
    assert client.get(f"/api/pedidos/{pedido['id_pedido']}").json()["entrega"]["repartidor_id"] == repartidor_id


def test_elimina_repartidor_sin_entregas(client, base):
    respuesta = client.delete(f"/api/repartidores/{base['repartidor_norte']['id_repartidor']}")
    assert respuesta.status_code == 204
