import type { Sesion } from '../api/tipos'

// El JWT se guarda en localStorage para que la sesión sobreviva a un refresco de la página.
const CLAVE = 'dely.sesion'

export function leerSesion(): Sesion | null {
  try {
    const guardada = localStorage.getItem(CLAVE)
    if (!guardada) return null
    const sesion = JSON.parse(guardada) as Sesion
    if (new Date(sesion.expira).getTime() <= Date.now()) {
      borrarSesion()
      return null
    }
    return sesion
  } catch {
    return null
  }
}

export function guardarSesion(sesion: Sesion) {
  try {
    localStorage.setItem(CLAVE, JSON.stringify(sesion))
  } catch {
    // Sin almacenamiento disponible la sesión dura hasta recargar la página.
  }
}

export function borrarSesion() {
  try {
    localStorage.removeItem(CLAVE)
  } catch {
    // nada que borrar
  }
}
