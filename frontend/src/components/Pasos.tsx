import { Icono } from './Icono'

interface Props {
  etiquetas: string[]
  actual: number
  indiceLlegando?: number
  etiquetaAccesible: string
}

export function Pasos({ etiquetas, actual, indiceLlegando, etiquetaAccesible }: Props) {
  return (
    <ol className="steps" style={{ listStyle: 'none', margin: 0, padding: 0 }} aria-label={etiquetaAccesible}>
      {etiquetas.map((etiqueta, i) => {
        const terminado = i < actual || actual >= etiquetas.length
        const esActual = i === actual
        const clase = [
          'step',
          terminado && 'is-done',
          esActual && 'is-current',
          esActual && i === indiceLlegando && 'is-arriving',
        ]
          .filter(Boolean)
          .join(' ')
        return (
          <li key={etiqueta} className={clase} aria-current={esActual ? 'step' : undefined}>
            <span className="step-dot">
              <Icono nombre="check" />
            </span>
            {etiqueta}
          </li>
        )
      })}
    </ol>
  )
}
