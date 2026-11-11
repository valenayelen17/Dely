import { useState, type FormEvent } from 'react'
import { api } from '../../api/dely'
import type { DatosRepartidor, Repartidor } from '../../api/tipos'
import { ErrorCarga, Esqueleto, EstadoVacio } from '../../components/Estados'
import { Icono } from '../../components/Icono'
import { useApi } from '../../hooks/useApi'
import { useComercio } from '../../hooks/useComercio'
import { useToasts } from '../../hooks/useToasts'
import { iniciales, nombreCompleto } from '../../lib/formato'

function Formulario({ comercioId, editando, zonas, alGuardar, alCancelar }: {
  comercioId: number
  editando?: Repartidor
  zonas: string[]
  alGuardar: () => void
  alCancelar: () => void
}) {
  const toasts = useToasts()
  const [datos, setDatos] = useState<DatosRepartidor>(
    editando ?? { nombre: '', apellido: '', telefono: '', zona: '', disponible: true, comercio_id: comercioId },
  )
  const set = (cambio: Partial<DatosRepartidor>) => setDatos({ ...datos, ...cambio })
  const completo = datos.nombre.trim() && datos.apellido.trim() && datos.telefono.trim() && datos.zona.trim()

  const guardar = async (e: FormEvent) => {
    e.preventDefault()
    try {
      const { nombre, apellido, telefono, zona, disponible, comercio_id } = datos
      const cuerpo = { nombre, apellido, telefono, zona, disponible, comercio_id }
      if (editando) await api.editarRepartidor(editando.id_repartidor, cuerpo)
      else await api.crearRepartidor(cuerpo)
      toasts.exito(editando ? 'Cambios guardados' : `${datos.nombre} ya puede recibir pedidos`)
      alGuardar()
    } catch (error) {
      toasts.error(error, 'No se pudo guardar')
    }
  }

  return (
    <form className="card" onSubmit={guardar} style={{ flex: '1 1 320px', minWidth: 0, padding: 20, display: 'flex', flexDirection: 'column', gap: 14 }} aria-labelledby="rep-form">
      <h2 id="rep-form" style={{ fontSize: 16, fontWeight: 700 }}>
        {editando ? `Editar · ${editando.nombre}` : 'Nuevo repartidor'}
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 12 }}>
        <div className="field"><label className="label" htmlFor="r-n">Nombre</label><input id="r-n" className="input" value={datos.nombre} onChange={(e) => set({ nombre: e.target.value })} placeholder="Ej.: Sofía" /></div>
        <div className="field"><label className="label" htmlFor="r-a">Apellido</label><input id="r-a" className="input" value={datos.apellido} onChange={(e) => set({ apellido: e.target.value })} /></div>
      </div>
      <div className="field"><label className="label" htmlFor="r-t">Teléfono</label><input id="r-t" className="input" type="tel" value={datos.telefono} onChange={(e) => set({ telefono: e.target.value })} placeholder="11 5555-0000" /></div>
      <div className="field">
        <label className="label" htmlFor="r-z">Zona</label>
        <input id="r-z" className="input" list="zonas" value={datos.zona} onChange={(e) => set({ zona: e.target.value })} placeholder="Elegí o escribí una zona" />
        <datalist id="zonas">{zonas.map((z) => <option key={z} value={z} />)}</datalist>
      </div>
      <div className="between">
        <span style={{ display: 'flex', flexDirection: 'column' }}>
          <b style={{ fontSize: 14 }}>Disponible</b>
          <span className="hint">Recibe pedidos de su zona</span>
        </span>
        <button type="button" className="switch" role="switch" aria-checked={datos.disponible} aria-label="Disponible" onClick={() => set({ disponible: !datos.disponible })} />
      </div>
      <div className="row" style={{ justifyContent: 'flex-end' }}>
        <button type="button" className="btn btn-ghost" onClick={alCancelar}>Cancelar</button>
        <button className="btn btn-primary" disabled={!completo}>Guardar</button>
      </div>
    </form>
  )
}

