import { useCallback, useEffect, useRef, useState } from 'react'

interface Resultado<T> {
  datos: T | undefined
  error: Error | undefined
  cargando: boolean
  recargar: () => Promise<void>
}

export function useApi<T>(pedir: (() => Promise<T>) | null, clave: string, refrescoMs?: number): Resultado<T> {
  const [datos, setDatos] = useState<T>()
  const [error, setError] = useState<Error>()
  const [cargando, setCargando] = useState(pedir !== null)
  const pedirRef = useRef(pedir)

  useEffect(() => {
    pedirRef.current = pedir
  })

  const recargar = useCallback(async () => {
    const actual = pedirRef.current
    if (!actual) return
    try {
      setDatos(await actual())
      setError(undefined)
    } catch (e) {
      setError(e instanceof Error ? e : new Error(String(e)))
    } finally {
      setCargando(false)
    }
  }, [])

  useEffect(() => {
    setCargando(pedirRef.current !== null)
    void recargar()
    if (!refrescoMs) return
    const id = window.setInterval(() => void recargar(), refrescoMs)
    return () => window.clearInterval(id)
  }, [recargar, refrescoMs, clave])

  return { datos, error, cargando, recargar }
}
