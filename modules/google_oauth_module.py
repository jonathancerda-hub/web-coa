"""
Módulo de Autenticación OAuth con Google para Flask
====================================================

Este módulo proporciona autenticación completa con Google OAuth 2.0
para aplicaciones Flask. Incluye auto-registro de usuarios con dominios
corporativos autorizados.

Autor: Equipo Coadix
Versión: 2.0
Fecha: Febrero 2026
"""

from flask import Flask, redirect, url_for, session, flash, request
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix
from functools import wraps
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class GoogleOAuthManager:
    """
    Gestor de autenticación OAuth con Google.
    
    Características:
    - Inicio de sesión con Google
    - Auto-registro de usuarios con dominios autorizados
    - Manejo de sesiones
    - Redirección segura
    """
    
    def __init__(self, app, authorized_domains=None, user_callback=None):
        """
        Inicializa el gestor de OAuth.
        
        Args:
            app (Flask): Instancia de la aplicación Flask
            authorized_domains (list): Lista de dominios autorizados (ej: ['@company.com'])
            user_callback (callable): Función para crear/actualizar usuario en tu BD
                                     Debe aceptar (email, name, picture) y retornar user_data
        """
        self.app = app
        self.authorized_domains = authorized_domains or []
        self.user_callback = user_callback
        
        # Configurar ProxyFix para HTTPS en producción
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
        
        # Inicializar OAuth
        self.oauth = OAuth()
        self.google = self.oauth.register(
            name='google',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
        )
        self.oauth.init_app(app)
        
        # Validar credenciales
        if not all([os.getenv('GOOGLE_CLIENT_ID'), os.getenv('GOOGLE_CLIENT_SECRET')]):
            print("\n*** ADVERTENCIA: Faltan GOOGLE_CLIENT_ID o GOOGLE_CLIENT_SECRET ***\n")
        
        # Registrar rutas
        self._register_routes()
    
    def _register_routes(self):
        """Registra las rutas de OAuth en la aplicación Flask."""
        
        @self.app.route('/login/google')
        def login_google():
            """Inicia el flujo de autenticación con Google."""
            redirect_uri = url_for('google_callback', _external=True)
            return self.google.authorize_redirect(redirect_uri)
        
        @self.app.route('/login/google/callback')
        def google_callback():
            """
            Callback de Google OAuth.
            Procesa la respuesta de Google y crea/actualiza el usuario.
            """
            try:
                # Obtener token de Google
                token = self.google.authorize_access_token()
                
                # Obtener información del usuario
                user_info = token.get('userinfo')
                if not user_info:
                    flash('No se pudo obtener la información del usuario de Google.', 'danger')
                    return redirect(url_for('login'))
                
                email = user_info.get('email')
                name = user_info.get('name', '')
                picture = user_info.get('picture', '')
                
                # Validar dominio si hay dominios autorizados
                if self.authorized_domains:
                    domain_valid = any(email.endswith(domain) for domain in self.authorized_domains)
                    if not domain_valid:
                        flash(f'El dominio de tu correo no está autorizado. Dominios permitidos: {", ".join(self.authorized_domains)}', 'danger')
                        return redirect(url_for('login'))
                
                # Llamar al callback de usuario (crear/actualizar en BD)
                if self.user_callback:
                    try:
                        user_data = self.user_callback(email, name, picture)
                        
                        # Establecer sesión
                        session.permanent = True
                        session['user'] = email
                        session['username'] = name
                        session['role'] = user_data.get('role', 'Usuario')
                        session['picture'] = picture
                        
                        flash(f'¡Bienvenido, {name}!', 'success')
                        return redirect(url_for('dashboard'))
                    
                    except Exception as e:
                        flash(f'Error al registrar/actualizar usuario: {e}', 'danger')
                        return redirect(url_for('login'))
                else:
                    # Sin callback, solo establecer sesión básica
                    session.permanent = True
                    session['user'] = email
                    session['username'] = name
                    session['picture'] = picture
                    
                    flash(f'¡Bienvenido, {name}!', 'success')
                    return redirect(url_for('dashboard'))
            
            except Exception as e:
                flash(f'Error en la autenticación con Google: {e}', 'danger')
                return redirect(url_for('login'))
    
    @staticmethod
    def login_required(f):
        """
        Decorador para proteger rutas que requieren autenticación.
        
        Uso:
            @app.route('/protected')
            @GoogleOAuthManager.login_required
            def protected_route():
                return "Contenido protegido"
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                flash('Debes iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == '__main__':
    """
    Ejemplo de cómo integrar GoogleOAuthManager en tu aplicación Flask.
    """
    
    # 1. Crear aplicación Flask
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'clave-secreta-para-desarrollo')
    
    # 2. Definir función callback para crear/actualizar usuario
    def handle_user_login(email, name, picture):
        """
        Esta función se llama cuando un usuario se autentica con Google.
        Aquí debes crear o actualizar el usuario en tu base de datos.
        
        Args:
            email (str): Email del usuario
            name (str): Nombre completo del usuario
            picture (str): URL de la foto de perfil
        
        Returns:
            dict: Datos del usuario (debe incluir 'role' si usas roles)
        """
        # Ejemplo: Buscar o crear usuario en tu base de datos
        # user = db.find_user(email)
        # if not user:
        #     user = db.create_user(email=email, name=name, picture=picture, role='Usuario')
        # else:
        #     db.update_user(email, name=name, picture=picture)
        
        # Por ahora, retornamos datos de ejemplo
        return {
            'email': email,
            'name': name,
            'picture': picture,
            'role': 'Usuario'  # Puedes asignar roles según tu lógica
        }
    
    # 3. Inicializar GoogleOAuthManager
    oauth_manager = GoogleOAuthManager(
        app=app,
        authorized_domains=['@agrovetmarket.com', '@pharmadix.com'],  # Opcional
        user_callback=handle_user_login  # Opcional
    )
    
    # 4. Definir rutas de tu aplicación
    @app.route('/')
    def index():
        return '''
            <h1>Bienvenido</h1>
            <a href="/login">Iniciar sesión</a>
        '''
    
    @app.route('/login')
    def login():
        return '''
            <h1>Iniciar Sesión</h1>
            <a href="/login/google">
                <button>Iniciar sesión con Google</button>
            </a>
        '''
    
    @app.route('/dashboard')
    @GoogleOAuthManager.login_required
    def dashboard():
        username = session.get('username', 'Usuario')
        picture = session.get('picture', '')
        role = session.get('role', 'Usuario')
        
        return f'''
            <h1>Dashboard</h1>
            <img src="{picture}" width="50" style="border-radius: 50%;">
            <p>Bienvenido, {username}</p>
            <p>Rol: {role}</p>
            <a href="/logout">Cerrar sesión</a>
        '''
    
    @app.route('/logout')
    def logout():
        session.clear()
        flash('Sesión cerrada correctamente.', 'success')
        return redirect(url_for('login'))
    
    # 5. Ejecutar aplicación
    app.run(debug=True, port=5000)
