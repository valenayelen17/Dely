import { pedirApi } from './cliente'
import type {
  Cliente,
  Comercio,
  DatosCliente,
  DatosPedido,
  DatosProducto,
  DatosRepartidor,
  EntregaDetalle,
  EstadoEntrega,
  Notificacion,
  Pedido,
  Producto,
  Repartidor,
  Seguimiento,
} from './tipos'

function query(params: Record<string, string | number | boolean | undefined>): string {
  const pares = Object.entries(params).filter(([, valor]) => valor !== undefined && valor !== '')
  return pares.length ? `?${new URLSearchParams(pares.map(([k, v]) => [k, String(v)]))}` : ''
}

const enviar = (method: string, body?: unknown): RequestInit => ({
  method,
  body: body === undefined ? undefined : JSON.stringify(body),
})

export const api = {
  comercios: () => pedirApi<Comercio[]>('/api/comercios/'),

  clientes: () => pedirApi<Cliente[]>('/api/clientes/?limit=500'),
  crearCliente: (datos: DatosCliente) => pedirApi<Cliente>('/api/clientes/', enviar('POST', datos)),
  editarCliente: (id: number, datos: DatosCliente) => pedirApi<Cliente>(`/api/clientes/${id}`, enviar('PUT', datos)),

  repartidores: (filtros: { comercio_id?: number; zona?: string; disponible?: boolean } = {}) =>
    pedirApi<Repartidor[]>(`/api/repartidores/${query({ ...filtros, limit: 500 })}`),
  repartidor: (id: number) => pedirApi<Repartidor>(`/api/repartidores/${id}`),
  crearRepartidor: (datos: DatosRepartidor) => pedirApi<Repartidor>('/api/repartidores/', enviar('POST', datos)),
  editarRepartidor: (id: number, datos: DatosRepartidor) =>
    pedirApi<Repartidor>(`/api/repartidores/${id}`, enviar('PUT', datos)),
  cambiarDisponibilidad: (id: number, disponible: boolean) =>
    pedirApi<Repartidor>(`/api/repartidores/${id}/disponibilidad`, enviar('PATCH', { disponible })),
  entregasDeRepartidor: (id: number, activas = true) =>
    pedirApi<EntregaDetalle[]>(`/api/repartidores/${id}/entregas${query({ activas })}`),

  productos: (comercio_id?: number) => pedirApi<Producto[]>(`/api/productos/${query({ comercio_id, limit: 500 })}`),
  crearProducto: (datos: DatosProducto) => pedirApi<Producto>('/api/productos/', enviar('POST', datos)),
  editarProducto: (id: number, datos: DatosProducto) => pedirApi<Producto>(`/api/productos/${id}`, enviar('PUT', datos)),

  pedidos: (comercio_id?: number) => pedirApi<Pedido[]>(`/api/pedidos/${query({ comercio_id, limit: 500 })}`),
  pendientes: (comercio_id?: number) => pedirApi<Pedido[]>(`/api/pedidos/pendientes${query({ comercio_id })}`),
  pedido: (id: number) => pedirApi<Pedido>(`/api/pedidos/${id}`),
  crearPedido: (datos: DatosPedido) => pedirApi<Pedido>('/api/pedidos/', enviar('POST', datos)),
  editarPedido: (id: number, datos: Pick<Pedido, 'direccion_entrega' | 'zona' | 'horario_estimado'>) =>
    pedirApi<Pedido>(`/api/pedidos/${id}`, enviar('PUT', datos)),
  asignar: (id: number, repartidor_id: number) =>
    pedirApi<Pedido>(`/api/pedidos/${id}/asignar`, enviar('PATCH', { repartidor_id })),
  cancelar: (id: number) => pedirApi<Pedido>(`/api/pedidos/${id}/cancelar`, enviar('PATCH')),
  notificaciones: (id: number) => pedirApi<Notificacion[]>(`/api/pedidos/${id}/notificaciones`),

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
