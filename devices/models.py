from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

# -----------------------------
# Modelo Base con atributos comunes
# -----------------------------
class BaseModel(models.Model):
    STATUS = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
    ]

    status = models.CharField(max_length=10, choices=STATUS, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)   # se asigna al crear
    updated_at = models.DateTimeField(auto_now=True)       # se actualiza cada vez que se guarda
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)  # opcional para borrado lógico

    class Meta:
        abstract = True   # no crea tabla, solo se hereda

# -----------------------------
# Tablas principales
# -----------------------------

class Organization(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Category(BaseModel):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Zone(BaseModel):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class DeviceType(models.Model):
    """Tipos de dispositivos"""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre',
        help_text='Nombre único del tipo de dispositivo'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción detallada del tipo de dispositivo'
    )
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.name:
            self.name = self.name.strip()
            if len(self.name) < 3:
                raise ValidationError({
                    'name': 'El nombre debe tener al menos 3 caracteres.'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Tipo de Dispositivo'
        verbose_name_plural = 'Tipos de Dispositivos'
        ordering = ['name']


class Device(models.Model):
    """Modelo para dispositivos de monitoreo"""
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre',
        help_text='Nombre descriptivo del dispositivo'
    )
    device_type = models.ForeignKey(
        DeviceType,
        on_delete=models.PROTECT,
        related_name='devices',
        verbose_name='Tipo'
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Ubicación',
        help_text='Ubicación física del dispositivo'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='devices',
        verbose_name='Propietario'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si el dispositivo está operativo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    def __str__(self):
        return f"{self.name} ({self.device_type})"
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.name:
            self.name = self.name.strip()
            if len(self.name) < 3:
                raise ValidationError({
                    'name': 'El nombre debe tener al menos 3 caracteres.'
                })
        
        if self.location:
            self.location = self.location.strip()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Dispositivo'
        verbose_name_plural = 'Dispositivos'
        ordering = ['-created_at']
        unique_together = [['name', 'owner']]  # No permitir nombres duplicados por usuario


class Measurement(models.Model):
    """Modelo para mediciones de energía"""
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='measurements',
        verbose_name='Dispositivo'
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0.01, message='El valor debe ser mayor a 0'),
            MaxValueValidator(999999.99, message='El valor es demasiado grande')
        ],
        verbose_name='Valor',
        help_text='Valor medido (debe ser positivo)'
    )
    unit = models.CharField(
        max_length=20,
        default='kWh',
        verbose_name='Unidad',
        help_text='Unidad de medida (kWh, W, etc.)'
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha y hora',
        db_index=True
    )
    
    def __str__(self):
        return f"{self.device.name} - {self.value} {self.unit} ({self.timestamp})"
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.value is not None and self.value <= 0:
            raise ValidationError({
                'value': 'El valor de la medición debe ser mayor a 0.'
            })
        
        if self.unit:
            self.unit = self.unit.strip()
            if not self.unit:
                raise ValidationError({
                    'unit': 'La unidad de medida es obligatoria.'
                })
        
        # Validar que el dispositivo esté activo
        if self.device and not self.device.is_active:
            raise ValidationError({
                'device': 'No se pueden registrar mediciones en un dispositivo inactivo.'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Medición'
        verbose_name_plural = 'Mediciones'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['device', '-timestamp']),
        ]


class Alert(models.Model):
    """Modelo para alertas del sistema"""
    SEVERITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]
    
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name='Dispositivo'
    )
    message = models.TextField(
        verbose_name='Mensaje',
        help_text='Descripción de la alerta'
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='medium',
        verbose_name='Severidad'
    )
    is_resolved = models.BooleanField(
        default=False,
        verbose_name='Resuelta'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de resolución'
    )
    
    def __str__(self):
        return f"Alerta {self.severity} - {self.device.name}"
    
    def clean(self):
        """Validaciones personalizadas"""
        if self.message:
            self.message = self.message.strip()
            if len(self.message) < 10:
                raise ValidationError({
                    'message': 'El mensaje debe tener al menos 10 caracteres.'
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-created_at']

