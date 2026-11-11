import { useState } from 'react'
import { Link, useParams } from 'react-router'
import { api } from '../../api/dely'
import type { Seguimiento as DatosSeguimiento } from '../../api/tipos'
import { BadgeEstado } from '../../components/BadgeEstado'
import { ErrorCarga, Esqueleto } from '../../components/Estados'
import { Icono } from '../../components/Icono'
import { Logo } from '../../components/Logo'
import { Pasos } from '../../components/Pasos'
import { useApi } from '../../hooks/useApi'
import { useToasts } from '../../hooks/useToasts'
import { TITULO_NOTIFICACION } from '../../lib/estados'
import { hora, horaDeFecha, moneda } from '../../lib/formato'

const PASOS = ['Recibido', 'Asignado', 'En camino', 'Llegando', 'Entregado']

type Etapa = 'Recibido' | 'Asignado' | 'En camino' | 'Llegando' | 'Entregado' | 'Cancelado'

function etapaDe(s: DatosSeguimiento): Etapa {
  if (s.estado === 'Cancelado') return 'Cancelado'
  if (s.estado === 'Entregado') return 'Entregado'
  if (s.estado_entrega === 'Llegando') return 'Llegando'
  if (s.estado === 'En camino') return 'En camino'
  if (s.estado === 'Asignado') return 'Asignado'
  return 'Recibido'
}

const TITULO: Record<Etapa, string> = {
  Recibido: 'Recibimos tu pedido',
  Asignado: 'Tu pedido ya tiene repartidor',
  'En camino': 'Tu pedido está en camino',
  Llegando: 'Tu pedido está llegando',
  Entregado: 'Tu pedido fue entregado',
  Cancelado: 'Tu pedido fue cancelado',
}

function lineaRepartidor(s: DatosSeguimiento, etapa: Etapa) {
  if (etapa === 'Entregado') return s.direccion_entrega
  if (etapa === 'Llegando') return `Llegando a ${s.direccion_entrega}`
  if (s.ubicacion_actual) return `Va por ${s.ubicacion_actual}`
  return etapa === 'Asignado' ? 'Preparando la salida' : 'En camino'
}

