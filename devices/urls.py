from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Dispositivos
    path('devices/', views.device_list, name='device_list'),
    path('devices/create/', views.create_device, name='create_device'),
    path('devices/<int:pk>/', views.device_detail, name='device_detail'),
    path('devices/<int:pk>/edit/', views.update_device, name='edit_device'),
    path('devices/<int:pk>/delete/', views.delete_device, name='delete_device'),
    
    # Mediciones
    path('measurements/', views.measurement_list, name='measurement_list'),
    path('measurements/create/', views.create_measurement, name='create_measurement'),
    path('measurements/<int:pk>/edit/', views.edit_measurement, name='edit_measurement'),
    path('measurements/<int:pk>/delete/', views.delete_measurement, name='delete_measurement'),
    
    # Alertas
    path('alerts/', views.alert_list, name='alert_list'),
    
    # Exportar
    path('export/devices/', views.export_devices_excel, name='export_devices'),
    path('export/measurements/', views.export_measurements_excel, name='export_measurements'),
]