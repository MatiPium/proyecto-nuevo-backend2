import re
from django.core.exceptions import ValidationError


def validate_strong_password(password):
    """
    Validar que la contraseña cumpla con los requisitos de seguridad:
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos un número
    - Al menos un carácter especial (opcional pero recomendado)
    """
    if len(password) < 8:
        raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError('La contraseña debe contener al menos una letra mayúscula.')
    
    if not re.search(r'[a-z]', password):
        raise ValidationError('La contraseña debe contener al menos una letra minúscula.')
    
    if not re.search(r'\d', password):
        raise ValidationError('La contraseña debe contener al menos un número.')
    
    # Opcional: validar caracteres especiales
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     raise ValidationError('La contraseña debe contener al menos un carácter especial.')
    
    return True


def validate_phone_number(phone):
    """
    Validar formato de número telefónico
    Acepta formatos: +56912345678, 912345678, +569 1234 5678
    """
    if not phone:
        return True
    
    # Remover espacios y guiones
    phone_clean = phone.replace(' ', '').replace('-', '')
    
    # Validar que solo contenga números y opcionalmente un '+'
    if not re.match(r'^\+?[\d]{8,15}$', phone_clean):
        raise ValidationError('Formato de teléfono inválido. Usa formato: +56912345678 o 912345678')
    
    return True