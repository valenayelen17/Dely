import { useState, type FormEvent } from 'react'
import { useParams } from 'react-router'
import { api } from '../../api/dely'
import type { EstadoEntrega } from '../../api/tipos'
import { BadgeEstado } from '../../components/BadgeEstado'
import { ErrorCarga, Esqueleto } from '../../components/Estados'
import { Icono } from '../../components/Icono'
import { Encabezado, Layout } from '../../components/Layout'
import { Pasos } from '../../components/Pasos'
import { useApi } from '../../hooks/useApi'
import { useToasts } from '../../hooks/useToasts'
import { SIGUIENTE_ENTREGA } from '../../lib/estados'
import { hora, moneda, nombreCompleto } from '../../lib/formato'

const PASOS: EstadoEntrega[] = ['Asignada', 'En camino', 'Llegando', 'Entregada']
const VOLVER = { a: '/entregas', texto: 'Mis entregas' }

const ACCION: Partial<Record<EstadoEntrega, { texto: string; clase: string; ayuda: (cliente: string) => string }>> = {
  Asignada: { texto: 'Salir a entregar', clase: 'btn-primary', ayuda: (c) => `Pasa a En camino. ${c} ve que saliste.` },
  'En camino': { texto: 'Estoy llegando', clase: 'btn-arrive', ayuda: (c) => `Pasa a Llegando y le avisa a ${c}.` },
  Llegando: { texto: 'Marcar como entregado', clase: 'btn-success', ayuda: () => 'Te pedimos confirmación antes de cerrar.' },
}

const AVISO: Partial<Record<EstadoEntrega, string>> = {
  'En camino': 'Saliste a entregar',
  Llegando: 'Le avisamos al cliente que estás llegando',
  Entregada: 'Entrega cerrada',
}

