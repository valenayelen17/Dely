import { useOutletContext } from 'react-router'
import type { Comercio } from '../api/tipos'

export interface ContextoComercio {
  comercio: Comercio
  refrescarContador: () => void
}

export const useComercio = () => useOutletContext<ContextoComercio>()
