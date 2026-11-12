# DELY — Frontend

React + TypeScript + Vite. Vistas mobile del **repartidor** y del **cliente**, que consumen la API de `backend/`. Usa una paleta verde azulado y la fuente Inter.

La gestión del comercio (pedidos, asignación, repartidores, productos, clientes e historial) está en el **panel Django** de [`web/`](../web/README.md).

## Vistas

| Rol | Ruta | Pantallas |
|---|---|---|
| Inicio | `/` | Selector de rol. *Comercio* abre el panel Django |
| Repartidor | `/repartidor` | ¿Quién sos?, mis entregas, detalle de la entrega (HU-04) |
| Cliente | `/seguimiento` | Ingreso del código y seguimiento con aviso de llegada (HU-03, HU-05) |

No hay login: cada rol entra desde el inicio. Las pantallas de entregas y seguimiento se refrescan cada 5 segundos, así que los cambios que hace el encargado en el panel se ven en vivo. Los links viejos a `/comercio` redirigen al panel.

## Estructura

| Carpeta | Contenido |
|---|---|
| `src/api` | Cliente HTTP, tipos de la API y una función por endpoint |
| `src/hooks` | `useApi` (carga con refresco) y toasts |
| `src/components` | Componentes compartidos: badge de estado, pasos, iconos, toasts |
| `src/lib` | Formatos, estados y la URL del panel Django |
| `src/vistas` | Una carpeta por rol: `repartidor` y `cliente` |
| `src/styles` | Tokens y estilos del diseño (`dely.css`) y ajustes de la app (`app.css`) |

## Ejecutar

Desde `frontend/`, con el backend corriendo en el puerto 8000:

```powershell
cd frontend
npm install
npm run dev
```

Abrí <http://localhost:5173>. En desarrollo, Vite redirige `/api` al backend (ver `vite.config.ts`), así que no hace falta configurar nada más.

Para apuntar a otra URL de la API, definí `VITE_API_URL` en `frontend/.env.local`. Si el panel Django no corre en `http://127.0.0.1:8001`, definí `VITE_PANEL_URL`.

## Scripts

| Comando | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo |
| `npm run build` | Chequeo de tipos y build de producción en `dist/` |
| `npm run lint` | Linter (oxlint) |
| `npm run preview` | Sirve el build de producción |
