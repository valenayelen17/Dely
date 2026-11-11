import type { EstadoEntrega, EstadoPedido } from '../api/tipos'
import { visualEstado } from '../lib/estados'
import { Icono } from './Icono'

interface Props {
  estado: EstadoPedido | EstadoEntrega
  grande?: boolean
  id?: string
}

export function BadgeEstado({ estado, grande = false, id }: Props) {
  const { clase, icono } = visualEstado(estado)
  return (
    <span id={id} className={`badge ${clase}${grande ? ' badge-lg' : ''}`}>
      <Icono nombre={icono} />
      {estado}
    </span>
  )
}
