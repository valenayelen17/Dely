from datetime import date, time
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from estados import EstadoEntrega, EstadoPedido


class Comercio(Base):
    __tablename__ = "comercios"

    id_comercio: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    repartidores: Mapped[list["Repartidor"]] = relationship(back_populates="comercio")
    productos: Mapped[list["Producto"]] = relationship(back_populates="comercio")
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="comercio")


class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="cliente")


class Repartidor(Base):
    __tablename__ = "repartidores"

    id_repartidor: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False)
    zona: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    comercio_id: Mapped[int] = mapped_column(
        ForeignKey("comercios.id_comercio", ondelete="RESTRICT"), nullable=False, index=True
    )

    comercio: Mapped[Comercio] = relationship(back_populates="repartidores")
    entregas: Mapped[list["Entrega"]] = relationship(back_populates="repartidor")


class Producto(Base):
    __tablename__ = "productos"

    id_producto: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(String(500), nullable=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    categoria: Mapped[str] = mapped_column(String(100), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comercio_id: Mapped[int] = mapped_column(
        ForeignKey("comercios.id_comercio", ondelete="RESTRICT"), nullable=False, index=True
    )

    comercio: Mapped[Comercio] = relationship(back_populates="productos")
    detalles: Mapped[list["DetallePedido"]] = relationship(back_populates="producto")


class Pedido(Base):
    __tablename__ = "pedidos"

    id_pedido: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fecha_pedido: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    direccion_entrega: Mapped[str] = mapped_column(String(255), nullable=False)
    zona: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    estado: Mapped[str] = mapped_column(
        String(30), default=EstadoPedido.PENDIENTE, nullable=False, index=True
    )
    horario_estimado: Mapped[time] = mapped_column(Time, nullable=False)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id_cliente", ondelete="RESTRICT"), nullable=False, index=True
    )
    comercio_id: Mapped[int] = mapped_column(
        ForeignKey("comercios.id_comercio", ondelete="RESTRICT"), nullable=False, index=True
    )

    cliente: Mapped[Cliente] = relationship(back_populates="pedidos")
    comercio: Mapped[Comercio] = relationship(back_populates="pedidos")
    detalles: Mapped[list["DetallePedido"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )
    entrega: Mapped["Entrega | None"] = relationship(
        back_populates="pedido", cascade="all, delete-orphan", uselist=False
    )

    @property
    def repartidor(self) -> Repartidor | None:
        return self.entrega.repartidor if self.entrega else None


class DetallePedido(Base):
    __tablename__ = "detalles_pedido"
    __table_args__ = (UniqueConstraint("pedido_id", "producto_id", name="uq_detalle_pedido_producto"),)

    id_detalle: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id_pedido"), nullable=False, index=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id_producto"), nullable=False, index=True)

    pedido: Mapped[Pedido] = relationship(back_populates="detalles")
    producto: Mapped[Producto] = relationship(back_populates="detalles")

    @property
    def subtotal(self) -> Decimal:
        return self.cantidad * self.precio_unitario


class Entrega(Base):
    __tablename__ = "entregas"

    id_entrega: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    estado: Mapped[str] = mapped_column(
        String(30), default=EstadoEntrega.ASIGNADA, nullable=False, index=True
    )
    ubicacion_actual: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fecha_entrega: Mapped[date | None] = mapped_column(Date, nullable=True)
    hora_entrega: Mapped[time | None] = mapped_column(Time, nullable=True)
    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedidos.id_pedido", ondelete="CASCADE"), unique=True, nullable=False
    )
    repartidor_id: Mapped[int] = mapped_column(
        ForeignKey("repartidores.id_repartidor", ondelete="RESTRICT"), nullable=False, index=True
    )

    pedido: Mapped[Pedido] = relationship(back_populates="entrega")
    repartidor: Mapped[Repartidor] = relationship(back_populates="entregas")
