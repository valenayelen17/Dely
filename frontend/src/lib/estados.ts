import type { EstadoEntrega, EstadoPedido } from '../api/tipos'
import type { NombreIcono } from '../components/Icono'

type Estado = EstadoPedido | EstadoEntrega

const VISUAL: Record<Estado, { clase: string; icono: NombreIcono }> = {
  Pendiente: { clase: 'badge-pendiente', icono: 'reloj' },
  Asignado: { clase: 'badge-asignado', icono: 'persona-check' },
  Asignada: { clase: 'badge-asignado', icono: 'persona-check' },
  'En camino': { clase: 'badge-camino', icono: 'camion' },
  Llegando: { clase: 'badge-llegando', icono: 'pin' },
  Entregado: { clase: 'badge-entregado', icono: 'check-circulo' },
  Entregada: { clase: 'badge-entregado', icono: 'check-circulo' },
  Cancelado: { clase: 'badge-cancelado', icono: 'x-circulo' },
  Cancelada: { clase: 'badge-cancelado', icono: 'x-circulo' },
}

export const visualEstado = (estado: Estado) => VISUAL[estado]

export const TITULO_NOTIFICACION: Record<string, string> = {
  Recibido: 'Pedido recibido',
  Asignada: 'Repartidor asignado',
  'En camino': 'En camino',
  Llegando: 'Está llegando',
  Entregada: 'Pedido entregado',
  Cancelada: 'Pedido cancelado',
}

export const SIGUIENTE_ENTREGA: Partial<Record<EstadoEntrega, EstadoEntrega>> = {
  Asignada: 'En camino',
  'En camino': 'Llegando',
  Llegando: 'Entregada',
}
