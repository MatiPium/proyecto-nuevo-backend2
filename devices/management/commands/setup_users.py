from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from devices.models import Device, Measurement, Alert


class Command(BaseCommand):
    help = 'Configurar usuarios y grupos del sistema'

    def handle(self, *args, **options):
        self.stdout.write('🔐 Configurando usuarios...')

        # Eliminar usuarios existentes
        User.objects.all().delete()
        
        # Crear grupos
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        editor_group, _ = Group.objects.get_or_create(name='Editor')
        lector_group, _ = Group.objects.get_or_create(name='Lector')

        # Obtener permisos
        device_ct = ContentType.objects.get_for_model(Device)
        measurement_ct = ContentType.objects.get_for_model(Measurement)
        alert_ct = ContentType.objects.get_for_model(Alert)

        all_perms = Permission.objects.filter(
            content_type__in=[device_ct, measurement_ct, alert_ct]
        )

        # Admin: todos los permisos
        admin_group.permissions.set(all_perms)

        # Editor: ver, agregar, cambiar
        editor_perms = Permission.objects.filter(
            content_type__in=[device_ct, measurement_ct, alert_ct],
            codename__startswith='view_'
        ) | Permission.objects.filter(
            content_type__in=[device_ct, measurement_ct, alert_ct],
            codename__startswith='add_'
        ) | Permission.objects.filter(
            content_type__in=[device_ct, measurement_ct, alert_ct],
            codename__startswith='change_'
        )
        editor_group.permissions.set(editor_perms)

        # Lector: solo ver
        lector_perms = Permission.objects.filter(
            content_type__in=[device_ct, measurement_ct, alert_ct],
            codename__startswith='view_'
        )
        lector_group.permissions.set(lector_perms)

        # Crear usuarios
        # ADMIN
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@ecoenergy.com',
            password='admin123'
        )
        admin.groups.add(admin_group)
        self.stdout.write(self.style.SUCCESS('✅ admin / admin123'))

        # EDITOR
        editor = User.objects.create_user(
            username='editor',
            email='editor@ecoenergy.com',
            password='editor123'
        )
        editor.is_staff = True
        editor.groups.add(editor_group)
        editor.save()
        self.stdout.write(self.style.SUCCESS('✅ editor / editor123'))

        # LECTOR
        lector = User.objects.create_user(
            username='lector',
            email='lector@ecoenergy.com',
            password='lector123'
        )
        lector.groups.add(lector_group)
        lector.save()
        self.stdout.write(self.style.SUCCESS('✅ lector / lector123'))

        self.stdout.write(self.style.SUCCESS('\n🎉 Usuarios configurados correctamente'))