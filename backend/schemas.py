from datetime import date, datetime, time, timedelta
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from estados import EstadoEntrega, EstadoPedido, Rol


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


# --- Validaciones compartidas ----------------------------------------------------

DIAS_MAXIMOS_PEDIDO = 7


def validar_nombre(valor: str) -> str:
    """Nombres y apellidos: letras, espacios, apóstrofos, puntos y guiones."""
    if not all(c.isalpha() or c in " '.-" for c in valor) or not any(c.isalpha() for c in valor):
        raise ValueError("sólo puede tener letras, espacios, apóstrofos y guiones.")
    return " ".join(valor.split())


def validar_telefono(valor: str) -> str:
    """Teléfonos: dígitos y, opcionalmente, espacios, +, guiones y paréntesis. Al menos 6 dígitos."""
    if not all(c.isdigit() or c in " +()-" for c in valor) or sum(c.isdigit() for c in valor) < 6:
        raise ValueError("tiene que tener al menos 6 dígitos y sólo puede incluir espacios, +, guiones y paréntesis.")
    return valor


def validar_password(valor: str) -> str:
    """Contraseñas: 8 caracteres como mínimo, con al menos una letra y un número."""
    if len(valor) < 8 or not any(c.isalpha() for c in valor) or not any(c.isdigit() for c in valor):
        raise ValueError("tiene que tener al menos 8 caracteres, con una letra y un número.")
    return valor


def email_en_minusculas(valor: str) -> str:
    return valor.lower()


class PersonaFields(Schema):
    """Campos comunes a clientes y repartidores, con sus validaciones."""

    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(min_length=2, max_length=100)
    telefono: str = Field(min_length=6, max_length=30)

    _nombres = field_validator("nombre", "apellido")(validar_nombre)
    _telefono = field_validator("telefono")(validar_telefono)


class ComercioFields(Schema):
    nombre: str = Field(min_length=2, max_length=150)
    direccion: str = Field(min_length=3, max_length=255)
    telefono: str = Field(min_length=6, max_length=30)
    email: EmailStr

    _telefono = field_validator("telefono")(validar_telefono)
    _email = field_validator("email")(email_en_minusculas)


class ComercioCreate(ComercioFields):
    pass


class ComercioUpdate(ComercioFields):
    pass


class ComercioOut(ComercioFields):
    id_comercio: int


class ClienteFields(PersonaFields):
    email: EmailStr
    direccion: str = Field(min_length=3, max_length=255)

    _email = field_validator("email")(email_en_minusculas)


class ClienteCreate(ClienteFields):
    pass


class ClienteUpdate(ClienteFields):
    pass


class ClienteOut(ClienteFields):
    id_cliente: int


class RepartidorFields(PersonaFields):
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

    @field_validator("fecha_pedido")
    @classmethod
    def _fecha_razonable(cls, valor: date) -> date:
        hoy = date.today()
        if valor < hoy:
            raise ValueError("no puede ser anterior a hoy.")
        if valor > hoy + timedelta(days=DIAS_MAXIMOS_PEDIDO):
            raise ValueError(f"no puede ser más de {DIAS_MAXIMOS_PEDIDO} días en el futuro.")
        return valor
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
    codigo_seguimiento: str
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


# --- Autenticación -------------------------------------------------------------

class LoginIn(Schema):
    email: EmailStr
    # bcrypt sólo usa los primeros 72 bytes de la contraseña.
    password: str = Field(min_length=1, max_length=72)

    _email = field_validator("email")(email_en_minusculas)


class UsuarioOut(Schema):
    id_usuario: int
    email: EmailStr
    rol: Rol
    nombre: str
    activo: bool
    repartidor_id: int | None
    cliente_id: int | None


class TokenOut(Schema):
    access_token: str
    token_type: str = "bearer"
    expira: datetime
    usuario: UsuarioOut


class AccesoIn(Schema):
    """Credenciales que el encargado le asigna a un repartidor o a un cliente."""

    email: EmailStr
    password: str = Field(max_length=72)

    _email = field_validator("email")(email_en_minusculas)
    _password = field_validator("password")(validar_password)
