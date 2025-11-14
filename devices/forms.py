from django import forms
from .models import Device, Measurement, Alert
from accounts.models import Category, Zone


# ---------------------------
# 📌 Device Form
# ---------------------------
class DeviceForm(forms.ModelForm):
    """Formulario para crear/editar dispositivos"""
    
    class Meta:
        model = Device
        fields = ['name', 'description', 'device_type', 'status', 'category', 'zone']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del dispositivo'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del dispositivo',
                'rows': 3
            }),
            'device_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'zone': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
            'device_type': 'Tipo de dispositivo',
            'status': 'Estado',
            'category': 'Categoría',
            'zone': 'Zona',
        }


# ---------------------------
# 📏 Measurement Form
# ---------------------------
class MeasurementForm(forms.ModelForm):
    """Formulario para crear mediciones"""
    
    class Meta:
        model = Measurement
        fields = ['device', 'value', 'unit']
        widgets = {
            'device': forms.Select(attrs={
                'class': 'form-select'
            }),
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Valor',
                'step': '0.01'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unidad (kWh, W, etc.)'
            }),
        }
        labels = {
            'device': 'Dispositivo',
            'value': 'Valor',
            'unit': 'Unidad',
        }


# ---------------------------
# 🚨 Alert Form
# ---------------------------
class AlertForm(forms.ModelForm):
    """Formulario para crear alertas"""
    
    class Meta:
        model = Alert
        fields = ['device', 'alert_type', 'message']
        widgets = {
            'device': forms.Select(attrs={
                'class': 'form-select'
            }),
            'alert_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Mensaje de la alerta',
                'rows': 3
            }),
        }
        labels = {
            'device': 'Dispositivo',
            'alert_type': 'Tipo de alerta',
            'message': 'Mensaje',
        }


# ---------------------------
# 🔍 Device Filter Form
# ---------------------------
class DeviceFilterForm(forms.Form):
    """Formulario para filtrar dispositivos"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar dispositivos...'
        })
    )
    device_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los tipos')] + list(Device._meta.get_field('device_type').choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los estados')] + list(Device._meta.get_field('status').choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.all(),
        empty_label='Todas las categorías',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    zone = forms.ModelChoiceField(
        required=False,
        queryset=Zone.objects.all(),
        empty_label='Todas las zonas',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
