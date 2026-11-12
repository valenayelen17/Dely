# DELY — Frontend

React + TypeScript + Vite. Vistas mobile del **repartidor** y del **cliente**, que consumen la API de `backend/`. Usa una paleta verde azulado y la fuente Inter.

Es una aplicación independiente del panel del encargado (`web/`): no hay links entre una y otra, y las dos se comunican sólo a través de la API.

## Vistas

| Rol | Ruta | Pantallas |
|---|---|---|
| Inicio | `/` | Selector de rol: repartidor o cliente |
| Repartidor | `/repartidor` | ¿Quién sos?, mis entregas, detalle de la entrega (HU-04) |
| Cliente | `/seguimiento` | Ingreso del código y seguimiento con aviso de llegada (HU-03, HU-05) |

No hay login: cada rol entra desde el inicio. Las pantallas de entregas y seguimiento se refrescan cada 5 segundos, así que los cambios que hace el encargado se ven en vivo.

## Estructura

| Carpeta | Contenido |
|---|---|
| `src/api` | Cliente HTTP, tipos de la API y una función por endpoint |
| `src/hooks` | `useApi` (carga con refresco) y toasts |
| `src/components` | Componentes compartidos: badge de estado, pasos, iconos, toasts |
| `src/lib` | Formatos y estados |
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

Para apuntar a otra URL de la API, definí `VITE_API_URL` en `frontend/.env.local`.

## Scripts

| Comando | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo |
| `npm run build` | Chequeo de tipos y build de producción en `dist/` |
| `npm run lint` | Linter (oxlint) |
| `npm run preview` | Sirve el build de producción |
