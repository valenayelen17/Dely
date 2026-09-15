class Entrega:

    def __init__(self, id_entrega, fecha_entrega, hora_entrega, estado, ubicacion_actual):
        self.id_entrega = id_entrega
        self.fecha_entrega = fecha_entrega
        self.hora_entrega = hora_entrega
        self.estado = estado
        self.ubicacion_actual = ubicacion_actual

    def iniciar_entrega(self):
        self.estado = "En camino"

    def actualizar_ubicacion(self, nueva_ubicacion):
        self.ubicacion_actual = nueva_ubicacion

    def finalizar_entrega(self):
        self.estado = "Entregado"