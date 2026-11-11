"""Conexión y sesiones de SQLAlchemy.

En producción se usa MySQL (mysql+pymysql). Los tests usan SQLite en memoria.
"""

import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

load_dotenv(Path(__file__).resolve().parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "Falta DATABASE_URL. Configurá MySQL con una URL como "
        "mysql+pymysql://usuario:clave@localhost:3306/dely_db"
    )

database_url = make_url(DATABASE_URL)
ES_SQLITE = database_url.get_backend_name() == "sqlite"
if not ES_SQLITE:
    if database_url.drivername != "mysql+pymysql":
        raise RuntimeError("DATABASE_URL debe usar el controlador mysql+pymysql.")
    if not database_url.database:
        raise RuntimeError("DATABASE_URL debe incluir el nombre de la base de datos.")


def crear_engine(url) -> Engine:
    """Crea un engine; SQLite en memoria comparte una única conexión."""
    url = make_url(url)
    if url.get_backend_name() == "sqlite":
        nuevo = create_engine(
            url, connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        # SQLite no valida claves foráneas salvo que se lo pidamos.
        event.listen(nuevo, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
        return nuevo
    return create_engine(url, pool_pre_ping=True)


engine = crear_engine(database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarativa común de los modelos."""


def crear_base_si_no_existe() -> None:
    if ES_SQLITE:
        return
    server_engine = create_engine(database_url.set(database=None), pool_pre_ping=True)
    nombre = engine.dialect.identifier_preparer.quote(database_url.database)
    with server_engine.begin() as connection:
        connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {nombre}"))
    server_engine.dispose()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
