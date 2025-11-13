from django.contrib import admin
from .models import Organization, Zone, Device, Category, Measurement, Alert, DeviceType # importa SOLO lo que exista
from accounts.models import UserProfile  # nuevo

def _user_org(request):
    return getattr(getattr(request.user, "userprofile", None), "organization", None)

class ZoneInline(admin.TabularInline):
    model = Zone
    extra = 0
    fields = ("name", "status")
    show_change_link = True

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)
    inlines = [ZoneInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        org = _user_org(request)
        if org:
            return qs.filter(pk=org.pk)
        return qs.none()


class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "status")
    search_fields = ("name", "organization__name")
    list_filter = ("organization", "status")
    list_select_related = ("organization",)

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("organization")
        if request.user.is_superuser:
            return qs
        org = _user_org(request)
        return qs.filter(organization=org)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == "organization":
            org = _user_org(request)
            if org:
                kwargs["queryset"] = Organization.objects.filter(pk=org.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.action(description="Activar dispositivos seleccionados")
def make_active(modeladmin, request, queryset):
    queryset.update(status="ACTIVE")  # ajusta si tu campo/valor difiere


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """Administración de dispositivos"""
    list_display = ['name', 'device_type', 'owner', 'location', 'is_active', 'created_at']
    list_filter = ['device_type', 'is_active', 'created_at']
    search_fields = ['name', 'location', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'device_type', 'owner', 'location')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("organization", "zone", "category")
        if request.user.is_superuser:
            return qs
        org = _user_org(request)
        return qs.filter(organization=org)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            org = _user_org(request)
            if org:
                if db_field.name == "organization":
                    kwargs["queryset"] = Organization.objects.filter(pk=org.pk)
                if db_field.name == "zone":
                    kwargs["queryset"] = Zone.objects.filter(organization=org)
                if db_field.name == "category":
                    kwargs["queryset"] = Category.objects.filter(organization=org)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "organization")
    search_fields = ("name", "organization__name")
    list_filter = ("organization",)

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("organization")
        if request.user.is_superuser:
            return qs
        org = _user_org(request)
        return qs.filter(organization=org)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == "organization":
            org = _user_org(request)
            if org:
                kwargs["queryset"] = Organization.objects.filter(pk=org.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    """Administración de mediciones"""
    list_display = ['device', 'value', 'unit', 'timestamp']
    list_filter = ['device', 'timestamp']
    search_fields = ['device__name']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('device', 'device__owner')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Administración de alertas"""
    list_display = ['device', 'severity', 'message', 'is_resolved', 'created_at']
    list_filter = ['severity', 'is_resolved', 'created_at']
    search_fields = ['device__name', 'message']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Información de la Alerta', {
            'fields': ('device', 'message', 'severity')
        }),
        ('Estado', {
            'fields': ('is_resolved', 'resolved_at')
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('device', 'device__owner')


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    """Administración de tipos de dispositivos"""
    list_display = ['name', 'description']
    search_fields = ['name']


# Personalizar el sitio de administración
admin.site.site_header = "EcoEnergy Monitor - Administración"
admin.site.site_title = "EcoEnergy Admin"
admin.site.index_title = "Panel de Control"