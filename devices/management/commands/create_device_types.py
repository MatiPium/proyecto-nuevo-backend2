from django.core.management.base import BaseCommand
from devices.models import DeviceType


class Command(BaseCommand):
    help = 'Crea tipos de dispositivos iniciales'

    def handle(self, *args, **kwargs):
        device_types = [
            {
                'name': 'Medidor Inteligente',
                'description': 'Medidor de consumo eléctrico inteligente'
            },
            {
                'name': 'Sensor de Temperatura',
                'description': 'Sensor para monitorear temperatura ambiente'
            },
            {
                'name': 'Panel Solar',
                'description': 'Panel solar con monitoreo de generación'
            },
            {
                'name': 'Inversor',
                'description': 'Inversor de corriente con telemetría'
            },
            {
                'name': 'Batería',
                'description': 'Sistema de almacenamiento de energía'
            },
        ]
        
        for dt_data in device_types:
            device_type, created = DeviceType.objects.get_or_create(
                name=dt_data['name'],
                defaults={'description': dt_data['description']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Tipo "{device_type.name}" creado'))
            else:
                self.stdout.write(self.style.WARNING(f'- Tipo "{device_type.name}" ya existe'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Tipos de dispositivos configurados'))