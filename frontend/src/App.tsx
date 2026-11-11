import { BrowserRouter, Route, Routes } from 'react-router'
import { ProveedorToasts } from './components/Toasts'
import { Inicio } from './vistas/Inicio'
import { LayoutEncargado } from './vistas/encargado/LayoutEncargado'
import { Pendientes } from './vistas/encargado/Pendientes'

function App() {
  return (
    <ProveedorToasts>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Inicio />} />
          <Route path="/comercio" element={<LayoutEncargado />}>
            <Route index element={<Pendientes />} />
          </Route>
          <Route path="*" element={<Inicio />} />
        </Routes>
      </BrowserRouter>
    </ProveedorToasts>
  )
}

export default App
