import { borrarSesion, leerSesion } from '../lib/sesion'

const BASE_URL = import.meta.env.VITE_API_URL ?? ''

export class ErrorApi extends Error {
  readonly status: number

  constructor(status: number, mensaje: string) {
    super(mensaje)
    this.status = status
  }
}

export async function pedirApi<T>(ruta: string, opciones: RequestInit = {}): Promise<T> {
  const token = leerSesion()?.token
  const respuesta = await fetch(`${BASE_URL}${ruta}`, {
    ...opciones,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...opciones.headers,
    },
  })
  if (!respuesta.ok) {
    const cuerpo = await respuesta.json().catch(() => null)
    const detalle = typeof cuerpo?.detail === 'string' ? cuerpo.detail : respuesta.statusText
    // Token vencido o inválido: se cierra la sesión y se vuelve al login.
    if (respuesta.status === 401 && token) {
      borrarSesion()
      window.location.assign('/login?vencida=1')
    }
    throw new ErrorApi(respuesta.status, detalle)
  }
  return (respuesta.status === 204 ? undefined : await respuesta.json()) as T
}
