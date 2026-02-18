"""
Módulo de Autenticación de Doble Factor (2FA) con TOTP
=======================================================

Cumple con ISO 27001 - Control A.9.4.2 (Secure log-on procedures)

Este módulo añade autenticación de dos factores usando TOTP (Time-based One-Time Password)
compatible con Google Authenticator, Microsoft Authenticator, Authy, etc.

Autor: Equipo Coadix
Versión: 1.0
Fecha: Febrero 2026
"""

import pyotp
import qrcode
from io import BytesIO
import base64
from flask import session, flash, redirect, url_for, render_template_string
from functools import wraps


class TwoFactorAuth:
    """
    Gestor de autenticación de dos factores (2FA) con TOTP.
    
    Características:
    - Generación de secretos únicos por usuario
    - Códigos QR para configuración rápida
    - Validación de códigos TOTP de 6 dígitos
    - Compatible con Google Authenticator, Microsoft Authenticator, Authy
    """
    
    @staticmethod
    def generate_secret():
        """
        Genera un secreto único para un usuario.
        
        Returns:
            str: Secreto base32 (ej: "JBSWY3DPEHPK3PXP")
        """
        return pyotp.random_base32()
    
    @staticmethod
    def get_totp_uri(secret, username, issuer_name="MiApp"):
        """
        Genera la URI para el código QR.
        
        Args:
            secret (str): Secreto del usuario
            username (str): Email o nombre del usuario
            issuer_name (str): Nombre de tu aplicación
        
        Returns:
            str: URI en formato otpauth://
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name=issuer_name)
    
    @staticmethod
    def generate_qr_code(uri):
        """
        Genera un código QR en formato base64 para mostrar en HTML.
        
        Args:
            uri (str): URI del TOTP
        
        Returns:
            str: Imagen QR en base64 (data:image/png;base64,...)
        """
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
    
    @staticmethod
    def verify_code(secret, code):
        """
        Verifica un código TOTP de 6 dígitos.
        
        Args:
            secret (str): Secreto del usuario
            code (str): Código de 6 dígitos ingresado por el usuario
        
        Returns:
            bool: True si el código es válido
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # Acepta ±30 segundos
    
    @staticmethod
    def require_2fa(f):
        """
        Decorador para proteger rutas que requieren 2FA.
        
        Uso:
            @app.route('/admin')
            @TwoFactorAuth.require_2fa
            def admin_panel():
                return "Panel de administración"
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('2fa_verified'):
                flash('Debes completar la autenticación de dos factores.', 'warning')
                return redirect(url_for('verify_2fa'))
            return f(*args, **kwargs)
        return decorated_function


# ============================================================================
# EJEMPLO DE INTEGRACIÓN CON FLASK
# ============================================================================

"""
PASO 1: Añadir campo 'totp_secret' a tu tabla de usuarios

En SQLAlchemy:
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(120), unique=True)
        password_hash = db.Column(db.String(255))
        totp_secret = db.Column(db.String(32))  # <-- NUEVO CAMPO
        totp_enabled = db.Column(db.Boolean, default=False)  # <-- NUEVO CAMPO

En Google Sheets:
    Añade columnas: TOTP_SECRET, TOTP_ENABLED
"""

# PASO 2: Ruta para configurar 2FA (primera vez)
"""
from flask import Flask, request, session, render_template_string

app = Flask(__name__)

@app.route('/setup-2fa', methods=['GET', 'POST'])
def setup_2fa():
    user_email = session.get('user')
    
    if request.method == 'GET':
        # Generar secreto nuevo
        secret = TwoFactorAuth.generate_secret()
        session['temp_2fa_secret'] = secret
        
        # Generar QR
        uri = TwoFactorAuth.get_totp_uri(secret, user_email, issuer_name="Coadix")
        qr_code = TwoFactorAuth.generate_qr_code(uri)
        
        # Mostrar página de configuración
        return render_template_string('''
            <h1>Configurar Autenticación de Dos Factores</h1>
            <p>Escanea este código QR con Google Authenticator:</p>
            <img src="{{ qr_code }}" alt="QR Code">
            <p>O ingresa manualmente este código: <strong>{{ secret }}</strong></p>
            
            <form method="POST">
                <label>Ingresa el código de 6 dígitos para verificar:</label>
                <input type="text" name="code" maxlength="6" required>
                <button type="submit">Verificar y Activar</button>
            </form>
        ''', qr_code=qr_code, secret=secret)
    
    else:  # POST
        code = request.form.get('code')
        secret = session.get('temp_2fa_secret')
        
        if TwoFactorAuth.verify_code(secret, code):
            # Guardar secreto en la base de datos
            # user = db.get_user(user_email)
            # user.totp_secret = secret
            # user.totp_enabled = True
            # db.save(user)
            
            session.pop('temp_2fa_secret')
            flash('¡2FA activado correctamente!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Código inválido. Intenta de nuevo.', 'danger')
            return redirect(url_for('setup_2fa'))
"""

# PASO 3: Ruta para verificar 2FA en cada login
"""
@app.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    user_email = session.get('user')
    
    if request.method == 'GET':
        return render_template_string('''
            <h1>Verificación de Dos Factores</h1>
            <form method="POST">
                <label>Ingresa el código de 6 dígitos de tu app:</label>
                <input type="text" name="code" maxlength="6" required autofocus>
                <button type="submit">Verificar</button>
            </form>
        ''')
    
    else:  # POST
        code = request.form.get('code')
        
        # Obtener secreto del usuario desde BD
        # user = db.get_user(user_email)
        # secret = user.totp_secret
        
        secret = "JBSWY3DPEHPK3PXP"  # Ejemplo (obtener de BD)
        
        if TwoFactorAuth.verify_code(secret, code):
            session['2fa_verified'] = True
            flash('Autenticación exitosa', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Código inválido', 'danger')
            return redirect(url_for('verify_2fa'))
"""

# PASO 4: Proteger rutas sensibles
"""
@app.route('/admin')
@TwoFactorAuth.require_2fa
def admin_panel():
    return "Panel de administración (protegido con 2FA)"
"""

# PASO 5: Modificar el flujo de login
"""
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Validar usuario y contraseña
    # user = db.authenticate(email, password)
    
    # if user:
    session['user'] = email
    
    # Verificar si tiene 2FA habilitado
    # if user.totp_enabled:
    #     return redirect(url_for('verify_2fa'))
    # else:
    #     return redirect(url_for('dashboard'))
"""
