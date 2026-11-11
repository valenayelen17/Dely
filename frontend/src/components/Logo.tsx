import { Link } from 'react-router'
import { Icono } from './Icono'

interface Props {
  tamano?: number
  conPunto?: boolean
}

export function Logo({ tamano = 20, conPunto = true }: Props) {
  const marca = Math.round(tamano * 1.5)
  return (
    <Link className="logo" to="/" style={{ fontSize: tamano }} aria-label="DELY, volver al inicio">
      <span className="logo-mark" style={{ width: marca, height: marca }}>
        <Icono nombre="logo" tamano={tamano > 20 ? 'lg' : 'md'} />
      </span>
      <span>
        DELY
        {conPunto && <span className="logo-dot">.</span>}
      </span>
    </Link>
  )
}
