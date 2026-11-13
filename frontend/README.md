# DELY — Frontend

React + TypeScript + Vite. Aplicación de escritorio del **repartidor** y del **cliente**, que consume la API de `backend/` con un JWT. Usa una paleta verde azulado y la fuente Inter.

Es una aplicación independiente del panel del encargado (`web/`): no hay links entre una y otra, y las dos se comunican sólo a través de la API.

## Vistas

| Rol | Ruta | Pantallas |
|---|---|---|
| Todos | `/login` | Inicio de sesión; después lleva a la pantalla del rol |
| Repartidor | `/entregas`, `/entregas/:id` | Mis entregas (activas e historial) y detalle de la entrega (HU-04) |
| Cliente | `/pedidos`, `/pedidos/:codigo` | Mis pedidos y seguimiento con aviso de llegada (HU-03, HU-05) |

Las pantallas de entregas y pedidos se refrescan cada 5 segundos, así que los cambios que hace el encargado se ven en vivo.

## Inicio de sesión

- `POST /api/auth/login` devuelve el JWT, que se guarda en `localStorage` (`src/lib/sesion.ts`) y se manda en el header `Authorization` de cada pedido (`src/api/cliente.ts`).
- `RequiereRol` (`src/components/Sesion.tsx`) protege cada ruta: sin sesión manda al login, y con otro rol manda a la pantalla que le corresponde.
- Si la API responde 401 (token vencido), se borra la sesión y se vuelve al login con un aviso.
- Las cuentas de encargado no entran: el comercio usa el panel Django.

## Diseño

Pensado para escritorio: barra superior con la navegación y el usuario, contenido de hasta 1280 px, indicadores arriba de cada listado, tarjetas en grilla y detalles en dos columnas con el panel de acciones fijo a la derecha. En pantallas angostas las columnas se apilan.

## Estructura

| Carpeta | Contenido |
|---|---|
| `src/api` | Cliente HTTP, tipos de la API y una función por endpoint |
| `src/hooks` | `useApi` (carga con refresco), sesión y toasts |
| `src/components` | Layout de escritorio, sesión y rutas protegidas, badge de estado, pasos, iconos, toasts |
| `src/lib` | Formatos, estados, etapas del seguimiento y la sesión guardada |
| `src/vistas` | `Login` y una carpeta por rol: `repartidor` y `cliente` |
| `src/styles` | Tokens y estilos del diseño (`dely.css`) y ajustes de la app (`app.css`) |

## Ejecutar

Desde `frontend/`, con el backend corriendo en el puerto 8000:

```powershell
cd frontend
npm install
npm run dev
```

Abrí <http://localhost:5173>. En desarrollo, Vite redirige `/api` al backend (ver `vite.config.ts`), así que no hace falta configurar nada más.

Para apuntar a otra URL de la API, definí `VITE_API_URL` en `frontend/.env.local`.

## Scripts

| Comando | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo |
| `npm run build` | Chequeo de tipos y build de producción en `dist/` |
| `npm run lint` | Linter (oxlint) |
| `npm run preview` | Sirve el build de producción |
