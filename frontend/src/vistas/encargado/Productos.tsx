import { useState, type FormEvent } from 'react'
import { api } from '../../api/dely'
import type { Producto } from '../../api/tipos'
import { ErrorCarga, Esqueleto, EstadoVacio } from '../../components/Estados'
import { Icono } from '../../components/Icono'
import { useApi } from '../../hooks/useApi'
import { useComercio } from '../../hooks/useComercio'
import { useToasts } from '../../hooks/useToasts'
import { moneda, plural } from '../../lib/formato'

const STOCK_BAJO = 5

interface DatosForm {
  nombre: string
  categoria: string
  precio: string
  stock: string
  descripcion: string
}

function Formulario({ comercioId, editando, categorias, alGuardar, alCancelar }: {
  comercioId: number
  editando?: Producto
  categorias: string[]
  alGuardar: () => void
  alCancelar: () => void
}) {
  const toasts = useToasts()
  const [datos, setDatos] = useState<DatosForm>({
    nombre: editando?.nombre ?? '',
    categoria: editando?.categoria ?? '',
    precio: editando ? String(Number(editando.precio)) : '',
    stock: editando ? String(editando.stock) : '',
    descripcion: editando?.descripcion ?? '',
  })
  const set = (cambio: Partial<DatosForm>) => setDatos({ ...datos, ...cambio })

  const guardar = async (e: FormEvent) => {
    e.preventDefault()
    const cuerpo = {
      nombre: datos.nombre,
      categoria: datos.categoria,
      precio: Number(datos.precio),
      stock: Number(datos.stock),
      descripcion: datos.descripcion.trim() || null,
      comercio_id: comercioId,
    }
    try {
      if (editando) await api.editarProducto(editando.id_producto, cuerpo)
      else await api.crearProducto(cuerpo)
      toasts.exito(editando ? 'Cambios guardados' : `${datos.nombre} quedó en el catálogo`)
      alGuardar()
    } catch (error) {
      toasts.error(error, 'No se pudo guardar')
    }
  }

  return (
    <form className="card" onSubmit={guardar} style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 14, maxWidth: 720 }} aria-labelledby="pf-t">
      <div className="between">
        <h2 id="pf-t" style={{ fontSize: 16, fontWeight: 700 }}>{editando ? `Editar · ${editando.nombre}` : 'Nuevo producto'}</h2>
        <span className="hint">Stock bajo: {STOCK_BAJO} o menos</span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
        <div className="field"><label className="label" htmlFor="pf-n">Nombre</label><input id="pf-n" className="input" value={datos.nombre} onChange={(e) => set({ nombre: e.target.value })} required minLength={2} /></div>
        <div className="field">
          <label className="label" htmlFor="pf-c">Categoría</label>
          <input id="pf-c" className="input" list="categorias" value={datos.categoria} onChange={(e) => set({ categoria: e.target.value })} required minLength={2} />
          <datalist id="categorias">{categorias.map((c) => <option key={c} value={c} />)}</datalist>
        </div>
        <div className="field"><label className="label" htmlFor="pf-p">Precio</label><input id="pf-p" className="input" type="number" min="1" step="0.01" value={datos.precio} onChange={(e) => set({ precio: e.target.value })} required /></div>
        <div className="field"><label className="label" htmlFor="pf-s">Stock</label><input id="pf-s" className="input" type="number" min="0" step="1" value={datos.stock} onChange={(e) => set({ stock: e.target.value })} required /></div>
      </div>
      <div className="field"><label className="label" htmlFor="pf-d">Descripción (opcional)</label><input id="pf-d" className="input" value={datos.descripcion} onChange={(e) => set({ descripcion: e.target.value })} placeholder="Algo que ayude a reconocerlo" /></div>
      <div className="row" style={{ justifyContent: 'flex-end' }}>
        <button type="button" className="btn btn-ghost" onClick={alCancelar}>Cancelar</button>
        <button className="btn btn-primary">{editando ? 'Guardar cambios' : 'Guardar'}</button>
      </div>
    </form>
  )
}

