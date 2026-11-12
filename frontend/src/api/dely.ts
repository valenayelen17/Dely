import { pedirApi } from './cliente'
import type { Comercio, EntregaDetalle, EstadoEntrega, Repartidor, Seguimiento } from './tipos'

function query(params: Record<string, string | number | boolean | undefined>): string {
  const pares = Object.entries(params).filter(([, valor]) => valor !== undefined && valor !== '')
  return pares.length ? `?${new URLSearchParams(pares.map(([k, v]) => [k, String(v)]))}` : ''
}

const enviar = (method: string, body?: unknown): RequestInit => ({
  method,
  body: body === undefined ? undefined : JSON.stringify(body),
})

// Endpoints que usan las vistas del repartidor y del cliente.
export const api = {
  comercios: () => pedirApi<Comercio[]>('/api/comercios/'),

  repartidores: (filtros: { comercio_id?: number; zona?: string; disponible?: boolean } = {}) =>
    pedirApi<Repartidor[]>(`/api/repartidores/${query({ ...filtros, limit: 500 })}`),
  repartidor: (id: number) => pedirApi<Repartidor>(`/api/repartidores/${id}`),
  entregasDeRepartidor: (id: number, activas = true) =>
    pedirApi<EntregaDetalle[]>(`/api/repartidores/${id}/entregas${query({ activas })}`),

  entregasActivas: () =>
    pedirApi<EntregaDetalle[]>('/api/entregas/?limit=500').then((entregas) =>
      entregas.filter((e) => ['Asignada', 'En camino', 'Llegando'].includes(e.estado)),
    ),
  entrega: (id: number) => pedirApi<EntregaDetalle>(`/api/entregas/${id}`),
  cambiarEstadoEntrega: (id: number, estado: EstadoEntrega, ubicacion_actual?: string) =>
    pedirApi<EntregaDetalle>(`/api/entregas/${id}/estado`, enviar('PATCH', { estado, ubicacion_actual })),
  informarUbicacion: (id: number, ubicacion_actual: string) =>
    pedirApi<EntregaDetalle>(`/api/entregas/${id}/ubicacion`, enviar('PATCH', { ubicacion_actual })),

  seguimiento: (codigo: string) => pedirApi<Seguimiento>(`/api/seguimiento/${encodeURIComponent(codigo)}`),
  marcarLeidas: (codigo: string) =>
    pedirApi<Seguimiento>(`/api/seguimiento/${encodeURIComponent(codigo)}/notificaciones/leidas`, enviar('PATCH')),
}
