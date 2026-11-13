"""Autenticación con JWT: contraseñas con bcrypt, tokens firmados y control de roles."""

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from estados import Rol
from models import Usuario

load_dotenv(Path(__file__).resolve().parent / ".env")

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("Falta JWT_SECRET en el .env: es la clave con la que se firman los tokens.")
JWT_ALGORITMO = "HS256"
JWT_HORAS = int(os.getenv("JWT_HORAS", "8"))
# Costo de bcrypt: 12 es el valor recomendado; los tests lo bajan para correr rápido.
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

esquema_bearer = HTTPBearer(auto_error=False, description="Token JWT obtenido en /api/auth/login")


# --- Contraseñas ---------------------------------------------------------------

def hashear(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode()


def verificar(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


# --- Tokens --------------------------------------------------------------------

def crear_token(usuario: Usuario) -> tuple[str, datetime]:
    vence = datetime.now(UTC) + timedelta(hours=JWT_HORAS)
    datos = {
        "sub": str(usuario.id_usuario),
        "rol": usuario.rol,
        "repartidor_id": usuario.repartidor_id,
        "cliente_id": usuario.cliente_id,
        "exp": vence,
    }
    return jwt.encode(datos, JWT_SECRET, algorithm=JWT_ALGORITMO), vence


def _no_autenticado(detalle: str) -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detalle, headers={"WWW-Authenticate": "Bearer"})


def usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    if credenciales is None:
        raise _no_autenticado("Tenés que iniciar sesión.")
    try:
        datos = jwt.decode(credenciales.credentials, JWT_SECRET, algorithms=[JWT_ALGORITMO])
    except jwt.ExpiredSignatureError:
        raise _no_autenticado("La sesión venció. Volvé a iniciar sesión.") from None
    except jwt.InvalidTokenError:
        raise _no_autenticado("El token no es válido.") from None

    usuario = db.get(Usuario, int(datos["sub"]))
    if usuario is None or not usuario.activo:
        raise _no_autenticado("La cuenta no existe o está desactivada.")
    return usuario


def requiere(*roles: Rol):
    """Dependencia que deja pasar sólo a los roles indicados."""

    def _verificar(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tenés permiso para esta acción.")
        return usuario

    return _verificar


solo_encargado = requiere(Rol.ENCARGADO)


def puede_ver_repartidor(usuario: Usuario, repartidor_id: int) -> None:
    """El encargado ve a todos; un repartidor sólo a sí mismo."""
    if usuario.rol == Rol.ENCARGADO:
        return
    if usuario.rol == Rol.REPARTIDOR and usuario.repartidor_id == repartidor_id:
        return
    raise HTTPException(status.HTTP_403_FORBIDDEN, "Sólo podés ver tus propias entregas.")
