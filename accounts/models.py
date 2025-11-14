from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from PIL import Image
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

def validate_image_size(image):
    """Valida que la imagen no supere 2MB"""
    filesize = image.size
    if filesize > 2 * 1024 * 1024:  # 2MB
        raise ValidationError("El tamaño máximo de la imagen es 2MB")

class Organization(models.Model):
    """Modelo para organizaciones"""
    name = models.CharField(max_length=200, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    
    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"
    
    def __str__(self):
        return self.name


class Zone(models.Model):
    """Modelo para zonas geográficas"""
    name = models.CharField(max_length=200, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='zones', null=True, blank=True)
    
    class Meta:
        verbose_name = "Zona"
        verbose_name_plural = "Zonas"
    
    def __str__(self):
        return self.name


class Category(models.Model):
    """Modelo para categorías de dispositivos"""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
    
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Perfil de usuario extendido"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Avatar")
    bio = models.TextField(blank=True, null=True, verbose_name="Biografía")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.SET_NULL, 
        null=True,  # ← IMPORTANTE: debe ser null=True
        blank=True,  # ← IMPORTANTE: debe ser blank=True
        related_name='users',
        verbose_name="Organización"
    )
    zone = models.ForeignKey(
        Zone, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='users',
        verbose_name="Zona"
    )
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Validar y redimensionar imagen si existe
        if self.avatar:
            try:
                img = Image.open(self.avatar.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except Exception:
                pass


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear perfil automáticamente cuando se crea un usuario"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guardar perfil cuando se guarda el usuario"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

