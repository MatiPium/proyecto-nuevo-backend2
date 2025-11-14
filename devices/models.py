from django.db import models
from django.contrib.auth.models import User
from accounts.models import Category, Zone


class DeviceType(models.TextChoices):
    SENSOR = 'sensor', 'Sensor'
    ACTUATOR = 'actuator', 'Actuador'
    METER = 'meter', 'Medidor'


class DeviceStatus(models.TextChoices):
    ACTIVE = 'active', 'Activo'
    INACTIVE = 'inactive', 'Inactivo'
    MAINTENANCE = 'maintenance', 'Mantenimiento'
    ERROR = 'error', 'Error'


class AlertType(models.TextChoices):
    INFO = 'info', 'Información'
    WARNING = 'warning', 'Advertencia'
    CRITICAL = 'critical', 'Crítico'


class Device(models.Model):
    """Modelo para dispositivos IoT"""
    name = models.CharField(max_length=200, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.SENSOR,
        verbose_name="Tipo"
    )
    status = models.CharField(
        max_length=20,
        choices=DeviceStatus.choices,
        default=DeviceStatus.ACTIVE,
        verbose_name="Estado"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='devices',
        verbose_name="Categoría"
    )
    zone = models.ForeignKey(
        Zone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='devices',
        verbose_name="Zona"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='devices',
        verbose_name="Propietario"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class Measurement(models.Model):
    """Modelo para mediciones de dispositivos"""
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='measurements',
        verbose_name="Dispositivo"
    )
    value = models.FloatField(verbose_name="Valor")
    unit = models.CharField(max_length=50, verbose_name="Unidad")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Medición"
        verbose_name_plural = "Mediciones"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.device.name}: {self.value} {self.unit}"


class Alert(models.Model):
    """Modelo para alertas de dispositivos"""
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name="Dispositivo"
    )
    alert_type = models.CharField(
        max_length=20,
        choices=AlertType.choices,
        default=AlertType.INFO,
        verbose_name="Tipo"
    )
    message = models.TextField(verbose_name="Mensaje")
    is_resolved = models.BooleanField(default=False, verbose_name="Resuelta")
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_alert_type_display()}: {self.device.name}"

