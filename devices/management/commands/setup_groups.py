from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from devices.models import Device, Measurement, Alert


class Command(BaseCommand):
    help = 'Configurar grupos y permisos del sistema'

    def handle(self, *args, **kwargs):
        # Limpiar grupos existentes
        Group.objects.all().delete()
        
        # ===== GRUPO ADMINISTRADOR =====
        admin_group, created = Group.objects.get_or_create(name='Administrador')
        
        # Obtener TODOS los permisos
        all_permissions = Permission.objects.all()
        admin_group.permissions.set(all_permissions)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Grupo "Administrador" creado con {all_permissions.count()} permisos'))
        
        # ===== GRUPO EDITOR =====
        editor_group, created = Group.objects.get_or_create(name='Editor')
        
        # Permisos para Editor (crear y editar, NO eliminar)
        editor_permissions = Permission.objects.filter(
            codename__in=[
                # Dispositivos
                'add_device',
                'change_device',
                'view_device',
                
                # Mediciones
                'add_measurement',
                'change_measurement',
                'view_measurement',
                
                # Alertas
                'add_alert',
                'change_alert',
                'view_alert',
                
                # Tipos de dispositivos
                'view_devicetype',
            ]
        )
        editor_group.permissions.set(editor_permissions)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Grupo "Editor" creado con {editor_permissions.count()} permisos'))
        
        # ===== GRUPO LECTOR =====
        reader_group, created = Group.objects.get_or_create(name='Lector')
        
        # Permisos para Lector (solo ver)
        reader_permissions = Permission.objects.filter(
            codename__in=[
                'view_device',
                'view_measurement',
                'view_alert',
                'view_devicetype',
            ]
        )
        reader_group.permissions.set(reader_permissions)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Grupo "Lector" creado con {reader_permissions.count()} permisos'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 ¡Grupos configurados exitosamente!'))
        self.stdout.write(self.style.WARNING('\n📋 Resumen de permisos:'))
        self.stdout.write(self.style.WARNING('  • Administrador: Acceso total (CRUD + gestión usuarios)'))
        self.stdout.write(self.style.WARNING('  • Editor: Crear, editar y ver'))
        self.stdout.write(self.style.WARNING('  • Lector: Solo visualizar'))