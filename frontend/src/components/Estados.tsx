import type { ReactNode } from 'react'
import { Icono, type NombreIcono } from './Icono'

interface VacioProps {
  icono?: NombreIcono
  titulo: string
  children?: ReactNode
}

export function EstadoVacio({ icono = 'caja', titulo, children }: VacioProps) {
  return (
    <div className="empty">
      <span className="empty-ic">
        <Icono nombre={icono} tamano="lg" />
      </span>
      <b>{titulo}</b>
      {children && <span className="muted" style={{ fontSize: 13 }}>{children}</span>}
    </div>
  )
}

export function Esqueleto({ filas = 3, alto = 72 }: { filas?: number; alto?: number }) {
  return (
    <div className="cargando-pagina" aria-busy="true" aria-label="Cargando">
      {Array.from({ length: filas }, (_, i) => (
        <div key={i} className="sk" style={{ height: alto }} />
      ))}
    </div>
  )
}

export function ErrorCarga({ error, reintentar }: { error: Error; reintentar?: () => void }) {
  return (
    <div className="inline-alert inline-alert-error" role="alert">
      <Icono nombre="error" tamano="lg" />
      <span style={{ display: 'flex', flexDirection: 'column', gap: 6, alignItems: 'flex-start' }}>
        <b>No pudimos cargar los datos.</b>
        <span>{error.message === 'Failed to fetch' ? '¿Está corriendo la API en el puerto 8000?' : error.message}</span>
        {reintentar && (
          <button className="btn btn-secondary btn-sm" onClick={reintentar}>
            Reintentar
          </button>
        )}
      </span>
    </div>
  )
}
