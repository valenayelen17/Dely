from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from seguridad import solo_encargado
from routers.comercios import buscar_comercio
from models import Producto
from schemas import ProductoCreate, ProductoOut, ProductoUpdate

router = APIRouter(prefix="/api/productos", tags=["Productos"], dependencies=[Depends(solo_encargado)])


def exigir_nombre_libre(db: Session, comercio_id: int, nombre: str, excepto_id: int | None = None) -> None:
    consulta = select(Producto).where(
        Producto.comercio_id == comercio_id, func.lower(Producto.nombre) == nombre.strip().lower()
    )
    otro = db.scalars(consulta).first()
    if otro is not None and otro.id_producto != excepto_id:
        raise HTTPException(409, f"Ya existe un producto llamado {otro.nombre} en el comercio.")


@router.get("/", response_model=list[ProductoOut])
def listar_productos(
    comercio_id: int | None = None,
    categoria: str | None = None,
    limit: int = Query(100, gt=0, le=500),
    db: Session = Depends(get_db),
):
    consulta = select(Producto).order_by(Producto.id_producto).limit(limit)
    if comercio_id is not None:
        consulta = consulta.where(Producto.comercio_id == comercio_id)
    if categoria:
        consulta = consulta.where(Producto.categoria == categoria.strip())
    return list(db.scalars(consulta).all())


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.get(Producto, producto_id)
    if producto is None:
        raise HTTPException(404, "Producto no encontrado.")
    return producto


@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate, db: Session = Depends(get_db)):
    buscar_comercio(db, datos.comercio_id)
    exigir_nombre_libre(db, datos.comercio_id, datos.nombre)
    producto = Producto(**datos.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(producto_id: int, datos: ProductoUpdate, db: Session = Depends(get_db)):
    producto = db.get(Producto, producto_id)
    if producto is None:
        raise HTTPException(404, "Producto no encontrado.")
    buscar_comercio(db, datos.comercio_id)
    if datos.comercio_id != producto.comercio_id and producto.detalles:
        raise HTTPException(409, "No se puede cambiar de comercio a un producto que forma parte de pedidos.")
    exigir_nombre_libre(db, datos.comercio_id, datos.nombre, excepto_id=producto_id)
    for campo, valor in datos.model_dump().items():
        setattr(producto, campo, valor)
    db.commit()
    db.refresh(producto)
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.get(Producto, producto_id)
    if producto is None:
        raise HTTPException(404, "Producto no encontrado.")
    if producto.detalles:
        raise HTTPException(409, "No se puede eliminar: el producto forma parte de pedidos.")
    db.delete(producto)
    db.commit()
