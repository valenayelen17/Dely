import { useState, type FormEvent } from 'react'
import { api } from '../../api/dely'
import type { Pedido, Repartidor } from '../../api/tipos'
import { BadgeEstado } from '../../components/BadgeEstado'
import { ErrorCarga, Esqueleto, EstadoVacio } from '../../components/Estados'
import { Icono } from '../../components/Icono'
import { useApi } from '../../hooks/useApi'
import { useToasts } from '../../hooks/useToasts'
import { TITULO_NOTIFICACION } from '../../lib/estados'
import { hora, horaDeFecha, iniciales, moneda, nombreCompleto, plural } from '../../lib/formato'

interface Props {
  pedidoId: number
  comercioId: number
  alCerrar: () => void
  alCambiar: () => void
}

const mismaZona = (a: string, b: string) => a.trim().toLowerCase() === b.trim().toLowerCase()

function Dato({ etiqueta, children }: { etiqueta: string; children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      <span className="label">{etiqueta}</span>
      <span style={{ fontWeight: 600 }}>{children}</span>
    </div>
  )
}

function Asignacion({ pedido, comercioId, alAsignar }: { pedido: Pedido; comercioId: number; alAsignar: (p: Pedido) => void }) {
  const toasts = useToasts()
  const repartidores = useApi(() => api.repartidores({ comercio_id: comercioId }), `rep-${comercioId}`)
  const activas = useApi(api.entregasActivas, 'activas')
  const actual = pedido.entrega?.repartidor_id
  const [elegido, setElegido] = useState<number>()
  const [enviando, setEnviando] = useState(false)

  const todos = repartidores.datos ?? []
  const candidatos = todos.filter((r) => r.disponible && mismaZona(r.zona, pedido.zona))
  const otros = todos.filter((r) => !candidatos.includes(r))
  const seleccion = elegido ?? candidatos.find((r) => r.id_repartidor !== actual)?.id_repartidor
  const elegidoRep = candidatos.find((r) => r.id_repartidor === seleccion)
  const cargaDe = (r: Repartidor) => activas.datos?.filter((e) => e.repartidor_id === r.id_repartidor).length ?? 0

  const asignar = async () => {
    if (!seleccion) return
    setEnviando(true)
    try {
      const actualizado = await api.asignar(pedido.id_pedido, seleccion)
      toasts.exito(`Pedido asignado a ${actualizado.entrega?.repartidor.nombre}`, 'Ya aparece en sus entregas.')
      alAsignar(actualizado)
    } catch (e) {
      toasts.error(e, 'No se pudo asignar')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <section className="psec" style={{ background: 'var(--c-surface-2)' }}>
      <div className="between">
        <h3>{actual ? 'Reasignar repartidor' : 'Asignar repartidor'}</h3>
        <span className="tag tag-zone">{pedido.zona}</span>
      </div>
      {repartidores.cargando ? (
        <Esqueleto filas={2} alto={56} />
      ) : candidatos.length === 0 ? (
        <EstadoVacio icono="camion" titulo={`No hay repartidores disponibles en ${pedido.zona}`}>
          Poné en turno a alguien de la zona desde Repartidores.
        </EstadoVacio>
      ) : (
        <fieldset style={{ border: 0, margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 8 }}>
          <legend className="hint" style={{ padding: 0, marginBottom: 8 }}>
            Sólo repartidores disponibles de la zona del pedido.
          </legend>
          {candidatos.map((r) => (
            <label key={r.id_repartidor} className={`opt${seleccion === r.id_repartidor ? ' is-on' : ''}`}>
              <input
                type="radio"
                name="repartidor"
                checked={seleccion === r.id_repartidor}
                onChange={() => setElegido(r.id_repartidor)}
              />
              <span className="avatar">{iniciales(r)}</span>
              <span style={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                <b>{nombreCompleto(r)}</b>
                <span className="muted" style={{ fontSize: 12 }}>
                  {r.zona} · en turno · {plural(cargaDe(r), 'entrega activa', 'entregas activas')}
                  {r.id_repartidor === actual && ' · asignado ahora'}
                </span>
              </span>
            </label>
          ))}
        </fieldset>
      )}
      {otros.length > 0 && (
        <span className="hint">
          {otros.map((r) => r.nombre).join(', ')} no {otros.length === 1 ? 'aparece' : 'aparecen'} porque no{' '}
          {otros.length === 1 ? 'está' : 'están'} en turno o cubren otra zona.
        </span>
      )}
      {candidatos.length > 0 && (
        <button
          className="btn btn-primary btn-lg"
          style={{ width: '100%' }}
          disabled={!seleccion || seleccion === actual || enviando}
          onClick={asignar}
        >
          {enviando && <span className="spinner" />}
          {elegidoRep ? `${actual ? 'Reasignar' : 'Asignar'} a ${elegidoRep.nombre}` : 'Elegí un repartidor'}
        </button>
      )}
    </section>
  )
}

function EditarEntrega({ pedido, alGuardar, alCancelar }: { pedido: Pedido; alGuardar: (p: Pedido) => void; alCancelar: () => void }) {
  const toasts = useToasts()
  const [direccion, setDireccion] = useState(pedido.direccion_entrega)
  const [zona, setZona] = useState(pedido.zona)
  const [horario, setHorario] = useState(hora(pedido.horario_estimado))

  const guardar = async (e: FormEvent) => {
    e.preventDefault()
    try {
      alGuardar(await api.editarPedido(pedido.id_pedido, { direccion_entrega: direccion, zona, horario_estimado: horario }))
      toasts.exito('Pedido actualizado')
    } catch (error) {
      toasts.error(error, 'No se pudo guardar')
    }
  }

  return (
    <form onSubmit={guardar} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div className="field">
        <label className="label" htmlFor="ed-dir">Dirección</label>
        <input id="ed-dir" className="input" value={direccion} onChange={(e) => setDireccion(e.target.value)} required minLength={3} />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 12 }}>
        <div className="field">
          <label className="label" htmlFor="ed-zona">Zona</label>
          <input id="ed-zona" className="input" value={zona} onChange={(e) => setZona(e.target.value)} required minLength={2} />
        </div>
        <div className="field">
          <label className="label" htmlFor="ed-hora">Horario</label>
          <input id="ed-hora" className="input" type="time" value={horario} onChange={(e) => setHorario(e.target.value)} required />
        </div>
      </div>
      <div className="row" style={{ justifyContent: 'flex-end' }}>
        <button type="button" className="btn btn-ghost" onClick={alCancelar}>Cancelar</button>
        <button className="btn btn-primary">Guardar</button>
      </div>
    </form>
  )
}

