from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.utils.timezone import now
from datetime import timedelta
from django.contrib import messages



from .models import Device, Measurement, Zone, Category, Alert, Organization
from .forms import DeviceForm, UserUpdateForm, MeasurementForm, AlertForm


# ---------------------------
# 🔐 Autenticación
# ---------------------------

def login_view(request):
    if request.method == 'POST':
        identifier = (request.POST.get('email') or '').strip()   # puede ser email o username
        password   = (request.POST.get('password') or '')
        next_url   = request.POST.get('next') or request.GET.get('next')

        # Resolver a username si nos pasaron un email
        username = identifier
        if '@' in identifier:
            User = get_user_model()
            user_obj = User.objects.filter(email__iexact=identifier).first()
            username = user_obj.get_username() if user_obj else None

        user = authenticate(request, username=username, password=password) if username else None
        if user and user.is_active:
            login(request, user)
            return redirect(next_url or 'dashboard')  # cambia 'dashboard' si tu nombre de url es otro

        messages.error(request, 'Email o contraseña incorrectos')

    return render(request, 'devices/login.html')


def register_view(request):
    if request.method == 'POST':
        company_name = request.POST['company_name']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        if password != password_confirm:
            return render(request, 'devices/register.html', {
                'error': 'Las contraseñas no coinciden'
            })

        if len(password) < 12:
            return render(request, 'devices/register.html', {
                'error': 'La contraseña debe tener al menos 12 caracteres'
            })

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=company_name
            )
            # 🔹 Crear organización asociada al usuario
            Organization.objects.create(name=company_name)

            return render(request, 'devices/register.html', {
                'success': f'¡Registro exitoso! La empresa {company_name} ha sido registrada correctamente.'
            })
        except IntegrityError:
            return render(request, 'devices/register.html', {
                'error': 'Este correo electrónico ya está registrado'
            })
        except Exception:
            return render(request, 'devices/register.html', {
                'error': 'Error al registrar la empresa. Intenta nuevamente.'
            })

    return render(request, 'devices/register.html')


def password_reset(request):
    message_sent = False
    if request.method == "POST":
        email = request.POST.get('email')
        message_sent = True
    return render(request, 'devices/password_reset.html', {'message_sent': message_sent})


@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'devices/edit_profile.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect("login")


# ---------------------------
# 📊 Dashboard
# ---------------------------

def _user_org(user):
    # Ajusta al nombre real de tu relación/perfil
    return getattr(getattr(user, "userprofile", None), "organization", None)

@login_required
def dashboard(request):
    org = _user_org(request.user)

    # Base querysets
    m_qs = Measurement.objects.all().select_related("device")
    a_qs = Alert.objects.all().select_related("device", "organization")
    d_qs = Device.objects.all().select_related("organization")
    c_qs = Category.objects.all()
    z_qs = Zone.objects.all()

    # ⬇️ Scoping: si NO es superuser, filtramos por organización del usuario
    if not request.user.is_superuser and org:
        m_qs = m_qs.filter(organization=org)
        a_qs = a_qs.filter(organization=org)
        d_qs = d_qs.filter(organization=org)
        # si Category/Zone tienen FK a Organization:
        c_qs = c_qs.filter(organization=org)
        z_qs = z_qs.filter(organization=org)

    # Últimas mediciones / alertas
    latest_measurements = m_qs.order_by("-date")[:10]
    recent_alerts = a_qs.order_by("-date")[:5]

    # Conteos
    devices = d_qs
    devices_count = d_qs.count()
    alert_count = a_qs.count()
    categories = c_qs
    zones = z_qs

    # Resumen de alertas última semana
    one_week_ago = now() - timedelta(days=7)
    alerts_week = a_qs.filter(date__gte=one_week_ago)
    alert_counts = {
        "high":   alerts_week.filter(severity="high").count(),
        "medium": alerts_week.filter(severity="medium").count(),
        "low":    alerts_week.filter(severity="low").count(),
    }

    # Pasamos la organización real del usuario (no la "first")
    organization = org

    return render(
        request,
        "devices/dashboard.html",
        {
            "latest_measurements": latest_measurements,
            "recent_alerts": recent_alerts,
            "alert_count": alert_count,
            "categories": categories,
            "zones": zones,
            "devices": devices,
            "devices_count": devices_count,
            "alert_counts": alert_counts,
            "organization": organization,
        },
    )



# ---------------------------
# 💻 Dispositivos
# ---------------------------

