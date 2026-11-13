from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from estados import Rol
from models import Usuario
from schemas import SeguimientoOut
from seguridad import requiere
from services import seguimiento as servicio

router = APIRouter(prefix="/api/seguimiento", tags=["Seguimiento"])

cliente_o_encargado = requiere(Rol.CLIENTE, Rol.ENCARGADO)


def _filtro_cliente(usuario: Usuario) -> int | None:
    # El cliente sólo ve sus pedidos; el encargado ve cualquiera.
    return usuario.cliente_id if usuario.rol == Rol.CLIENTE else None


@router.get("/", response_model=list[SeguimientoOut])
def mis_pedidos(db: Session = Depends(get_db), usuario: Usuario = Depends(requiere(Rol.CLIENTE))):
    return servicio.pedidos_del_cliente(db, usuario.cliente_id)


@router.get("/{codigo}", response_model=SeguimientoOut)
def consultar_seguimiento(codigo: str, db: Session = Depends(get_db), usuario: Usuario = Depends(cliente_o_encargado)):
    return servicio.consultar(db, codigo, _filtro_cliente(usuario))


@router.patch("/{codigo}/notificaciones/leidas", response_model=SeguimientoOut)
def marcar_leidas(codigo: str, db: Session = Depends(get_db), usuario: Usuario = Depends(cliente_o_encargado)):
    return servicio.marcar_notificaciones_leidas(db, codigo, _filtro_cliente(usuario))
