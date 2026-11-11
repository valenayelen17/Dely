import { useCallback, useMemo, useState, type ReactNode } from 'react'
import { ContextoToasts, type ApiToasts } from '../hooks/useToasts'
import { Icono } from './Icono'

type Tipo = 'exito' | 'error'

interface Toast {
  id: number
  tipo: Tipo
  titulo: string
  detalle?: string
}

export function ProveedorToasts({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const quitar = useCallback((id: number) => setToasts((lista) => lista.filter((t) => t.id !== id)), [])

  const agregar = useCallback(
    (tipo: Tipo, titulo: string, detalle?: string) => {
      const id = Date.now() + Math.random()
      setToasts((lista) => [...lista.slice(-2), { id, tipo, titulo, detalle }])
      window.setTimeout(() => quitar(id), tipo === 'error' ? 7000 : 4000)
    },
    [quitar],
  )

  const api = useMemo<ApiToasts>(
    () => ({
      exito: (titulo, detalle) => agregar('exito', titulo, detalle),
      error: (error, titulo = 'No se pudo completar la acción') =>
        agregar('error', titulo, error instanceof Error ? error.message : String(error)),
    }),
    [agregar],
  )

  return (
    <ContextoToasts.Provider value={api}>
      {children}
      <div className="toasts" aria-live="polite">
        {toasts.map((t) => (
          <div key={t.id} className={`toast ${t.tipo === 'error' ? 'toast-error' : 'toast-success'}`} role="status">
            <Icono nombre={t.tipo === 'error' ? 'error' : 'check-circulo'} tamano="lg" className="toast-ic" />
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span className="toast-title">{t.titulo}</span>
              {t.detalle && <span style={{ opacity: 0.85 }}>{t.detalle}</span>}
            </div>
            <button className="toast-cerrar" onClick={() => quitar(t.id)} aria-label="Cerrar aviso">
              <Icono nombre="cerrar" />
            </button>
          </div>
        ))}
      </div>
    </ContextoToasts.Provider>
  )
}
