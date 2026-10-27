"""Conexión y sesiones de SQLAlchemy para MySQL."""

import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv(Path(__file__).resolve().parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "Falta DATABASE_URL. Configurá MySQL con una URL como "
        "mysql+pymysql://usuario:clave@localhost:3306/dely_db"
    )

database_url = make_url(DATABASE_URL)
if database_url.drivername != "mysql+pymysql":
    raise RuntimeError("DATABASE_URL debe usar el controlador mysql+pymysql.")
if not database_url.database:
    raise RuntimeError("DATABASE_URL debe incluir el nombre de la base de datos.")

engine = create_engine(database_url, pool_pre_ping=True)
server_engine = create_engine(database_url.set(database=None), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarativa común de los modelos."""


def crear_base_si_no_existe() -> None:
    nombre = engine.dialect.identifier_preparer.quote(database_url.database)
    with server_engine.begin() as connection:
        connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {nombre}"))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
