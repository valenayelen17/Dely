# DELY — Backend (API)

## Preparar y ejecutar

Requiere Python 3.11 o superior y MySQL. Todos los comandos se corren desde `backend/`.

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Configurá en `.env`:

| Variable | Para qué sirve |
|---|---|
| `DATABASE_URL` | Conexión a MySQL (o `sqlite:///./dely.db` para probar). La cuenta tiene que poder crear la base y las tablas, porque se crean solas en el primer inicio. |
| `JWT_SECRET` | Clave con la que se firman los tokens. Obligatoria. Generala con `python -c "import secrets; print(secrets.token_urlsafe(48))"`. |
| `JWT_HORAS` | Validez del token en horas (8 por defecto). |
| `CORS_ORIGINS` | Orígenes del frontend habilitados. |

> Si ya tenías una base creada con una versión anterior de la API, usá una base nueva (por ejemplo `dely_db_v2`): el arranque crea las tablas que faltan, pero no modifica las que ya existen.

```powershell
.\.venv\Scripts\python.exe seed.py                    # datos de demo y cuentas de acceso (contraseña dely1234)
.\.venv\Scripts\python.exe -m uvicorn api:app --reload
```

La documentación interactiva queda en <http://127.0.0.1:8000/docs>.

### Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Los tests usan una base SQLite en memoria y no tocan MySQL. Corren autenticados como encargado; `tests/test_auth.py` prueba el login, los tokens vencidos o adulterados y los permisos de cada rol.

## Autenticación y permisos

`POST /api/auth/login` recibe `{email, password}` y devuelve un JWT firmado con HS256 (`access_token`), su vencimiento y los datos del usuario. El resto de la API se usa con el header `Authorization: Bearer <token>`. En `/docs`, el botón *Authorize* permite pegarlo.

| Rol | Puede usar |
|---|---|
| Encargado | Todos los endpoints |
| Repartidor | `GET /api/repartidores/{su id}`, `GET /api/repartidores/{su id}/entregas`, y `GET` / `PATCH` de **sus** entregas |
| Cliente | `GET /api/seguimiento/` (sus pedidos), `GET /api/seguimiento/{codigo}` y marcar leídas, sólo de **sus** pedidos |

Sin token o con un token vencido o inválido la respuesta es 401, y con un rol sin permiso es 403. El token lleva una huella de la contraseña: si el encargado la cambia, los tokens anteriores dejan de valer. Tras 5 logins fallidos seguidos el email queda bloqueado 15 minutos (429 con `Retry-After`); el límite se lleva en memoria y se configura con `LOGIN_MAX_INTENTOS` y `LOGIN_BLOQUEO_MINUTOS`. El código de seguimiento de otro cliente devuelve 404, así no se revela que existe. `seguridad.py` concentra el hash de contraseñas (bcrypt), la creación y validación de tokens y las dependencias de FastAPI que exigen un rol.

## Arquitectura (MVC)

| Capa | Archivos | Rol |
|---|---|---|
| Modelo | `models.py`, `estados.py`, `database.py` | Entidades ORM (incluido `Usuario`), estados, roles y conexión a MySQL |
| Vista | `schemas.py` (y el frontend) | Qué datos entran y salen de la API |
| Controlador | `routers/` | Endpoints HTTP: reciben el pedido y delegan |
| Reglas de negocio | `services/` | Asignación, recorrido, stock, notificaciones, seguimiento |
| Seguridad | `seguridad.py`, `routers/auth.py`, `routers/usuarios.py` | Contraseñas, JWT, control de roles y accesos |

`errores.py` traduce los errores de negocio a respuestas HTTP: 404 si no existe, 409 si hay un conflicto de estado y 422 si los datos no son válidos.

## Endpoints

| Recurso | Ruta | Operaciones |
|---|---|---|
| Login | `/api/auth/login` | POST (público) |
| Usuario actual | `/api/auth/yo` | GET |
| Accesos | `/api/usuarios/?rol=` | GET |
| Dar o quitar acceso | `/api/usuarios/repartidores/{id}/acceso`, `/api/usuarios/clientes/{id}/acceso` | PUT (crea la cuenta o cambia la contraseña), DELETE (la desactiva) |
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
| Mis pedidos (cliente) | `/api/seguimiento/` | GET |
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
- Un repartidor con entregas activas no puede salir de turno, cambiar de zona ni de comercio.
- El pedido sólo se crea en una zona que cubra algún repartidor del comercio, con fecha entre hoy y 7 días.
- Las validaciones de formato (nombres, teléfonos, emails en minúsculas, contraseñas) están en `schemas.py`; las de unicidad (teléfono de repartidor, nombre de producto por comercio) en los routers.
- Sólo se editan pedidos **Pendientes**, y sólo se eliminan los Pendientes o Cancelados.

## Flujo de un pedido

1. `POST /api/pedidos/` con `comercio_id`, `cliente_id`, `zona`, `horario_estimado` y `detalles`. Valida el stock, lo descuenta, guarda el precio vigente y genera el `codigo_seguimiento`. Si no se envía `direccion_entrega`, se usa la del cliente.
2. `GET /api/repartidores/?zona=Centro&disponible=true` para elegir repartidor.
3. `PATCH /api/pedidos/{id}/asignar` con `{ "repartidor_id": 1 }`.
4. El repartidor consulta `GET /api/repartidores/{id}/entregas` y avanza con `PATCH /api/entregas/{id}/estado`, enviando `{ "estado": "En camino" }`, después `Llegando` y por último `Entregada`.
5. El cliente sigue el pedido en `GET /api/seguimiento/{codigo}` y recibe una notificación por cada cambio. Cuando el repartidor marca **Llegando**, recibe el aviso de llegada.
