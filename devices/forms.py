from django import forms
from .models import Device, Measurement, Alert, Organization
from django.contrib.auth.models import User


# ---------------------------
# 📌 Device Form
# ---------------------------
class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name', 'category', 'zone', 'maximum_consumption', 'organization', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'zone': forms.Select(attrs={'class': 'form-control'}),
            'maximum_consumption': forms.NumberInput(attrs={'class': 'form-control'}),
            'organization': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


# ---------------------------
# 👤 User Update Form
# ---------------------------
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }


# ---------------------------
# 📏 Measurement Form
# ---------------------------
class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ["device", "consumption", "organization"]
        widgets = {
            "device": forms.Select(attrs={"class": "form-control"}),
            "consumption": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "organization": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Tomar la organización del usuario (si la tienes en UserProfile)
        org = getattr(getattr(user, "userprofile", None), "organization", None) if user else None

        if org:
            # Devices solo de su organización
            self.fields["device"].queryset = Device.objects.filter(organization=org)

            # Organization fija (initial + queryset recortado)
            self.fields["organization"].initial = org
            self.fields["organization"].queryset = Organization.objects.filter(pk=org.pk)

            # Opcional: bloquear edición para no-supers
            if not user.is_superuser:
                self.fields["organization"].disabled = True

    def clean(self):
        cleaned = super().clean()
        device = cleaned.get("device")
        org = cleaned.get("organization")
        if device and org and device.organization_id != org.id:
            self.add_error("device", "El dispositivo no pertenece a la organización seleccionada.")
        return cleaned


# ---------------------------
# 🚨 Alert Form
# ---------------------------
class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = ["device", "message", "severity", "organization"]
        widgets = {
            "device": forms.Select(attrs={"class":"form-control"}),
            "message": forms.Textarea(attrs={"class":"form-control","rows":3,"maxlength":200}),
            "severity": forms.Select(attrs={"class":"form-control"}),
            "organization": forms.Select(attrs={"class":"form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        org = getattr(getattr(user, "userprofile", None), "organization", None) if user else None
        if org:
            self.fields["device"].queryset = Device.objects.filter(organization=org)
            self.fields["organization"].initial = org
            self.fields["organization"].queryset = Organization.objects.filter(pk=org.pk)
            if not user.is_superuser:
                self.fields["organization"].disabled = True

    def clean(self):
        cleaned = super().clean()
        device = cleaned.get("device")
        org = cleaned.get("organization")
        if device and org and device.organization_id != org.id:
            self.add_error("device", "El dispositivo no pertenece a la organización seleccionada.")
        return cleaned
