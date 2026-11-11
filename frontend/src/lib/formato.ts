const pesos = new Intl.NumberFormat('es-AR', { maximumFractionDigits: 0 })

export const moneda = (valor: string | number) => `$ ${pesos.format(Number(valor))}`

export const hora = (valor: string | null | undefined) => (valor ? valor.slice(0, 5) : '')

export const horaDeFecha = (fechaHora: string) => fechaHora.slice(11, 16)

export const nombreCompleto = (p: { nombre: string; apellido: string }) => `${p.nombre} ${p.apellido}`

export const iniciales = (p: { nombre: string; apellido?: string }) =>
  `${p.nombre[0] ?? ''}${p.apellido?.[0] ?? ''}`.toUpperCase()

export const cantidadProductos = (detalles: { cantidad: number }[]) =>
  detalles.reduce((total, d) => total + d.cantidad, 0)

export const plural = (n: number, singular: string, pluralTexto = `${singular}s`) =>
  `${n} ${n === 1 ? singular : pluralTexto}`

export function horaSugerida(minutos = 45): string {
  const fecha = new Date(Date.now() + minutos * 60_000)
  fecha.setMinutes(Math.ceil(fecha.getMinutes() / 15) * 15)
  return `${String(fecha.getHours()).padStart(2, '0')}:${String(fecha.getMinutes()).padStart(2, '0')}`
}