export function DetalleEntrega() {
  const entregaId = Number(useParams().entregaId)
  const toasts = useToasts()
  const entrega = useApi(() => api.entrega(entregaId), `ent-${entregaId}`, 5000)
  const [ubicacion, setUbicacion] = useState('')
  const [confirmando, setConfirmando] = useState(false)
  const [enviando, setEnviando] = useState(false)

  const e = entrega.datos

  const avanzar = async (estado: EstadoEntrega) => {
    setEnviando(true)
    try {
      await api.cambiarEstadoEntrega(entregaId, estado, ubicacion.trim() || undefined)
      setConfirmando(false)
      setUbicacion('')
      await entrega.recargar()
      toasts.exito(AVISO[estado] ?? 'Entrega actualizada')
    } catch (error) {
      toasts.error(error, 'No se pudo actualizar la entrega')
    } finally {
      setEnviando(false)
    }
  }

  const informar = async (ev: FormEvent) => {
    ev.preventDefault()
    if (!ubicacion.trim()) return
    try {
      await api.informarUbicacion(entregaId, ubicacion.trim())
      toasts.exito('Ubicación informada', 'El cliente ya la ve en su seguimiento.')
      setUbicacion('')
      await entrega.recargar()
    } catch (error) {
      toasts.error(error, 'No se pudo informar la ubicación')
    }
  }

  if (!e) {
    return (
      <Layout>
        <Encabezado titulo="Entrega" volver={VOLVER} />
        {entrega.error ? <ErrorCarga error={entrega.error} reintentar={entrega.recargar} /> : <Esqueleto filas={2} alto={180} />}
      </Layout>
    )
  }

  const { pedido } = e
  const cliente = pedido.cliente.nombre
  const siguiente = SIGUIENTE_ENTREGA[e.estado]
  const accion = ACCION[e.estado]
  const enRecorrido = e.estado === 'En camino' || e.estado === 'Llegando'
  const indice = e.estado === 'Entregada' ? PASOS.length : PASOS.indexOf(e.estado)

  return (
    <Layout>
      <Encabezado
        volver={VOLVER}
        titulo={<span className="row" style={{ gap: 14, flexWrap: 'wrap' }}>Entrega a {nombreCompleto(pedido.cliente)} <BadgeEstado estado={e.estado} grande /></span>}
        bajada={<>Pedido <span className="code">{pedido.codigo_seguimiento}</span> · llega {hora(pedido.horario_estimado)}</>}
      />

      <div className="dos-columnas">
        <div className="columna">
          {e.estado !== 'Cancelada' && (
            <section className="seccion">
              <h2 className="seccion-titulo">Recorrido</h2>
              <Pasos etiquetas={PASOS} actual={indice} indiceLlegando={2} etiquetaAccesible="Progreso de la entrega" />
            </section>
          )}

          <section className="seccion">
            <h2 className="seccion-titulo"><Icono nombre="pin" tamano="lg" /> Destino</h2>
            <span style={{ fontSize: 28, fontWeight: 800, lineHeight: 1.2, letterSpacing: '-0.01em' }}>{pedido.direccion_entrega}</span>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 16 }}>
              <div className="dato"><span className="overline">Zona</span><span>{pedido.zona}</span></div>
              <div className="dato"><span className="overline">Horario estimado</span><span>{hora(pedido.horario_estimado)}</span></div>
              <div className="dato"><span className="overline">Cliente</span><span>{nombreCompleto(pedido.cliente)}</span></div>
              <div className="dato"><span className="overline">Teléfono</span><a href={`tel:${pedido.cliente.telefono}`}>{pedido.cliente.telefono}</a></div>
            </div>
            {e.ubicacion_actual && enRecorrido && (
              <span className="row muted" style={{ gap: 6 }}><Icono nombre="camion" />Última ubicación informada: {e.ubicacion_actual}</span>
            )}
          </section>

          <section className="seccion" style={{ padding: 0, gap: 0 }}>
            <h2 className="seccion-titulo" style={{ padding: '20px 24px 12px' }}><Icono nombre="caja" tamano="lg" /> Productos</h2>
            <table className="table" style={{ minWidth: 0 }}>
              <thead><tr><th>Producto</th><th className="r">Cantidad</th><th className="r">Unitario</th><th className="r">Subtotal</th></tr></thead>
              <tbody>
                {pedido.detalles.map((d) => (
                  <tr key={d.id_detalle}>
                    <td>{d.producto_nombre}</td>
                    <td className="r">{d.cantidad}</td>
                    <td className="r">{moneda(d.precio_unitario)}</td>
                    <td className="r">{moneda(d.subtotal)}</td>
                  </tr>
                ))}
                <tr>
                  <td colSpan={3}><b>A cobrar</b></td>
                  <td className="r"><b style={{ fontSize: 20 }}>{moneda(pedido.total)}</b></td>
                </tr>
              </tbody>
            </table>
          </section>
        </div>

        <aside className="columna columna-fija">
          <section className="seccion">
            <h2 className="seccion-titulo">Próximo paso</h2>
            {e.estado === 'Llegando' && (
              <div className="inline-alert inline-alert-warn" role="status">
                <Icono nombre="campana" tamano="lg" />
                <span>Le avisamos a {cliente} que estás llegando.</span>
              </div>
            )}
            {e.estado === 'Entregada' && (
              <div className="inline-alert" style={{ background: 'var(--st-entregado-bg)', color: '#14532D' }} role="status">
                <Icono nombre="check-circulo" tamano="lg" />
                <span><b>Entregado a las {hora(e.hora_entrega)}.</b> No hay más pasos.</span>
              </div>
            )}
            {e.estado === 'Cancelada' && (
              <div className="inline-alert inline-alert-error" role="status">
                <Icono nombre="x-circulo" tamano="lg" />
                <span><b>El comercio canceló este pedido.</b> No hace falta que lo entregues.</span>
              </div>
            )}
            {siguiente && accion && (
              <>
                <button
                  className={`btn btn-lg ${accion.clase}`}
                  style={{ width: '100%', minHeight: 56 }}
                  disabled={enviando}
                  onClick={() => (siguiente === 'Entregada' ? setConfirmando(true) : void avanzar(siguiente))}
                >
                  {enviando && <span className="spinner" />}
                  {accion.texto}
                </button>
                <span className="hint">{accion.ayuda(cliente)}</span>
              </>
            )}
          </section>

          {enRecorrido && (
            <form className="seccion" onSubmit={informar}>
              <h2 className="seccion-titulo">¿Por dónde vas?</h2>
              <input className="input" aria-label="Ubicación actual" value={ubicacion} onChange={(ev) => setUbicacion(ev.target.value)} placeholder={e.ubicacion_actual ?? 'Ej.: Av. Callao 200'} />
              <button className="btn btn-secondary" disabled={!ubicacion.trim()}>Informar ubicación</button>
              <span className="hint">{cliente} ve este texto en su seguimiento.</span>
            </form>
          )}
        </aside>
      </div>

      {confirmando && (
        <div className="overlay" onKeyDown={(ev) => ev.key === 'Escape' && setConfirmando(false)}>
          <div className="scrim" onClick={() => setConfirmando(false)} />
          <div className="modal dely" role="dialog" aria-modal="true" aria-labelledby="de-cf">
            <h2 id="de-cf" style={{ fontSize: 21, fontWeight: 700 }}>¿Confirmás la entrega?</h2>
            <p className="muted">
              Vas a marcar el pedido de {cliente} como entregado y cobrado ({moneda(pedido.total)}). No se puede deshacer.
            </p>
            <div className="row" style={{ justifyContent: 'flex-end', gap: 8 }}>
              <button className="btn btn-ghost" onClick={() => setConfirmando(false)}>Todavía no</button>
              <button className="btn btn-success" disabled={enviando} onClick={() => void avanzar('Entregada')} autoFocus>
                {enviando && <span className="spinner" />}
                Sí, lo entregué
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}
