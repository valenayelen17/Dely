from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from models import Usuario
from schemas import LoginIn, TokenOut, UsuarioOut
from seguridad import crear_token, usuario_actual, verificar

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenOut)
def login(datos: LoginIn, db: Session = Depends(get_db)):
    usuario = db.scalars(select(Usuario).where(func.lower(Usuario.email) == datos.email.lower())).first()
    # Mismo mensaje si no existe el email o si la contraseña está mal, para no revelar qué cuentas hay.
    if usuario is None or not usuario.activo or not verificar(datos.password, usuario.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email o contraseña incorrectos.")
    token, vence = crear_token(usuario)
    return TokenOut(access_token=token, expira=vence, usuario=UsuarioOut.model_validate(usuario))


@router.get("/yo", response_model=UsuarioOut)
def quien_soy(usuario: Usuario = Depends(usuario_actual)):
    return usuario
