import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'
import { api } from '../../api/dely'
import type { Cliente, DatosCliente, Pedido, Producto } from '../../api/tipos'
import { ErrorCarga, Esqueleto } from '../../components/Estados'
import { Icono } from '../../components/Icono'
import { useApi } from '../../hooks/useApi'
import { useComercio } from '../../hooks/useComercio'
import { useToasts } from '../../hooks/useToasts'
import { hora, horaSugerida, iniciales, moneda, nombreCompleto, plural } from '../../lib/formato'

const STOCK_BAJO = 5
const CLIENTE_VACIO: DatosCliente = { nombre: '', apellido: '', telefono: '', email: '', direccion: '' }

function AltaCliente({ alCrear, alCancelar }: { alCrear: (c: Cliente) => void; alCancelar: () => void }) {
  const toasts = useToasts()
  const [datos, setDatos] = useState<DatosCliente>(CLIENTE_VACIO)
  const campo = (clave: keyof DatosCliente) => ({
    value: datos[clave],
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => setDatos({ ...datos, [clave]: e.target.value }),
  })

  const guardar = async () => {
    try {
      const cliente = await api.crearCliente(datos)
      toasts.exito(`${cliente.nombre} quedó registrado`)
      alCrear(cliente)
    } catch (e) {
      toasts.error(e, 'No se pudo crear el cliente')
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12, padding: 14, border: '1px dashed var(--c-border)', borderRadius: 8 }}>
      <b style={{ fontSize: 14 }}>Cliente nuevo</b>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
        <div className="field"><label className="label" htmlFor="cn-n">Nombre</label><input id="cn-n" className="input" {...campo('nombre')} /></div>
        <div className="field"><label className="label" htmlFor="cn-a">Apellido</label><input id="cn-a" className="input" {...campo('apellido')} /></div>
        <div className="field"><label className="label" htmlFor="cn-t">Teléfono</label><input id="cn-t" className="input" type="tel" {...campo('telefono')} /></div>
        <div className="field"><label className="label" htmlFor="cn-e">Email</label><input id="cn-e" className="input" type="email" {...campo('email')} /></div>
      </div>
      <div className="field"><label className="label" htmlFor="cn-d">Dirección</label><input id="cn-d" className="input" {...campo('direccion')} /></div>
      <div className="row" style={{ justifyContent: 'flex-end' }}>
        <button type="button" className="btn btn-ghost" onClick={alCancelar}>Cancelar</button>
        <button type="button" className="btn btn-primary" onClick={guardar}>Guardar cliente</button>
      </div>
    </div>
  )
}

function PedidoCreado({ pedido, alCerrar }: { pedido: Pedido; alCerrar: () => void }) {
  const toasts = useToasts()
  const copiar = async () => {
    try {
      await navigator.clipboard.writeText(pedido.codigo_seguimiento)
      toasts.exito('Código copiado')
    } catch {
      toasts.error('Copialo a mano: el navegador no dio permiso.', 'No se pudo copiar')
    }
  }

  return (
    <div className="overlay overlay-centro" onKeyDown={(e) => e.key === 'Escape' && alCerrar()}>
      <div className="scrim" onClick={alCerrar} />
      <div className="modal dely" role="dialog" aria-modal="true" aria-labelledby="pc-t" style={{ position: 'relative', width: 460, maxWidth: '100%', alignItems: 'center', textAlign: 'center', padding: 32 }}>
        <span className="empty-ic" style={{ width: 56, height: 56, background: 'var(--st-entregado-bg)', color: 'var(--c-success)' }}>
          <Icono nombre="check-circulo" tamano="xl" />
        </span>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <h2 id="pc-t" style={{ fontSize: 21, fontWeight: 700 }}>Pedido creado</h2>
          <p className="muted">Pasale este código a {pedido.cliente.nombre} para que siga su pedido.</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 12px 12px 20px', border: '1px dashed var(--c-muted)', borderRadius: 12, background: 'var(--c-surface-2)', width: '100%', justifyContent: 'space-between' }}>
          <span className="mono" style={{ fontSize: 30, fontWeight: 800, letterSpacing: '0.14em' }}>{pedido.codigo_seguimiento}</span>
          <button className="btn btn-secondary" onClick={copiar} autoFocus>
            <Icono nombre="copiar" />
            Copiar
          </button>
        </div>
        <span className="hint">
          {nombreCompleto(pedido.cliente)} · {pedido.zona} · {hora(pedido.horario_estimado)} · {moneda(pedido.total)}
        </span>
        <div className="row" style={{ width: '100%', gap: 10 }}>
          <Link className="btn btn-ghost btn-lg" to="/comercio" style={{ flex: '1 1 0' }}>Volver a pedidos</Link>
          <Link className="btn btn-primary btn-lg" to={`/comercio?pedido=${pedido.id_pedido}`} style={{ flex: '1 1 0' }}>Asignar repartidor</Link>
        </div>
      </div>
    </div>
  )
}