function EstadoStock({ stock }: { stock: number }) {
  if (stock === 0)
    return <span className="tag tag-danger"><Icono nombre="x-circulo" />Sin stock</span>
  if (stock <= STOCK_BAJO)
    return <span className="tag tag-warn"><Icono nombre="alerta" />Stock bajo</span>
  return <span className="muted" style={{ fontSize: 13 }}>Normal</span>
}

export function Productos() {
  const { comercio } = useComercio()
  const productos = useApi(() => api.productos(comercio.id_comercio), `prod-${comercio.id_comercio}`)
  const [formulario, setFormulario] = useState<{ editando?: Producto } | null>(null)

  const lista = productos.datos ?? []
  const categorias = [...new Set(lista.map((p) => p.categoria))]
  const reponer = lista.filter((p) => p.stock <= STOCK_BAJO)
  const sinStock = reponer.filter((p) => p.stock === 0)
  const bajos = reponer.filter((p) => p.stock > 0)

  return (
    <>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <h1 className="page-title">Productos</h1>
          <p className="muted">{plural(lista.length, 'producto')} en {plural(categorias.length, 'categoría')}.</p>
        </div>
        <button className="btn btn-primary btn-lg" onClick={() => setFormulario({})}>
          <Icono nombre="mas" />
          Nuevo producto
        </button>
      </div>

      {reponer.length > 0 && (
        <div className="inline-alert inline-alert-warn" role="status">
          <Icono nombre="alerta" tamano="lg" />
          <span>
            <b>{plural(reponer.length, 'producto necesita', 'productos necesitan')} reposición.</b>
            {bajos.length > 0 && ` ${bajos.map((p) => p.nombre).join(', ')}: stock bajo.`}
            {sinStock.length > 0 && ` ${sinStock.map((p) => p.nombre).join(', ')}: sin stock, no se puede agregar a pedidos nuevos.`}
          </span>
        </div>
      )}

      {formulario && (
        <Formulario
          key={formulario.editando?.id_producto ?? 'nuevo'}
          comercioId={comercio.id_comercio}
          editando={formulario.editando}
          categorias={categorias}
          alCancelar={() => setFormulario(null)}
          alGuardar={() => {
            setFormulario(null)
            void productos.recargar()
          }}
        />
      )}

      {productos.error && <ErrorCarga error={productos.error} reintentar={productos.recargar} />}
      {productos.cargando ? (
        <Esqueleto />
      ) : lista.length === 0 ? (
        <EstadoVacio icono="producto" titulo="Todavía no hay productos" />
      ) : (
        <div className="table-box">
          <table className="table">
            <thead>
              <tr><th>Producto</th><th>Descripción</th><th className="r">Precio</th><th className="r">Stock</th><th>Estado</th><th className="r"><span className="sr-only">Acciones</span></th></tr>
            </thead>
            <tbody>
              {categorias.map((categoria) => [
                <tr key={`cat-${categoria}`} className="cat"><td colSpan={6}>{categoria}</td></tr>,
                ...lista
                  .filter((p) => p.categoria === categoria)
                  .map((p) => (
                    <tr key={p.id_producto} className={p.stock === 0 ? 'out' : p.stock <= STOCK_BAJO ? 'low' : undefined}>
                      <td><b>{p.nombre}</b></td>
                      <td className="muted">{p.descripcion ?? '—'}</td>
                      <td className="r">{moneda(p.precio)}</td>
                      <td className="r" style={p.stock <= STOCK_BAJO ? { color: p.stock === 0 ? 'var(--c-danger)' : 'var(--c-warning)', fontWeight: 700 } : undefined}>{p.stock}</td>
                      <td><EstadoStock stock={p.stock} /></td>
                      <td className="r">
                        <button className="btn btn-ghost btn-sm" onClick={() => setFormulario({ editando: p })}>
                          <Icono nombre="editar" />
                          Editar
                        </button>
                      </td>
                    </tr>
                  )),
              ])}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
