import { useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { api } from '../../api/dely'
import type { EstadoPedido, Pedido } from '../../api/tipos'
import { BadgeEstado } from '../../components/BadgeEstado'
import { ErrorCarga, Esqueleto, EstadoVacio } from '../../components/Estados'
import { Icono } from '../../components/Icono'
import { useApi } from '../../hooks/useApi'
import { useComercio } from '../../hooks/useComercio'
import { ESTADOS_ACTIVOS } from '../../lib/estados'
import { cantidadProductos, hora, iniciales, moneda, plural } from '../../lib/formato'
import { PanelPedido } from './PanelPedido'

function TarjetaPedido({ pedido }: { pedido: Pedido }) {
  const sinRepartidor = pedido.estado === 'Pendiente'
  const repartidor = pedido.entrega?.repartidor
  return (
    <Link className={`order-card${sinRepartidor ? ' is-unassigned' : ''}`} to={`?pedido=${pedido.id_pedido}`}>
      <div className="between">
        <span className="code">{pedido.codigo_seguimiento}</span>
        <span className="row" style={{ gap: 4, fontWeight: 700 }}>
          <Icono nombre="reloj" />
          {hora(pedido.horario_estimado)}
        </span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <span className="addr">{pedido.direccion_entrega}</span>
        <span className="muted" style={{ fontSize: 13 }}>
          {pedido.cliente.nombre} {pedido.cliente.apellido}
        </span>
      </div>
      <div className="row">
        <span className="tag tag-zone">{pedido.zona}</span>
        <span className="muted" style={{ fontSize: 13 }}>
          {plural(cantidadProductos(pedido.detalles), 'producto')}
        </span>
      </div>
      {pedido.entrega?.ubicacion_actual && pedido.estado === 'En camino' && (
        <div className="row muted" style={{ gap: 6, fontSize: 13 }}>
          <Icono nombre="pin" />
          Va por {pedido.entrega.ubicacion_actual}
        </div>
      )}
      <hr className="divider" />
      <div className="between">
        {repartidor ? (
          <span className="row" style={{ gap: 6, fontSize: 13, fontWeight: 600 }}>
            <span className="avatar" style={{ width: 24, height: 24, fontSize: 10 }}>
              {iniciales(repartidor)}
            </span>
            {repartidor.nombre}
          </span>
        ) : (
          <span className="tag tag-alert">
            <Icono nombre="alerta" />
            Sin repartidor
          </span>
        )}
        <b>{moneda(pedido.total)}</b>
      </div>
    </Link>
  )
}

export function Pendientes() {
  const { comercio, refrescarContador } = useComercio()
  const [params, setParams] = useSearchParams()
  const [zona, setZona] = useState<string>()
  const pendientes = useApi(() => api.pendientes(comercio.id_comercio), String(comercio.id_comercio), 5000)
  const seleccionado = Number(params.get('pedido')) || undefined

  const pedidos = pendientes.datos ?? []
  const zonas = [...new Set(pedidos.map((p) => p.zona))].sort()
  const visibles = zona ? pedidos.filter((p) => p.zona === zona) : pedidos
  const sinAsignar = pedidos.filter((p) => p.estado === 'Pendiente').length

  const alCambiar = () => {
    void pendientes.recargar()
    refrescarContador()
  }

  return (
    <>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <h1 className="page-title">Pedidos pendientes</h1>
          <p className="muted">{plural(pedidos.length, 'pedido activo', 'pedidos activos')}, ordenados por horario estimado.</p>
        </div>
        <Link className="btn btn-primary btn-lg" to="/comercio/nuevo">
          <Icono nombre="mas" />
          Nuevo pedido
        </Link>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'center', justifyContent: 'space-between' }}>
        <div className="row" style={{ flexWrap: 'wrap' }} role="group" aria-label="Filtrar por zona">
          <button className="chip" aria-pressed={!zona} onClick={() => setZona(undefined)}>
            Todas las zonas
          </button>
          {zonas.map((z) => (
            <button key={z} className="chip" aria-pressed={zona === z} onClick={() => setZona(z)}>
              {z}
            </button>
          ))}
        </div>
        {sinAsignar > 0 && (
          <span className="tag tag-alert" style={{ height: 30, padding: '0 12px', fontSize: 13 }}>
            <Icono nombre="alerta" />
            {plural(sinAsignar, 'pedido')} sin repartidor
          </span>
        )}
      </div>

      {pendientes.error && <ErrorCarga error={pendientes.error} reintentar={pendientes.recargar} />}
      {pendientes.cargando ? (
        <Esqueleto filas={2} alto={180} />
      ) : pedidos.length === 0 ? (
        <EstadoVacio titulo="No hay pedidos pendientes">Cuando cargues un pedido nuevo, aparece acá.</EstadoVacio>
      ) : (
        <div className="board">
          {ESTADOS_ACTIVOS.map((estado: EstadoPedido) => {
            const columna = visibles.filter((p) => p.estado === estado)
            const id = `col-${estado.replace(' ', '-')}`
            return (
              <section key={estado} className="col" aria-labelledby={id}>
                <div className="col-head">
                  <BadgeEstado estado={estado} id={id} />
                  <span className="muted" style={{ fontWeight: 700 }}>
                    {columna.length}
                  </span>
                </div>
                {columna.map((p) => (
                  <TarjetaPedido key={p.id_pedido} pedido={p} />
                ))}
              </section>
            )
          })}
        </div>
      )}

      {seleccionado && (
        <PanelPedido
          pedidoId={seleccionado}
          comercioId={comercio.id_comercio}
          alCerrar={() => setParams({})}
          alCambiar={alCambiar}
        />
      )}
    </>
  )
}
