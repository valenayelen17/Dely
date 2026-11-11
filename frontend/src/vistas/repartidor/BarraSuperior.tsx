import type { ReactNode } from 'react'
import { Link } from 'react-router'
import { Icono } from '../../components/Icono'

export function BarraSuperior({ volverA, etiquetaVolver, children }: { volverA: string; etiquetaVolver: string; children: ReactNode }) {
  return (
    <div className="topbar">
      <Link className="btn btn-ghost btn-icon" to={volverA} aria-label={etiquetaVolver} style={{ minHeight: 44, width: 44 }}>
        <Icono nombre="atras" tamano="lg" />
      </Link>
      {children}
    </div>
  )
}
