const pesos = new Intl.NumberFormat('es-AR', { maximumFractionDigits: 0 })

export const moneda = (valor: string | number) => `$ ${pesos.format(Number(valor))}`

export const hora = (valor: string | null | undefined) => (valor ? valor.slice(0, 5) : '')

export const horaDeFecha = (fechaHora: string) => fechaHora.slice(11, 16)

export const nombreCompleto = (p: { nombre: string; apellido: string }) => `${p.nombre} ${p.apellido}`

export const iniciales = (p: { nombre: string; apellido?: string }) =>
  `${p.nombre[0] ?? ''}${p.apellido?.[0] ?? ''}`.toUpperCase()

export const plural = (n: number, singular: string, pluralTexto = `${singular}s`) =>
  `${n} ${n === 1 ? singular : pluralTexto}`

