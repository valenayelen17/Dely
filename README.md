# DELY

Sistema de gestión de entregas de última milla para comercios con repartidores propios. Centraliza los pedidos, los asigna a repartidores por zona, sigue el recorrido de cada entrega y le avisa al cliente en qué estado está su pedido.

Trabajo práctico de Análisis y Metodologías de Sistemas. Integrantes: Marco Passador y Valentina Ayelén De Jesús.

## Estructura del repositorio

```
Dely/
├── backend/    API REST (FastAPI + SQLAlchemy + MySQL)
├── frontend/   Interfaz web (React + TypeScript + Vite)
└── .github/    CI: tests del backend, lint y build del frontend
```

## Tecnologías

| Parte | Stack |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy 2, MySQL, Pydantic, pytest |
| Frontend | React, TypeScript, Vite |

## Cómo ejecutarlo

Se necesitan dos terminales:

```powershell
# 1. Backend: http://127.0.0.1:8000 (documentación en /docs)
cd backend
.\.venv\Scripts\python.exe -m uvicorn api:app --reload

# 2. Frontend: http://localhost:5173
cd frontend
npm run dev
```

Para la demo conviene abrir tres ventanas: <http://localhost:5173/comercio>, <http://localhost:5173/repartidor> y <http://localhost:5173/seguimiento>.

La preparación inicial (entorno virtual, `.env`, datos de demo y tests) está en [backend/README.md](backend/README.md) y [frontend/README.md](frontend/README.md).

## Historias de usuario

| HU | Historia | Cómo se resuelve |
|---|---|---|
| HU-01 | Como encargado quiero ver los pedidos no entregados | `GET /api/pedidos/pendientes`, con cliente, productos, total y repartidor |
| HU-02 | Como encargado quiero asignar cada pedido a un repartidor disponible | `GET /api/repartidores/?zona=&disponible=true` y `PATCH /api/pedidos/{id}/asignar` |
| HU-03 | Como cliente quiero saber en qué estado está mi pedido | `GET /api/seguimiento/{codigo}`, con estado y horario estimado |
| HU-04 | Como repartidor quiero actualizar el estado de mi entrega | `GET /api/repartidores/{id}/entregas` y `PATCH /api/entregas/{id}/estado` |
| HU-05 | Como cliente quiero un aviso cuando el repartidor esté llegando | Notificación automática cuando la entrega pasa a **Llegando** |

## Decisiones respecto del diseño del TP1

- **Entrega–Repartidor**: el repartidor queda vinculado a la Entrega (relación *Efectúa* del DER). Asignar un pedido genera su entrega.
- **Zona del pedido**: se agregó el atributo `zona` al Pedido para cumplir el criterio de la HU-02 (asignar según zonas).
- **Notificación**: es una entidad nueva que persiste el flujo *Notificación al cliente* del proceso 4 del DFD.
- **Código de seguimiento**: el cliente consulta su pedido con un código aleatorio, sin exponer ids ni datos de otros clientes.
- **Aviso de llegada sin GPS**: la cercanía la informa el repartidor marcando la entrega como *Llegando*.