@login_required
def device_list(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category', '')

    devices = Device.objects.select_related("category", "zone")
    if selected_category:
        devices = devices.filter(category_id=selected_category)

    return render(request, "devices/device.html", {
        "devices": devices,
        "categories": categories,
        "selected_category": selected_category,
    })


@login_required
def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk)
    measurements = Measurement.objects.filter(device=device).order_by('-date')[:10]
    alerts = Alert.objects.filter(device=device).order_by('-date')[:10]

    return render(request, 'devices/device_detail.html', {
        'device': device,
        'measurements': measurements,
        'alerts': alerts,
    })

@permission_required('devices.add_device', raise_exception=True)
@login_required
def create_device(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('device_list')
    else:
        form = DeviceForm()
    return render(request, 'devices/create.html', {'form': form})

@permission_required('devices.change_device', raise_exception=True)
@login_required
def update_device(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            return redirect('device_detail', pk=device.pk)
    else:
        form = DeviceForm(instance=device)
    return render(request, 'devices/update_device.html', {'form': form, 'device': device})

@permission_required('devices.delete_device', raise_exception=True)
@login_required
def delete_device(request, pk):
    device = get_object_or_404(Device, pk=pk)
    if request.method == 'POST':
        device.delete()
        return redirect('device_list')
    return render(request, 'devices/delete_device.html', {'device': device})


# ---------------------------
# 📏 Mediciones
# ---------------------------

@login_required
def measurement_list(request):
    # scoping: solo mediciones de mi organización
    org = getattr(getattr(request.user, "userprofile", None), "organization", None)
    qs = Measurement.objects.all().select_related("device", "organization")
    if not request.user.is_superuser and org:
        qs = qs.filter(organization=org)
    return render(request, "devices/measurement_list.html", {"measurements": qs})


@login_required
def measurement_create(request):
    if request.method == "POST":
        form = MeasurementForm(request.POST, user=request.user)
        if form.is_valid():
            m = form.save(commit=False)
            # forzamos organización del usuario si no es superuser
            if not request.user.is_superuser and hasattr(request.user, "userprofile"):
                m.organization = request.user.userprofile.organization
            m.save()
            return redirect("measurement_list")
    else:
        form = MeasurementForm(user=request.user)
    return render(request, "devices/measurement_form.html", {"form": form})


# ---------------------------
# 🚨 Alertas
# ---------------------------

@login_required
def add_alert(request, device_id=None):
    devices = Device.objects.all()
    device = None

    if device_id:
        device = get_object_or_404(Device, id=device_id)

    if request.method == 'POST':
        device_id = request.POST.get('device') or (device.id if device else None)
        message = request.POST.get('message')
        severity = request.POST.get('severity')

        if device_id and message and severity:
            device_obj = get_object_or_404(Device, id=device_id)
            Alert.objects.create(
                device=device_obj,
                message=message,
                severity=severity,
                organization=device_obj.organization
            )
            return redirect('dashboard')

    return render(request, 'devices/alert_form.html', {
        'devices': devices,
        'device': device
    })



@login_required
def alert_summary(request):
    week_ago = now() - timedelta(days=7)
    alerts = Alert.objects.filter(date__gte=week_ago).order_by('-date')

    alert_counts = {
        'high': alerts.filter(severity='high').count(),
        'medium': alerts.filter(severity='medium').count(),
        'low': alerts.filter(severity='low').count(),
    }

    from .models import Organization
    organization = Organization.objects.first()

    return render(request, 'devices/alert_summary.html', {
        'alerts': alerts,
        'alert_counts': alert_counts,
        'one_week_ago': week_ago,
        'organization': organization,   
    })




# ---------------------------
# 🌐 Página inicial
# ---------------------------

def start(request):
    devices = Device.objects.all()
    return render(request, "devices/start.html", {"devices": devices})


@login_required
def alert_list(request):
    org = getattr(getattr(request.user, "userprofile", None), "organization", None)
    qs = Alert.objects.all().select_related("device","organization").order_by("-created_at")
    if not request.user.is_superuser and org:
        qs = qs.filter(organization=org)
    return render(request, "devices/alert_list.html", {"alerts": qs})

@login_required
def alert_create(request):
    if request.method == "POST":
        form = AlertForm(request.POST, user=request.user)
        if form.is_valid():
            a = form.save(commit=False)
            if not request.user.is_superuser:
                a.organization = request.user.userprofile.organization
            a.save()
            return redirect("alert_list")
    else:
        form = AlertForm(user=request.user)
    return render(request, "devices/alert_form.html", {"form": form})