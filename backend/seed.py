"""Carga datos de demostración si la base está vacía: python seed.py"""

from datetime import time

from sqlalchemy import func, select
from sqlalchemy.orm import Session

import models
from database import Base, SessionLocal, crear_base_si_no_existe, engine
from estados import EstadoEntrega
from schemas import DetalleCreate, PedidoCreate
from services import entregas, pedidos


def cargar(db: Session) -> bool:
    if db.scalar(select(func.count(models.Comercio.id_comercio))):
        return False

    comercio = models.Comercio(
        nombre="La Esquina Pizzería", direccion="Av. Corrientes 1234", telefono="1140001234", email="contacto@laesquina.com.ar"
    )
    db.add(comercio)
    db.flush()

    productos = [
        models.Producto(nombre=n, descripcion=d, precio=p, categoria=c, stock=s, comercio_id=comercio.id_comercio)
        for n, d, p, c, s in [
            ("Pizza muzzarella", "Grande, 8 porciones", 12000, "Pizzas", 30),
            ("Pizza napolitana", "Tomate, ajo y albahaca", 14500, "Pizzas", 20),
            ("Fainá", "Porción", 1800, "Pizzas", 40),
            ("Empanada de carne", "Cortada a cuchillo", 1600, "Empanadas", 60),
            ("Empanada de jamón y queso", None, 1500, "Empanadas", 60),
            ("Gaseosa 1,5 L", None, 3500, "Bebidas", 25),
        ]
    ]
    repartidores = [
        models.Repartidor(nombre=n, apellido=a, telefono=t, zona=z, disponible=disp, comercio_id=comercio.id_comercio)
        for n, a, t, z, disp in [
            ("Juan", "Gómez", "1150001111", "Centro", True),
            ("Lucía", "Fernández", "1150002222", "Palermo", True),
            ("Martín", "Sosa", "1150003333", "Caballito", True),
            ("Sofía", "Ríos", "1150004444", "Centro", False),
        ]
    ]
    clientes = [
        models.Cliente(nombre=n, apellido=a, telefono=t, email=e, direccion=d)
        for n, a, t, e, d in [
            ("Ana", "Pérez", "1160001111", "ana.perez@ejemplo.com", "Av. Callao 456"),
            ("Bruno", "López", "1160002222", "bruno.lopez@ejemplo.com", "Thames 1500"),
            ("Carla", "Méndez", "1160003333", "carla.mendez@ejemplo.com", "Av. Rivadavia 5000"),
        ]
    ]
    db.add_all(productos + repartidores + clientes)
    db.commit()

    def pedido(cliente, zona, hora, items):
        return pedidos.crear_pedido(
            db,
            PedidoCreate(
                zona=zona,
                horario_estimado=hora,
                cliente_id=cliente.id_cliente,
                comercio_id=comercio.id_comercio,
                detalles=[DetalleCreate(producto_id=p.id_producto, cantidad=c) for p, c in items],
            ),
        )

    def avanzar(pedido_id, repartidor, *estados):
        entrega_id = pedidos.asignar_repartidor(db, pedido_id, repartidor.id_repartidor).entrega.id_entrega
        for estado in estados:
            entregas.cambiar_estado(db, entrega_id, estado)

    ana, bruno, carla = clientes
    juan, lucia, martin, _ = repartidores
    muzza, napo, faina, carne, jyq, gaseosa = productos

    pedido(ana, "Centro", time(20, 30), [(muzza, 1), (gaseosa, 1)])
    pedido(bruno, "Palermo", time(21, 0), [(carne, 6), (jyq, 6)])
    p3 = pedido(carla, "Caballito", time(20, 45), [(napo, 1), (faina, 2)])
    avanzar(p3.id_pedido, martin)
    p4 = pedido(ana, "Centro", time(20, 0), [(carne, 12)])
    avanzar(p4.id_pedido, juan, EstadoEntrega.EN_CAMINO)
    p5 = pedido(bruno, "Palermo", time(19, 30), [(muzza, 2)])
    avanzar(p5.id_pedido, lucia, EstadoEntrega.EN_CAMINO, EstadoEntrega.LLEGANDO)
    p6 = pedido(carla, "Caballito", time(19, 0), [(jyq, 3), (gaseosa, 1)])
    avanzar(p6.id_pedido, martin, EstadoEntrega.EN_CAMINO, EstadoEntrega.ENTREGADA)
    p7 = pedido(ana, "Centro", time(21, 30), [(faina, 4)])
    pedidos.cancelar_pedido(db, p7.id_pedido)
    return True


if __name__ == "__main__":
    crear_base_si_no_existe()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as sesion:
        print("Datos de demo cargados." if cargar(sesion) else "La base ya tiene datos; no se cargó nada.")
