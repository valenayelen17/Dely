import { Link, useNavigate } from 'react-router'
import { api } from '../../api/dely'
import type { Seguimiento } from '../../api/tipos'
import { BadgeEstado } from '../../components/BadgeEstado'
import { ErrorCarga, Esqueleto, EstadoVacio } from '../../components/Estados'
import { Icono } from '../../components/Icono'
import { Encabezado, Indicador, Layout } from '../../components/Layout'
import { Pasos } from '../../components/Pasos'
import { useApi } from '../../hooks/useApi'
import { useSesion } from '../../hooks/useSesion'
import { hora, moneda } from '../../lib/formato'
import { PASOS_CLIENTE, TITULO_ETAPA, esActivo, etapaDe, indicePaso } from '../../lib/seguimiento'

function TarjetaPedido({ pedido }: { pedido: Seguimiento }) {
  const etapa = etapaDe(pedido)
  const destino = `/pedidos/${pedido.codigo_seguimiento}`
  const sinLeer = pedido.notificaciones.filter((n) => !n.leida).length
  return (
    <article className={`dcard${etapa === 'Llegando' ? ' is-next' : ''}`}>
      <div className="between">
        <BadgeEstado estado={etapa === 'Llegando' ? 'Llegando' : pedido.estado} />
        <span className="code muted" style={{ fontSize: 12 }}>{pedido.codigo_seguimiento}</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <Link to={destino} style={{ color: 'var(--c-ink)', textDecoration: 'none', fontSize: 21, fontWeight: 800, lineHeight: 1.25 }}>
          {TITULO_ETAPA[etapa]}
        </Link>
        <span className="muted" style={{ fontSize: 14 }}>{pedido.comercio} · {pedido.direccion_entrega}</span>
      </div>
      <Pasos etiquetas={PASOS_CLIENTE} actual={indicePaso(etapa)} indiceLlegando={3} etiquetaAccesible={`Estado del pedido ${pedido.codigo_seguimiento}`} />
      <hr className="divider" />
      <div className="between">
        <span style={{ display: 'flex', flexDirection: 'column' }}>
          <span className="muted" style={{ fontSize: 13 }}>Llega aprox.</span>
          <b style={{ fontSize: 22 }}>{hora(pedido.horario_estimado)}</b>
        </span>
        <Link className={`btn ${etapa === 'Llegando' ? 'btn-primary' : 'btn-secondary'}`} to={destino}>
          {sinLeer > 0 && <span className="tag tag-alert">{sinLeer} nueva{sinLeer > 1 ? 's' : ''}</span>}
          Ver seguimiento
          <Icono nombre="adelante" />
        </Link>
      </div>
    </article>
  )
}

export function MisPedidos() {
  const { usuario } = useSesion()
  const navegar = useNavigate()
  const pedidos = useApi(() => api.misPedidos(), 'mis-pedidos', 5000)
  const lista = pedidos.datos ?? []
  const activos = lista.filter(esActivo)
  const anteriores = lista.filter((p) => !esActivo(p))
  const gastado = anteriores.filter((p) => p.estado === 'Entregado').reduce((t, p) => t + Number(p.total), 0)

  return (
    <Layout>
      <Encabezado titulo={`Hola, ${usuario?.nombre.split(' ')[0] ?? ''}`} bajada="Seguí tus pedidos en vivo. La pantalla se actualiza sola." />

      <div className="stats">
        <Indicador etiqueta="Pedidos en curso" valor={activos.length} icono="camion" tono="marca" />
        <Indicador etiqueta="Llegando ahora" valor={activos.filter((p) => etapaDe(p) === 'Llegando').length} icono="pin" tono="alerta" />
        <Indicador etiqueta="Pedidos recibidos" valor={anteriores.filter((p) => p.estado === 'Entregado').length} icono="check-circulo" tono="ok" />
        <Indicador etiqueta="Total en pedidos recibidos" valor={moneda(gastado)} icono="caja" />
      </div>

      {pedidos.error && <ErrorCarga error={pedidos.error} reintentar={pedidos.recargar} />}

      <h2 className="seccion-titulo">En curso</h2>
      {pedidos.cargando ? (
        <div className="grilla-tarjetas"><Esqueleto filas={1} alto={280} /><Esqueleto filas={1} alto={280} /></div>
      ) : activos.length === 0 ? (
        <EstadoVacio icono="caja" titulo="No tenés pedidos en curso">Cuando hagas un pedido al comercio, lo vas a ver acá.</EstadoVacio>
      ) : (
        <div className="grilla-tarjetas">{activos.map((p) => <TarjetaPedido key={p.codigo_seguimiento} pedido={p} />)}</div>
      )}

      {anteriores.length > 0 && (
        <>
          <h2 className="seccion-titulo">Anteriores</h2>
          <div className="table-box">
            <table className="table">
              <thead>
                <tr><th>Código</th><th>Fecha</th><th>Comercio</th><th>Productos</th><th>Entregado</th><th className="r">Total</th><th>Estado</th></tr>
              </thead>
              <tbody>
                {anteriores.map((p) => (
                  <tr key={p.codigo_seguimiento} className="fila-clic" onClick={() => navegar(`/pedidos/${p.codigo_seguimiento}`)}>
                    <td><span className="code">{p.codigo_seguimiento}</span></td>
                    <td>{p.fecha_pedido}</td>
                    <td>{p.comercio}</td>
                    <td className="muted">{p.productos.map((x) => `${x.cantidad} × ${x.nombre}`).join(' · ')}</td>
                    <td>{p.hora_entrega ? hora(p.hora_entrega) : '—'}</td>
                    <td className="r">{moneda(p.total)}</td>
                    <td><BadgeEstado estado={p.estado} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </Layout>
  )
}
