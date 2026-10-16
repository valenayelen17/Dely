from fastapi import FastAPI
from app.routers import pedidos

app = FastAPI(title="DELY API")

app.include_router(pedidos.router)


@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido a la API de DELY",
        "estado": "Funcionando"
    }
