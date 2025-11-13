from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Configura los grupos y permisos del sistema'

    def handle(self, *args, **kwargs):
        # Limpiar grupos existentes
        Group.objects.all().delete()
        
        # GRUPO: Administrador
        admin_group, created = Group.objects.get_or_create(name='Administrador')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Administrador" creado'))
        
        # Asignar TODOS los permisos al Administrador
        all_permissions = Permission.objects.all()
        admin_group.permissions.set(all_permissions)
        self.stdout.write(self.style.SUCCESS(f'✓ Asignados {all_permissions.count()} permisos a Administrador'))

        # GRUPO: Editor
        editor_group, created = Group.objects.get_or_create(name='Editor')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Editor" creado'))
        
        # Permisos para Editor (add, change, view - sin delete)
        editor_permissions = Permission.objects.filter(
            codename__in=[
                # Device permissions
                'add_device',
                'change_device',
                'view_device',
                # Measurement permissions
                'add_measurement',
                'change_measurement',
                'view_measurement',
                # Alert permissions
                'add_alert',
                'change_alert',
                'view_alert',
                # DeviceType permissions
                'view_devicetype',
                # User profile permissions
                'view_userprofile',
                'change_userprofile',
            ]
        )
        editor_group.permissions.set(editor_permissions)
        self.stdout.write(self.style.SUCCESS(f'✓ Asignados {editor_permissions.count()} permisos a Editor'))

        # GRUPO: Lector
        reader_group, created = Group.objects.get_or_create(name='Lector')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Lector" creado'))
        
        # Permisos para Lector (solo view)
        reader_permissions = Permission.objects.filter(
            codename__startswith='view_'
        )
        reader_group.permissions.set(reader_permissions)
        self.stdout.write(self.style.SUCCESS(f'✓ Asignados {reader_permissions.count()} permisos a Lector'))

        self.stdout.write(self.style.SUCCESS('\n✅ Configuración de grupos completada'))
        self.stdout.write(self.style.WARNING('\n⚠ Recuerda asignar usuarios a los grupos desde el admin'))