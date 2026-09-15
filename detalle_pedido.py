class DetallePedido:

    def __init__(self, id_detalle, cantidad, precio_unitario):
        self.id_detalle = id_detalle
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario

    def calcular_subtotal(self):
        return self.cantidad * self.precio_unitario