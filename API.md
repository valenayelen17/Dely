# API de DELY

## Preparar y ejecutar

Se requiere Python 3.10 o superior y MySQL.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Configurá `DATABASE_URL` en `.env`. La cuenta de MySQL debe poder crear la base de datos y las tablas durante el primer inicio.

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --reload
```

La documentación interactiva se publica en <http://127.0.0.1:8000/docs>.

## Organización MVC

- `models.py`: entidades ORM y relaciones de MySQL.
- `schemas.py`: validación Pydantic y modelos de respuesta.
- `routers/`: controladores de cada recurso y operaciones del sistema.
- `database.py`: conexión, sesiones y dependencia de base de datos.
- `api.py`: inicialización de FastAPI y registro de controladores.

## Endpoints

| Recurso | Ruta | Operaciones |
|---|---|---|
| Clientes | `/api/clientes/` | GET, POST, GET por ID, PUT, DELETE |
| Productos | `/api/productos/` | GET, POST, GET por ID, PUT, DELETE |
| Repartidores | `/api/repartidores/` | GET, POST, GET por ID, PUT, DELETE |
| Pedidos | `/api/pedidos/` | GET, POST, GET por ID, PUT, DELETE |
| Asignación de repartidor | `/api/pedidos/{id}/asignar` | PATCH |
| Estado de pedido | `/api/pedidos/{id}/estado` | PATCH |
| Entregas | `/api/entregas/` | GET, POST, GET por ID, PUT, DELETE |

Las listas aceptan el parámetro `limit` entre 1 y 500.

## Flujo de un pedido

1. Crear un cliente en `/api/clientes/` y guardar `id_cliente`.
2. Crear los productos en `/api/productos/` y guardar sus `id_producto`.
3. Crear un repartidor en `/api/repartidores/` con su zona.
4. Crear un pedido en `/api/pedidos/`, indicando `cliente_id`, `zona` y uno o más productos en `detalles`.
5. Asignar un repartidor de la misma zona con `PATCH /api/pedidos/{id}/asignar` y el cuerpo `{ "repartidor_id": 1 }`.
6. Crear una entrega para el pedido en `/api/entregas/` y actualizar su ubicación y estado mediante `PUT /api/entregas/{id}`.

Al crear el pedido, la API valida el stock y registra el precio unitario vigente en cada detalle. Al eliminarlo, devuelve las cantidades al stock. Los estados aceptados son Pendiente, Preparando, Listo para retirar, En camino, Entregado y Cancelado. Para pasar a En camino debe haber un repartidor disponible asignado a la zona del pedido.
