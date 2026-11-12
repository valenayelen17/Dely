import { BrowserRouter, Route, Routes } from 'react-router'
import { ProveedorToasts } from './components/Toasts'
import { Inicio } from './vistas/Inicio'
import { IngresarCodigo } from './vistas/cliente/IngresarCodigo'
import { Seguimiento } from './vistas/cliente/Seguimiento'
import { DetalleEntrega } from './vistas/repartidor/DetalleEntrega'
import { MisEntregas } from './vistas/repartidor/MisEntregas'
import { QuienSos } from './vistas/repartidor/QuienSos'

function App() {
  return (
    <ProveedorToasts>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Inicio />} />
          <Route path="/repartidor" element={<QuienSos />} />
          <Route path="/repartidor/:repartidorId" element={<MisEntregas />} />
          <Route path="/repartidor/:repartidorId/entregas/:entregaId" element={<DetalleEntrega />} />
          <Route path="/seguimiento" element={<IngresarCodigo />} />
          <Route path="/seguimiento/:codigo" element={<Seguimiento />} />
          <Route path="*" element={<Inicio />} />
        </Routes>
      </BrowserRouter>
    </ProveedorToasts>
  )
}

export default App
