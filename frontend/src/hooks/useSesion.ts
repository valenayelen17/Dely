import { createContext, useContext } from 'react'
import type { Sesion, Usuario } from '../api/tipos'

export interface ApiSesion {
  sesion: Sesion | null
  usuario: Usuario | null
  iniciar: (email: string, password: string) => Promise<Usuario>
  cerrar: () => void
}

export const ContextoSesion = createContext<ApiSesion | null>(null)

export function useSesion(): ApiSesion {
  const contexto = useContext(ContextoSesion)
  if (!contexto) throw new Error('useSesion requiere ProveedorSesion')
  return contexto
}

// Pantalla de inicio de cada rol después del login.
export const INICIO_POR_ROL = {
  repartidor: '/entregas',
  cliente: '/pedidos',
} as const