export function NuevoPedido() {
  const { comercio, refrescarContador } = useComercio()
  const toasts = useToasts()
  const navegar = useNavigate()
  const clientes = useApi(api.clientes, 'clientes')
  const productos = useApi(() => api.productos(comercio.id_comercio), `prod-${comercio.id_comercio}`)
  const repartidores = useApi(() => api.repartidores({ comercio_id: comercio.id_comercio }), `rep-${comercio.id_comercio}`)

  const [busqueda, setBusqueda] = useState('')
  const [cliente, setCliente] = useState<Cliente>()
  const [altaCliente, setAltaCliente] = useState(false)
  const [cantidades, setCantidades] = useState<Record<number, number>>({})
  const [direccion, setDireccion] = useState('')
  const [zona, setZona] = useState('')
  const [horario, setHorario] = useState(horaSugerida)
  const [creando, setCreando] = useState(false)
  const [creado, setCreado] = useState<Pedido>()

  const zonas = [...new Set((repartidores.datos ?? []).map((r) => r.zona))].sort()
  const zonaElegida = zona || zonas[0] || ''
  const coincidencias = (clientes.datos ?? []).filter((c) =>
    `${c.nombre} ${c.apellido} ${c.telefono}`.toLowerCase().includes(busqueda.trim().toLowerCase()),
  )
  const items = (productos.datos ?? []).filter((p) => (cantidades[p.id_producto] ?? 0) > 0)
  const total = items.reduce((suma, p) => suma + Number(p.precio) * cantidades[p.id_producto], 0)
  const unidades = items.reduce((suma, p) => suma + cantidades[p.id_producto], 0)

  const elegirCliente = (c: Cliente) => {
    setCliente(c)
    setDireccion(c.direccion)
    setAltaCliente(false)
  }

  const cambiarCantidad = (p: Producto, delta: number) =>
    setCantidades((actual) => ({
      ...actual,
      [p.id_producto]: Math.min(p.stock, Math.max(0, (actual[p.id_producto] ?? 0) + delta)),
    }))

  const crear = async (e: FormEvent) => {
    e.preventDefault()
    if (!cliente || items.length === 0) return
    setCreando(true)
    try {
      const pedido = await api.crearPedido({
        comercio_id: comercio.id_comercio,
        cliente_id: cliente.id_cliente,
        zona: zonaElegida,
        horario_estimado: horario,
        direccion_entrega: direccion || undefined,
        detalles: items.map((p) => ({ producto_id: p.id_producto, cantidad: cantidades[p.id_producto] })),
      })
      setCreado(pedido)
      refrescarContador()
    } catch (error) {
      toasts.error(error, 'No se pudo crear el pedido')
      void productos.recargar()
    } finally {
      setCreando(false)
    }
  }

  const errorCarga = clientes.error ?? productos.error ?? repartidores.error

  return (
    <>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <Link to="/comercio" className="row" style={{ gap: 4, fontSize: 13, fontWeight: 600, textDecoration: 'none' }}>
          <Icono nombre="atras" />
          Pedidos
        </Link>
        <h1 className="page-title">Nuevo pedido</h1>
      </div>

      {errorCarga && <ErrorCarga error={errorCarga} />}

      <form onSubmit={crear} style={{ display: 'flex', flexWrap: 'wrap', gap: 24, alignItems: 'flex-start' }}>
        <div style={{ flex: '999 1 520px', minWidth: 0, display: 'flex', flexDirection: 'column', gap: 20 }}>
          <section className="card card-pad" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <h2 style={{ fontSize: 16, fontWeight: 700 }}>1. Cliente</h2>
            {cliente ? (
              <div className="between" style={{ padding: '12px 14px', border: '2px solid var(--c-primary)', borderRadius: 8, background: 'var(--c-primary-soft)' }}>
                <span className="row" style={{ gap: 12 }}>
                  <span className="avatar">{iniciales(cliente)}</span>
                  <span style={{ display: 'flex', flexDirection: 'column' }}>
                    <b>{nombreCompleto(cliente)}</b>
                    <span className="muted" style={{ fontSize: 12 }}>{cliente.telefono} · {cliente.direccion}</span>
                  </span>
                </span>
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => setCliente(undefined)}>Cambiar</button>
              </div>
            ) : (
              <>
                <div className="field">
                  <label className="label" htmlFor="np-cli">Buscá un cliente</label>
                  <div className="input-icon">
                    <Icono nombre="buscar" />
                    <input id="np-cli" className="input" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} placeholder="Nombre, apellido o teléfono" autoComplete="off" />
                  </div>
                </div>
                {clientes.cargando ? (
                  <Esqueleto filas={2} alto={48} />
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 240, overflowY: 'auto' }}>
                    {coincidencias.slice(0, 6).map((c) => (
                      <button key={c.id_cliente} type="button" className="list-btn" style={{ minHeight: 56 }} onClick={() => elegirCliente(c)}>
                        <span className="avatar">{iniciales(c)}</span>
                        <span style={{ display: 'flex', flexDirection: 'column' }}>
                          <b>{nombreCompleto(c)}</b>
                          <span className="muted" style={{ fontSize: 12 }}>{c.telefono} · {c.direccion}</span>
                        </span>
                      </button>
                    ))}
                    {coincidencias.length === 0 && <span className="hint">No encontramos clientes con “{busqueda}”.</span>}
                  </div>
                )}
                {altaCliente ? (
                  <AltaCliente
                    alCancelar={() => setAltaCliente(false)}
                    alCrear={(c) => {
                      void clientes.recargar()
                      elegirCliente(c)
                    }}
                  />
                ) : (
                  <button type="button" className="btn btn-ghost btn-sm" style={{ alignSelf: 'flex-start' }} onClick={() => setAltaCliente(true)}>
                    <Icono nombre="mas" />
                    Cliente nuevo
                  </button>
                )}
              </>
            )}
          </section>

          <section className="card" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="between" style={{ padding: '16px 16px 8px' }}>
              <h2 style={{ fontSize: 16, fontWeight: 700 }}>2. Productos</h2>
              <span className="hint">El stock se descuenta al crear el pedido</span>
            </div>
            {productos.cargando && <div style={{ padding: 16 }}><Esqueleto filas={3} alto={48} /></div>}
            {(productos.datos ?? []).map((p) => {
              const cantidad = cantidades[p.id_producto] ?? 0
              const sinStock = p.stock === 0
              return (
                <div key={p.id_producto} className="prod" style={sinStock ? { opacity: 0.6 } : undefined}>
                  <span style={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                    <b>{p.nombre}</b>
                    <span style={{ fontSize: 12, display: 'flex', gap: 6, alignItems: 'center' }}>
                      <span className="muted">{p.categoria} · {moneda(p.precio)} ·</span>
                      {sinStock ? (
                        <span className="tag tag-danger" style={{ height: 18 }}>Sin stock</span>
                      ) : p.stock <= STOCK_BAJO ? (
                        <span className="tag tag-warn" style={{ height: 18 }}>Quedan {p.stock}</span>
                      ) : (
                        <span className="muted">Quedan {p.stock}</span>
                      )}
                    </span>
                  </span>
                  <div className="qty">
                    <button type="button" aria-label={`Restar ${p.nombre}`} disabled={cantidad === 0} onClick={() => cambiarCantidad(p, -1)}>−</button>
                    <span aria-live="polite">{cantidad}</span>
                    <button type="button" aria-label={`Sumar ${p.nombre}`} disabled={cantidad >= p.stock} onClick={() => cambiarCantidad(p, 1)}>+</button>
                  </div>
                  {cantidad > 0 ? (
                    <b style={{ width: 96, textAlign: 'right' }}>{moneda(Number(p.precio) * cantidad)}</b>
                  ) : (
                    <span className="muted" style={{ width: 96, textAlign: 'right' }}>—</span>
                  )}
                </div>
              )
            })}
          </section>

          <section className="card card-pad" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <h2 style={{ fontSize: 16, fontWeight: 700 }}>3. Entrega</h2>
            <div className="field">
              <label className="label" htmlFor="np-dir">Dirección de entrega</label>
              <input id="np-dir" className="input" value={direccion} onChange={(e) => setDireccion(e.target.value)} placeholder="Elegí un cliente primero" />
              <span className="hint">Por defecto, la del cliente. Podés cambiarla para este pedido.</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 14 }}>
              <div className="field">
                <label className="label" htmlFor="np-zona">Zona</label>
                {zonas.length > 0 ? (
                  <select id="np-zona" className="select" value={zonaElegida} onChange={(e) => setZona(e.target.value)}>
                    {zonas.map((z) => <option key={z}>{z}</option>)}
                  </select>
                ) : (
                  <input id="np-zona" className="input" value={zona} onChange={(e) => setZona(e.target.value)} required />
                )}
              </div>
              <div className="field">
                <label className="label" htmlFor="np-hora">Horario estimado</label>
                <input id="np-hora" className="input" type="time" value={horario} onChange={(e) => setHorario(e.target.value)} required />
              </div>
            </div>
          </section>
        </div>

        <aside className="card" aria-label="Resumen del pedido" style={{ flex: '1 1 320px', minWidth: 0, padding: 20, display: 'flex', flexDirection: 'column', gap: 14, boxShadow: 'var(--sh-2)', position: 'sticky', top: 24 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700 }}>Resumen</h2>
          {items.length === 0 ? (
            <span className="hint">Sumá productos para ver el total.</span>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 14 }}>
              {items.map((p) => (
                <div key={p.id_producto} className="between">
                  <span>{cantidades[p.id_producto]} × {p.nombre}</span>
                  <span>{moneda(Number(p.precio) * cantidades[p.id_producto])}</span>
                </div>
              ))}
            </div>
          )}
          <hr className="divider" />
          <div className="between" style={{ alignItems: 'baseline' }}>
            <span style={{ fontWeight: 600 }}>Total</span>
            <span style={{ fontSize: 30, fontWeight: 800, letterSpacing: '-0.02em' }} aria-live="polite">{moneda(total)}</span>
          </div>
          <div className="muted" style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: 13 }}>
            <span>{cliente ? nombreCompleto(cliente) : 'Sin cliente'} · {zonaElegida || 'sin zona'} · {horario}</span>
            <span>{plural(unidades, 'producto')}</span>
          </div>
          <button className="btn btn-primary btn-lg" style={{ width: '100%' }} disabled={!cliente || items.length === 0 || creando}>
            {creando && <span className="spinner" />}
            Crear pedido
          </button>
          <span className="hint" style={{ textAlign: 'center' }}>
            {cliente ? `Al crearlo te damos el código para pasarle a ${cliente.nombre}.` : 'Elegí un cliente y al menos un producto.'}
          </span>
        </aside>
      </form>

      {creado && <PedidoCreado pedido={creado} alCerrar={() => navegar('/comercio')} />}
    </>
  )
}
