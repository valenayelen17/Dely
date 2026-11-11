from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from estados import EstadoEntrega, EstadoPedido


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class ComercioFields(Schema):
    nombre: str = Field(min_length=2, max_length=150)
    direccion: str = Field(min_length=3, max_length=255)
    telefono: str = Field(min_length=6, max_length=30)
    email: EmailStr


class ComercioCreate(ComercioFields):
    pass


class ComercioUpdate(ComercioFields):
    pass


class ComercioOut(ComercioFields):
    id_comercio: int


class ClienteFields(Schema):
    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(min_length=2, max_length=100)
    telefono: str = Field(min_length=6, max_length=30)
    email: EmailStr
    direccion: str = Field(min_length=3, max_length=255)


class ClienteCreate(ClienteFields):
    pass


class ClienteUpdate(ClienteFields):
    pass


class ClienteOut(ClienteFields):
    id_cliente: int


class RepartidorFields(Schema):
    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(min_length=2, max_length=100)
    telefono: str = Field(min_length=6, max_length=30)
    zona: str = Field(min_length=2, max_length=100)
    disponible: bool = True
    comercio_id: int = Field(gt=0)


class RepartidorCreate(RepartidorFields):
    pass


class RepartidorUpdate(RepartidorFields):
    pass


class RepartidorOut(RepartidorFields):
    id_repartidor: int


class RepartidorDisponibilidad(Schema):
    disponible: bool


class ProductoFields(Schema):
    nombre: str = Field(min_length=2, max_length=150)
    descripcion: str | None = Field(default=None, max_length=500)
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    categoria: str = Field(min_length=2, max_length=100)
    stock: int = Field(ge=0)
    comercio_id: int = Field(gt=0)


class ProductoCreate(ProductoFields):
    pass


class ProductoUpdate(ProductoFields):
    pass


class ProductoOut(ProductoFields):
    id_producto: int


class DetalleCreate(Schema):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0)


class ClienteResumen(Schema):
    id_cliente: int
    nombre: str
    apellido: str
    telefono: str


class RepartidorResumen(Schema):
    id_repartidor: int
    nombre: str
    apellido: str
    telefono: str
    zona: str


class DetalleOut(Schema):
    id_detalle: int
    producto_id: int
    producto_nombre: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class PedidoCreate(Schema):
    fecha_pedido: date = Field(default_factory=date.today)
    direccion_entrega: str | None = Field(default=None, min_length=3, max_length=255)
    zona: str = Field(min_length=2, max_length=100)
    horario_estimado: time
    cliente_id: int = Field(gt=0)
    comercio_id: int = Field(gt=0)
    detalles: list[DetalleCreate] = Field(min_length=1)


class PedidoUpdate(Schema):
    direccion_entrega: str = Field(min_length=3, max_length=255)
    zona: str = Field(min_length=2, max_length=100)
    horario_estimado: time


class PedidoAsignacion(Schema):
    repartidor_id: int = Field(gt=0)


class EntregaOut(Schema):
    id_entrega: int
    pedido_id: int
    repartidor_id: int
    repartidor: RepartidorResumen
    estado: EstadoEntrega
    ubicacion_actual: str | None
    fecha_entrega: date | None
    hora_entrega: time | None


class EntregaEstado(Schema):
    estado: EstadoEntrega
    ubicacion_actual: str | None = Field(default=None, min_length=2, max_length=255)


class EntregaUbicacion(Schema):
    ubicacion_actual: str = Field(min_length=2, max_length=255)


class PedidoDeEntrega(Schema):
    id_pedido: int
    direccion_entrega: str
    zona: str
    estado: EstadoPedido
    horario_estimado: time
    cliente: ClienteResumen
    detalles: list[DetalleOut]
    total: Decimal


class EntregaDetalle(EntregaOut):
    pedido: PedidoDeEntrega


class NotificacionOut(Schema):
    id_notificacion: int
    tipo: str
    mensaje: str
    fecha_hora: datetime
    leida: bool


class PedidoOut(Schema):
    id_pedido: int
    codigo_seguimiento: str
    fecha_pedido: date
    direccion_entrega: str
    zona: str
    estado: EstadoPedido
    horario_estimado: time
    cliente_id: int
    comercio_id: int
    cliente: ClienteResumen
    detalles: list[DetalleOut]
    total: Decimal
    entrega: EntregaOut | None


class ProductoSeguimiento(Schema):
    nombre: str
    cantidad: int
    subtotal: Decimal


class SeguimientoOut(Schema):
    codigo_seguimiento: str
    estado: EstadoPedido
    estado_entrega: EstadoEntrega | None
    fecha_pedido: date
    horario_estimado: time
    direccion_entrega: str
    comercio: str
    comercio_telefono: str
    repartidor: str | None
    ubicacion_actual: str | None
    hora_entrega: time | None
    productos: list[ProductoSeguimiento]
    total: Decimal
    notificaciones: list[NotificacionOut]