export function PanelPedido({ pedidoId, comercioId, alCerrar, alCambiar }: Props) {
  const toasts = useToasts()
  const pedido = useApi(() => api.pedido(pedidoId), `p-${pedidoId}`, 5000)
  const notificaciones = useApi(() => api.notificaciones(pedidoId), `n-${pedidoId}`, 5000)
  const [editando, setEditando] = useState(false)
  const [confirmandoCancelacion, setConfirmandoCancelacion] = useState(false)

  const actualizar = () => {
    void pedido.recargar()
    void notificaciones.recargar()
    alCambiar()
  }

  const cancelar = async () => {
    try {
      await api.cancelar(pedidoId)
      toasts.exito('Pedido cancelado', 'El stock volvió a estar disponible.')
      setConfirmandoCancelacion(false)
      actualizar()
    } catch (e) {
      toasts.error(e, 'No se pudo cancelar')
    }
  }

  const p = pedido.datos
  const recibido = notificaciones.datos?.find((n) => n.tipo === 'Recibido')
  const finalizado = p && (p.estado === 'Entregado' || p.estado === 'Cancelado')

  return (
    <div className="overlay" onKeyDown={(e) => e.key === 'Escape' && alCerrar()}>
      <div className="scrim" onClick={alCerrar} />
      <aside className="panel panel-lateral dely" role="dialog" aria-modal="true" aria-labelledby="panel-titulo">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, padding: '20px 24px', borderBottom: '1px solid var(--c-divider)' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div className="row">
              <h2 id="panel-titulo" className="code" style={{ fontSize: 21 }}>
                {p?.codigo_seguimiento ?? 'Pedido'}
              </h2>
              {p && <BadgeEstado estado={p.estado} />}
            </div>
            {p && (
              <span className="muted" style={{ fontSize: 13 }}>
                {recibido && `Recibido ${horaDeFecha(recibido.fecha_hora)} · `}Entrega estimada{' '}
                <b style={{ color: 'var(--c-ink)' }}>{hora(p.horario_estimado)}</b>
              </span>
            )}
          </div>
          <button className="btn btn-ghost btn-icon" aria-label="Cerrar detalle" onClick={alCerrar} autoFocus>
            <Icono nombre="cerrar" tamano="lg" />
          </button>
        </div>

        {pedido.error && (
          <div style={{ padding: 24 }}>
            <ErrorCarga error={pedido.error} reintentar={pedido.recargar} />
          </div>
        )}
        {!p ? (
          !pedido.error && <div style={{ padding: 24 }}><Esqueleto filas={4} alto={90} /></div>
        ) : (
          <>
            <section className="psec">
              <div className="between">
                <h3>Cliente y entrega</h3>
                {p.estado === 'Pendiente' && !editando && (
                  <button className="btn btn-secondary btn-sm" onClick={() => setEditando(true)}>
                    <Icono nombre="editar" />
                    Editar
                  </button>
                )}
              </div>
              {editando ? (
                <EditarEntrega
                  pedido={p}
                  alCancelar={() => setEditando(false)}
                  alGuardar={() => {
                    setEditando(false)
                    actualizar()
                  }}
                />
              ) : (
                <>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '12px 16px' }}>
                    <Dato etiqueta="Cliente">{nombreCompleto(p.cliente)}</Dato>
                    <Dato etiqueta="Teléfono">
                      <a href={`tel:${p.cliente.telefono}`}>{p.cliente.telefono}</a>
                    </Dato>
                    <Dato etiqueta="Dirección">{p.direccion_entrega}</Dato>
                    <Dato etiqueta="Zona · horario">
                      {p.zona} · {hora(p.horario_estimado)}
                    </Dato>
                  </div>
                  {p.estado === 'Pendiente' && (
                    <span className="hint">Dirección, zona y horario se pueden editar mientras el pedido esté Pendiente.</span>
                  )}
                </>
              )}
            </section>

            {(p.estado === 'Pendiente' || p.estado === 'Asignado') && (
              <Asignacion pedido={p} comercioId={comercioId} alAsignar={actualizar} />
            )}

            <section className="psec">
              <h3>Productos</h3>
              <table className="table" style={{ minWidth: 0 }}>
                <thead>
                  <tr>
                    <th style={{ padding: '8px 0' }}>Producto</th>
                    <th className="r" style={{ padding: '8px 0' }}>Cant.</th>
                    <th className="r" style={{ padding: '8px 0' }}>Unitario</th>
                    <th className="r" style={{ padding: '8px 0' }}>Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {p.detalles.map((d) => (
                    <tr key={d.id_detalle}>
                      <td style={{ padding: '10px 0' }}>{d.producto_nombre}</td>
                      <td className="r" style={{ padding: '10px 0' }}>{d.cantidad}</td>
                      <td className="r" style={{ padding: '10px 0' }}>{moneda(d.precio_unitario)}</td>
                      <td className="r" style={{ padding: '10px 0' }}>{moneda(d.subtotal)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="between" style={{ fontSize: 18 }}>
                <b>Total</b>
                <b>{moneda(p.total)}</b>
              </div>
            </section>

            <section className="psec">
              <h3>Entrega</h3>
              {p.entrega ? (
                <>
                  <div className="between">
                    <span className="row" style={{ gap: 10 }}>
                      <span className="avatar">{iniciales(p.entrega.repartidor)}</span>
                      <b>{nombreCompleto(p.entrega.repartidor)}</b>
                    </span>
                    <BadgeEstado estado={p.entrega.estado} />
                  </div>
                  <div className="between">
                    <span className="muted">Ubicación actual</span>
                    <span style={{ fontWeight: 600 }}>{p.entrega.ubicacion_actual ?? <span className="muted">Sin datos</span>}</span>
                  </div>
                  {p.entrega.hora_entrega && (
                    <div className="between">
                      <span className="muted">Entregado a las</span>
                      <b>{hora(p.entrega.hora_entrega)}</b>
                    </div>
                  )}
                </>
              ) : (
                <div className="inline-alert inline-alert-info">
                  <Icono nombre="info" tamano="lg" />
                  <span>Todavía no tiene entrega. Se crea al asignar un repartidor; mientras no salga, lo podés reasignar.</span>
                </div>
              )}
            </section>

            <section className="psec">
              <h3>Notificaciones enviadas a {p.cliente.nombre}</h3>
              <ol style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 10 }}>
                {[...(notificaciones.datos ?? [])].reverse().map((n) => (
                  <li key={n.id_notificacion} className="row" style={{ alignItems: 'flex-start', gap: 10 }}>
                    <span className="empty-ic" style={{ width: 28, height: 28, background: 'var(--st-pendiente-bg)' }}>
                      <Icono nombre="campana" />
                    </span>
                    <span style={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                      <b style={{ fontSize: 13 }}>{TITULO_NOTIFICACION[n.tipo] ?? n.tipo}</b>
                      <span className="muted" style={{ fontSize: 13 }}>{n.mensaje}</span>
                    </span>
                    <span className="muted" style={{ fontSize: 12 }}>{horaDeFecha(n.fecha_hora)}</span>
                  </li>
                ))}
              </ol>
            </section>

            {!finalizado && (
              <div style={{ padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: 12 }}>
                {confirmandoCancelacion ? (
                  <div className="inline-alert inline-alert-error" role="alert" style={{ flexDirection: 'column' }}>
                    <span>
                      <b>¿Cancelar el pedido {p.codigo_seguimiento}?</b> El stock vuelve y le avisamos a {p.cliente.nombre}.
                    </span>
                    <div className="row">
                      <button className="btn btn-danger-solid" onClick={cancelar}>Sí, cancelar</button>
                      <button className="btn btn-ghost" onClick={() => setConfirmandoCancelacion(false)}>No</button>
                    </div>
                  </div>
                ) : (
                  <div className="row" style={{ justifyContent: 'space-between', flexWrap: 'wrap' }}>
                    <button className="btn btn-danger" onClick={() => setConfirmandoCancelacion(true)}>
                      <Icono nombre="x-circulo" />
                      Cancelar pedido
                    </button>
                    <span className="hint">Al cancelar, el stock vuelve.</span>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </aside>
    </div>
  )
}
