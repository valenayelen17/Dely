import type { Seguimiento } from '../api/tipos'

// Etapas que ve el cliente: combina el estado del pedido con el de la entrega (Llegando).
export type Etapa = 'Recibido' | 'Asignado' | 'En camino' | 'Llegando' | 'Entregado' | 'Cancelado'

export const PASOS_CLIENTE = ['Recibido', 'Asignado', 'En camino', 'Llegando', 'Entregado']

export function etapaDe(s: Seguimiento): Etapa {
  if (s.estado === 'Cancelado') return 'Cancelado'
  if (s.estado === 'Entregado') return 'Entregado'
  if (s.estado_entrega === 'Llegando') return 'Llegando'
  if (s.estado === 'En camino') return 'En camino'
  if (s.estado === 'Asignado') return 'Asignado'
  return 'Recibido'
}

export const TITULO_ETAPA: Record<Etapa, string> = {
  Recibido: 'Recibimos tu pedido',
  Asignado: 'Tu pedido ya tiene repartidor',
  'En camino': 'Tu pedido está en camino',
  Llegando: 'Tu pedido está llegando',
  Entregado: 'Tu pedido fue entregado',
  Cancelado: 'Tu pedido fue cancelado',
}

export const indicePaso = (etapa: Etapa) => (etapa === 'Entregado' ? PASOS_CLIENTE.length : PASOS_CLIENTE.indexOf(etapa))

export const esActivo = (s: Seguimiento) => s.estado !== 'Entregado' && s.estado !== 'Cancelado'
