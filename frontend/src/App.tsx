import { BrowserRouter, Route, Routes } from 'react-router'
import { ProveedorToasts } from './components/Toasts'
import { Inicio } from './vistas/Inicio'

function App() {
  return (
    <ProveedorToasts>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Inicio />} />
          <Route path="*" element={<Inicio />} />
        </Routes>
      </BrowserRouter>
    </ProveedorToasts>
  )
}

export default App
