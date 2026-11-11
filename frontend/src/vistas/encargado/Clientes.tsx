import { useState, type FormEvent } from 'react'
import { api } from '../../api/dely'
import type { Cliente, DatosCliente } from '../../api/tipos'
import { ErrorCarga, Esqueleto, EstadoVacio } from '../../components/Estados'
import { Icono } from '../../components/Icono'
import { useApi } from '../../hooks/useApi'
import { useToasts } from '../../hooks/useToasts'
import { iniciales, nombreCompleto, plural } from '../../lib/formato'

const CAMPOS: { clave: keyof DatosCliente; etiqueta: string; tipo?: string }[] = [
  { clave: 'nombre', etiqueta: 'Nombre' },
  { clave: 'apellido', etiqueta: 'Apellido' },
  { clave: 'telefono', etiqueta: 'Teléfono', tipo: 'tel' },
  { clave: 'email', etiqueta: 'Email', tipo: 'email' },
  { clave: 'direccion', etiqueta: 'Dirección' },
]

function Formulario({ editando, alGuardar, alCancelar }: { editando?: Cliente; alGuardar: () => void; alCancelar: () => void }) {
  const toasts = useToasts()
  const [datos, setDatos] = useState<DatosCliente>(
    editando ?? { nombre: '', apellido: '', telefono: '', email: '', direccion: '' },
  )

  const guardar = async (e: FormEvent) => {
    e.preventDefault()
    const { nombre, apellido, telefono, email, direccion } = datos
    const cuerpo = { nombre, apellido, telefono, email, direccion }
    try {
      if (editando) await api.editarCliente(editando.id_cliente, cuerpo)
      else await api.crearCliente(cuerpo)
      toasts.exito(editando ? 'Cambios guardados' : `${nombre} quedó registrado`)
      alGuardar()
    } catch (error) {
      toasts.error(error, 'No se pudo guardar')
    }
  }

  return (
    <form className="card" onSubmit={guardar} style={{ flex: '1 1 320px', minWidth: 0, padding: 20, display: 'flex', flexDirection: 'column', gap: 14 }} aria-labelledby="cl-form">
      <h2 id="cl-form" style={{ fontSize: 16, fontWeight: 700 }}>{editando ? `Editar · ${editando.nombre}` : 'Nuevo cliente'}</h2>
      {CAMPOS.map(({ clave, etiqueta, tipo }) => (
        <div key={clave} className="field">
          <label className="label" htmlFor={`cl-${clave}`}>{etiqueta}</label>
          <input id={`cl-${clave}`} className="input" type={tipo ?? 'text'} value={datos[clave]} onChange={(e) => setDatos({ ...datos, [clave]: e.target.value })} required />
        </div>
      ))}
      <div className="row" style={{ justifyContent: 'flex-end' }}>
        <button type="button" className="btn btn-ghost" onClick={alCancelar}>Cancelar</button>
        <button className="btn btn-primary">Guardar</button>
      </div>
    </form>
  )
}

export function Clientes() {
  const clientes = useApi(api.clientes, 'clientes')
  const [busqueda, setBusqueda] = useState('')
  const [formulario, setFormulario] = useState<{ editando?: Cliente } | null>(null)

  const lista = (clientes.datos ?? []).filter((c) =>
    `${c.nombre} ${c.apellido} ${c.telefono} ${c.email}`.toLowerCase().includes(busqueda.trim().toLowerCase()),
  )

  return (
    <>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <h1 className="page-title">Clientes</h1>
          <p className="muted">{plural(clientes.datos?.length ?? 0, 'cliente registrado', 'clientes registrados')}.</p>
        </div>
        <button className="btn btn-primary btn-lg" onClick={() => setFormulario({})}>
          <Icono nombre="mas" />
          Nuevo cliente
        </button>
      </div>

      <div className="input-icon" style={{ maxWidth: 360 }}>
        <Icono nombre="buscar" />
        <input className="input" aria-label="Buscar cliente" placeholder="Buscar por nombre, teléfono o email" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
      </div>

      {clientes.error && <ErrorCarga error={clientes.error} reintentar={clientes.recargar} />}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 24, alignItems: 'flex-start' }}>
        <div className="table-box" style={{ flex: '999 1 560px', minWidth: 0 }}>
          {clientes.cargando ? (
            <div style={{ padding: 16 }}><Esqueleto /></div>
          ) : lista.length === 0 ? (
            <div style={{ padding: 16 }}><EstadoVacio icono="persona" titulo="No hay clientes para mostrar" /></div>
          ) : (
            <table className="table">
              <thead><tr><th>Cliente</th><th>Teléfono</th><th>Email</th><th>Dirección</th><th className="r"><span className="sr-only">Acciones</span></th></tr></thead>
              <tbody>
                {lista.map((c) => (
                  <tr key={c.id_cliente}>
                    <td><span className="row" style={{ gap: 10 }}><span className="avatar">{iniciales(c)}</span><b>{nombreCompleto(c)}</b></span></td>
                    <td>{c.telefono}</td>
                    <td>{c.email}</td>
                    <td>{c.direccion}</td>
                    <td className="r">
                      <button className="btn btn-ghost btn-sm" onClick={() => setFormulario({ editando: c })}>
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
            key={formulario.editando?.id_cliente ?? 'nuevo'}
            editando={formulario.editando}
            alCancelar={() => setFormulario(null)}
            alGuardar={() => {
              setFormulario(null)
              void clientes.recargar()
            }}
          />
        )}
      </div>
    </>
  )
}
