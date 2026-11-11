"""Punto de entrada de la API DELY: uvicorn api:app --reload."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models  # noqa: F401  Registra las tablas ORM antes de inicializarlas.
from database import Base, crear_base_si_no_existe, engine
from errores import registrar_manejadores
from routers.clientes import router as clientes_router
from routers.entregas import router as entregas_router
from routers.pedidos import router as pedidos_router
from routers.productos import router as productos_router
from routers.repartidores import router as repartidores_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    crear_base_si_no_existe()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="DELY API",
    description="API para gestionar comercios, clientes, productos, pedidos y entregas.",
    version="1.0.0",
    lifespan=lifespan,
)

origenes = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origen.strip() for origen in origenes if origen.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)
registrar_manejadores(app)

app.include_router(clientes_router)
app.include_router(repartidores_router)
app.include_router(productos_router)
app.include_router(pedidos_router)
app.include_router(entregas_router)


@app.get("/", tags=["Inicio"])
def inicio():
    return {"mensaje": "Bienvenido a DELY API", "estado": "Funcionando", "documentacion": "/docs"}
