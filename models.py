"""Entidades ORM y relaciones de DELY."""

from datetime import date, time
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


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
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="repartidor")


class Producto(Base):
    __tablename__ = "productos"

    id_producto: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(String(500), nullable=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    categoria: Mapped[str] = mapped_column(String(100), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    detalles: Mapped[list["DetallePedido"]] = relationship(back_populates="producto")


class Pedido(Base):
    __tablename__ = "pedidos"

    id_pedido: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fecha_pedido: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    direccion_entrega: Mapped[str] = mapped_column(String(255), nullable=False)
    zona: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    estado: Mapped[str] = mapped_column(String(30), default="Pendiente", nullable=False, index=True)
    horario_estimado: Mapped[time] = mapped_column(Time, nullable=False)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id_cliente"), nullable=False, index=True)
    repartidor_id: Mapped[int | None] = mapped_column(ForeignKey("repartidores.id_repartidor"), nullable=True)

    cliente: Mapped[Cliente] = relationship(back_populates="pedidos")
    repartidor: Mapped[Repartidor | None] = relationship(back_populates="pedidos")
    detalles: Mapped[list["DetallePedido"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )
    entrega: Mapped["Entrega | None"] = relationship(
        back_populates="pedido", cascade="all, delete-orphan", uselist=False
    )


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
    fecha_entrega: Mapped[date] = mapped_column(Date, nullable=False)
    hora_entrega: Mapped[time] = mapped_column(Time, nullable=False)
    estado: Mapped[str] = mapped_column(String(30), default="Pendiente", nullable=False)
    ubicacion_actual: Mapped[str] = mapped_column(String(255), nullable=False)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id_pedido"), unique=True, nullable=False)
    pedido: Mapped[Pedido] = relationship(back_populates="entrega")
