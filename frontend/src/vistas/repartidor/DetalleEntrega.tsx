import { useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router'
import { api } from '../../api/dely'
import type { EstadoEntrega } from '../../api/tipos'
import { BadgeEstado } from '../../components/BadgeEstado'
import { ErrorCarga, Esqueleto } from '../../components/Estados'
import { Icono } from '../../components/Icono'
import { Pasos } from '../../components/Pasos'
import { useApi } from '../../hooks/useApi'
import { useToasts } from '../../hooks/useToasts'
import { SIGUIENTE_ENTREGA } from '../../lib/estados'
import { hora, moneda, nombreCompleto } from '../../lib/formato'
import { BarraSuperior } from './BarraSuperior'

const PASOS: EstadoEntrega[] = ['Asignada', 'En camino', 'Llegando', 'Entregada']

const ACCION: Partial<Record<EstadoEntrega, { texto: string; clase: string; ayuda: (cliente: string) => string }>> = {
  Asignada: { texto: 'Salir a entregar', clase: 'btn-primary', ayuda: (c) => `Pasa a En camino. ${c} ve que saliste.` },
  'En camino': { texto: 'Estoy llegando', clase: 'btn-arrive', ayuda: (c) => `Pasa a Llegando y le avisa a ${c}.` },
  Llegando: { texto: 'Entregado', clase: 'btn-success', ayuda: () => 'Te pedimos confirmación antes de cerrar.' },
}

export function DetalleEntrega() {
  const params = useParams()
  const repartidorId = Number(params.repartidorId)
  const entregaId = Number(params.entregaId)
  const toasts = useToasts()
  const entrega = useApi(() => api.entrega(entregaId), `ent-${entregaId}`, 5000)
  const [ubicacion, setUbicacion] = useState('')
  const [confirmando, setConfirmando] = useState(false)
  const [enviando, setEnviando] = useState(false)

  const e = entrega.datos
  const volver = `/repartidor/${repartidorId}`

  const avanzar = async (estado: EstadoEntrega) => {
    setEnviando(true)
    try {
      await api.cambiarEstadoEntrega(entregaId, estado, ubicacion.trim() || undefined)
      setConfirmando(false)
      setUbicacion('')
      await entrega.recargar()
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
      <div className="dely phone">
        <BarraSuperior volverA={volver} etiquetaVolver="Volver a mis entregas"><b>Entrega</b></BarraSuperior>
        <div className="m-body">
          {entrega.error ? <ErrorCarga error={entrega.error} reintentar={entrega.recargar} /> : <Esqueleto filas={3} alto={140} />}
        </div>
      </div>
    )
  }

  const { pedido } = e
  const cliente = pedido.cliente.nombre
  const siguiente = SIGUIENTE_ENTREGA[e.estado]
  const accion = ACCION[e.estado]
  const enRecorrido = e.estado === 'En camino' || e.estado === 'Llegando'
  const indice = e.estado === 'Entregada' ? PASOS.length : PASOS.indexOf(e.estado)

  return (
    <div className="dely phone" style={{ position: 'relative' }}>
      <BarraSuperior volverA={volver} etiquetaVolver="Volver a mis entregas">
        <span style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.3, flexGrow: 1 }}>
          <b>Entrega a {cliente}</b>
          <span className="code muted" style={{ fontSize: 12 }}>{pedido.codigo_seguimiento}</span>
        </span>
        <BadgeEstado estado={e.estado} grande />
      </BarraSuperior>

      <div className="m-body" style={{ flexGrow: 1 }}>
        {e.estado !== 'Cancelada' && <Pasos etiquetas={PASOS} actual={indice} indiceLlegando={2} etiquetaAccesible="Progreso de la entrega" />}

        <section className="card" style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <span className="overline">Llevalo a</span>
          <span style={{ fontSize: 26, fontWeight: 800, lineHeight: 1.2, letterSpacing: '-0.01em' }}>{pedido.direccion_entrega}</span>
          <div className="row muted" style={{ fontSize: 14, gap: 10 }}>
            <span className="tag tag-zone">{pedido.zona}</span>
            <span className="row" style={{ gap: 4 }}><Icono nombre="reloj" />Llega {hora(pedido.horario_estimado)}</span>
          </div>
          <hr className="divider" />
          <div className="between">
            <span style={{ display: 'flex', flexDirection: 'column' }}>
              <b>{nombreCompleto(pedido.cliente)}</b>
              <span className="muted" style={{ fontSize: 14 }}>{pedido.cliente.telefono}</span>
            </span>
            <a className="btn btn-secondary" href={`tel:${pedido.cliente.telefono}`} style={{ minHeight: 48 }}>
              <Icono nombre="telefono" />
              Llamar
            </a>
          </div>
        </section>

        {enRecorrido && (
          <form className="card" onSubmit={informar} style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div className="field">
              <label className="label" htmlFor="de-ub">¿Por dónde vas?</label>
              <div className="row" style={{ gap: 8 }}>
                <input id="de-ub" className="input" value={ubicacion} onChange={(ev) => setUbicacion(ev.target.value)} placeholder={e.ubicacion_actual ?? 'Ej.: Av. Callao 200'} style={{ height: 48 }} />
                <button className="btn btn-secondary" style={{ minHeight: 48 }} disabled={!ubicacion.trim()}>Informar</button>
              </div>
              <span className="hint">
                {cliente} ve este texto en su seguimiento.{e.ubicacion_actual && ` Última: ${e.ubicacion_actual}.`}
              </span>
            </div>
          </form>
        )}

        {e.estado === 'Llegando' && (
          <div className="inline-alert inline-alert-warn" role="status">
            <Icono nombre="campana" tamano="lg" />
            <span>Le avisamos a {cliente} que estás llegando.</span>
          </div>
        )}
        {e.estado === 'Entregada' && (
          <div className="inline-alert" style={{ background: 'var(--st-entregado-bg)', color: '#14532D' }} role="status">
            <Icono nombre="check-circulo" tamano="lg" />
            <span><b>Entregado a las {hora(e.hora_entrega)}.</b> Volvé a Mis entregas para ver la próxima.</span>
          </div>
        )}
        {e.estado === 'Cancelada' && (
          <div className="inline-alert inline-alert-error" role="status">
            <Icono nombre="x-circulo" tamano="lg" />
            <span><b>El comercio canceló este pedido.</b> No hace falta que lo entregues.</span>
          </div>
        )}

        <section className="card" style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 8, fontSize: 15 }}>
          <span className="overline">Productos</span>
          {pedido.detalles.map((d) => (
            <div key={d.id_detalle} className="between">
              <span>{d.cantidad} × {d.producto_nombre}</span>
              <span>{moneda(d.subtotal)}</span>
            </div>
          ))}
          <hr className="divider" />
          <div className="between"><b>A cobrar</b><b style={{ fontSize: 24 }}>{moneda(pedido.total)}</b></div>
        </section>
      </div>

      <div className="bottom-bar">
        {siguiente && accion ? (
          <>
            <button
              className={`btn btn-xl ${accion.clase}`}
              disabled={enviando}
              onClick={() => (siguiente === 'Entregada' ? setConfirmando(true) : void avanzar(siguiente))}
            >
              {enviando && <span className="spinner" />}
              {accion.texto}
            </button>
            <span className="hint" style={{ textAlign: 'center' }}>{accion.ayuda(cliente)}</span>
          </>
        ) : (
          <Link className="btn btn-secondary btn-xl" to={volver}>Volver a mis entregas</Link>
        )}
      </div>

      {confirmando && (
        <div className="overlay" onKeyDown={(ev) => ev.key === 'Escape' && setConfirmando(false)}>
          <div className="scrim" onClick={() => setConfirmando(false)} />
          <div className="hoja-inferior dely" role="dialog" aria-modal="true" aria-labelledby="de-cf">
            <h2 id="de-cf" style={{ fontSize: 21, fontWeight: 700 }}>¿Confirmás la entrega?</h2>
            <p className="muted">
              Vas a marcar el pedido de {cliente} como entregado y cobrado ({moneda(pedido.total)}). No se puede deshacer.
            </p>
            <button className="btn btn-success btn-xl" disabled={enviando} onClick={() => void avanzar('Entregada')} autoFocus>
              {enviando && <span className="spinner" />}
              Sí, lo entregué
            </button>
            <button className="btn btn-ghost btn-lg" onClick={() => setConfirmando(false)}>Todavía no</button>
          </div>
        </div>
      )}
    </div>
  )
}
