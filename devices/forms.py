from django import forms
from django.core.exceptions import ValidationError
from .models import Device, Measurement, Alert


# ---------------------------
# 📌 Device Form
# ---------------------------
class DeviceForm(forms.ModelForm):
    """Formulario para crear/editar dispositivos"""
    
    class Meta:
        model = Device
        fields = ['name', 'device_type', 'location', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del dispositivo',
                'required': True
            }),
            'device_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación del dispositivo'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Nombre',
            'device_type': 'Tipo de Dispositivo',
            'location': 'Ubicación',
            'is_active': 'Activo',
        }
        error_messages = {
            'name': {
                'required': 'El nombre del dispositivo es obligatorio.',
                'max_length': 'El nombre no puede exceder 200 caracteres.',
            },
            'device_type': {
                'required': 'Debe seleccionar un tipo de dispositivo.',
            },
        }
    
    def clean_name(self):
        """Validar que el nombre no esté vacío y no tenga solo espacios"""
        name = self.cleaned_data.get('name', '').strip()
        
        if not name:
            raise ValidationError('El nombre del dispositivo no puede estar vacío.')
        
        if len(name) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres.')
        
        # Verificar duplicados para el mismo usuario
        user = self.instance.owner if self.instance.pk else None
        if user:
            existing = Device.objects.filter(
                name__iexact=name,
                owner=user
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            if existing.exists():
                raise ValidationError(f'Ya tienes un dispositivo con el nombre "{name}".')
        
        return name
    
    def clean_location(self):
        """Validar ubicación"""
        location = self.cleaned_data.get('location', '').strip()
        
        if location and len(location) < 3:
            raise ValidationError('La ubicación debe tener al menos 3 caracteres.')
        
        return location


# ---------------------------
# 📏 Measurement Form
# ---------------------------
class MeasurementForm(forms.ModelForm):
    """Formulario para registrar mediciones"""
    
    class Meta:
        model = Measurement
        fields = ['device', 'value', 'unit']
        widgets = {
            'device': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Valor medido',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'kWh, W, etc.',
                'required': True
            }),
        }
        labels = {
            'device': 'Dispositivo',
            'value': 'Valor',
            'unit': 'Unidad',
        }
        error_messages = {
            'device': {
                'required': 'Debe seleccionar un dispositivo.',
            },
            'value': {
                'required': 'El valor de la medición es obligatorio.',
                'invalid': 'Ingrese un valor numérico válido.',
            },
            'unit': {
                'required': 'La unidad de medida es obligatoria.',
            },
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar dispositivos por usuario
        if user:
            self.fields['device'].queryset = Device.objects.filter(
                owner=user,
                is_active=True
            ).select_related('device_type')
        
        # Ayuda contextual
        self.fields['value'].help_text = 'Ingrese un valor numérico positivo mayor a 0'
        self.fields['unit'].help_text = 'Ejemplo: kWh, W, kW, V, A'
    
    def clean_value(self):
        """Validar que el valor sea positivo y mayor a 0"""
        value = self.cleaned_data.get('value')
        
        if value is None:
            raise ValidationError('El valor de la medición es obligatorio.')
        
        if value <= 0:
            raise ValidationError('El valor debe ser mayor a 0.')
        
        if value > 999999.99:
            raise ValidationError('El valor es demasiado grande. Máximo permitido: 999,999.99')
        
        return value
    
    def clean_unit(self):
        """Validar que la unidad no esté vacía"""
        unit = self.cleaned_data.get('unit', '').strip()
        
        if not unit:
            raise ValidationError('La unidad de medida es obligatoria.')
        
        if len(unit) > 20:
            raise ValidationError('La unidad no puede exceder 20 caracteres.')
        
        # Unidades válidas comunes
        valid_units = ['kWh', 'W', 'kW', 'MW', 'V', 'A', 'mA', 'Hz', 'Wh', 'MWh']
        if unit not in valid_units:
            # Solo advertencia, no error
            pass
        
        return unit
    
    def clean(self):
        """Validación general del formulario"""
        cleaned_data = super().clean()
        device = cleaned_data.get('device')
        value = cleaned_data.get('value')
        
        # Validar que el dispositivo esté activo
        if device and not device.is_active:
            raise ValidationError({
                'device': 'No puede registrar mediciones en un dispositivo inactivo.'
            })
        
        return cleaned_data
