import { useEffect, useState } from 'react'
import { pedirApi } from './api/cliente'

type EstadoConexion = 'verificando' | 'conectada' | 'sin conexión'

function App() {
  const [conexion, setConexion] = useState<EstadoConexion>('verificando')

  useEffect(() => {
    pedirApi<unknown[]>('/api/comercios/?limit=1')
      .then(() => setConexion('conectada'))
      .catch(() => setConexion('sin conexión'))
  }, [])

  return (
    <main>
      <h1>DELY</h1>
      <p>Gestión de entregas de última milla.</p>
      <p>API: {conexion}</p>
    </main>
  )
}

export default App
