"""Formularios del panel. Validan con los mismos límites que la API (backend/schemas.py)."""

from datetime import time
from decimal import Decimal

from django import forms


class FormularioDely(forms.Form):
    """Agrega las clases de Bootstrap y convierte los datos al formato JSON de la API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.CheckboxInput):
                campo.widget.attrs.setdefault("class", "form-check-input")
            else:
                campo.widget.attrs.setdefault("class", "form-control")

    def datos_api(self) -> dict:
        datos = {}
        for clave, valor in self.cleaned_data.items():
            if isinstance(valor, Decimal):
                valor = str(valor)
            elif isinstance(valor, time):
                valor = valor.strftime("%H:%M")
            elif valor == "" and not self.fields[clave].required:
                valor = None
            datos[clave] = valor
        return datos


class ClienteForm(FormularioDely):
    nombre = forms.CharField(min_length=2, max_length=100)
    apellido = forms.CharField(min_length=2, max_length=100)
    telefono = forms.CharField(label="Teléfono", min_length=6, max_length=30)
    email = forms.EmailField()
    direccion = forms.CharField(label="Dirección", min_length=3, max_length=255)


class ProductoForm(FormularioDely):
    nombre = forms.CharField(min_length=2, max_length=150)
    categoria = forms.CharField(
        label="Categoría", min_length=2, max_length=100, widget=forms.TextInput(attrs={"list": "categorias"})
    )
    precio = forms.DecimalField(min_value=Decimal("0.01"), max_digits=10, decimal_places=2)
    stock = forms.IntegerField(min_value=0)
    descripcion = forms.CharField(label="Descripción", max_length=500, required=False)


class RepartidorForm(FormularioDely):
    nombre = forms.CharField(min_length=2, max_length=100)
    apellido = forms.CharField(min_length=2, max_length=100)
    telefono = forms.CharField(label="Teléfono", min_length=6, max_length=30)
    zona = forms.CharField(
        min_length=2,
        max_length=100,
        help_text="Elegí una existente o escribí una nueva.",
        widget=forms.TextInput(attrs={"list": "zonas"}),
    )
    disponible = forms.BooleanField(label="En turno", required=False, initial=True)


class PedidoEdicionForm(FormularioDely):
    direccion_entrega = forms.CharField(label="Dirección de entrega", min_length=3, max_length=255)
    zona = forms.CharField(min_length=2, max_length=100, widget=forms.TextInput(attrs={"list": "zonas"}))
    horario_estimado = forms.TimeField(label="Horario estimado", widget=forms.TimeInput(attrs={"type": "time"}, format="%H:%M"))
