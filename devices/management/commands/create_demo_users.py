from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = 'Crear usuarios de demostración con diferentes roles'

    def handle(self, *args, **kwargs):
        # Obtener los grupos
        try:
            admin_group = Group.objects.get(name='Administrador')
            editor_group = Group.objects.get(name='Editor')
            reader_group = Group.objects.get(name='Lector')
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Error: Primero ejecuta "python manage.py setup_groups"'))
            return
        
        # ===== USUARIO ADMINISTRADOR =====
        if User.objects.filter(username='admin').exists():
            admin_user = User.objects.get(username='admin')
            self.stdout.write(self.style.WARNING('⚠️  Usuario "admin" ya existe, actualizando...'))
        else:
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@ecoenergy.com',
                password='Admin123!',
                first_name='Administrador',
                last_name='Sistema',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS('✅ Usuario "admin" creado'))
        
        admin_user.groups.clear()
        admin_user.groups.add(admin_group)
        
        # ===== USUARIO EDITOR =====
        if User.objects.filter(username='editor').exists():
            editor_user = User.objects.get(username='editor')
            self.stdout.write(self.style.WARNING('⚠️  Usuario "editor" ya existe, actualizando...'))
        else:
            editor_user = User.objects.create_user(
                username='editor',
                email='editor@ecoenergy.com',
                password='Editor123!',
                first_name='Editor',
                last_name='Contenido',
                is_staff=False
            )
            self.stdout.write(self.style.SUCCESS('✅ Usuario "editor" creado'))
        
        editor_user.groups.clear()
        editor_user.groups.add(editor_group)
        
        # ===== USUARIO LECTOR =====
        if User.objects.filter(username='lector').exists():
            reader_user = User.objects.get(username='lector')
            self.stdout.write(self.style.WARNING('⚠️  Usuario "lector" ya existe, actualizando...'))
        else:
            reader_user = User.objects.create_user(
                username='lector',
                email='lector@ecoenergy.com',
                password='Lector123!',
                first_name='Usuario',
                last_name='Lector',
                is_staff=False
            )
            self.stdout.write(self.style.SUCCESS('✅ Usuario "lector" creado'))
        
        reader_user.groups.clear()
        reader_user.groups.add(reader_group)
        
        # Resumen
        self.stdout.write(self.style.SUCCESS('\n🎉 ¡Usuarios de demostración creados!'))
        self.stdout.write(self.style.WARNING('\n📋 Credenciales:'))
        self.stdout.write(self.style.WARNING('\n1️⃣  ADMINISTRADOR:'))
        self.stdout.write(self.style.WARNING('   Usuario: admin'))
        self.stdout.write(self.style.WARNING('   Contraseña: Admin123!'))
        self.stdout.write(self.style.WARNING('   Permisos: Acceso total'))
        
        self.stdout.write(self.style.WARNING('\n2️⃣  EDITOR:'))
        self.stdout.write(self.style.WARNING('   Usuario: editor'))
        self.stdout.write(self.style.WARNING('   Contraseña: Editor123!'))
        self.stdout.write(self.style.WARNING('   Permisos: Crear y editar'))
        
        self.stdout.write(self.style.WARNING('\n3️⃣  LECTOR:'))
        self.stdout.write(self.style.WARNING('   Usuario: lector'))
        self.stdout.write(self.style.WARNING('   Contraseña: Lector123!'))
        self.stdout.write(self.style.WARNING('   Permisos: Solo visualizar'))