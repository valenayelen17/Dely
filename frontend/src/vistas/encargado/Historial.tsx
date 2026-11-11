import { useState } from 'react'
import { useSearchParams } from 'react-router'
import { api } from '../../api/dely'
import type { EstadoPedido } from '../../api/tipos'
import { BadgeEstado } from '../../components/BadgeEstado'
import { ErrorCarga, Esqueleto, EstadoVacio } from '../../components/Estados'
import { useApi } from '../../hooks/useApi'
import { useComercio } from '../../hooks/useComercio'
import { hora, moneda, nombreCompleto, plural } from '../../lib/formato'
import { PanelPedido } from './PanelPedido'

const FINALIZADOS: EstadoPedido[] = ['Entregado', 'Cancelado']

export function Historial() {
  const { comercio } = useComercio()
  const [params, setParams] = useSearchParams()
  const [filtro, setFiltro] = useState<EstadoPedido>()
  const pedidos = useApi(() => api.pedidos(comercio.id_comercio), `hist-${comercio.id_comercio}`)
  const seleccionado = Number(params.get('pedido')) || undefined

  const finalizados = (pedidos.datos ?? []).filter((p) => FINALIZADOS.includes(p.estado))
  const visibles = filtro ? finalizados.filter((p) => p.estado === filtro) : finalizados
  const entregados = finalizados.filter((p) => p.estado === 'Entregado')
  const facturado = entregados.reduce((suma, p) => suma + Number(p.total), 0)

  return (
    <>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <h1 className="page-title">Historial</h1>
        <p className="muted">
          {plural(entregados.length, 'pedido entregado', 'pedidos entregados')} por {moneda(facturado)}.
        </p>
      </div>
      <div className="row" style={{ flexWrap: 'wrap' }} role="group" aria-label="Filtrar por estado">
        <button className="chip" aria-pressed={!filtro} onClick={() => setFiltro(undefined)}>Todos</button>
        {FINALIZADOS.map((e) => (
          <button key={e} className="chip" aria-pressed={filtro === e} onClick={() => setFiltro(e)}>{e}s</button>
        ))}
      </div>

      {pedidos.error && <ErrorCarga error={pedidos.error} reintentar={pedidos.recargar} />}
      {pedidos.cargando ? (
        <Esqueleto />
      ) : visibles.length === 0 ? (
        <EstadoVacio icono="historial" titulo="Todavía no hay pedidos finalizados" />
      ) : (
        <div className="table-box">
          <table className="table">
            <thead>
              <tr><th>Código</th><th>Fecha</th><th>Cliente</th><th>Zona</th><th>Repartidor</th><th>Entregado</th><th className="r">Total</th><th>Estado</th></tr>
            </thead>
            <tbody>
              {visibles.map((p) => (
                <tr key={p.id_pedido}>
                  <td>
                    <button className="btn btn-ghost btn-sm code" onClick={() => setParams({ pedido: String(p.id_pedido) })}>
                      {p.codigo_seguimiento}
                    </button>
                  </td>
                  <td>{p.fecha_pedido.split('-').reverse().join('/')}</td>
                  <td>{nombreCompleto(p.cliente)}</td>
                  <td><span className="tag tag-zone">{p.zona}</span></td>
                  <td>{p.entrega?.repartidor.nombre ?? <span className="muted">—</span>}</td>
                  <td>{p.entrega?.hora_entrega ? hora(p.entrega.hora_entrega) : <span className="muted">—</span>}</td>
                  <td className="r">{moneda(p.total)}</td>
                  <td><BadgeEstado estado={p.estado} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {seleccionado && (
        <PanelPedido
          pedidoId={seleccionado}
          comercioId={comercio.id_comercio}
          alCerrar={() => setParams({})}
          alCambiar={() => void pedidos.recargar()}
        />
      )}
    </>
  )
}
