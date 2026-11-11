import { BrowserRouter, Route, Routes } from 'react-router'
import { ProveedorToasts } from './components/Toasts'
import { Inicio } from './vistas/Inicio'
import { IngresarCodigo } from './vistas/cliente/IngresarCodigo'
import { Seguimiento } from './vistas/cliente/Seguimiento'
import { Clientes } from './vistas/encargado/Clientes'
import { Historial } from './vistas/encargado/Historial'
import { LayoutEncargado } from './vistas/encargado/LayoutEncargado'
import { NuevoPedido } from './vistas/encargado/NuevoPedido'
import { Pendientes } from './vistas/encargado/Pendientes'
import { Productos } from './vistas/encargado/Productos'
import { Repartidores } from './vistas/encargado/Repartidores'
import { DetalleEntrega } from './vistas/repartidor/DetalleEntrega'
import { MisEntregas } from './vistas/repartidor/MisEntregas'
import { QuienSos } from './vistas/repartidor/QuienSos'

function App() {
  return (
    <ProveedorToasts>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Inicio />} />
          <Route path="/comercio" element={<LayoutEncargado />}>
            <Route index element={<Pendientes />} />
            <Route path="nuevo" element={<NuevoPedido />} />
            <Route path="repartidores" element={<Repartidores />} />
            <Route path="productos" element={<Productos />} />
            <Route path="clientes" element={<Clientes />} />
            <Route path="historial" element={<Historial />} />
          </Route>
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
