from django.contrib import admin
from .models import Organization, Zone, Device, Category, Measurement, Alert # importa SOLO lo que exista
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
    list_display = ("name", "organization", "zone", "status")
    search_fields = ("name", "organization__name", "zone__name")
    list_filter = ("organization", "zone", "status")
    list_select_related = ("organization", "zone", "category")
    readonly_fields = ("created_at", "updated_at", "deleted_at")  # evita tocar soft-delete
    actions = [make_active]  # deja tu acción como la tienes

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
    list_display = ("device", "organization", "consumption", "created_at")
    search_fields = ("device__name", "organization__name")
    list_filter = ("organization", "device")
    date_hierarchy = "created_at"
    list_select_related = ("device", "organization")

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("device", "organization")
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
                if db_field.name == "device":
                    kwargs["queryset"] = Device.objects.filter(organization=org)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("device", "organization", "severity", "message", "created_at")
    search_fields = ("device__name", "organization__name", "message")
    list_filter = ("organization", "severity", "device")
    date_hierarchy = "created_at"
    list_select_related = ("device", "organization")

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("device", "organization")
        if request.user.is_superuser:
            return qs
        org = _user_org(request)  # mismo helper que usaste para Device/Measurement
        return qs.filter(organization=org)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            org = _user_org(request)
            if org:
                if db_field.name == "organization":
                    kwargs["queryset"] = Organization.objects.filter(pk=org.pk)
                if db_field.name == "device":
                    kwargs["queryset"] = Device.objects.filter(organization=org)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)