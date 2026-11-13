import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate, useSearchParams } from 'react-router'
import { Icono, type NombreIcono } from '../components/Icono'
import { Logo } from '../components/Logo'
import { INICIO_POR_ROL, useSesion } from '../hooks/useSesion'

const PUNTOS: { icono: NombreIcono; titulo: string; texto: string }[] = [
  { icono: 'camion', titulo: 'Repartidores', texto: 'Mirá tus entregas del turno y avisá cuando salís, cuando llegás y cuando entregás.' },
  { icono: 'pin', titulo: 'Clientes', texto: 'Seguí tus pedidos en vivo y recibí el aviso cuando el repartidor está llegando.' },
]

export function Login() {
  const { usuario, iniciar } = useSesion()
  const navegar = useNavigate()
  const [params] = useSearchParams()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  if (usuario && usuario.rol !== 'encargado') {
    return <Navigate to={INICIO_POR_ROL[usuario.rol]} replace />
  }

  const ingresar = async (ev: FormEvent) => {
    ev.preventDefault()
    setError('')
    setEnviando(true)
    try {
      const yo = await iniciar(email.trim(), password)
      const siguiente = params.get('siguiente')
      const destino = yo.rol === 'encargado' ? '/login' : INICIO_POR_ROL[yo.rol]
      // Sólo se vuelve a una ruta interna de la app, nunca a otro sitio.
      navegar(siguiente?.startsWith(destino) ? siguiente : destino, { replace: true })
    } catch (e) {
      setError(e instanceof Error && e.message !== 'Failed to fetch' ? e.message : 'No pudimos conectar con el servidor. Probá de nuevo.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="dely login">
      <aside className="login-marca">
        <Logo tamano={24} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, maxWidth: 480 }}>
          <span className="overline" style={{ color: 'rgba(255,255,255,0.75)' }}>Entregas de última milla</span>
          <h1 style={{ fontSize: 40, lineHeight: 1.15, fontWeight: 800, letterSpacing: '-0.02em' }}>
            Cada pedido, de la cocina a la puerta.
          </h1>
        </div>
        <div className="login-puntos" style={{ display: 'flex', flexDirection: 'column', gap: 20, maxWidth: 480 }}>
          {PUNTOS.map((p) => (
            <div key={p.titulo} className="login-punto">
              <span className="ic-burbuja"><Icono nombre={p.icono} tamano="lg" /></span>
              <span style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <b>{p.titulo}</b>
                <span style={{ opacity: 0.85 }}>{p.texto}</span>
              </span>
            </div>
          ))}
        </div>
      </aside>

      <section className="login-form">
        <form onSubmit={ingresar} noValidate>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <h2 style={{ fontSize: 28, fontWeight: 800, letterSpacing: '-0.01em' }}>Iniciá sesión</h2>
            <p className="muted" style={{ fontSize: 15 }}>Usá el email y la contraseña que te dio el comercio.</p>
          </div>

          {params.get('vencida') && !error && (
            <div className="inline-alert inline-alert-warn" role="status">
              <Icono nombre="reloj" tamano="lg" />
              <span>Tu sesión venció. Volvé a ingresar.</span>
            </div>
          )}
          {error && (
            <div className="inline-alert inline-alert-error" role="alert">
              <Icono nombre="error" tamano="lg" />
              <span>{error}</span>
            </div>
          )}

          <div className="field">
            <label className="label" htmlFor="lg-email">Email</label>
            <input id="lg-email" className="input" type="email" autoComplete="username" autoFocus required value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div className="field">
            <label className="label" htmlFor="lg-pass">Contraseña</label>
            <input id="lg-pass" className="input" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          <button className="btn btn-primary btn-lg" disabled={enviando || !email.trim() || !password}>
            {enviando && <span className="spinner" />}
            Ingresar
          </button>
        </form>
      </section>
    </div>
  )
}
