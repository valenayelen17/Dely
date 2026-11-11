import { Link, useParams } from 'react-router'
import { api } from '../../api/dely'
import type { EntregaDetalle } from '../../api/tipos'
import { BadgeEstado } from '../../components/BadgeEstado'
import { ErrorCarga, Esqueleto, EstadoVacio } from '../../components/Estados'
import { Icono } from '../../components/Icono'
import { useApi } from '../../hooks/useApi'
import { hora, iniciales, moneda, nombreCompleto } from '../../lib/formato'

function TarjetaEntrega({ entrega, repartidorId, proxima }: { entrega: EntregaDetalle; repartidorId: number; proxima: boolean }) {
  const { pedido } = entrega
  const destino = `/repartidor/${repartidorId}/entregas/${entrega.id_entrega}`
  return (
    <article className={`dcard${proxima ? ' is-next' : ''}`}>
      <div className="between">
        <BadgeEstado estado={entrega.estado} />
        <span className="row" style={{ gap: 4, fontWeight: 800, fontSize: 20 }}>
          <Icono nombre="reloj" tamano="lg" />
          {hora(pedido.horario_estimado)}
        </span>
      </div>
      <Link to={destino} style={{ color: 'var(--c-ink)', textDecoration: 'none', fontSize: 22, fontWeight: 800, lineHeight: 1.25, letterSpacing: '-0.01em' }}>
        {pedido.direccion_entrega}
      </Link>
      <div className="between">
        <span style={{ fontWeight: 600 }}>{nombreCompleto(pedido.cliente)}</span>
        <a className="btn btn-secondary" href={`tel:${pedido.cliente.telefono}`} style={{ minHeight: 48 }}>
          <Icono nombre="telefono" />
          Llamar
        </a>
      </div>
      <span className="muted" style={{ fontSize: 14 }}>
        {pedido.detalles.map((d) => `${d.cantidad} ${d.producto_nombre}`).join(' · ')}
      </span>
      <hr className="divider" />
      <div className="between">
        <span className="muted" style={{ fontSize: 14 }}>A cobrar</span>
        <b style={{ fontSize: 22 }}>{moneda(pedido.total)}</b>
      </div>
      <Link className={`btn ${proxima ? 'btn-primary' : 'btn-secondary'} btn-lg`} to={destino} style={{ width: '100%', minHeight: 52 }}>
        Ver entrega
      </Link>
    </article>
  )
}

export function MisEntregas() {
  const repartidorId = Number(useParams().repartidorId)
  const repartidor = useApi(() => api.repartidor(repartidorId), `r-${repartidorId}`)
  const entregas = useApi(() => api.entregasDeRepartidor(repartidorId), `e-${repartidorId}`, 5000)
  const r = repartidor.datos
  const lista = entregas.datos ?? []

  return (
    <div className="dely phone">
      <div className="topbar" style={{ justifyContent: 'space-between' }}>
        <span className="row" style={{ gap: 10 }}>
          <span className="avatar">{r ? iniciales(r) : '··'}</span>
          <span style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.3 }}>
            <b>Hola{r ? `, ${r.nombre}` : ''}</b>
            {r && <span className="muted" style={{ fontSize: 13 }}>{r.zona} · {r.disponible ? 'en turno' : 'fuera de turno'}</span>}
          </span>
        </span>
        <Link className="btn btn-ghost btn-sm" to="/repartidor" style={{ minHeight: 44 }}>
          No soy {r?.nombre ?? 'yo'}
        </Link>
      </div>
      <div className="m-body">
        <div className="between">
          <h1 style={{ fontSize: 24, fontWeight: 700 }}>Mis entregas</h1>
          <span className="tag tag-zone" style={{ height: 26 }}>{lista.length} {lista.length === 1 ? 'activa' : 'activas'}</span>
        </div>
        {(repartidor.error ?? entregas.error) && <ErrorCarga error={(repartidor.error ?? entregas.error)!} reintentar={entregas.recargar} />}
        {entregas.cargando ? (
          <Esqueleto filas={2} alto={260} />
        ) : lista.length === 0 ? (
          <EstadoVacio icono="camion" titulo="No tenés entregas asignadas">
            Cuando el comercio te asigne un pedido, aparece acá.
          </EstadoVacio>
        ) : (
          lista.map((e, i) => <TarjetaEntrega key={e.id_entrega} entrega={e} repartidorId={repartidorId} proxima={i === 0} />)
        )}
      </div>
    </div>
  )
}
