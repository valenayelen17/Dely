from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()

COLORES = {
    "Pendiente": "secondary",
    "Asignado": "primary",
    "Asignada": "primary",
    "En camino": "warning",
    "Llegando": "danger",
    "Entregado": "success",
    "Entregada": "success",
    "Cancelado": "dark",
    "Cancelada": "dark",
}

ICONOS = {
    "Pendiente": "bi-clock",
    "Asignado": "bi-person-check",
    "Asignada": "bi-person-check",
    "En camino": "bi-truck",
    "Llegando": "bi-geo-alt",
    "Entregado": "bi-check-circle",
    "Entregada": "bi-check-circle",
    "Cancelado": "bi-x-circle",
    "Cancelada": "bi-x-circle",
}


@register.filter
def pesos(valor) -> str:
    """15500.00 -> '$ 15.500'"""
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError):
        return "—"
    entero = f"{numero:,.0f}".replace(",", ".")
    return f"$ {entero}"


@register.filter
def hora(valor) -> str:
    """'20:30:00' -> '20:30'"""
    return str(valor)[:5] if valor else "—"


@register.filter
def color_estado(estado) -> str:
    return COLORES.get(estado, "secondary")


@register.filter
def icono_estado(estado) -> str:
    return ICONOS.get(estado, "bi-circle")


@register.filter
def obtener(diccionario, clave):
    """Acceso a un diccionario con clave variable: {{ datos.cantidades|obtener:id }}"""
    if not isinstance(diccionario, dict):
        return ""
    return diccionario.get(str(clave), "")
