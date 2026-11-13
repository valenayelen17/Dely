import type { ReactNode } from 'react'
import { Link, NavLink } from 'react-router'
import { useSesion } from '../hooks/useSesion'
import { iniciales } from '../lib/formato'
import { Icono, type NombreIcono } from './Icono'
import { Logo } from './Logo'

const NAVEGACION: Record<'repartidor' | 'cliente', { a: string; texto: string; icono: NombreIcono }[]> = {
  repartidor: [{ a: '/entregas', texto: 'Mis entregas', icono: 'camion' }],
  cliente: [{ a: '/pedidos', texto: 'Mis pedidos', icono: 'caja' }],
}

const ROL_VISIBLE = { repartidor: 'Repartidor', cliente: 'Cliente', encargado: 'Encargado' }

/** Estructura de escritorio: barra superior fija y contenido centrado y ancho. */
export function Layout({ children }: { children: ReactNode }) {
  const { usuario, cerrar } = useSesion()
  const enlaces = usuario && usuario.rol !== 'encargado' ? NAVEGACION[usuario.rol] : []
  const [nombre, apellido] = (usuario?.nombre ?? '').split(' ')

  const salir = () => {
    cerrar()
    // Recarga completa: no queda en memoria ningún dato de la sesión anterior.
    window.location.replace('/login')
  }

  return (
    <div className="dely shell">
      <header className="shell-header">
        <div className="shell-header-in">
          <Logo />
          <nav className="shell-nav" aria-label="Principal">
            {enlaces.map((e) => (
              <NavLink key={e.a} to={e.a} className="shell-nav-link">
                <Icono nombre={e.icono} />
                {e.texto}
              </NavLink>
            ))}
          </nav>
          {usuario && (
            <div className="shell-user">
              <span className="avatar">{iniciales({ nombre: nombre ?? '', apellido })}</span>
              <span className="shell-user-txt">
                <b>{usuario.nombre}</b>
                <span className="muted">{ROL_VISIBLE[usuario.rol]} · {usuario.email}</span>
              </span>
              <button className="btn btn-ghost btn-sm" onClick={salir}>
                Salir
              </button>
            </div>
          )}
        </div>
      </header>
      <main className="shell-main">{children}</main>
    </div>
  )
}

interface EncabezadoProps {
  titulo: ReactNode
  bajada?: ReactNode
  volver?: { a: string; texto: string }
  acciones?: ReactNode
}

/** Título de página con migas de "volver" y acciones a la derecha. */
export function Encabezado({ titulo, bajada, volver, acciones }: EncabezadoProps) {
  return (
    <div className="page-head">
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, minWidth: 0 }}>
        {volver && (
          <Link to={volver.a} className="back-link">
            <Icono nombre="atras" />
            {volver.texto}
          </Link>
        )}
        <h1 className="page-title">{titulo}</h1>
        {bajada && <p className="muted" style={{ fontSize: 15 }}>{bajada}</p>}
      </div>
      {acciones && <div className="row" style={{ gap: 12, flexWrap: 'wrap' }}>{acciones}</div>}
    </div>
  )
}

/** Indicador numérico de la cabecera de una página. */
export function Indicador({ etiqueta, valor, icono, tono = 'neutro' }: { etiqueta: string; valor: ReactNode; icono: NombreIcono; tono?: 'neutro' | 'marca' | 'alerta' | 'ok' }) {
  return (
    <div className={`stat stat-${tono}`}>
      <span className="stat-ic"><Icono nombre={icono} tamano="lg" /></span>
      <span style={{ display: 'flex', flexDirection: 'column' }}>
        <span className="stat-valor">{valor}</span>
        <span className="muted" style={{ fontSize: 13 }}>{etiqueta}</span>
      </span>
    </div>
  )
}
