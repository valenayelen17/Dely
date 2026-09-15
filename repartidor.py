class Repartidor:

    def __init__(self, id_repartidor, nombre, apellido, telefono, zona):
        self.id_repartidor = id_repartidor
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.zona = zona
        self.disponible = True

    def cambiar_disponibilidad(self):
        self.disponible = not self.disponible