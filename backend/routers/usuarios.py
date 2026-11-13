"""Accesos de repartidores y clientes. Sólo el encargado los administra."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from estados import Rol
from models import Cliente, Repartidor, Usuario
from schemas import AccesoIn, UsuarioOut
from seguridad import hashear, solo_encargado

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"], dependencies=[Depends(solo_encargado)])


@router.get("/", response_model=list[UsuarioOut])
def listar_usuarios(rol: Rol | None = None, db: Session = Depends(get_db)):
    consulta = select(Usuario).order_by(Usuario.id_usuario)
    if rol is not None:
        consulta = consulta.where(Usuario.rol == rol)
    return list(db.scalars(consulta).all())


def _guardar_acceso(db: Session, usuario: Usuario | None, datos: AccesoIn, **vinculo) -> Usuario:
    otro = db.scalars(select(Usuario).where(func.lower(Usuario.email) == datos.email)).first()
    if otro is not None and otro is not usuario:
        raise HTTPException(409, "Ese email ya lo usa otra cuenta.")
    if usuario is None:
        usuario = Usuario(**vinculo)
        db.add(usuario)
    usuario.email = datos.email
    usuario.password_hash = hashear(datos.password)
    usuario.activo = True
    db.commit()
    db.refresh(usuario)
    return usuario


@router.put("/repartidores/{repartidor_id}/acceso", response_model=UsuarioOut)
def acceso_de_repartidor(repartidor_id: int, datos: AccesoIn, db: Session = Depends(get_db)):
    if db.get(Repartidor, repartidor_id) is None:
        raise HTTPException(404, "Repartidor no encontrado.")
    usuario = db.scalars(select(Usuario).where(Usuario.repartidor_id == repartidor_id)).first()
    return _guardar_acceso(db, usuario, datos, rol=Rol.REPARTIDOR, repartidor_id=repartidor_id)


@router.put("/clientes/{cliente_id}/acceso", response_model=UsuarioOut)
def acceso_de_cliente(cliente_id: int, datos: AccesoIn, db: Session = Depends(get_db)):
    if db.get(Cliente, cliente_id) is None:
        raise HTTPException(404, "Cliente no encontrado.")
    usuario = db.scalars(select(Usuario).where(Usuario.cliente_id == cliente_id)).first()
    return _guardar_acceso(db, usuario, datos, rol=Rol.CLIENTE, cliente_id=cliente_id)


def _desactivar(db: Session, usuario: Usuario | None) -> None:
    """Deja la cuenta sin acceso. Volver a asignarle credenciales (PUT) la reactiva."""
    if usuario is None:
        raise HTTPException(404, "Esa persona no tiene una cuenta de acceso.")
    usuario.activo = False
    db.commit()


@router.delete("/repartidores/{repartidor_id}/acceso", status_code=status.HTTP_204_NO_CONTENT)
def quitar_acceso_de_repartidor(repartidor_id: int, db: Session = Depends(get_db)):
    _desactivar(db, db.scalars(select(Usuario).where(Usuario.repartidor_id == repartidor_id)).first())


@router.delete("/clientes/{cliente_id}/acceso", status_code=status.HTTP_204_NO_CONTENT)
def quitar_acceso_de_cliente(cliente_id: int, db: Session = Depends(get_db)):
    _desactivar(db, db.scalars(select(Usuario).where(Usuario.cliente_id == cliente_id)).first())
