import re
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit

def clave_valida(clave):
    return bool(len(clave) >= 8 and re.search(r'[A-Z]', clave) and re.search(r'\d', clave) and re.search(r'[^\w\s]|_', clave))

def correo_valido(correo):
    return re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', correo) is not None

def estado_login(activo, intentos, hasta, correcta, ahora):
    if not activo:
        return False, intentos, hasta, 'Cuenta inactiva.'
    limite = datetime.fromisoformat(hasta) if hasta else None
    if limite and ahora < limite:
        return False, intentos, hasta, 'Cuenta bloqueada durante 15 minutos. Intente más tarde.'
    if limite:
        intentos = 0
    if correcta:
        return True, 0, None, ''
    intentos += 1
    hasta = (ahora + timedelta(minutes=15)).isoformat() if intentos >= 5 else None
    return False, intentos, hasta, 'Cuenta bloqueada durante 15 minutos.' if hasta else 'Credenciales incorrectas.'

def centesimas(valor):
    try:
        numero = Decimal(str(valor).replace(',', '.')) * 100
        if not numero.is_finite() or numero <= 0 or numero != numero.to_integral_value():
            raise ValueError('Puntaje positivo con máximo dos decimales.')
        return int(numero)
    except (InvalidOperation, TypeError):
        raise ValueError('Puntaje inválido.') from None

def suma_valida(puntajes):
    return sum(puntajes) == 500

def video_valido(url):
    try:
        partes = urlsplit(url)
        return partes.scheme in ('http', 'https') and bool(partes.hostname)
    except ValueError:
        return False

def pdf_valido(nombre, mime, contenido):
    return nombre.lower().endswith('.pdf') and mime == 'application/pdf' and contenido.startswith(b'%PDF') and len(contenido) <= 10485760
