# DELY — Frontend

React + TypeScript + Vite. Consume la API de `backend/`.

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
