import { NavLink, Outlet } from 'react-router'
import { api } from '../../api/dely'
import { ErrorCarga, Esqueleto, EstadoVacio } from '../../components/Estados'
import { Icono, type NombreIcono } from '../../components/Icono'
import { Logo } from '../../components/Logo'
import type { ContextoComercio } from '../../hooks/useComercio'
import { useApi } from '../../hooks/useApi'

const SECCIONES: { a: string; texto: string; icono: NombreIcono; fin?: boolean }[] = [
  { a: '/comercio', texto: 'Pedidos', icono: 'caja', fin: true },
  { a: '/comercio/nuevo', texto: 'Nuevo pedido', icono: 'mas' },
  { a: '/comercio/repartidores', texto: 'Repartidores', icono: 'camion' },
  { a: '/comercio/productos', texto: 'Productos', icono: 'producto' },
  { a: '/comercio/clientes', texto: 'Clientes', icono: 'persona' },
  { a: '/comercio/historial', texto: 'Historial', icono: 'historial' },
]

export function LayoutEncargado() {
  const comercios = useApi(api.comercios, 'comercios')
  const comercio = comercios.datos?.[0]
  const pendientes = useApi(comercio ? () => api.pendientes(comercio.id_comercio) : null, String(comercio?.id_comercio), 10_000)
  const sinAsignar = pendientes.datos?.filter((p) => p.estado === 'Pendiente').length ?? 0

  let contenido
  if (comercios.error) contenido = <ErrorCarga error={comercios.error} reintentar={comercios.recargar} />
  else if (comercios.cargando) contenido = <Esqueleto />
  else if (!comercio)
    contenido = (
      <EstadoVacio icono="tienda" titulo="Todavía no hay ningún comercio cargado">
        Corré <code>python seed.py</code> en el backend para cargar los datos de demo.
      </EstadoVacio>
    )
  else {
    const contexto: ContextoComercio = { comercio, refrescarContador: () => void pendientes.recargar() }
    contenido = <Outlet context={contexto} />
  }

  return (
    <div className="dely app">
      <aside className="side">
        <Logo />
        <nav className="nav" aria-label="Secciones">
          {SECCIONES.map((s) => (
            <NavLink key={s.a} to={s.a} end={s.fin}>
              <Icono nombre={s.icono} />
              {s.texto}
              {s.a === '/comercio' && sinAsignar > 0 && (
                <span className="count" aria-label={`${sinAsignar} sin asignar`}>
                  {sinAsignar}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
        {comercio && (
          <div
            style={{
              marginTop: 'auto',
              padding: 12,
              borderRadius: 8,
              background: 'var(--c-bg)',
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
            }}
          >
            <span style={{ fontWeight: 700, fontSize: 13 }}>{comercio.nombre}</span>
            <span className="muted" style={{ fontSize: 12 }}>
              Encargado
            </span>
          </div>
        )}
      </aside>
      <main className="main">{contenido}</main>
    </div>
  )
}
