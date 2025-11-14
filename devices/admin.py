from django.contrib import admin
from .models import Device, Measurement, Alert


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """Administración de dispositivos"""
    list_display = ['name', 'device_type', 'status', 'category', 'zone', 'owner']
    list_filter = ['device_type', 'status', 'category', 'zone']
    search_fields = ['name', 'description']


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    """Administración de mediciones"""
    list_display = ['device', 'value', 'unit', 'timestamp']
    list_filter = ['device', 'timestamp']
    search_fields = ['device__name']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Administración de alertas"""
    list_display = ['device', 'alert_type', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'is_resolved']
    search_fields = ['device__name', 'message']


# Personalizar el sitio de administración
admin.site.site_header = "EcoEnergy Monitor - Administración"
admin.site.site_title = "EcoEnergy Admin"
admin.site.index_title = "Panel de Control"