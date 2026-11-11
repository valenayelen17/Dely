import { createContext, useContext } from 'react'

export interface ApiToasts {
  exito: (titulo: string, detalle?: string) => void
  error: (error: unknown, titulo?: string) => void
}

export const ContextoToasts = createContext<ApiToasts | null>(null)

export function useToasts(): ApiToasts {
  const contexto = useContext(ContextoToasts)
  if (!contexto) throw new Error('useToasts requiere ProveedorToasts')
  return contexto
}
