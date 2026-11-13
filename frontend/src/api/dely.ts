import { pedirApi } from './cliente'
import type { EntregaDetalle, EstadoEntrega, Repartidor, RespuestaLogin, Seguimiento } from './tipos'

const enviar = (method: string, body?: unknown): RequestInit => ({
  method,
  body: body === undefined ? undefined : JSON.stringify(body),
})

// Endpoints que usan las vistas del repartidor y del cliente.
// La API controla con el JWT que cada uno vea sólo lo suyo.
export const api = {
  login: (email: string, password: string) => pedirApi<RespuestaLogin>('/api/auth/login', enviar('POST', { email, password })),

  // Repartidor
  repartidor: (id: number) => pedirApi<Repartidor>(`/api/repartidores/${id}`),
  entregasDeRepartidor: (id: number, activas: boolean) =>
    pedirApi<EntregaDetalle[]>(`/api/repartidores/${id}/entregas?activas=${activas}`),
  entrega: (id: number) => pedirApi<EntregaDetalle>(`/api/entregas/${id}`),
  cambiarEstadoEntrega: (id: number, estado: EstadoEntrega, ubicacion_actual?: string) =>
    pedirApi<EntregaDetalle>(`/api/entregas/${id}/estado`, enviar('PATCH', { estado, ubicacion_actual })),
  informarUbicacion: (id: number, ubicacion_actual: string) =>
    pedirApi<EntregaDetalle>(`/api/entregas/${id}/ubicacion`, enviar('PATCH', { ubicacion_actual })),

  // Cliente
  misPedidos: () => pedirApi<Seguimiento[]>('/api/seguimiento/'),
  seguimiento: (codigo: string) => pedirApi<Seguimiento>(`/api/seguimiento/${encodeURIComponent(codigo)}`),
  marcarLeidas: (codigo: string) =>
    pedirApi<Seguimiento>(`/api/seguimiento/${encodeURIComponent(codigo)}/notificaciones/leidas`, enviar('PATCH')),
}
