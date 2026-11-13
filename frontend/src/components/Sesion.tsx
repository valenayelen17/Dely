import { useCallback, useMemo, useState, type ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router'
import { api } from '../api/dely'
import type { Rol, Sesion } from '../api/tipos'
import { ContextoSesion, INICIO_POR_ROL, useSesion, type ApiSesion } from '../hooks/useSesion'
import { borrarSesion, guardarSesion, leerSesion } from '../lib/sesion'

export function ProveedorSesion({ children }: { children: ReactNode }) {
  const [sesion, setSesion] = useState<Sesion | null>(() => leerSesion())

  const iniciar = useCallback(async (email: string, password: string) => {
    const respuesta = await api.login(email, password)
    if (respuesta.usuario.rol === 'encargado') {
      throw new Error('Esta cuenta es de encargado. Ingresá desde el panel del comercio.')
    }
    const nueva: Sesion = { token: respuesta.access_token, expira: respuesta.expira, usuario: respuesta.usuario }
    guardarSesion(nueva)
    setSesion(nueva)
    return respuesta.usuario
  }, [])

  const cerrar = useCallback(() => {
    borrarSesion()
    setSesion(null)
  }, [])

  const valor = useMemo<ApiSesion>(
    () => ({ sesion, usuario: sesion?.usuario ?? null, iniciar, cerrar }),
    [sesion, iniciar, cerrar],
  )
  return <ContextoSesion.Provider value={valor}>{children}</ContextoSesion.Provider>
}

/** Muestra la ruta sólo si hay sesión del rol pedido; si no, manda al login o a la pantalla de su rol. */
export function RequiereRol({ rol, children }: { rol: Exclude<Rol, 'encargado'>; children: ReactNode }) {
  const { usuario } = useSesion()
  const ubicacion = useLocation()
  if (!usuario) {
    return <Navigate to={`/login?siguiente=${encodeURIComponent(ubicacion.pathname)}`} replace />
  }
  if (usuario.rol !== rol) {
    return <Navigate to={usuario.rol === 'encargado' ? '/login' : INICIO_POR_ROL[usuario.rol]} replace />
  }
  return children
}

/** "/" lleva al inicio del rol logueado, o al login. */
export function RedirigirSegunRol() {
  const { usuario } = useSesion()
  if (!usuario || usuario.rol === 'encargado') return <Navigate to="/login" replace />
  return <Navigate to={INICIO_POR_ROL[usuario.rol]} replace />
}
