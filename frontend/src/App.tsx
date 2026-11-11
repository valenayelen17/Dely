import { BrowserRouter, Route, Routes } from 'react-router'
import { ProveedorToasts } from './components/Toasts'
import { Inicio } from './vistas/Inicio'
import { Clientes } from './vistas/encargado/Clientes'
import { Historial } from './vistas/encargado/Historial'
import { LayoutEncargado } from './vistas/encargado/LayoutEncargado'
import { NuevoPedido } from './vistas/encargado/NuevoPedido'
import { Pendientes } from './vistas/encargado/Pendientes'
import { Productos } from './vistas/encargado/Productos'
import { Repartidores } from './vistas/encargado/Repartidores'

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
          <Route path="*" element={<Inicio />} />
        </Routes>
      </BrowserRouter>
    </ProveedorToasts>
  )
}

export default App
