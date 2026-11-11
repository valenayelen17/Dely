def test_no_elimina_cliente_con_pedidos(client, base, crear_pedido):
    crear_pedido()
    assert client.delete(f"/api/clientes/{base['cliente']['id_cliente']}").status_code == 409


def test_no_elimina_producto_vendido(client, base, crear_pedido):
    crear_pedido()
    assert client.delete(f"/api/productos/{base['pizza']['id_producto']}").status_code == 409
    assert client.delete(f"/api/productos/{base['empanada']['id_producto']}").status_code == 204


def test_no_elimina_comercio_con_datos(client, base):
    assert client.delete(f"/api/comercios/{base['comercio']['id_comercio']}").status_code == 409


def test_email_duplicado_y_email_invalido(client, base):
    datos = {"nombre": "Otra", "apellido": "Ana", "telefono": "1150000001", "email": "ana@mail.com", "direccion": "Calle 2"}
    assert client.post("/api/clientes/", json=datos).status_code == 409
    assert client.post("/api/clientes/", json={**datos, "email": "no-es-un-mail"}).status_code == 422


def test_filtra_productos_por_categoria(client, base):
    productos = client.get("/api/productos/", params={"categoria": "Pizzas"}).json()
    assert [p["nombre"] for p in productos] == ["Pizza muzzarella"]
