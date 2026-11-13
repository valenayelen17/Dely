import { useState } from 'react'
import { useParams } from 'react-router'
import { api } from '../../api/dely'
import type { Seguimiento as DatosSeguimiento } from '../../api/tipos'
import { BadgeEstado } from '../../components/BadgeEstado'
import { ErrorCarga, Esqueleto } from '../../components/Estados'
import { Icono } from '../../components/Icono'
import { Encabezado, Layout } from '../../components/Layout'
import { Pasos } from '../../components/Pasos'
import { useApi } from '../../hooks/useApi'
import { useToasts } from '../../hooks/useToasts'
import { TITULO_NOTIFICACION } from '../../lib/estados'
import { hora, horaDeFecha, moneda } from '../../lib/formato'
import { PASOS_CLIENTE, TITULO_ETAPA, etapaDe, indicePaso, type Etapa } from '../../lib/seguimiento'

const VOLVER = { a: '/pedidos', texto: 'Mis pedidos' }

function lineaRepartidor(s: DatosSeguimiento, etapa: Etapa) {
  if (etapa === 'Entregado') return `Te lo entregó en ${s.direccion_entrega}`
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
  if (!s) {
    return (
      <Layout>
        <Encabezado titulo="Seguimiento" volver={VOLVER} />
        {seguimiento.error ? <ErrorCarga error={seguimiento.error} reintentar={seguimiento.recargar} /> : <Esqueleto filas={2} alto={200} />}
      </Layout>
    )
  }

  const etapa = etapaDe(s)
  const cancelado = etapa === 'Cancelado'
  const notificaciones = [...s.notificaciones].reverse()
  const sinLeer = notificaciones.filter((n) => !n.leida).length
  const cancelacion = s.notificaciones.find((n) => n.tipo === 'Cancelada')
  const eta =
    etapa === 'Entregado'
      ? { etiqueta: 'Entregado a las', valor: hora(s.hora_entrega), fondo: 'var(--st-entregado-bg)', color: 'var(--c-success)' }
      : etapa === 'Llegando'
        ? { etiqueta: 'Llega aprox.', valor: hora(s.horario_estimado), fondo: '#FFF1EA', color: '#A3360A' }
        : { etiqueta: 'Llega aprox.', valor: hora(s.horario_estimado), fondo: 'var(--c-bg)', color: 'var(--c-ink)' }

  return (
    <Layout>
      <Encabezado
        volver={VOLVER}
        titulo={<span className="row" style={{ gap: 14, flexWrap: 'wrap' }}>Pedido <span className="code" style={{ fontSize: 26 }}>{s.codigo_seguimiento}</span></span>}
        bajada={`${s.comercio} · ${s.fecha_pedido} · entrega en ${s.direccion_entrega}`}
      />

      {etapa === 'Llegando' && (
        <div className="banner-arrive" role="alert">
          <Icono nombre="pin" tamano="xl" />
          <span style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <b style={{ fontSize: 20, lineHeight: 1.3 }}>{s.repartidor} está llegando a {s.direccion_entrega}.</b>
            <span style={{ fontSize: 15 }}>¡Preparate para recibirlo!</span>
          </span>
        </div>
      )}

      <div className="dos-columnas">
        <div className="columna">
          <section className="seccion" style={{ gap: 24 }}>
            <div className="between" style={{ alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'flex-start' }}>
                <BadgeEstado estado={etapa === 'Llegando' ? 'Llegando' : s.estado} grande />
                <h2 style={{ fontSize: 28, lineHeight: 1.2, fontWeight: 800, letterSpacing: '-0.01em' }}>{TITULO_ETAPA[etapa]}</h2>
              </div>
              {!cancelado && (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', padding: '12px 20px', borderRadius: 12, background: eta.fondo }}>
                  <span style={{ fontWeight: 600, color: 'var(--c-ink-2)', fontSize: 14 }}>{eta.etiqueta}</span>
                  <span style={{ fontSize: 44, lineHeight: 1, fontWeight: 800, letterSpacing: '-0.03em', color: eta.color }}>{eta.valor}</span>
                </div>
              )}
            </div>
            {!cancelado && <Pasos etiquetas={PASOS_CLIENTE} actual={indicePaso(etapa)} indiceLlegando={3} etiquetaAccesible="Estado del pedido" />}
            {cancelado && (
              <div className="inline-alert" style={{ background: 'var(--st-cancelado-bg)', color: '#6E2424' }}>
                <Icono nombre="error" tamano="lg" />
                <span>El comercio canceló el pedido{cancelacion && ` a las ${horaDeFecha(cancelacion.fecha_hora)}`}. Si tenés dudas, llamalos.</span>
              </div>
            )}
          </section>

          {s.repartidor && !cancelado && (
            <section className="seccion" style={{ flexDirection: 'row', alignItems: 'center' }}>
              <span className="avatar avatar-lg">{s.repartidor[0]}</span>
              <span style={{ display: 'flex', flexDirection: 'column', gap: 2, flexGrow: 1 }}>
                <b>{s.repartidor}</b>
                <span className="row muted" style={{ gap: 6, fontSize: 14 }}><Icono nombre="pin" />{lineaRepartidor(s, etapa)}</span>
              </span>
            </section>
          )}

          <section className="seccion" style={{ padding: 0, gap: 0 }}>
            <h2 className="seccion-titulo" style={{ padding: '20px 24px 12px' }}><Icono nombre="caja" tamano="lg" /> Tu pedido</h2>
            <table className="table" style={{ minWidth: 0 }}>
              <thead><tr><th>Producto</th><th className="r">Cantidad</th><th className="r">Subtotal</th></tr></thead>
              <tbody>
                {s.productos.map((p) => (
                  <tr key={p.nombre}>
                    <td>{p.nombre}</td>
                    <td className="r">{p.cantidad}</td>
                    <td className="r">{moneda(p.subtotal)}</td>
                  </tr>
                ))}
                <tr>
                  <td colSpan={2}><b>Total</b></td>
                  <td className="r"><b style={{ fontSize: 20 }}>{moneda(s.total)}</b></td>
                </tr>
              </tbody>
            </table>
          </section>
        </div>

        <aside className="columna columna-fija">
          <section className="seccion">
            <div className="between">
              <h2 className="seccion-titulo">
                <Icono nombre="campana" tamano="lg" /> Notificaciones
                {sinLeer > 0 && <span className="tag tag-alert" aria-label={`${sinLeer} sin leer`}>{sinLeer}</span>}
              </h2>
              <button className="btn btn-ghost btn-sm" onClick={marcarLeidas} disabled={sinLeer === 0 || marcando}>Marcar como leídas</button>
            </div>
            <ol style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 14 }}>
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

          <section className="seccion" style={{ flexDirection: 'row', alignItems: 'center' }}>
            <span className="empty-ic" style={{ width: 44, height: 44, background: 'var(--c-brand-soft)', color: 'var(--c-brand-ink)', flex: 'none' }}>
              <Icono nombre="tienda" tamano="lg" />
            </span>
            <span style={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
              <b>{s.comercio}</b>
              <a href={`tel:${s.comercio_telefono}`} style={{ fontSize: 14 }}>{s.comercio_telefono}</a>
            </span>
          </section>
        </aside>
      </div>
    </Layout>
  )
}
