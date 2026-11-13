import { BrowserRouter, Navigate, Route, Routes } from 'react-router'
import { ProveedorSesion, RedirigirSegunRol, RequiereRol } from './components/Sesion'
import { ProveedorToasts } from './components/Toasts'
import { Login } from './vistas/Login'
import { MisPedidos } from './vistas/cliente/MisPedidos'
import { Seguimiento } from './vistas/cliente/Seguimiento'
import { DetalleEntrega } from './vistas/repartidor/DetalleEntrega'
import { MisEntregas } from './vistas/repartidor/MisEntregas'

function App() {
  return (
    <ProveedorToasts>
      <BrowserRouter>
        <ProveedorSesion>
          <Routes>
            <Route path="/" element={<RedirigirSegunRol />} />
            <Route path="/login" element={<Login />} />
            <Route path="/entregas" element={<RequiereRol rol="repartidor"><MisEntregas /></RequiereRol>} />
            <Route path="/entregas/:entregaId" element={<RequiereRol rol="repartidor"><DetalleEntrega /></RequiereRol>} />
            <Route path="/pedidos" element={<RequiereRol rol="cliente"><MisPedidos /></RequiereRol>} />
            <Route path="/pedidos/:codigo" element={<RequiereRol rol="cliente"><Seguimiento /></RequiereRol>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ProveedorSesion>
      </BrowserRouter>
    </ProveedorToasts>
  )
}

export default App
