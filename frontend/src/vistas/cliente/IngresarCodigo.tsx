import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router'
import { api } from '../../api/dely'
import { ErrorApi } from '../../api/cliente'
import { Icono } from '../../components/Icono'
import { Logo } from '../../components/Logo'
import { BarraSuperior } from '../repartidor/BarraSuperior'

export function IngresarCodigo() {
  const navegar = useNavigate()
  const [codigo, setCodigo] = useState('')
  const [error, setError] = useState<string>()
  const [buscando, setBuscando] = useState(false)

  const buscar = async (e: FormEvent) => {
    e.preventDefault()
    const limpio = codigo.trim().toUpperCase()
    setBuscando(true)
    try {
      await api.seguimiento(limpio)
      navegar(`/seguimiento/${limpio}`)
    } catch (err) {
      setError(
        err instanceof ErrorApi && err.status === 404
          ? 'No encontramos un pedido con ese código. Revisalo con el comercio: no importa si va en mayúsculas o minúsculas.'
          : 'No pudimos consultar tu pedido. Probá de nuevo en un rato.',
      )
    } finally {
      setBuscando(false)
    }
  }

  return (
    <div className="dely phone" style={{ background: '#fff' }}>
      <BarraSuperior volverA="/" etiquetaVolver="Volver al inicio">
        <span />
      </BarraSuperior>
      <div style={{ padding: '16px 24px 32px', display: 'flex', flexDirection: 'column', gap: 28 }}>
        <Logo tamano={22} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <h1 style={{ fontSize: 32, lineHeight: 1.15, fontWeight: 800, letterSpacing: '-0.02em' }}>Seguí tu pedido</h1>
          <p style={{ color: 'var(--c-ink-2)' }}>Ingresá el código de 8 caracteres que te pasó el comercio.</p>
        </div>
        <form onSubmit={buscar} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="field">
            <label className="label" htmlFor="cg-code">Código de seguimiento</label>
            <input
              id="cg-code"
              className={`input mono${error ? ' is-error' : ''}`}
              value={codigo}
              onChange={(e) => {
                setCodigo(e.target.value.toUpperCase())
                setError(undefined)
              }}
              maxLength={8}
              autoComplete="off"
              autoCapitalize="characters"
              spellCheck={false}
              aria-invalid={Boolean(error)}
              aria-describedby={error ? 'cg-err' : undefined}
              style={{ height: 60, fontSize: 26, fontWeight: 700, letterSpacing: '0.2em', textAlign: 'center' }}
            />
            {error && (
              <span id="cg-err" className="error-text" style={{ fontSize: 14, alignItems: 'flex-start' }}>
                <Icono nombre="error" />
                {error}
              </span>
            )}
          </div>
          <button className="btn btn-primary btn-xl" disabled={codigo.trim().length < 8 || buscando}>
            {buscando && <span className="spinner" />}
            Seguir mi pedido
          </button>
        </form>
        <div className="inline-alert" style={{ background: 'var(--c-bg)', color: 'var(--c-ink-2)', fontSize: 13 }}>
          <Icono nombre="info" />
          <span>El código viene en el mensaje del comercio y tiene 8 letras y números.</span>
        </div>
      </div>
    </div>
  )
}
