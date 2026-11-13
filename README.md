# DELY

[![CI](https://github.com/valenayelen17/Dely/actions/workflows/ci.yml/badge.svg)](https://github.com/valenayelen17/Dely/actions/workflows/ci.yml)

Sistema de gestión de entregas de última milla para comercios con repartidores propios. Centraliza los pedidos, los asigna a repartidores por zona, sigue el recorrido de cada entrega y le avisa al cliente en qué estado está su pedido.

Trabajo práctico de Análisis y Metodologías de Sistemas. Integrantes: Marco Passador y Valentina Ayelén De Jesús.

![Tablero de pedidos en el panel del encargado](docs/capturas/12-django-pendientes.png)

## Contenido

- [Estructura del repositorio](#estructura-del-repositorio)
- [Tecnologías](#tecnologías)
- [Cómo ejecutarlo](#cómo-ejecutarlo)
- [Arquitectura MVC](#arquitectura-mvc)
- [Autenticación (JWT)](#autenticación-jwt)
- [Historias de usuario](#historias-de-usuario)
- [Flujos del sistema](#flujos-del-sistema)
- [Estados del pedido y de la entrega](#estados-del-pedido-y-de-la-entrega)
- [Decisiones respecto del diseño del TP1](#decisiones-respecto-del-diseño-del-tp1)
- [Versionado](#versionado)

## Estructura del repositorio

```
Dely/
├── backend/        API REST (FastAPI + SQLAlchemy + MySQL): datos y reglas de negocio
├── web/            Panel del encargado (Django + AdminLTE), consume la API con requests
├── frontend/       App del repartidor y del cliente (React + TypeScript + Vite)
├── docs/capturas/  Capturas de pantalla usadas en este README
└── .github/        CI: tests del backend y del panel, lint y build del frontend
```

## Tecnologías

| Parte | Stack |
|---|---|
| API (`backend/`) | Python 3.11+, FastAPI, SQLAlchemy 2, MySQL (PyMySQL), Pydantic, JWT (PyJWT) y bcrypt, pytest |
| Panel del encargado (`web/`) | Django 6.1, templates con AdminLTE 4 + Bootstrap 5 + Bootstrap Icons, sesión en cookie firmada, `requests`, `python-dotenv` |
| Repartidor y cliente (`frontend/`) | React 19, TypeScript, Vite, React Router |
| Calidad | GitHub Actions: `pytest` en la API, `manage.py test` en el panel, `oxlint` y build en el frontend |

El esquema sigue el que vimos en clase: **Django consume una API FastAPI** a partir de un `API_URL` definido en el `.env`, y la API es la única que accede a la base de datos. El panel Django y el front React son **aplicaciones separadas**: no se enlazan entre sí y sólo comparten la API.

## Cómo ejecutarlo

### Primera vez

```powershell
# Backend
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env          # configurar DATABASE_URL y JWT_SECRET
.\.venv\Scripts\python.exe seed.py   # datos de demo y cuentas de acceso

# Panel Django
cd ..\web
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env          # API_URL apunta a la API local

# Frontend
cd ..\frontend
npm install
```

La base y las tablas se crean solas al iniciar la API. Para probar sin MySQL se puede usar SQLite poniendo `DATABASE_URL=sqlite:///./dely.db` en el `.env`.

`JWT_SECRET` es la clave con la que la API firma los tokens: tiene que ser larga y aleatoria, y no se sube al repositorio. Se genera con `python -c "import secrets; print(secrets.token_urlsafe(48))"`.

`seed.py` se puede correr también sobre una base que ya tiene datos: en ese caso sólo crea las cuentas de demo que falten.

### Día a día (tres terminales)

```powershell
# 1. API: http://127.0.0.1:8000 (documentación interactiva en /docs)
cd backend
.\.venv\Scripts\python.exe -m uvicorn api:app --reload

# 2. Panel del encargado (Django): http://127.0.0.1:8001
cd web
.\.venv\Scripts\python.exe manage.py runserver 8001

# 3. Vistas del repartidor y del cliente (React): http://localhost:5173
cd frontend
npm run dev
```

Para la demo conviene abrir tres ventanas (o perfiles del navegador, para tener sesiones separadas): el panel en <http://127.0.0.1:8001> como encargado, y <http://localhost:5173> una vez como repartidor y otra como cliente. Las pantallas del repartidor y del cliente se refrescan cada 5 segundos, así que los cambios que hace el encargado se ven en vivo.

Más detalle (endpoints, tests, estructura de cada parte) en [backend/README.md](backend/README.md), [web/README.md](web/README.md) y [frontend/README.md](frontend/README.md).

## Arquitectura MVC

```mermaid
flowchart LR
    subgraph Clientes de la API
        W[Panel Django web/<br/>controllers + templates]
        F[Frontend React<br/>repartidor y cliente]
    end
    subgraph API FastAPI backend/
        R[routers/<br/>controladores HTTP]
        S[schemas.py<br/>entrada y salida]
        SV[services/<br/>asignación, stock,<br/>recorrido, notificaciones]
        M[models.py + estados.py<br/>entidades ORM]
    end
    DB[(MySQL)]
    W -- "requests + API_URL" --> R
    F -- "fetch /api" --> R
    R -- valida con --> S
    R --> SV
    SV --> M
    M --> DB
```

El MVC se aplica en las dos capas:

| Capa | API (`backend/`) | Panel Django (`web/`) |
|---|---|---|
| Modelo | `models.py`, `estados.py`, `database.py`: entidades del DER y conexión a la base | `panel/src/services.py`: obtiene y guarda los datos llamando a la API con `requests` |
| Vista | `schemas.py`: qué datos entran y salen | `panel/templates/`: templates de Django con AdminLTE |
| Controlador | `routers/`: reciben el pedido HTTP y delegan | `panel/controllers/`: vistas basadas en clase con `get` y `post` |
| Reglas de negocio | `services/`: asignación por zona, recorrido, stock, notificaciones y seguimiento | — (siempre pasa por la API) |

En la API, `errores.py` traduce los errores de negocio a respuestas HTTP: 404 si no existe, 409 si hay un conflicto de estado y 422 si los datos no son válidos. El panel muestra esos mensajes tal cual al encargado.

## Autenticación (JWT)

Todo el sistema requiere iniciar sesión. La **API emite el token** y las dos aplicaciones lo usan:

```mermaid
sequenceDiagram
    actor U as Usuario
    participant App as Panel Django o app React
    participant API as API DELY
    U->>App: Email y contraseña
    App->>API: POST /api/auth/login
    API->>API: Verifica la contraseña (bcrypt)
    API-->>App: JWT firmado (rol, id, vencimiento)
    App->>API: Cada pedido con Authorization: Bearer JWT
    API->>API: Valida firma, vencimiento y rol
    API-->>App: Datos (sólo los que le corresponden)
```

| Rol | Dónde entra | Qué puede hacer |
|---|---|---|
| Encargado | Panel Django | Todo: pedidos, asignación, ABM, historial y dar acceso a repartidores y clientes |
| Repartidor | App React | Ver y avanzar **sólo sus** entregas, informar su ubicación |
| Cliente | App React | Ver **sólo sus** pedidos, su seguimiento y sus notificaciones |

- Las contraseñas se guardan con **bcrypt**; nunca en texto plano.
- El token dura 8 horas (`JWT_HORAS`). Cuando vence, las dos aplicaciones vuelven al login.
- El **panel Django** guarda el token en su sesión (cookie firmada, `HttpOnly`) y lo agrega en cada llamada con `requests`. Sólo deja entrar a cuentas de encargado.
- La **app React** guarda el token en `localStorage` y lo manda en cada `fetch`. Rechaza las cuentas de encargado.
- El encargado crea o cambia las credenciales de cada repartidor y cliente desde el panel (botón de la llave en *Repartidores* y *Clientes*).
- Si un repartidor pide entregas de otro, la API responde 403. Si un cliente pide el pedido de otro, responde 404 y así no revela que el código existe.

**Cuentas de demo** (las crea `seed.py`, contraseña `dely1234`):

| Rol | Email |
|---|---|
| Encargado | `encargado@dely.com` |
| Repartidor | `juan.gomez@dely.com`, `lucia.fernandez@dely.com`, `martin.sosa@dely.com`, `sofia.rios@dely.com` |
| Cliente | `ana.perez@ejemplo.com`, `bruno.lopez@ejemplo.com`, `carla.mendez@ejemplo.com` |

## Historias de usuario

| HU | Historia | Cómo se resuelve |
|---|---|---|
| HU-01 | Como encargado quiero ver los pedidos no entregados | Tablero de pendientes. `GET /api/pedidos/pendientes`, con cliente, productos, total y repartidor |
| HU-02 | Como encargado quiero asignar cada pedido a un repartidor disponible | Panel del pedido. `GET /api/repartidores/?zona=&disponible=true` y `PATCH /api/pedidos/{id}/asignar` |
| HU-03 | Como cliente quiero saber en qué estado está mi pedido | *Mis pedidos* y su seguimiento. `GET /api/seguimiento/` y `GET /api/seguimiento/{codigo}`, con estado y horario estimado |
| HU-04 | Como repartidor quiero actualizar el estado de mi entrega | Vista del repartidor. `GET /api/repartidores/{id}/entregas` y `PATCH /api/entregas/{id}/estado` |
| HU-05 | Como cliente quiero un aviso cuando el repartidor esté llegando | Notificación automática cuando la entrega pasa a **Llegando** |

## Flujos del sistema

Cada usuario inicia sesión en su aplicación: el encargado en el panel Django (<http://127.0.0.1:8001>) y el repartidor y el cliente en la app React (<http://localhost:5173>), que los lleva a su pantalla según el rol del token.

| Login del panel (encargado) | Login de la app (repartidor y cliente) |
|---|---|
| ![Login del panel Django](docs/capturas/20-django-login.png) | ![Login de la app React](docs/capturas/07-login.png) |

### Flujo completo de un pedido

```mermaid
sequenceDiagram
    actor E as Encargado
    participant API as API DELY
    participant DB as Base de datos
    actor R as Repartidor
    actor C as Cliente

    E->>API: Carga el pedido (cliente, productos, zona, horario)
    API->>DB: Valida y descuenta stock, guarda precios y genera el código
    API-->>C: Notificación "Recibido" + código de seguimiento
    E->>API: Asigna un repartidor disponible de la zona
    API->>DB: Crea la Entrega (Asignada) y el pedido pasa a Asignado
    API-->>C: Notificación "Repartidor asignado"
    R->>API: Marca "En camino"
    API-->>C: Notificación "En camino"
    R->>API: Marca "Llegando"
    API-->>C: Aviso de llegada (HU-05)
    R->>API: Marca "Entregada"
    API->>DB: Registra fecha y hora real, el pedido pasa a Entregado
    API-->>C: Notificación "Entregado"
```

### 1. Comercio (encargado)

El encargado trabaja desde el **panel Django** (`web/`, <http://127.0.0.1:8001>), una aplicación aparte de la del repartidor y el cliente.

**Tablero de pendientes (HU-01).** El encargado ve los pedidos activos en tres columnas (Pendiente, Asignado y En camino), ordenados por horario estimado. Puede filtrar por zona, y un aviso marca cuántos pedidos siguen sin repartidor. Cada tarjeta muestra el código, la dirección, el cliente, la cantidad de productos, el total y el repartidor.

**Cargar un pedido.** En *Nuevo pedido* elige al cliente, la zona y el horario, y carga las cantidades de cada producto viendo el stock disponible y el total en vivo. Al crear el pedido, la API valida y descuenta el stock, congela el precio vigente de cada producto y genera el código de seguimiento que se le pasa al cliente.

![Carga de un pedido nuevo](docs/capturas/14-django-nuevo-pedido.png)

**Asignar repartidor (HU-02).** En el detalle del pedido, el sistema ofrece **sólo los repartidores en turno de la zona del pedido**. Al asignarlo se crea la entrega. Mientras el repartidor no salió, el pedido se puede reasignar. Mientras esté *Pendiente* se pueden editar la dirección, la zona y el horario. El detalle también muestra las notificaciones que recibió el cliente.

![Detalle del pedido con la asignación de repartidor](docs/capturas/13-django-asignar.png)

**Cancelar.** Un pedido no entregado se puede cancelar desde el detalle. La cancelación **devuelve el stock** y le avisa al cliente.

**Administración e historial.** El menú lateral incluye el alta y la edición de repartidores (con su zona y el turno), de productos (agrupados por categoría, con aviso de stock bajo) y de clientes (con buscador). En repartidores y clientes, la columna *Acceso* muestra quién puede iniciar sesión, y el botón de la llave crea la cuenta o cambia la contraseña. Los formularios validan los datos antes de enviarlos y muestran los errores de negocio que devuelve la API. *Historial* lista los pedidos entregados y cancelados, con la hora real de entrega y el total facturado.

| Repartidores | Productos |
|---|---|
| ![Repartidores](docs/capturas/15-django-repartidores.png) | ![Productos por categoría](docs/capturas/17-django-productos.png) |
| **Clientes** | **Historial** |
| ![Clientes](docs/capturas/18-django-clientes.png) | ![Historial de pedidos](docs/capturas/16-django-historial.png) |

### 2. Repartidor (HU-04)

Después del login, el repartidor ve *Mis entregas*: indicadores del turno (activas, en recorrido, entregadas y monto a cobrar), las entregas activas en tarjetas con la próxima destacada, y una pestaña de historial. Sólo ve las entregas que tiene asignadas: la API lo controla con el token.

![Mis entregas del repartidor](docs/capturas/08-repartidor-entregas.png)

En el detalle avanza el recorrido **sin poder saltear estados**: *Asignada → En camino → Llegando → Entregada*. El panel de la derecha siempre muestra el próximo paso. Además puede informar por dónde va, y ese texto le aparece al cliente en su seguimiento. Cada cambio actualiza el estado del pedido en el panel del comercio. Antes de cerrar una entrega se pide confirmación.

![Detalle de la entrega](docs/capturas/09-repartidor-detalle.png)

### 3. Cliente (HU-03 y HU-05)

Después del login, el cliente ve *Mis pedidos*: los que están en curso, con su etapa y la hora estimada, y una tabla con los anteriores. Sólo ve sus propios pedidos.

![Mis pedidos del cliente](docs/capturas/10-cliente-pedidos.png)

El seguimiento muestra el estado, el horario estimado, los pasos del recorrido, quién lleva el pedido, los productos y, a la derecha, el historial de notificaciones. Cuando el repartidor marca **Llegando**, aparece el aviso de llegada destacado arriba de todo (HU-05).

![Seguimiento con aviso de llegada](docs/capturas/11-cliente-seguimiento.png)

## Estados del pedido y de la entrega

```mermaid
stateDiagram-v2
    direction LR
    state "Pedido" as P {
        [*] --> Pendiente
        Pendiente --> Asignado: se asigna repartidor
        Asignado --> EnCamino: el repartidor sale
        EnCamino --> Entregado: el repartidor entrega
        Pendiente --> Cancelado
        Asignado --> Cancelado
        EnCamino --> Cancelado
        EnCamino: En camino
    }
```

```mermaid
stateDiagram-v2
    direction LR
    state "Entrega" as E {
        [*] --> Asignada: al asignar el pedido
        Asignada --> EnCamino
        EnCamino --> Llegando: dispara el aviso de llegada
        Llegando --> Entregada: registra fecha y hora real
        EnCamino: En camino
    }
```

Reglas principales:

- La entrega se crea al asignar el repartidor y se puede reasignar mientras siga en *Asignada*.
- El estado del pedido se deriva del de la entrega: el encargado no lo cambia a mano.
- Sólo se editan pedidos *Pendientes*, y sólo se eliminan los *Pendientes* o *Cancelados*.
- Un pedido *Entregado* no se puede cancelar. Cancelar devuelve el stock.

## Decisiones respecto del diseño del TP1

- **Entrega–Repartidor**: el repartidor queda vinculado a la Entrega (relación *Efectúa* del DER). Asignar un pedido genera su entrega.
- **Zona del pedido**: se agregó el atributo `zona` al Pedido para cumplir el criterio de la HU-02 (asignar según zonas).
- **Notificación**: es una entidad nueva que persiste el flujo *Notificación al cliente* del proceso 4 del DFD.
- **Código de seguimiento**: el cliente consulta su pedido con un código aleatorio, sin exponer ids ni datos de otros clientes.
- **Aviso de llegada sin GPS**: la cercanía la informa el repartidor marcando la entrega como *Llegando*.
- **Usuario**: es una entidad nueva para el inicio de sesión. Guarda el email, la contraseña (con bcrypt) y el rol, y se vincula con un repartidor o un cliente del DER. Así las personas del modelo original no cambian.

## Versionado

| Release | Contenido |
|---|---|
| [`v1.0-api`](https://github.com/valenayelen17/Dely/releases/tag/v1.0-api) | API completa: ABM, pedidos con stock, asignación, recorrido, notificaciones y seguimiento |
| [`v2.0`](https://github.com/valenayelen17/Dely/releases/tag/v2.0) | Monorepo (`backend/` + `frontend/`), interfaz web para los tres roles y CI |

El trabajo se integra a `main` mediante ramas `feature/*` y pull requests. El archivo `.sql`, el entorno virtual y el `.env` no se suben al repositorio (ver `.gitignore`).
