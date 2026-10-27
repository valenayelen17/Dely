"""Esquemas Pydantic para validar entradas y representar respuestas."""

from datetime import date, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ClienteFields(Schema):
    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(min_length=2, max_length=100)
    telefono: str = Field(min_length=6, max_length=30)
    email: str = Field(min_length=5, max_length=255)
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


class RepartidorCreate(RepartidorFields):
    pass


class RepartidorUpdate(RepartidorFields):
    pass


class RepartidorOut(RepartidorFields):
    id_repartidor: int


class ProductoFields(Schema):
    nombre: str = Field(min_length=2, max_length=150)
    descripcion: str | None = Field(default=None, max_length=500)
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    categoria: str = Field(min_length=2, max_length=100)
    stock: int = Field(ge=0)


class ProductoCreate(ProductoFields):
    pass


class ProductoUpdate(ProductoFields):
    pass


class ProductoOut(ProductoFields):
    id_producto: int


class DetalleCreate(Schema):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0)


class DetalleOut(Schema):
    id_detalle: int
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class PedidoCreate(Schema):
    fecha_pedido: date = Field(default_factory=date.today)
    direccion_entrega: str = Field(min_length=3, max_length=255)
    zona: str = Field(min_length=2, max_length=100)
    horario_estimado: time
    cliente_id: int = Field(gt=0)
    detalles: list[DetalleCreate] = Field(min_length=1)


class PedidoUpdate(Schema):
    fecha_pedido: date
    direccion_entrega: str = Field(min_length=3, max_length=255)
    zona: str = Field(min_length=2, max_length=100)
    estado: str = Field(min_length=2, max_length=30)
    horario_estimado: time
    cliente_id: int = Field(gt=0)
    repartidor_id: int | None = Field(default=None, gt=0)


class PedidoEstado(Schema):
    estado: str = Field(min_length=2, max_length=30)


class PedidoAsignacion(Schema):
    repartidor_id: int = Field(gt=0)


class PedidoOut(Schema):
    id_pedido: int
    fecha_pedido: date
    direccion_entrega: str
    zona: str
    estado: str
    horario_estimado: time
    cliente_id: int
    repartidor_id: int | None
    detalles: list[DetalleOut]


class EntregaCreate(Schema):
    fecha_entrega: date
    hora_entrega: time
    ubicacion_actual: str = Field(min_length=2, max_length=255)
    pedido_id: int = Field(gt=0)


class EntregaUpdate(Schema):
    fecha_entrega: date
    hora_entrega: time
    estado: str = Field(min_length=2, max_length=30)
    ubicacion_actual: str = Field(min_length=2, max_length=255)


class EntregaOut(EntregaCreate):
    id_entrega: int
    estado: str
