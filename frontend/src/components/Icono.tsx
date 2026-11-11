const TRAZOS = {
  logo: <><path d="M4 12h11" /><path d="M11 6l6 6-6 6" /><path d="M20 5v14" /></>,
  reloj: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
  'persona-check': <><circle cx="9" cy="8" r="4" /><path d="M2 21c0-4 3-7 7-7s7 3 7 7" /><path d="M16 11l2 2 4-4" /></>,
  persona: <><circle cx="9" cy="8" r="4" /><path d="M2 21c0-4 3-7 7-7s7 3 7 7" /></>,
  camion: <><path d="M3 6h11v10H3z" /><path d="M14 10h4l3 3v3h-7" /><circle cx="7" cy="18" r="2" /><circle cx="17" cy="18" r="2" /></>,
  pin: <><path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z" /><circle cx="12" cy="10" r="2.5" /></>,
  'check-circulo': <><circle cx="12" cy="12" r="9" /><path d="M8 12l3 3 5-6" /></>,
  'x-circulo': <><circle cx="12" cy="12" r="9" /><path d="M9 9l6 6M15 9l-6 6" /></>,
  check: <path d="M5 12l4 4 10-10" />,
  alerta: <><path d="M12 3l10 18H2z" /><path d="M12 10v4M12 17h.01" /></>,
  info: <><circle cx="12" cy="12" r="9" /><path d="M12 11v5M12 8h.01" /></>,
  error: <><circle cx="12" cy="12" r="9" /><path d="M12 8v5M12 16h.01" /></>,
  campana: <><path d="M6 16V11a6 6 0 0 1 12 0v5l2 2H4z" /><path d="M10 20a2 2 0 0 0 4 0" /></>,
  caja: <><path d="M3 7l9-4 9 4v10l-9 4-9-4z" /><path d="M3 7l9 4 9-4M12 11v10" /></>,
  mas: <path d="M12 5v14M5 12h14" />,
  editar: <path d="M4 20h4L19 9l-4-4L4 16z" />,
  cerrar: <path d="M6 6l12 12M18 6L6 18" />,
  atras: <path d="M15 6l-6 6 6 6" />,
  adelante: <path d="M9 6l6 6-6 6" />,
  tienda: <><path d="M4 10v10h16V10" /><path d="M3 10l2-6h14l2 6z" /><path d="M10 20v-5h4v5" /></>,
  telefono: <path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z" />,
  copiar: <><rect x="9" y="9" width="11" height="11" rx="2" /><path d="M5 15V5a1 1 0 0 1 1-1h10" /></>,
  buscar: <><circle cx="11" cy="11" r="7" /><path d="M20 20l-4-4" /></>,
  historial: <><path d="M3 12a9 9 0 1 0 3-6.7L3 8" /><path d="M3 3v5h5" /><path d="M12 7v5l3 2" /></>,
  producto: <><circle cx="12" cy="12" r="9" /><path d="M12 3v18M3 12h18" /></>,
}

export type NombreIcono = keyof typeof TRAZOS

interface Props {
  nombre: NombreIcono
  tamano?: 'md' | 'lg' | 'xl'
  className?: string
}

export function Icono({ nombre, tamano = 'md', className = '' }: Props) {
  const clase = ['ic', tamano === 'lg' && 'ic-lg', tamano === 'xl' && 'ic-xl', className].filter(Boolean).join(' ')
  return (
    <svg className={clase} viewBox="0 0 24 24" aria-hidden="true">
      {TRAZOS[nombre]}
    </svg>
  )
}
