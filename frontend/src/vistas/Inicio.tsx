import { Link } from 'react-router'
import { Icono, type NombreIcono } from '../components/Icono'
import { Logo } from '../components/Logo'
import { PANEL_URL } from '../lib/panel'

interface Rol {
  a: string
  titulo: string
  texto: string
  accion: string
  icono: NombreIcono
  fondo: string
  color: string
  externo?: boolean
}

const ROLES: Rol[] = [
  {
    a: PANEL_URL,
    externo: true,
    titulo: 'Comercio',
    texto: 'Cargá pedidos, asigná repartidores y seguí cada entrega en el panel del encargado.',
    accion: 'Abrir el panel',
    icono: 'tienda',
    fondo: 'var(--c-brand-soft)',
    color: 'var(--c-brand-ink)',
  },
  {
    a: '/repartidor',
    titulo: 'Repartidor',
    texto: 'Mirá tus entregas del turno y avisá cuando salís, cuando llegás y cuando entregás.',
    accion: 'Entrar como repartidor',
    icono: 'camion',
    fondo: 'var(--st-camino-bg)',
    color: 'var(--st-camino-fg)',
  },
  {
    a: '/seguimiento',
    titulo: 'Seguí tu pedido',
    texto: 'Ingresá el código que te pasó el comercio y mirá dónde está tu pedido.',
    accion: 'Ingresar código',
    icono: 'pin',
    fondo: 'var(--st-asignado-bg)',
    color: 'var(--st-asignado-fg)',
  },
]

export function Inicio() {
  return (
    <div className="dely dely-root" style={{ display: 'flex', flexDirection: 'column' }}>
      <header style={{ display: 'flex', alignItems: 'center', padding: '20px 32px' }}>
        <Logo />
      </header>
      <main
        style={{
          flexGrow: 1,
          width: '100%',
          maxWidth: 1120,
          margin: '0 auto',
          padding: '48px 24px 64px',
          display: 'flex',
          flexDirection: 'column',
          gap: 40,
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxWidth: 640 }}>
          <span className="overline">Entregas de última milla</span>
          <h1 style={{ fontSize: 40, lineHeight: 1.15, fontWeight: 800, letterSpacing: '-0.02em' }}>¿Cómo querés entrar?</h1>
          <p style={{ fontSize: 18, color: 'var(--c-ink-2)' }}>Elegí tu rol para ver tu pantalla. Sin usuarios ni contraseñas.</p>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 20 }}>
          {ROLES.map((rol) => {
            const contenido = (
              <>
                <span className="role-ic" style={{ background: rol.fondo, color: rol.color }}>
                  <Icono nombre={rol.icono} tamano="xl" />
                </span>
                <span style={{ fontSize: 24, fontWeight: 700 }}>{rol.titulo}</span>
                <span style={{ color: 'var(--c-ink-2)', flexGrow: 1 }}>{rol.texto}</span>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontWeight: 700, color: 'var(--c-primary)' }}>
                  {rol.accion}
                  <Icono nombre="adelante" />
                </span>
              </>
            )
            // El panel del comercio es otra aplicación (Django): se abre con un link común.
            return rol.externo ? (
              <a key={rol.a} className="role" href={rol.a}>
                {contenido}
              </a>
            ) : (
              <Link key={rol.a} className="role" to={rol.a}>
                {contenido}
              </Link>
            )
          })}
        </div>
      </main>
    </div>
  )
}
