from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from routers.comercios import buscar_comercio
from models import Producto
from schemas import ProductoCreate, ProductoOut, ProductoUpdate

router = APIRouter(prefix="/api/productos", tags=["Productos"])


@router.get("/", response_model=list[ProductoOut])
def listar_productos(
    comercio_id: int | None = None,
    limit: int = Query(100, gt=0, le=500),
    db: Session = Depends(get_db),
):
    consulta = select(Producto).order_by(Producto.id_producto).limit(limit)
    if comercio_id is not None:
        consulta = consulta.where(Producto.comercio_id == comercio_id)
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
    db.delete(producto)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, "No se puede eliminar: el producto forma parte de pedidos.") from error