export function Repartidores() {
  const { comercio } = useComercio()
  const toasts = useToasts()
  const repartidores = useApi(() => api.repartidores({ comercio_id: comercio.id_comercio }), `rep-${comercio.id_comercio}`)
  const activas = useApi(api.entregasActivas, 'activas', 10_000)
  const [formulario, setFormulario] = useState<{ editando?: Repartidor } | null>(null)

  const lista = repartidores.datos ?? []
  const enTurno = lista.filter((r) => r.disponible).length
  const zonas = [...new Set(lista.map((r) => r.zona))].sort()
  const cargaDe = (r: Repartidor) => activas.datos?.filter((e) => e.repartidor_id === r.id_repartidor).length ?? 0

  const alternar = async (r: Repartidor) => {
    try {
      await api.cambiarDisponibilidad(r.id_repartidor, !r.disponible)
      toasts.exito(
        r.disponible ? `${r.nombre} quedó fuera de turno` : `${r.nombre} está en turno`,
        r.disponible && cargaDe(r) > 0 ? 'Sus entregas en curso siguen activas.' : undefined,
      )
      void repartidores.recargar()
    } catch (e) {
      toasts.error(e)
    }
  }

  return (
    <>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <h1 className="page-title">Repartidores</h1>
          <p className="muted">{enTurno} de {lista.length} en turno. Sólo los disponibles reciben pedidos.</p>
        </div>
        <button className="btn btn-primary btn-lg" onClick={() => setFormulario({})}>
          <Icono nombre="mas" />
          Nuevo repartidor
        </button>
      </div>

      {repartidores.error && <ErrorCarga error={repartidores.error} reintentar={repartidores.recargar} />}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 24, alignItems: 'flex-start' }}>
        <div className="table-box" style={{ flex: '999 1 560px', minWidth: 0 }}>
          {repartidores.cargando ? (
            <div style={{ padding: 16 }}><Esqueleto /></div>
          ) : lista.length === 0 ? (
            <div style={{ padding: 16 }}><EstadoVacio icono="camion" titulo="Todavía no hay repartidores" /></div>
          ) : (
            <table className="table">
              <thead>
                <tr><th>Repartidor</th><th>Zona</th><th>Teléfono</th><th>Entregas activas</th><th>Disponible</th><th className="r"><span className="sr-only">Acciones</span></th></tr>
              </thead>
              <tbody>
                {lista.map((r) => (
                  <tr key={r.id_repartidor}>
                    <td><span className="row" style={{ gap: 10 }}><span className="avatar">{iniciales(r)}</span><b>{nombreCompleto(r)}</b></span></td>
                    <td><span className="tag tag-zone">{r.zona}</span></td>
                    <td>{r.telefono}</td>
                    <td>{cargaDe(r)}</td>
                    <td>
                      <span className="row">
                        <button className="switch" role="switch" aria-checked={r.disponible} aria-label={`${r.nombre} disponible`} onClick={() => alternar(r)} />
                        <span className={r.disponible ? '' : 'muted'} style={{ fontSize: 13, fontWeight: 600, color: r.disponible ? 'var(--c-success)' : undefined }}>
                          {r.disponible ? 'En turno' : 'Fuera de turno'}
                        </span>
                      </span>
                    </td>
                    <td className="r">
                      <button className="btn btn-ghost btn-sm" onClick={() => setFormulario({ editando: r })}>
                        <Icono nombre="editar" />
                        Editar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        {formulario && (
          <Formulario
            key={formulario.editando?.id_repartidor ?? 'nuevo'}
            comercioId={comercio.id_comercio}
            editando={formulario.editando}
            zonas={zonas}
            alCancelar={() => setFormulario(null)}
            alGuardar={() => {
              setFormulario(null)
              void repartidores.recargar()
            }}
          />
        )}
      </div>
    </>
  )
}