export function Seguimiento() {
  const codigo = useParams().codigo ?? ''
  const toasts = useToasts()
  const seguimiento = useApi(() => api.seguimiento(codigo), codigo, 5000)
  const [marcando, setMarcando] = useState(false)

  const marcarLeidas = async () => {
    setMarcando(true)
    try {
      await api.marcarLeidas(codigo)
      await seguimiento.recargar()
    } catch (e) {
      toasts.error(e)
    } finally {
      setMarcando(false)
    }
  }

  const s = seguimiento.datos
  const encabezado = (
    <div className="topbar" style={{ justifyContent: 'space-between' }}>
      <Logo tamano={18} conPunto={false} />
      <span className="code muted" style={{ fontSize: 13 }}>{codigo.toUpperCase()}</span>
    </div>
  )

  if (!s) {
    return (
      <div className="dely phone">
        {encabezado}
        <div className="m-body">
          {seguimiento.error ? (
            <>
              <ErrorCarga error={seguimiento.error} reintentar={seguimiento.recargar} />
              <Link className="btn btn-secondary btn-lg" to="/seguimiento">Probar con otro código</Link>
            </>
          ) : (
            <Esqueleto filas={3} alto={160} />
          )}
        </div>
      </div>
    )
  }

  const etapa = etapaDe(s)
  const cancelado = etapa === 'Cancelado'
  const notificaciones = [...s.notificaciones].reverse()
  const sinLeer = notificaciones.filter((n) => !n.leida).length
  const cancelacion = s.notificaciones.find((n) => n.tipo === 'Cancelada')
  const actual = etapa === 'Entregado' ? PASOS.length : PASOS.indexOf(etapa)
  const eta =
    etapa === 'Entregado'
      ? { etiqueta: 'Entregado a las', valor: hora(s.hora_entrega), fondo: 'var(--st-entregado-bg)', color: 'var(--c-success)' }
      : etapa === 'Llegando'
        ? { etiqueta: 'Llega aprox.', valor: hora(s.horario_estimado), fondo: '#FFF1EA', color: '#A3360A' }
        : { etiqueta: 'Llega aprox.', valor: hora(s.horario_estimado), fondo: 'var(--c-bg)', color: 'var(--c-ink)' }

  return (
    <div className="dely phone">
      {encabezado}
      <div className="m-body">
        {etapa === 'Llegando' && (
          <div className="banner-arrive" role="alert">
            <span style={{ width: 40, height: 40, borderRadius: '50%', background: 'rgba(255,255,255,0.18)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', flex: 'none' }}>
              <Icono nombre="pin" tamano="lg" />
            </span>
            <span style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <b style={{ fontSize: 18, lineHeight: 1.3 }}>{s.repartidor} está llegando a {s.direccion_entrega}.</b>
              <span style={{ fontSize: 15 }}>¡Preparate para recibirlo!</span>
            </span>
          </div>
        )}

        <section className="card" style={{ padding: '20px 16px', display: 'flex', flexDirection: 'column', gap: 18, borderRadius: 16 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, alignItems: 'flex-start' }}>
            <BadgeEstado estado={etapa === 'Llegando' ? 'Llegando' : s.estado} grande />
            <h1 style={{ fontSize: 24, lineHeight: 1.25, fontWeight: 800, letterSpacing: '-0.01em' }}>{TITULO[etapa]}</h1>
          </div>
          {!cancelado && (
            <>
              <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 12, padding: '14px 16px', borderRadius: 12, background: eta.fondo }}>
                <span style={{ fontWeight: 600, color: 'var(--c-ink-2)' }}>{eta.etiqueta}</span>
                <span style={{ fontSize: 44, lineHeight: 1, fontWeight: 800, letterSpacing: '-0.03em', color: eta.color }}>{eta.valor}</span>
              </div>
              <Pasos etiquetas={PASOS} actual={actual} indiceLlegando={3} etiquetaAccesible="Estado del pedido" />
            </>
          )}
          {cancelado && (
            <div className="inline-alert" style={{ background: 'var(--st-cancelado-bg)', color: '#6E2424' }}>
              <Icono nombre="error" tamano="lg" />
              <span>
                El comercio canceló el pedido{cancelacion && ` a las ${horaDeFecha(cancelacion.fecha_hora)}`}. Si tenés dudas, llamalos.
              </span>
            </div>
          )}
        </section>

        {s.repartidor && !cancelado && (
          <section className="card" style={{ padding: 16, display: 'flex', gap: 14, alignItems: 'center' }}>
            <span className="avatar avatar-lg">{s.repartidor[0]}</span>
            <span style={{ display: 'flex', flexDirection: 'column', gap: 2, flexGrow: 1 }}>
              <b>{etapa === 'Entregado' ? `Te lo entregó ${s.repartidor}` : s.repartidor}</b>
              <span className="row muted" style={{ gap: 6, fontSize: 14 }}>
                <Icono nombre="pin" />
                {lineaRepartidor(s, etapa)}
              </span>
            </span>
          </section>
        )}

        <section className="card" style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div className="between">
            <h2 style={{ fontSize: 16, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
              Notificaciones
              {sinLeer > 0 && (
                <span style={{ background: 'var(--c-brand)', color: '#fff', borderRadius: 999, fontSize: 12, lineHeight: '20px', padding: '0 7px' }} aria-label={`${sinLeer} sin leer`}>
                  {sinLeer}
                </span>
              )}
            </h2>
            <button className="btn btn-ghost btn-sm" onClick={marcarLeidas} disabled={sinLeer === 0 || marcando} style={{ minHeight: 44 }}>
              Marcar como leídas
            </button>
          </div>
          <ol style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 12 }}>
            {notificaciones.map((n) => (
              <li key={n.id_notificacion} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                <span className={n.leida ? 'read-dot' : 'unread-dot'} aria-hidden="true" />
                <span style={{ display: 'flex', flexDirection: 'column', flexGrow: 1, fontSize: 14 }}>
                  <b style={{ fontWeight: n.leida ? 600 : 700 }}>
                    {TITULO_NOTIFICACION[n.tipo] ?? n.tipo}
                    {!n.leida && <span className="sr-only"> (sin leer)</span>}
                  </b>
                  <span className="muted">{n.mensaje}</span>
                </span>
                <span className="muted" style={{ fontSize: 12 }}>{horaDeFecha(n.fecha_hora)}</span>
              </li>
            ))}
          </ol>
        </section>

        <section className="card" style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 8, fontSize: 15 }}>
          <span className="overline">Tu pedido</span>
          {s.productos.map((p) => (
            <div key={p.nombre} className="between">
              <span>{p.cantidad} × {p.nombre}</span>
              <span>{moneda(p.subtotal)}</span>
            </div>
          ))}
          <hr className="divider" />
          <div className="between"><b>Total</b><b style={{ fontSize: 22 }}>{moneda(s.total)}</b></div>
          <span className="hint">Entrega en {s.direccion_entrega}</span>
        </section>

        <section className="card" style={{ padding: 16, display: 'flex', gap: 14, alignItems: 'center' }}>
          <span className="empty-ic" style={{ width: 44, height: 44, background: 'var(--c-brand-soft)', color: 'var(--c-brand-ink)' }}>
            <Icono nombre="tienda" tamano="lg" />
          </span>
          <span style={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
            <b>{s.comercio}</b>
            <span className="muted" style={{ fontSize: 14 }}>{s.comercio_telefono}</span>
          </span>
          <a className="btn btn-secondary" href={`tel:${s.comercio_telefono}`} style={{ minHeight: 48 }} aria-label={`Llamar a ${s.comercio}`}>
            <Icono nombre="telefono" />
            Llamar
          </a>
        </section>
      </div>
    </div>
  )
}
