# Ruta -> entrada del menú lateral que se marca como activa.
MENU = {
    "pendientes": "pedidos",
    "pedido_detalle": "pedidos",
    "pedido_editar": "pedidos",
    "nuevo_pedido": "nuevo_pedido",
    "repartidores": "repartidores",
    "repartidor_nuevo": "repartidores",
    "repartidor_editar": "repartidores",
    "productos": "productos",
    "producto_nuevo": "productos",
    "producto_editar": "productos",
    "clientes": "clientes",
    "cliente_nuevo": "clientes",
    "cliente_editar": "clientes",
    "cliente_acceso": "clientes",
    "repartidor_acceso": "repartidores",
    "historial": "historial",
}


def dely(request):
    """Datos comunes a todas las pantallas del panel."""
    match = getattr(request, "resolver_match", None)
    return {
        "menu": MENU.get(match.url_name, "") if match else "",
        "usuario": request.session.get("usuario") if hasattr(request, "session") else None,
    }
