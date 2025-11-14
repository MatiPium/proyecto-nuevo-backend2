from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Organization, Zone, Category, UserProfile


# Inline para UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'


# Extender UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_organization']
    list_select_related = ['profile']
    
    def get_organization(self, obj):
        if hasattr(obj, 'profile') and obj.profile.organization:
            return obj.profile.organization.name
        return '-'
    get_organization.short_description = 'Organización'


# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'
    ordering = ['name']


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization']
    list_filter = ['organization']
    search_fields = ['name', 'description']
    ordering = ['organization', 'name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'zone', 'phone']
    list_filter = ['organization', 'zone']
    search_fields = ['user__username', 'user__email', 'phone']
    raw_id_fields = ['user']
    list_select_related = ['user', 'organization', 'zone']

# Personalizar el título del admin
admin.site.site_header = "EcoEnergy - Administración"
admin.site.site_title = "EcoEnergy Admin"
admin.site.index_title = "Panel de Administración"

