# API de DELY

## Preparar y ejecutar

Requiere Python 3.11 o superior y MySQL.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Configurá `DATABASE_URL` en `.env`. La cuenta de MySQL tiene que poder crear la base y las tablas, porque se crean solas en el primer inicio.

> Si ya tenías una base creada con una versión anterior de la API, usá una base nueva (por ejemplo `dely_db_v2`): el arranque crea las tablas que faltan, pero no modifica las que ya existen.

```powershell
.\.venv\Scripts\python.exe seed.py                    # opcional: datos de demo
.\.venv\Scripts\python.exe -m uvicorn api:app --reload
```

La documentación interactiva queda en <http://127.0.0.1:8000/docs>.

### Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Los tests usan una base SQLite en memoria y no tocan MySQL.

## Arquitectura (MVC)

| Capa | Archivos | Rol |
|---|---|---|
| Modelo | `models.py`, `estados.py`, `database.py` | Entidades ORM, estados y conexión a MySQL |
| Vista | `schemas.py` (y el frontend) | Qué datos entran y salen de la API |
| Controlador | `routers/` | Endpoints HTTP: reciben el pedido y delegan |
| Reglas de negocio | `services/` | Asignación, recorrido, stock, notificaciones, seguimiento |

`errores.py` traduce los errores de negocio a respuestas HTTP: 404 si no existe, 409 si hay un conflicto de estado y 422 si los datos no son válidos.

## Endpoints

| Recurso | Ruta | Operaciones |
|---|---|---|
| Comercios | `/api/comercios/` | GET, POST, GET por id, PUT, DELETE |
| Clientes | `/api/clientes/` | GET, POST, GET por id, PUT, DELETE |
| Productos | `/api/productos/?comercio_id=&categoria=` | GET, POST, GET por id, PUT, DELETE |
| Repartidores | `/api/repartidores/?comercio_id=&zona=&disponible=` | GET, POST, GET por id, PUT, DELETE |
| Disponibilidad | `/api/repartidores/{id}/disponibilidad` | PATCH |
| Entregas del repartidor | `/api/repartidores/{id}/entregas?activas=` | GET |
| Pedidos | `/api/pedidos/?comercio_id=&estado=` | GET, POST, GET por id, PUT, DELETE |
| Pedidos pendientes | `/api/pedidos/pendientes?comercio_id=&zona=` | GET |
| Asignar repartidor | `/api/pedidos/{id}/asignar` | PATCH |
| Cancelar pedido | `/api/pedidos/{id}/cancelar` | PATCH |
| Notificaciones | `/api/pedidos/{id}/notificaciones` | GET |
| Entregas | `/api/entregas/?repartidor_id=&estado=` | GET, GET por id |
| Estado de entrega | `/api/entregas/{id}/estado` | PATCH |
| Ubicación | `/api/entregas/{id}/ubicacion` | PATCH |
| Seguimiento | `/api/seguimiento/{codigo}` | GET |
| Marcar leídas | `/api/seguimiento/{codigo}/notificaciones/leidas` | PATCH |

Los listados aceptan `limit` entre 1 y 500.

## Estados

```
Pedido:   Pendiente → Asignado → En camino → Entregado
              └──────────┴───────────┴──→ Cancelado

Entrega:  Asignada → En camino → Llegando → Entregada
```

- La entrega se crea al asignar el repartidor. Mientras no salió, se puede reasignar.
- El repartidor avanza la entrega sin saltear estados y el pedido se actualiza solo.
- Al pasar a **Entregada** se registran la fecha y la hora reales de la entrega.
- Cancelar devuelve el stock. No se cancelan pedidos ya entregados.
- Sólo se editan pedidos **Pendientes**, y sólo se eliminan los Pendientes o Cancelados.

## Flujo de un pedido

1. `POST /api/pedidos/` con `comercio_id`, `cliente_id`, `zona`, `horario_estimado` y `detalles`. Valida el stock, lo descuenta, guarda el precio vigente y genera el `codigo_seguimiento`. Si no se envía `direccion_entrega`, se usa la del cliente.
2. `GET /api/repartidores/?zona=Centro&disponible=true` para elegir repartidor.
3. `PATCH /api/pedidos/{id}/asignar` con `{ "repartidor_id": 1 }`.
4. El repartidor consulta `GET /api/repartidores/{id}/entregas` y avanza con `PATCH /api/entregas/{id}/estado`, enviando `{ "estado": "En camino" }`, después `Llegando` y por último `Entregada`.
5. El cliente sigue el pedido en `GET /api/seguimiento/{codigo}` y recibe una notificación por cada cambio. Cuando el repartidor marca **Llegando**, recibe el aviso de llegada.
