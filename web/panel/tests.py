"""Tests del panel: la API se reemplaza por respuestas simuladas, no hace falta tenerla corriendo."""

from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse

from panel.src.services import ErrorApi
from panel.templatetags.dely import hora, pesos

COMERCIO = {"id_comercio": 1, "nombre": "La Esquina Pizzería"}
CLIENTE = {"id_cliente": 1, "nombre": "Ana", "apellido": "Pérez", "telefono": "1160001111"}
REPARTIDOR = {"id_repartidor": 1, "nombre": "Juan", "apellido": "Gómez", "telefono": "1150001111", "zona": "Centro"}


def pedido(id_pedido=1, estado="Pendiente", entrega=None):
    return {
        "id_pedido": id_pedido,
        "codigo_seguimiento": "ABCD1234",
        "fecha_pedido": "2026-11-12",
        "direccion_entrega": "Av. Callao 456",
        "zona": "Centro",
        "estado": estado,
        "horario_estimado": "20:30:00",
        "cliente": CLIENTE,
        "detalles": [
            {"id_detalle": 1, "producto_id": 1, "producto_nombre": "Pizza", "cantidad": 1,
             "precio_unitario": "12000.00", "subtotal": "12000.00"}
        ],
        "total": "12000.00",
        "entrega": entrega,
    }


SERVICIOS = "panel.src.services"


class FiltrosTest(SimpleTestCase):
    def test_pesos_con_separador_de_miles(self):
        self.assertEqual(pesos("15500.00"), "$ 15.500")

    def test_hora_sin_segundos(self):
        self.assertEqual(hora("20:30:00"), "20:30")


@patch(f"{SERVICIOS}.obtener_comercio", return_value=COMERCIO)
class PendientesTest(SimpleTestCase):
    @patch(f"{SERVICIOS}.listar_repartidores", return_value=[{**REPARTIDOR, "disponible": True}])
    @patch(f"{SERVICIOS}.listar_pendientes")
    def test_agrupa_los_pedidos_por_estado(self, pendientes, _repartidores, _comercio):
        pendientes.return_value = [pedido(1), pedido(2, "Asignado", {"repartidor": REPARTIDOR, "estado": "Asignada"})]

        respuesta = self.client.get(reverse("pendientes"))

        self.assertEqual(respuesta.status_code, 200)
        columnas = dict(respuesta.context["columnas"])
        self.assertEqual(len(columnas["Pendiente"]), 1)
        self.assertEqual(len(columnas["Asignado"]), 1)
        self.assertEqual(respuesta.context["sin_repartidor"], 1)
        self.assertContains(respuesta, "ABCD1234")

    @patch(f"{SERVICIOS}.listar_pendientes", side_effect=ErrorApi("No se pudo conectar con la API de DELY."))
    def test_muestra_error_si_la_api_no_responde(self, _pendientes, _comercio):
        respuesta = self.client.get(reverse("pendientes"))

        self.assertEqual(respuesta.status_code, 502)
        self.assertContains(respuesta, "No se pudo conectar", status_code=502)

    @patch(f"{SERVICIOS}.obtener_pedido", side_effect=ErrorApi("Pedido no encontrado.", 404))
    def test_pedido_inexistente_devuelve_404(self, _pedido, _comercio):
        respuesta = self.client.get(reverse("pedido_detalle", args=[9999]))

        self.assertContains(respuesta, "Pedido no encontrado.", status_code=404)


@patch(f"{SERVICIOS}.obtener_comercio", return_value=COMERCIO)
class AsignacionTest(SimpleTestCase):
    @patch(f"{SERVICIOS}.notificaciones_del_pedido", return_value=[])
    @patch(f"{SERVICIOS}.listar_repartidores", return_value=[{**REPARTIDOR, "disponible": True}])
    @patch(f"{SERVICIOS}.obtener_pedido", return_value=pedido())
    def test_ofrece_repartidores_disponibles_de_la_zona(self, _pedido, repartidores, _notif, _comercio):
        respuesta = self.client.get(reverse("pedido_detalle", args=[1]))

        self.assertTrue(respuesta.context["puede_asignar"])
        repartidores.assert_called_once_with(1, zona="Centro", disponible=True)
        self.assertContains(respuesta, "Juan Gómez")

    @patch(f"{SERVICIOS}.notificaciones_del_pedido", return_value=[])
    @patch(f"{SERVICIOS}.listar_repartidores")
    @patch(f"{SERVICIOS}.obtener_pedido")
    def test_no_permite_reasignar_si_el_repartidor_ya_salio(self, obtener, repartidores, _notif, _comercio):
        obtener.return_value = pedido(estado="En camino", entrega={"repartidor": REPARTIDOR, "estado": "En camino"})

        respuesta = self.client.get(reverse("pedido_detalle", args=[1]))

        self.assertFalse(respuesta.context["puede_asignar"])
        repartidores.assert_not_called()

    @patch(f"{SERVICIOS}.asignar_repartidor")
    def test_asigna_y_vuelve_al_detalle(self, asignar, _comercio):
        asignar.return_value = pedido(estado="Asignado", entrega={"repartidor": REPARTIDOR, "estado": "Asignada"})

        respuesta = self.client.post(reverse("asignar_repartidor", args=[1]), {"repartidor_id": "1"})

        asignar.assert_called_once_with(1, 1)
        self.assertRedirects(respuesta, reverse("pedido_detalle", args=[1]), fetch_redirect_response=False)


