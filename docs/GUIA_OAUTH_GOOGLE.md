# Guía de Implementación: Autenticación OAuth con Google en Flask

## 📋 Requisitos Previos

### 1. Dependencias de Python

Instala las siguientes librerías:

```bash
pip install Flask Authlib python-dotenv
```

### 2. Configuración de Google Cloud Console

#### Paso 1: Crear Proyecto en Google Cloud
1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Crea un nuevo proyecto o selecciona uno existente

#### Paso 2: Habilitar Google+ API
1. En el menú lateral, ve a **"APIs y servicios"** → **"Biblioteca"**
2. Busca **"Google+ API"** (o "Google People API")
3. Haz clic en **"Habilitar"**

#### Paso 3: Crear Credenciales OAuth 2.0
1. Ve a **"APIs y servicios"** → **"Credenciales"**
2. Haz clic en **"Crear credenciales"** → **"ID de cliente de OAuth"**
3. Tipo de aplicación: **"Aplicación web"**
4. Nombre: `Mi Aplicación Flask`
5. **URIs de redireccionamiento autorizados:**
   - Para desarrollo local: `http://127.0.0.1:5000/login/google/callback`
   - Para producción: `https://tu-dominio.com/login/google/callback`
6. Haz clic en **"Crear"**
7. **Guarda** el `Client ID` y `Client Secret`

---

## 🚀 Implementación Paso a Paso

### Paso 1: Configurar Variables de Entorno

Crea un archivo `.env` en la raíz de tu proyecto:

```env
# Clave secreta de Flask (genera una aleatoria)
SECRET_KEY=tu_clave_secreta_muy_larga_y_aleatoria

# Credenciales de Google OAuth
GOOGLE_CLIENT_ID=tu_client_id_aqui.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu_client_secret_aqui
```

**⚠️ IMPORTANTE:** Nunca subas el archivo `.env` a Git. Agrégalo a `.gitignore`.

---

### Paso 2: Usar el Módulo en tu Aplicación

```python
from flask import Flask, session, redirect, url_for, flash
from google_oauth_module import GoogleOAuthManager
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Función callback para manejar usuarios
def handle_user_login(email, name, picture):
    """
    Esta función se ejecuta cuando un usuario se autentica con Google.
    Aquí debes crear o actualizar el usuario en tu base de datos.
    """
    # Ejemplo con SQLAlchemy:
    # user = User.query.filter_by(email=email).first()
    # if not user:
    #     user = User(email=email, name=name, picture=picture, role='Usuario')
    #     db.session.add(user)
    #     db.session.commit()
    
    # Retornar datos del usuario
    return {
        'email': email,
        'name': name,
        'picture': picture,
        'role': 'Usuario'  # Asigna roles según tu lógica
    }

# Inicializar OAuth Manager
oauth_manager = GoogleOAuthManager(
    app=app,
    authorized_domains=['@tuempresa.com'],  # Opcional: restringir dominios
    user_callback=handle_user_login
)

# Rutas de tu aplicación
@app.route('/')
def index():
    return '<a href="/login">Iniciar sesión</a>'

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
    return f'<h1>Bienvenido, {username}</h1>'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

## 🎨 Ejemplo de Botón de Google con Estilo

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        .google-btn {
            display: inline-flex;
            align-items: center;
            background: white;
            border: 1px solid #ddd;
            padding: 10px 20px;
            border-radius: 4px;
            font-family: 'Roboto', sans-serif;
            font-size: 14px;
            cursor: pointer;
            transition: box-shadow 0.3s;
        }
        .google-btn:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        .google-btn img {
            width: 20px;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <a href="/login/google" style="text-decoration: none;">
        <button class="google-btn">
            <img src="https://www.google.com/favicon.ico" alt="Google">
            Iniciar sesión con Google
        </button>
    </a>
</body>
</html>
```

---

## 🔒 Seguridad y Mejores Prácticas

### 1. Proteger Rutas
Usa el decorador `@GoogleOAuthManager.login_required`:

```python
@app.route('/admin')
@GoogleOAuthManager.login_required
def admin_panel():
    return "Panel de administración"
```

### 2. Validar Dominios Corporativos
Restringe el acceso solo a emails de tu empresa:

```python
oauth_manager = GoogleOAuthManager(
    app=app,
    authorized_domains=['@miempresa.com', '@subsidiaria.com']
)
```

### 3. Manejo de Sesiones
Configura el tiempo de expiración de sesiones:

```python
from datetime import timedelta

app.permanent_session_lifetime = timedelta(minutes=30)
```

### 4. HTTPS en Producción
El módulo ya incluye `ProxyFix` para manejar HTTPS correctamente cuando está detrás de un proxy (como Render, Heroku, etc.).

---

## 🐛 Solución de Problemas Comunes

### Error: `redirect_uri_mismatch`
**Causa:** La URI de redirección no coincide con la configurada en Google Cloud Console.

**Solución:**
1. Ve a Google Cloud Console → Credenciales
2. Edita tu ID de cliente OAuth
3. Agrega exactamente la URI que aparece en el error
4. Ejemplo: `http://127.0.0.1:5000/login/google/callback`

### Error: `invalid_client`
**Causa:** `GOOGLE_CLIENT_ID` o `GOOGLE_CLIENT_SECRET` incorrectos.

**Solución:**
1. Verifica que las credenciales en `.env` sean correctas
2. Asegúrate de que no haya espacios extra
3. Reinicia la aplicación después de cambiar `.env`

### Error: `No se pudo obtener la información del usuario`
**Causa:** Google+ API no está habilitada.

**Solución:**
1. Ve a Google Cloud Console → APIs y servicios → Biblioteca
2. Busca "Google+ API" y habilítala

---

## 📦 Despliegue en Producción (Render/Heroku)

### Variables de Entorno en Render
1. Ve a tu servicio en Render
2. Environment → Add Environment Variable
3. Agrega:
   - `SECRET_KEY`: Clave secreta de producción
   - `GOOGLE_CLIENT_ID`: Tu Client ID
   - `GOOGLE_CLIENT_SECRET`: Tu Client Secret

### Actualizar URIs de Redirección
En Google Cloud Console, agrega la URI de producción:
```
https://tu-app.onrender.com/login/google/callback
```

---

## 📚 Recursos Adicionales

- [Documentación de Authlib](https://docs.authlib.org/)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Flask Sessions](https://flask.palletsprojects.com/en/2.3.x/quickstart/#sessions)

---

**¡Listo!** Ahora tienes un módulo completo y reutilizable de autenticación OAuth con Google para tus proyectos Flask.
