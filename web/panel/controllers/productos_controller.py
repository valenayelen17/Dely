from itertools import groupby

from django.shortcuts import render

from ..forms import ProductoForm
from ..src import services
from .base import ControladorDely
from .formulario_controller import FormularioController


class ProductosController(ControladorDely):
    """Productos agrupados por categoría, con aviso de stock bajo."""

    def get(self, request):
        comercio = services.obtener_comercio()
        productos = sorted(services.listar_productos(comercio["id_comercio"]), key=lambda p: (p["categoria"], p["nombre"]))
        categorias = [(categoria, list(items)) for categoria, items in groupby(productos, key=lambda p: p["categoria"])]
        contexto = {
            "comercio": comercio,
            "categorias": categorias,
            "cantidad": len(productos),
            "sin_stock": sum(1 for p in productos if p["stock"] == 0),
        }
        return render(request, "productos.html", contexto)


class ProductoFormularioController(FormularioController):
    form_class = ProductoForm
    entidad = "producto"
    url_volver = "productos"
    usa_comercio = True

    def obtener(self, pk):
        return services.obtener_producto(pk)

    def crear(self, datos):
        return services.crear_producto(datos)

    def editar(self, pk, datos):
        return services.editar_producto(pk, datos)

    def contexto_extra(self, comercio):
        categorias = sorted({p["categoria"] for p in services.listar_productos(comercio["id_comercio"])})
        return {"datalists": {"categorias": categorias}}
