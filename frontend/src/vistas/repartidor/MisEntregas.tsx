import { useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { api } from '../../api/dely'
import type { EntregaDetalle } from '../../api/tipos'
import { BadgeEstado } from '../../components/BadgeEstado'
import { ErrorCarga, Esqueleto, EstadoVacio } from '../../components/Estados'
import { Icono } from '../../components/Icono'
import { Encabezado, Indicador, Layout } from '../../components/Layout'
import { useApi } from '../../hooks/useApi'
import { useSesion } from '../../hooks/useSesion'
import { hora, moneda, nombreCompleto } from '../../lib/formato'

const ACTIVAS = ['Asignada', 'En camino', 'Llegando']

function TarjetaEntrega({ entrega, proxima }: { entrega: EntregaDetalle; proxima: boolean }) {
  const { pedido } = entrega
  const destino = `/entregas/${entrega.id_entrega}`
  return (
    <article className={`dcard${proxima ? ' is-next' : ''}`}>
      <div className="between">
        <BadgeEstado estado={entrega.estado} />
        {proxima && <span className="tag tag-alert">Próxima</span>}
        <span className="row" style={{ gap: 6, fontWeight: 800, fontSize: 20, marginLeft: 'auto' }}>
          <Icono nombre="reloj" tamano="lg" />
          {hora(pedido.horario_estimado)}
        </span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <Link to={destino} style={{ color: 'var(--c-ink)', textDecoration: 'none', fontSize: 21, fontWeight: 800, lineHeight: 1.25 }}>
          {pedido.direccion_entrega}
        </Link>
        <span className="row muted" style={{ gap: 8, fontSize: 14 }}>
          <span className="tag tag-zone">{pedido.zona}</span>
          <span className="code" style={{ fontSize: 12 }}>{pedido.codigo_seguimiento}</span>
        </span>
      </div>
      <div className="between" style={{ fontSize: 15 }}>
        <span className="row" style={{ gap: 6 }}><Icono nombre="persona" />{nombreCompleto(pedido.cliente)}</span>
        <span className="muted">{pedido.cliente.telefono}</span>
      </div>
      <span className="muted" style={{ fontSize: 14 }}>
        {pedido.detalles.map((d) => `${d.cantidad} × ${d.producto_nombre}`).join(' · ')}
      </span>
      <hr className="divider" />
      <div className="between">
        <span style={{ display: 'flex', flexDirection: 'column' }}>
          <span className="muted" style={{ fontSize: 13 }}>A cobrar</span>
          <b style={{ fontSize: 22 }}>{moneda(pedido.total)}</b>
        </span>
        <Link className={`btn ${proxima ? 'btn-primary' : 'btn-secondary'}`} to={destino}>
          Ver entrega
          <Icono nombre="adelante" />
        </Link>
      </div>
    </article>
  )
}

function TablaHistorial({ entregas }: { entregas: EntregaDetalle[] }) {
  const navegar = useNavigate()
  if (entregas.length === 0) {
    return <EstadoVacio icono="historial" titulo="Todavía no cerraste entregas">Las entregas terminadas aparecen acá.</EstadoVacio>
  }
  return (
    <div className="table-box">
      <table className="table">
        <thead>
          <tr><th>Código</th><th>Dirección</th><th>Cliente</th><th>Zona</th><th>Entregada</th><th className="r">Total</th><th>Estado</th></tr>
        </thead>
        <tbody>
          {entregas.map((e) => (
            <tr key={e.id_entrega} className="fila-clic" onClick={() => navegar(`/entregas/${e.id_entrega}`)}>
              <td><span className="code">{e.pedido.codigo_seguimiento}</span></td>
              <td>{e.pedido.direccion_entrega}</td>
              <td>{nombreCompleto(e.pedido.cliente)}</td>
              <td><span className="tag tag-zone">{e.pedido.zona}</span></td>
              <td>{e.fecha_entrega ? `${e.fecha_entrega} ${hora(e.hora_entrega)}` : '—'}</td>
              <td className="r">{moneda(e.pedido.total)}</td>
              <td><BadgeEstado estado={e.estado} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function MisEntregas() {
  const { usuario } = useSesion()
  const repartidorId = usuario?.repartidor_id ?? 0
  const [pestana, setPestana] = useState<'activas' | 'historial'>('activas')
  const repartidor = useApi(() => api.repartidor(repartidorId), `r-${repartidorId}`)
  const entregas = useApi(() => api.entregasDeRepartidor(repartidorId, false), `e-${repartidorId}`, 5000)

  const todas = entregas.datos ?? []
  const activas = todas.filter((e) => ACTIVAS.includes(e.estado))
  const cerradas = todas.filter((e) => !ACTIVAS.includes(e.estado)).reverse()
  const entregadas = cerradas.filter((e) => e.estado === 'Entregada')
  const aCobrar = activas.reduce((total, e) => total + Number(e.pedido.total), 0)
  const r = repartidor.datos

  return (
    <Layout>
      <Encabezado
        titulo={`Hola${r ? `, ${r.nombre}` : ''}`}
        bajada={r ? `Zona ${r.zona} · ${r.disponible ? 'en turno' : 'fuera de turno'}` : 'Tus entregas del turno'}
      />

      <div className="stats">
        <Indicador etiqueta="Entregas activas" valor={activas.length} icono="camion" tono="marca" />
        <Indicador etiqueta="En recorrido" valor={activas.filter((e) => e.estado !== 'Asignada').length} icono="pin" tono="alerta" />
        <Indicador etiqueta="Entregadas" valor={entregadas.length} icono="check-circulo" tono="ok" />
        <Indicador etiqueta="A cobrar en activas" valor={moneda(aCobrar)} icono="caja" />
      </div>

      <div className="tabs" role="tablist">
        <button className="tab" role="tab" aria-selected={pestana === 'activas'} onClick={() => setPestana('activas')}>
          Activas <span className="cuenta">{activas.length}</span>
        </button>
        <button className="tab" role="tab" aria-selected={pestana === 'historial'} onClick={() => setPestana('historial')}>
          Historial <span className="cuenta">{cerradas.length}</span>
        </button>
      </div>

      {(repartidor.error ?? entregas.error) && <ErrorCarga error={(repartidor.error ?? entregas.error)!} reintentar={entregas.recargar} />}

      {entregas.cargando ? (
        <div className="grilla-tarjetas"><Esqueleto filas={1} alto={300} /><Esqueleto filas={1} alto={300} /></div>
      ) : pestana === 'activas' ? (
        activas.length === 0 ? (
          <EstadoVacio icono="camion" titulo="No tenés entregas asignadas">Cuando el comercio te asigne un pedido, aparece acá.</EstadoVacio>
        ) : (
          <div className="grilla-tarjetas">
            {activas.map((e, i) => <TarjetaEntrega key={e.id_entrega} entrega={e} proxima={i === 0} />)}
          </div>
        )
      ) : (
        <TablaHistorial entregas={cerradas} />
      )}
    </Layout>
  )
}
