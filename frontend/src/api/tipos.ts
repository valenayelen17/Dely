export type EstadoPedido = 'Pendiente' | 'Asignado' | 'En camino' | 'Entregado' | 'Cancelado'
export type EstadoEntrega = 'Asignada' | 'En camino' | 'Llegando' | 'Entregada' | 'Cancelada'

export interface Comercio {
  id_comercio: number
  nombre: string
  direccion: string
  telefono: string
  email: string
}

export interface Cliente {
  id_cliente: number
  nombre: string
  apellido: string
  telefono: string
  email: string
  direccion: string
}

export interface Repartidor {
  id_repartidor: number
  nombre: string
  apellido: string
  telefono: string
  zona: string
  disponible: boolean
  comercio_id: number
}

export interface Producto {
  id_producto: number
  nombre: string
  descripcion: string | null
  precio: string
  categoria: string
  stock: number
  comercio_id: number
}

export type ClienteResumen = Pick<Cliente, 'id_cliente' | 'nombre' | 'apellido' | 'telefono'>
export type RepartidorResumen = Pick<Repartidor, 'id_repartidor' | 'nombre' | 'apellido' | 'telefono' | 'zona'>

export interface Detalle {
  id_detalle: number
  producto_id: number
  producto_nombre: string
  cantidad: number
  precio_unitario: string
  subtotal: string
}

export interface Entrega {
  id_entrega: number
  pedido_id: number
  repartidor_id: number
  repartidor: RepartidorResumen
  estado: EstadoEntrega
  ubicacion_actual: string | null
  fecha_entrega: string | null
  hora_entrega: string | null
}

export interface Pedido {
  id_pedido: number
  codigo_seguimiento: string
  fecha_pedido: string
  direccion_entrega: string
  zona: string
  estado: EstadoPedido
  horario_estimado: string
  cliente_id: number
  comercio_id: number
  cliente: ClienteResumen
  detalles: Detalle[]
  total: string
  entrega: Entrega | null
}

export interface EntregaDetalle extends Entrega {
  pedido: Pick<Pedido, 'id_pedido' | 'direccion_entrega' | 'zona' | 'estado' | 'horario_estimado' | 'cliente' | 'detalles' | 'total'>
}

export interface Notificacion {
  id_notificacion: number
  tipo: string
  mensaje: string
  fecha_hora: string
  leida: boolean
}

export interface Seguimiento {
  codigo_seguimiento: string
  estado: EstadoPedido
  estado_entrega: EstadoEntrega | null
  fecha_pedido: string
  horario_estimado: string
  direccion_entrega: string
  comercio: string
  comercio_telefono: string
  repartidor: string | null
  ubicacion_actual: string | null
  hora_entrega: string | null
  productos: { nombre: string; cantidad: number; subtotal: string }[]
  total: string
  notificaciones: Notificacion[]
}

export type DatosCliente = Omit<Cliente, 'id_cliente'>
export type DatosRepartidor = Omit<Repartidor, 'id_repartidor'>
export type DatosProducto = Omit<Producto, 'id_producto' | 'precio'> & { precio: string | number }

export interface DatosPedido {
  comercio_id: number
  cliente_id: number
  zona: string
  horario_estimado: string
  direccion_entrega?: string
  detalles: { producto_id: number; cantidad: number }[]
}