@patch(f"{SERVICIOS}.obtener_comercio", return_value=COMERCIO)
@patch(f"{SERVICIOS}.listar_repartidores", return_value=[{**REPARTIDOR, "disponible": True}])
@patch(f"{SERVICIOS}.listar_clientes", return_value=[{**CLIENTE, "direccion": "Av. Callao 456"}])
@patch(f"{SERVICIOS}.listar_productos", return_value=[
    {"id_producto": 1, "nombre": "Pizza", "descripcion": None, "precio": "12000.00", "categoria": "Pizzas", "stock": 5}
])
class NuevoPedidoTest(SimpleTestCase):
    @patch(f"{SERVICIOS}.crear_pedido", return_value=pedido(7))
    def test_crea_el_pedido_con_los_productos_elegidos(self, crear, *_):
        datos = {"cliente_id": "1", "zona": "Centro", "horario_estimado": "21:00", "cantidad_1": "2"}

        respuesta = self.client.post(reverse("nuevo_pedido"), datos)

        cuerpo = crear.call_args.args[0]
        self.assertEqual(cuerpo["detalles"], [{"producto_id": 1, "cantidad": 2}])
        self.assertEqual(cuerpo["comercio_id"], 1)
        self.assertNotIn("direccion_entrega", cuerpo)
        self.assertRedirects(respuesta, reverse("pedido_detalle", args=[7]), fetch_redirect_response=False)

    @patch(f"{SERVICIOS}.crear_pedido")
    def test_exige_al_menos_un_producto(self, crear, *_):
        datos = {"cliente_id": "1", "zona": "Centro", "horario_estimado": "21:00", "cantidad_1": "0"}

        respuesta = self.client.post(reverse("nuevo_pedido"), datos)

        self.assertEqual(respuesta.status_code, 400)
        self.assertContains(respuesta, "Agregá al menos un producto", status_code=400)
        crear.assert_not_called()

    @patch(f"{SERVICIOS}.crear_pedido", side_effect=ErrorApi("Stock insuficiente para Pizza."))
    def test_muestra_el_error_de_negocio_de_la_api(self, _crear, *_):
        datos = {"cliente_id": "1", "zona": "Centro", "horario_estimado": "21:00", "cantidad_1": "9"}

        respuesta = self.client.post(reverse("nuevo_pedido"), datos)

        self.assertContains(respuesta, "Stock insuficiente para Pizza.", status_code=400)


@patch(f"{SERVICIOS}.obtener_comercio", return_value=COMERCIO)
class AbmTest(SimpleTestCase):
    CLIENTE_VALIDO = {
        "nombre": "Ana", "apellido": "Pérez", "telefono": "1160001111",
        "email": "ana@ejemplo.com", "direccion": "Av. Callao 456",
    }

    @patch(f"{SERVICIOS}.crear_cliente", return_value={**CLIENTE, "id_cliente": 9})
    def test_crea_un_cliente(self, crear, _comercio):
        respuesta = self.client.post(reverse("cliente_nuevo"), self.CLIENTE_VALIDO)

        crear.assert_called_once_with(self.CLIENTE_VALIDO)
        self.assertRedirects(respuesta, reverse("clientes"), fetch_redirect_response=False)

    @patch(f"{SERVICIOS}.crear_cliente")
    def test_valida_el_formulario_antes_de_llamar_a_la_api(self, crear, _comercio):
        respuesta = self.client.post(reverse("cliente_nuevo"), {**self.CLIENTE_VALIDO, "email": "no-es-un-email"})

        self.assertEqual(respuesta.status_code, 400)
        crear.assert_not_called()

    @patch(f"{SERVICIOS}.listar_productos", return_value=[])
    @patch(f"{SERVICIOS}.crear_producto", return_value={"id_producto": 3, "nombre": "Fugazzeta"})
    def test_crea_un_producto_del_comercio(self, crear, _productos, _comercio):
        datos = {"nombre": "Fugazzeta", "categoria": "Pizzas", "precio": "13500", "stock": "10", "descripcion": ""}

        self.client.post(reverse("producto_nuevo"), datos)

        cuerpo = crear.call_args.args[0]
        self.assertEqual(cuerpo["comercio_id"], 1)
        self.assertEqual(cuerpo["precio"], "13500")
        self.assertIsNone(cuerpo["descripcion"])

    @patch(f"{SERVICIOS}.listar_repartidores", return_value=[])
    @patch(f"{SERVICIOS}.editar_repartidor", side_effect=ErrorApi("Ya existe un repartidor con ese teléfono."))
    def test_muestra_el_error_de_la_api_en_el_formulario(self, _editar, _rep, _comercio):
        datos = {"nombre": "Juan", "apellido": "Gómez", "telefono": "1150001111", "zona": "Centro", "disponible": "on"}

        respuesta = self.client.post(reverse("repartidor_editar", args=[1]), datos)

        self.assertContains(respuesta, "Ya existe un repartidor con ese teléfono.", status_code=400)

    @patch(f"{SERVICIOS}.listar_repartidores", return_value=[])
    @patch(f"{SERVICIOS}.editar_pedido", return_value=pedido(5))
    def test_edita_un_pedido_y_vuelve_al_detalle(self, editar, _rep, _comercio):
        datos = {"direccion_entrega": "Thames 1500", "zona": "Palermo", "horario_estimado": "22:15"}

        respuesta = self.client.post(reverse("pedido_editar", args=[5]), datos)

        editar.assert_called_once_with(5, datos)
        self.assertRedirects(respuesta, reverse("pedido_detalle", args=[5]), fetch_redirect_response=False)
