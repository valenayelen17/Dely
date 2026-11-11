# DELY — Frontend

React + TypeScript + Vite. Consume la API de `backend/`. Usa una paleta verde azulado y la fuente Inter.

## Vistas

| Rol | Ruta | Pantallas |
|---|---|---|
| Inicio | `/` | Selector de rol |
| Encargado | `/comercio` | Pedidos pendientes (HU-01), detalle y asignación (HU-02), nuevo pedido, repartidores, productos, clientes, historial |
| Repartidor | `/repartidor` | ¿Quién sos?, mis entregas, detalle de la entrega (HU-04) |
| Cliente | `/seguimiento` | Ingreso del código y seguimiento con aviso de llegada (HU-03, HU-05) |

No hay login: cada rol entra desde el inicio. Las pantallas de pedidos, entregas y seguimiento se refrescan cada 5 segundos, así que con tres ventanas abiertas (comercio, repartidor y cliente) los cambios se ven en vivo.

## Estructura

| Carpeta | Contenido |
|---|---|
| `src/api` | Cliente HTTP, tipos de la API y una función por endpoint |
| `src/hooks` | `useApi` (carga con refresco), toasts y contexto del comercio |
| `src/components` | Componentes compartidos: badge de estado, pasos, iconos, toasts |
| `src/vistas` | Una carpeta por rol: `encargado`, `repartidor`, `cliente` |
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
