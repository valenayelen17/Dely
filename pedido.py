class Pedido:

    def __init__(self, id_pedido, fecha_pedido, direccion_entrega, estado, horario_estimado):
        self.id_pedido = id_pedido
        self.fecha_pedido = fecha_pedido
        self.direccion_entrega = direccion_entrega
        self.estado = estado
        self.horario_estimado = horario_estimado