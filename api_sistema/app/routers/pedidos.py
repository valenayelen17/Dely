from fastapi import APIRouter, HTTPException
from app.database import obtener_conexion

router = APIRouter(
    prefix="/api/pedidos",
    tags=["Pedidos"]
)


@router.get("/")
def listar_pedidos():
    conexion = obtener_conexion()

    if conexion is None:
        raise HTTPException(
            status_code=500,
            detail="No se pudo conectar con la base de datos"
        )

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM vw_pedidos_completos
            ORDER BY Pedido DESC
            """)

        pedidos = cursor.fetchall()

        return pedidos

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar los pedidos: {error}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
