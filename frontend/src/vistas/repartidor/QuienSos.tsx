import { Link } from 'react-router'
import { api } from '../../api/dely'
import { ErrorCarga, Esqueleto, EstadoVacio } from '../../components/Estados'
import { Icono } from '../../components/Icono'
import { Logo } from '../../components/Logo'
import { useApi } from '../../hooks/useApi'
import { iniciales, plural } from '../../lib/formato'
import { BarraSuperior } from './BarraSuperior'

export function QuienSos() {
  const datos = useApi(async () => {
    const [comercio] = await api.comercios()
    if (!comercio) return { comercio, repartidores: [], activas: [] }
    const [repartidores, activas] = await Promise.all([
      api.repartidores({ comercio_id: comercio.id_comercio }),
      api.entregasActivas(),
    ])
    return { comercio, repartidores, activas }
  }, 'quien-sos')

  const { comercio, repartidores = [], activas = [] } = datos.datos ?? {}

  return (
    <div className="dely phone">
      <BarraSuperior volverA="/" etiquetaVolver="Volver al inicio">
        <Logo tamano={18} conPunto={false} />
      </BarraSuperior>
      <div className="m-body" style={{ gap: 20, paddingTop: 28 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {comercio && <span className="overline">{comercio.nombre}</span>}
          <h1 style={{ fontSize: 30, fontWeight: 800, letterSpacing: '-0.02em' }}>¿Quién sos?</h1>
          <p style={{ color: 'var(--c-ink-2)' }}>Elegí tu nombre para ver tus entregas.</p>
        </div>
        {datos.error && <ErrorCarga error={datos.error} reintentar={datos.recargar} />}
        {datos.cargando ? (
          <Esqueleto filas={3} alto={72} />
        ) : repartidores.length === 0 ? (
          <EstadoVacio icono="camion" titulo="Todavía no hay repartidores cargados" />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {repartidores.map((r) => {
              const cantidad = activas.filter((e) => e.repartidor_id === r.id_repartidor).length
              const detalle = !r.disponible ? 'fuera de turno' : cantidad ? plural(cantidad, 'entrega') : 'sin entregas'
              return (
                <Link key={r.id_repartidor} className="list-btn" to={`/repartidor/${r.id_repartidor}`}>
                  <span className="avatar avatar-lg" style={r.disponible ? undefined : { background: 'var(--st-pendiente-bg)', color: 'var(--st-pendiente-fg)' }}>
                    {iniciales(r)}
                  </span>
                  <span style={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                    <b style={{ fontSize: 18 }}>{r.nombre}</b>
                    <span className="muted" style={{ fontSize: 14 }}>{r.zona} · {detalle}</span>
                  </span>
                  <Icono nombre="adelante" tamano="lg" className="muted" />
                </Link>
              )
            })}
          </div>
        )}
        <p className="hint" style={{ textAlign: 'center', marginTop: 8 }}>¿No estás en la lista? Pedile al encargado que te dé de alta.</p>
      </div>
    </div>
  )
}
