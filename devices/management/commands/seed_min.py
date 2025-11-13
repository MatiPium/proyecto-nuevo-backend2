from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal
from devices.models import Device, DeviceType, Measurement, Alert


class Command(BaseCommand):
    help = 'Seed mínimo con datos de prueba'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Creando datos...')

        # Obtener admin
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            self.stdout.write(self.style.ERROR('❌ Crea primero un superusuario'))
            return

        # Tipos de dispositivos
        tipos = []
        for nombre in ['Panel Solar', 'Medidor Inteligente', 'Inversor', 'Batería', 'Sensor']:
            tipo, _ = DeviceType.objects.get_or_create(
                name=nombre, 
                defaults={'description': f'Dispositivo tipo {nombre} para monitoreo energético'}
            )
            tipos.append(tipo)
        self.stdout.write(f'✅ {len(tipos)} tipos de dispositivos')

        # Dispositivos
        dispositivos = []
        nombres_devices = [
            'Panel Solar Techo A',
            'Panel Solar Techo B', 
            'Medidor Principal',
            'Inversor Central',
            'Batería Respaldo'
        ]
        
        for i, nombre in enumerate(nombres_devices):
            device, created = Device.objects.get_or_create(
                name=nombre,
                owner=admin,
                defaults={
                    'device_type': tipos[i % len(tipos)],
                    'location': f'Zona {chr(65+i)} - Piso {(i % 3) + 1}',
                    'is_active': True
                }
            )
            dispositivos.append(device)
            
        self.stdout.write(f'✅ {len(dispositivos)} dispositivos')

        # Mediciones (últimos 7 días, 2 por día)
        now = timezone.now()
        count_measurements = 0
        
        for device in dispositivos:
            for day in range(7):
                for hour in [9, 18]:
                    try:
                        # Generar valor entre 10 y 100 con 2 decimales
                        value = Decimal(str(round(random.uniform(10.0, 100.0), 2)))
                        
                        Measurement.objects.create(
                            device=device,
                            value=value,
                            unit='kWh',
                            timestamp=now - timedelta(days=day, hours=24-hour)
                        )
                        count_measurements += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'⚠️  Error: {e}'))

        self.stdout.write(f'✅ {count_measurements} mediciones')

        # Alertas
        count_alerts = 0
        mensajes = [
            'Consumo superior al promedio detectado en las últimas 24 horas',
            'Dispositivo presenta lecturas irregulares que requieren revisión',
            'Mantenimiento preventivo recomendado según horas de operación',
            'Temperatura del sistema por encima del rango normal de operación',
            'Eficiencia de conversión por debajo del umbral esperado'
        ]
        
        try:
            for device in random.sample(dispositivos, min(3, len(dispositivos))):
                Alert.objects.create(
                    device=device,
                    severity=random.choice(['low', 'medium', 'high']),
                    message=random.choice(mensajes),
                    is_resolved=random.choice([True, False])
                )
                count_alerts += 1
            self.stdout.write(f'✅ {count_alerts} alertas')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Error creando alertas: {e}'))

        # Resumen
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('🎉 SEED COMPLETADO EXITOSAMENTE'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'📊 Tipos: {len(tipos)}')
        self.stdout.write(f'📱 Dispositivos: {len(dispositivos)}')
        self.stdout.write(f'📈 Mediciones: {count_measurements}')
        self.stdout.write(f'⚠️  Alertas: {count_alerts}')
        self.stdout.write(self.style.SUCCESS('='*50))