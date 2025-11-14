from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from devices.models import Device, DeviceType, DeviceStatus, Measurement, Alert, AlertType
from accounts.models import Organization, Zone, Category
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Crear datos mínimos de prueba compartidos por organización'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            default='admin',
            help='Username del propietario principal (default: admin)'
        )

    def handle(self, *args, **options):
        username = options.get('user', 'admin')
        
        try:
            owner = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Usuario {username} no existe'))
            return

        self.stdout.write(f'🌱 Creando datos de prueba compartidos para organización...')

        # Limpiar datos existentes
        Measurement.objects.all().delete()
        Alert.objects.all().delete()
        Device.objects.all().delete()
        Category.objects.all().delete()
        Zone.objects.all().delete()
        Organization.objects.all().delete()

        # Crear organización
        org = Organization.objects.create(
            name='EcoEnergy Corp',
            description='Organización de monitoreo energético'
        )
        self.stdout.write(self.style.SUCCESS(f'✅ Organización: {org.name}'))

        # Crear zonas
        zones = []
        zone_names = ['Zona Norte', 'Zona Centro', 'Zona Sur']
        for zone_name in zone_names:
            zone = Zone.objects.create(
                name=zone_name,
                description=f'Zona geográfica: {zone_name}',
                organization=org
            )
            zones.append(zone)
        self.stdout.write(self.style.SUCCESS(f'✅ {len(zones)} zonas creadas'))

        # Crear categorías
        categories = []
        category_data = [
            ('Solar', 'Dispositivos de energía solar'),
            ('Eólica', 'Dispositivos de energía eólica'),
            ('Hidráulica', 'Dispositivos de energía hidráulica'),
            ('Térmica', 'Dispositivos de energía térmica'),
        ]
        for cat_name, cat_desc in category_data:
            cat = Category.objects.create(
                name=cat_name,
                description=cat_desc
            )
            categories.append(cat)
        self.stdout.write(self.style.SUCCESS(f'✅ {len(categories)} categorías creadas'))

        # Asignar organización a TODOS los usuarios
        all_users = User.objects.all()
        for user in all_users:
            if hasattr(user, 'profile'):
                user.profile.organization = org
                user.profile.zone = random.choice(zones)
                user.profile.save()
                self.stdout.write(self.style.SUCCESS(f'   👤 {user.username} → {org.name}'))

        # Crear dispositivos
        devices_data = [
            {'name': 'Panel Solar A1', 'type': DeviceType.SENSOR, 'category': categories[0], 'zone': zones[0]},
            {'name': 'Panel Solar A2', 'type': DeviceType.SENSOR, 'category': categories[0], 'zone': zones[0]},
            {'name': 'Turbina Eólica B1', 'type': DeviceType.ACTUATOR, 'category': categories[1], 'zone': zones[1]},
            {'name': 'Turbina Eólica B2', 'type': DeviceType.ACTUATOR, 'category': categories[1], 'zone': zones[1]},
            {'name': 'Generador Hidro C1', 'type': DeviceType.SENSOR, 'category': categories[2], 'zone': zones[2]},
            {'name': 'Medidor Central D1', 'type': DeviceType.METER, 'category': categories[3], 'zone': zones[0]},
            {'name': 'Sensor Térmico E1', 'type': DeviceType.SENSOR, 'category': categories[3], 'zone': zones[1]},
        ]

        devices = []
        for device_data in devices_data:
            device = Device.objects.create(
                name=device_data['name'],
                device_type=device_data['type'],
                category=device_data['category'],
                zone=device_data['zone'],
                owner=owner,
                status=DeviceStatus.ACTIVE,
                description=f'Dispositivo compartido: {device_data["name"]}'
            )
            devices.append(device)
            self.stdout.write(self.style.SUCCESS(f'✅ Dispositivo: {device.name}'))

        # Crear mediciones
        total_measurements = 0
        for device in devices:
            num_measurements = random.randint(15, 30)
            for i in range(num_measurements):
                hours_ago = random.randint(1, 720)
                timestamp = datetime.now() - timedelta(hours=hours_ago)
                
                if device.device_type == DeviceType.SENSOR:
                    value = round(random.uniform(50, 150), 2)
                elif device.device_type == DeviceType.ACTUATOR:
                    value = round(random.uniform(100, 300), 2)
                else:
                    value = round(random.uniform(20, 80), 2)
                
                Measurement.objects.create(
                    device=device,
                    value=value,
                    unit='kWh',
                    timestamp=timestamp
                )
                total_measurements += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ {total_measurements} mediciones creadas'))

        # Crear alertas
        alert_configs = [
            {'type': AlertType.CRITICAL, 'count': 2},
            {'type': AlertType.WARNING, 'count': 3},
            {'type': AlertType.INFO, 'count': 2},
        ]
        
        alerts_created = 0
        for config in alert_configs:
            sample_devices = random.sample(devices, min(config['count'], len(devices)))
            for device in sample_devices:
                Alert.objects.create(
                    device=device,
                    alert_type=config['type'],
                    message=f"Alerta {config['type']}: {device.name} requiere atención",
                    is_resolved=random.choice([True, False])
                )
                alerts_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ {alerts_created} alertas creadas'))

        self.stdout.write(self.style.SUCCESS('\n🎉 ¡Datos compartidos creados exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'\n📊 Resumen:'))
        self.stdout.write(self.style.SUCCESS(f'   🏢 1 organización: {org.name}'))
        self.stdout.write(self.style.SUCCESS(f'   🗺️  {len(zones)} zonas'))
        self.stdout.write(self.style.SUCCESS(f'   📁 {len(categories)} categorías'))
        self.stdout.write(self.style.SUCCESS(f'   🔌 {len(devices)} dispositivos'))
        self.stdout.write(self.style.SUCCESS(f'   📈 {total_measurements} mediciones'))
        self.stdout.write(self.style.SUCCESS(f'   ⚠️  {alerts_created} alertas'))
        self.stdout.write(self.style.SUCCESS(f'\n👥 Todos los usuarios de "{org.name}" pueden ver estos datos'))