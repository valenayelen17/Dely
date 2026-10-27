"""Punto de entrada de la API DELY: uvicorn api:app --reload."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

import models  # Registra las tablas ORM antes de inicializarlas.
from database import Base, crear_base_si_no_existe, engine
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
    description="API para gestionar clientes, productos, pedidos y entregas.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(clientes_router)
app.include_router(repartidores_router)
app.include_router(productos_router)
app.include_router(pedidos_router)
app.include_router(entregas_router)


@app.get("/", tags=["Inicio"])
def inicio():
    return {"mensaje": "Bienvenido a DELY API", "estado": "Funcionando", "documentacion": "/docs"}
