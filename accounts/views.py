from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .validators import validate_strong_password, validate_phone_number
from .models import UserProfile


def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'accounts/login.html')


def register_view(request):
    """Vista de registro de usuarios"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        if not username or not email or not password:
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'accounts/register.html')
        
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'accounts/register.html')
        
        # Validar contraseña fuerte
        try:
            validate_strong_password(password)
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return render(request, 'accounts/register.html')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
            return redirect('login')
            
        except IntegrityError:
            messages.error(request, 'Error al crear el usuario. Intenta con otros datos.')
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')
    
    return render(request, 'accounts/register.html')


@login_required
def logout_view(request):
    """Vista para cerrar sesión"""
    username = request.user.username
    logout(request)
    messages.info(request, f'Sesión cerrada. ¡Hasta pronto {username}!')
    return redirect('login')


@login_required
def profile_view(request):
    """Vista del perfil del usuario"""
    from devices.models import Device, Measurement, Alert
    
    # Crear perfil si no existe
    if not hasattr(request.user, 'profile'):
        UserProfile.objects.create(user=request.user)
    
    device_count = Device.objects.filter(owner=request.user).count()
    measurement_count = Measurement.objects.filter(device__owner=request.user).count()
    alert_count = Alert.objects.filter(device__owner=request.user).count()
    
    context = {
        'user': request.user,
        'device_count': device_count,
        'measurement_count': measurement_count,
        'alert_count': alert_count,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Vista para editar el perfil del usuario"""
    # Crear perfil si no existe
    if not hasattr(request.user, 'profile'):
        UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user = request.user
        profile = user.profile
        
        # Actualizar datos básicos
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', user.email)
        
        # Actualizar teléfono
        phone = request.POST.get('phone', '')
        try:
            validate_phone_number(phone)
            profile.phone = phone
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'accounts/edit_profile.html')
        
        # Actualizar biografía
        profile.bio = request.POST.get('bio', '')
        
        # Procesar imagen de perfil (avatar)
        if 'avatar' in request.FILES:
            avatar = request.FILES['avatar']
            
            # Validar tamaño (máximo 2MB)
            if avatar.size > 2 * 1024 * 1024:
                messages.error(request, 'La imagen no puede superar los 2MB.')
                return render(request, 'accounts/edit_profile.html')
            
            # Validar tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if avatar.content_type not in allowed_types:
                messages.error(request, 'Formato de imagen inválido. Usa JPG, PNG o GIF.')
                return render(request, 'accounts/edit_profile.html')
            
            profile.avatar = avatar
        
        # Cambiar contraseña si se proporciona
        new_password = request.POST.get('new_password')
        if new_password:
            password_confirm = request.POST.get('password_confirm')
            
            if new_password != password_confirm:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'accounts/edit_profile.html')
            
            # Validar contraseña fuerte
            try:
                validate_strong_password(new_password)
            except ValidationError as e:
                messages.error(request, str(e))
                return render(request, 'accounts/edit_profile.html')
            
            user.set_password(new_password)
            messages.success(request, 'Contraseña actualizada. Por favor, inicia sesión nuevamente.')
            user.save()
            profile.save()
            logout(request)
            return redirect('login')
        
        try:
            user.save()
            profile.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('profile')
        except IntegrityError:
            messages.error(request, 'El correo electrónico ya está en uso.')
        except Exception as e:
            messages.error(request, f'Error al actualizar el perfil: {str(e)}')
    
    return render(request, 'accounts/edit_profile.html')

