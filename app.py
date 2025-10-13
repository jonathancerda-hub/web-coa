from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify
from datetime import datetime, timedelta
import pandas as pd
import os
import json
import re
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from urllib.parse import quote_plus, unquote_plus
from werkzeug.middleware.proxy_fix import ProxyFix
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# --- IMPORTACIÓN CORREGIDA ---
# Se asegura de importar las funciones necesarias de los otros archivos.
from pdf_generator import generar_certificado_en_memoria

# Cargar variables de entorno del archivo .env
load_dotenv()

# Importar nuestro gestor de datos después de cargar las variables
from google_sheets_manager import GoogleSheetManager, get_column_order

# Inicializar la App y el Gestor de Datos
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'una_clave_secreta_muy_larga_y_aleatoria_para_desarrollo')
app.permanent_session_lifetime = timedelta(minutes=15)

# --- INICIO DE LA CORRECCIÓN PARA DESPLIEGUE ---
# Se añade ProxyFix para que Flask genere URLs con https correctamente cuando
# se ejecuta detrás de un proxy inverso como el de Render.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
# --- FIN DE LA CORRECCIÓN ---

# --- INICIO DE LA CONFIGURACIÓN DE OAUTH ---
# --- INICIO DE LA CORRECCIÓN ---
# Se inicializa OAuth sin la app y se configura después con init_app.
# Esto evita problemas de contexto y asegura que la sesión se maneje correctamente.
oauth = OAuth()
# --- FIN DE LA CORRECCIÓN ---
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    # --- INICIO DE LA CORRECCIÓN ---
    # Se eliminan los endpoints manuales y se confía únicamente en server_metadata_url.
    # Esto asegura que Authlib siempre use la configuración correcta de Google.
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)
# --- INICIO DE LA CORRECCIÓN ---
# Se llama a init_app para vincular correctamente OAuth con la aplicación Flask.
oauth.init_app(app)
# --- FIN DE LA CORRECCIÓN ---

# --- FIN DE LA CONFIGURACIÓN DE OAUTH ---

# --- INICIO DE LA VALIDACIÓN DE CREDENCIALES OAUTH ---
google_client_id = os.getenv('GOOGLE_CLIENT_ID')
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
if not all([google_client_id, google_client_secret]):
    print("\n\n*** ADVERTENCIA: Faltan las variables de entorno GOOGLE_CLIENT_ID o GOOGLE_CLIENT_SECRET. El inicio de sesión con Google no funcionará. ***\n\n")
# --- FIN DE LA VALIDACIÓN DE CREDENCIALES OAUTH ---

limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"], storage_uri="memory://")

try:
    data_manager = GoogleSheetManager()
except Exception as e:
    print(f"Error Crítico al iniciar GoogleSheetManager: {e}")
    data_manager = None

# --- Decoradores de Seguridad para Roles ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'Administrador':
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('registros'))
        return f(*args, **kwargs)
    return decorated_function

def supervisor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') not in ['Administrador', 'Supervisor']:
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('registros'))
        return f(*args, **kwargs)
    return decorated_function

# --- Función Auxiliar para Fechas ---
def format_date_for_sheet(date_str_from_form):
    if not date_str_from_form: return ""
    try:
        return datetime.strptime(date_str_from_form, '%d-%m-%Y').strftime('%d-%m-%Y')
    except ValueError:
        try:
            return datetime.strptime(date_str_from_form, '%Y-%m-%d').strftime('%d-%m-%Y')
        except ValueError:
            return date_str_from_form

@app.before_request
def before_request():
    session.modified = True

# --- Rutas de Autenticación ---
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("3 per minute", methods=["POST"], error_message="Demasiados intentos. Por favor, espera un minuto.")
def login():
    if 'username' in session:
        return redirect(url_for('registros'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = data_manager.get_all_users()
        # Se busca el usuario por nombre de usuario
        user_found = next((u for u in users if u.get('USERNAME') == username), None)

        # Se verifica el usuario y la contraseña hasheada
        if user_found and check_password_hash(user_found.get('PASSWORD', ''), password):
            session.pop('login_failures', None)
            session.permanent = True
            session['username'] = user_found['USERNAME']
            session['role'] = user_found.get('ROL', 'Operario')
            flash('Inicio de sesión exitoso!', 'success')
            data_manager.log_action(session.get('username'), "Inicio de Sesión")
            return redirect(url_for('registros'))
        else:
            failures = session.get('login_failures', 0) + 1
            session['login_failures'] = failures
            max_attempts = 3
            remaining = max_attempts - failures

            if remaining > 1:
                flash(f'Usuario o contraseña incorrectos. Quedan {remaining} intentos.', 'warning')
            elif remaining == 1:
                flash('Usuario o contraseña incorrectos. Queda 1 (último) intento.', 'danger')
            else:
                flash('Usuario o contraseña incorrectos. Has agotado tus intentos.', 'danger')
            
            return render_template('login.html')

    if 'login_failures' not in session:
        session['login_failures'] = 0
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    username_before_clear = session.get('username', 'desconocido')
    data_manager.log_action(username_before_clear, "Cierre de Sesión")
    session.clear()
    flash("Has cerrado la sesión.", "info")
    return redirect(url_for('login'))

# --- INICIO DE LAS NUEVAS RUTAS DE OAUTH ---
@app.route('/login/google')
def login_google():
    """Redirige al usuario a la página de inicio de sesión de Google."""
    # --- INICIO DE LA CORRECCIÓN PARA ENTORNO DUAL ---
    # Se detecta si la app corre en Render para forzar HTTPS.
    # De lo contrario, se usa el esquema por defecto (HTTP para local).
    if os.environ.get('RENDER'):
        redirect_uri = url_for('auth_google', _external=True, _scheme='https')
    else:
        redirect_uri = url_for('auth_google', _external=True)
    # --- FIN DE LA CORRECCIÓN ---
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def auth_google():
    """Ruta a la que Google redirige después del login."""
    try:
        token = google.authorize_access_token()
        # --- INICIO DE LA CORRECCIÓN ---
        # Se utiliza el método userinfo() que es la forma recomendada y más segura
        # para obtener la información del usuario, lo que resuelve el error 'invalid_claim'.
        user_info = google.userinfo()
        user_email = user_info.get('email')

        # --- LÓGICA DE AUTORIZACIÓN ---
        # 1. Verifica que el dominio del correo esté en la lista de dominios permitidos.
        allowed_domains = ['@agrovetmarket.com', '@pharmadix.com']
        if not any(user_email.endswith(domain) for domain in allowed_domains):
            flash('Acceso denegado. Solo se permiten cuentas corporativas autorizadas.', 'danger')
            return redirect(url_for('login'))

        # 2. Busca al usuario en tu hoja de "Usuarios" para obtener su rol
        all_users = data_manager.get_all_users()
        user_in_sheet = next((u for u in all_users if u.get('USERNAME').lower() == user_email.lower()), None)

        # --- INICIO DE LA MODIFICACIÓN: Auto-registro de usuarios ---
        # Si el usuario no está en la hoja de cálculo pero tiene un dominio válido,
        # se crea automáticamente con un rol por defecto.
        if not user_in_sheet:
            print(f"Usuario '{user_email}' no encontrado. Creando nuevo usuario...")
            default_role = 'Operario'
            # La contraseña se deja como un placeholder ya que el login será vía Google.
            new_user_data = [user_email, 'N/A_OAUTH_USER', default_role]
            success, message = data_manager.add_user(new_user_data)
            if not success:
                flash(f'Error al registrar automáticamente al usuario: {message}', 'danger')
                return redirect(url_for('login'))
            user_in_sheet = {'USERNAME': user_email, 'ROL': default_role}
            data_manager.log_action(user_email, "Auto-registro (Google)")
        # --- FIN DE LA MODIFICACIÓN ---

        # 3. Inicia la sesión en Flask
        session.permanent = True
        session['username'] = user_in_sheet.get('USERNAME') # O puedes usar user_info.get('name')
        session['role'] = user_in_sheet.get('ROL', 'Operario')
        flash('Inicio de sesión con Google exitoso!', 'success')
        data_manager.log_action(session.get('username'), "Inicio de Sesión (Google)")
        return redirect(url_for('registros'))

    except Exception as e:
        flash(f'Ocurrió un error durante la autenticación con Google: {e}', 'danger')
        return redirect(url_for('login'))
# --- FIN DE LAS NUEVAS RUTAS DE OAUTH ---

@app.route('/forgot-password')
def forgot_password():
    # Simplemente renderiza una página estática con instrucciones.
    return render_template('forgot_password.html')

# --- Rutas Principales ---
@app.route('/')
def registros():
    if 'username' not in session:
        return redirect(url_for('login'))
    if not data_manager:
        return "Error: No se pudo conectar con el gestor de datos.", 500
    
    search_term = request.args.get('search', '').lower()
    page = request.args.get('page', 1, type=int)
    per_page = 20

    all_records = data_manager.get_all_records()

    # --- INICIO DE LA MODIFICACIÓN ---
    # 1. Ordenar los registros por fecha de creación, de más reciente a más antiguo
    try:
        all_records.sort(
            key=lambda r: datetime.strptime(r.get('FECHA_DE_REGISTRO', '01-01-1900 00:00:00'), '%d-%m-%Y %H:%M:%S'),
            reverse=True
        )
    except (ValueError, TypeError):
        # Si hay un error en el formato de fecha, se mantiene el orden original.
        flash('Advertencia: No se pudo ordenar por fecha debido a formatos inconsistentes.', 'warning')

    # 2. Filtrar si hay un término de búsqueda
    if search_term:
        filtered_records = [rec for rec in all_records if any(search_term in str(val).lower() for val in rec.values())]
    else:
        filtered_records = all_records

    # 3. Aplicar paginación a los registros (ya filtrados si es el caso)
    total_records = len(filtered_records)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_records = filtered_records[start:end]
    total_pages = (total_records + per_page - 1) // per_page
    # --- FIN DE LA MODIFICACIÓN ---

    # --- INICIO DE LA NUEVA LÓGICA ---
    # Si la solicitud es AJAX (viene de nuestro script de búsqueda), devolvemos solo los datos necesarios en formato JSON.
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'table_html': render_template('_registros_table_rows.html', records=paginated_records),
            'pagination_html': render_template('_pagination.html', current_page=page, total_pages=total_pages, search_term=search_term)
        })
    # --- FIN DE LA NUEVA LÓGICA ---

    # Si es una carga de página normal, renderizamos la plantilla completa.
    return render_template('registros.html', 
                           records=paginated_records, 
                           search_term=search_term, 
                           current_page=page, 
                           total_pages=total_pages)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session: 
        return redirect(url_for('login'))

    producto_filtro = request.args.get('producto', 'Todos los Productos')
    fecha_inicio_str = request.args.get('fecha_inicio', '')
    fecha_fin_str = request.args.get('fecha_fin', '')
    
    all_records = data_manager.get_all_records()
    df = pd.DataFrame(all_records)
    
    if df.empty:
        product_list = ["Todos los Productos"] + sorted(list(data_manager.product_data.keys()))
        return render_template('dashboard.html', stats={'total': 0, 'aprobados': 0, 'rechazados': 0, 'pendientes': 0}, chart_labels=[], chart_data=[], monthly_summary=[], product_list=product_list, current_filters={}, target_year=datetime.now().year)

    df['FECHA_DE_REGISTRO_DT'] = pd.to_datetime(df['FECHA_DE_REGISTRO'], errors='coerce', dayfirst=True)
    df_filtrado_final = df.copy()
    if producto_filtro and producto_filtro != 'Todos los Productos':
        df_filtrado_final = df_filtrado_final[df_filtrado_final['PRODUCTO'] == producto_filtro]
    if fecha_inicio_str:
        fecha_inicio = pd.to_datetime(fecha_inicio_str, dayfirst=True, errors='coerce')
        if pd.notna(fecha_inicio):
            df_filtrado_final = df_filtrado_final[df_filtrado_final['FECHA_DE_REGISTRO_DT'].dt.normalize() >= fecha_inicio]
    if fecha_fin_str:
        fecha_fin = pd.to_datetime(fecha_fin_str, dayfirst=True, errors='coerce')
        if pd.notna(fecha_fin):
            df_filtrado_final = df_filtrado_final[df_filtrado_final['FECHA_DE_REGISTRO_DT'].dt.normalize() <= fecha_fin]

    stats = df_filtrado_final['CONCLUSION'].value_counts().to_dict()
    chart_labels = list(stats.keys())
    chart_data = list(stats.values())
    dashboard_stats = {
        'total': df_filtrado_final.shape[0],
        'aprobados': stats.get('APROBADO', 0),
        'rechazados': stats.get('RECHAZADO', 0),
        'pendientes': stats.get('PENDIENTE', 0)
    }
    if dashboard_stats['total'] > 0:
        tasa_aprobacion = (dashboard_stats['aprobados'] / dashboard_stats['total']) * 100
        dashboard_stats['tasa_aprobacion'] = f"{tasa_aprobacion:.1f}%"
    else:
        dashboard_stats['tasa_aprobacion'] = "N/A"
    
    # --- INICIO DE LA MODIFICACIÓN ---
    # Se determina el año objetivo para el resumen mensual.
    target_year = datetime.now().year
    if fecha_inicio_str:
        try:
            target_year = pd.to_datetime(fecha_inicio_str, dayfirst=True).year
        except (ValueError, TypeError):
            pass
    # Se usa FECHA_DE_REGISTRO_DT para el resumen anual, asegurando consistencia.
    # AHORA SE USA EL DATAFRAME YA FILTRADO (df_filtrado_final) para el resumen.
    df_para_resumen_anual = df_filtrado_final[df_filtrado_final['FECHA_DE_REGISTRO_DT'].dt.year == target_year]
    monthly_summary_raw = df_para_resumen_anual.groupby(df_para_resumen_anual['FECHA_DE_REGISTRO_DT'].dt.month)['CONCLUSION'].value_counts().unstack(fill_value=0)
    # --- FIN DE LA MODIFICACIÓN ---
    
    meses_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    monthly_summary = []
    for i, mes in enumerate(meses_es):
        month_num = i + 1
        
        # --- INICIO DE LA CORRECCIÓN ---
        # Calcular las fechas de inicio y fin para cada mes
        start_date = datetime(target_year, month_num, 1)
        if month_num == 12:
            end_date = datetime(target_year, 12, 31)
        else:
            end_date = datetime(target_year, month_num + 1, 1) - timedelta(days=1)

        month_data = {
            'mes': mes, 'aprobado': 0, 'rechazado': 0, 'pendiente': 0,
            'start_date_str': start_date.strftime('%d-%m-%Y'),
            'end_date_str': end_date.strftime('%d-%m-%Y')
        }
        # --- FIN DE LA CORRECCIÓN ---

        if month_num in monthly_summary_raw.index:
            data = monthly_summary_raw.loc[month_num]
            month_data.update({'aprobado': data.get('APROBADO', 0), 'rechazado': data.get('RECHAZADO', 0), 'pendiente': data.get('PENDIENTE', 0)})
        monthly_summary.append(month_data)
    
    # --- INICIO DE LA NUEVA MODIFICACIÓN: Datos para el gráfico de líneas ---
    line_chart_labels = [m['mes'] for m in monthly_summary] # Esto ya es texto, está bien
    line_chart_aprobados = [int(m['aprobado']) for m in monthly_summary] # Convertimos a int estándar
    line_chart_rechazados = [int(m['rechazado']) for m in monthly_summary] # Convertimos a int estándar
    # --- FIN DE LA NUEVA MODIFICACIÓN ---

    product_list = ["Todos los Productos"] + sorted(list(data_manager.product_data.keys()))

    return render_template(
        'dashboard.html',
        stats=dashboard_stats,
        chart_labels=chart_labels,
        chart_data=chart_data,
        # --- INICIO DE LA NUEVA MODIFICACIÓN ---
        line_chart_labels=line_chart_labels,
        line_chart_aprobados=line_chart_aprobados,
        line_chart_rechazados=line_chart_rechazados,
        # --- FIN DE LA NUEVA MODIFICACIÓN ---
        monthly_summary=monthly_summary,
        product_list=product_list,
        target_year=target_year,
        current_filters={ 'producto': producto_filtro, 'fecha_inicio': fecha_inicio_str, 'fecha_fin': fecha_fin_str }
    )

# --- Rutas de Gestión y Log ---
@app.route('/gestion-usuarios')
@admin_required
def gestion_usuarios():
    try:
        users = data_manager.get_all_users()
        return render_template('gestion_usuarios.html', users=users)
    except Exception as e:
        flash(f'Error al cargar los usuarios: {e}', 'danger')
        return redirect(url_for('registros'))

@app.route('/nuevo-usuario', methods=['GET', 'POST'])
@admin_required
def nuevo_usuario():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        if not all([username, role]):
            flash('El nombre de usuario y el rol son obligatorios.', 'warning')
            return redirect(url_for('nuevo_usuario'))

        # Validación de formato de correo electrónico en el servidor
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, username):
            flash('El nombre de usuario debe ser una dirección de correo electrónico válida.', 'danger')
            return redirect(url_for('nuevo_usuario'))
        
        # Hashear la contraseña solo si se proporciona una.
        password_to_save = generate_password_hash(password) if password else "N/A"
        user_data = [username, password_to_save, role]
        success, message = data_manager.add_user(user_data)
        if success:
            data_manager.log_action(session.get('username'), "Creó Usuario", f"Nuevo usuario: {username}")
            flash(message, 'success')
            return redirect(url_for('gestion_usuarios'))
        else:
            flash(message, 'danger')
            return redirect(url_for('nuevo_usuario'))
    return render_template('formulario_usuario.html', is_edit_mode=False)

@app.route('/editar-usuario/<string:username>', methods=['GET', 'POST'])
@admin_required
def editar_usuario(username):
    user = data_manager.find_user(username)
    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('gestion_usuarios'))
    if request.method == 'POST':
        new_password = request.form.get('password')
        new_role = request.form.get('role')
        data_to_update = {'ROL': new_role}
        if new_password:
            data_to_update['PASSWORD'] = generate_password_hash(new_password)
        success, message = data_manager.update_user(username, data_to_update)
        if success:
            data_manager.log_action(session.get('username'), "Editó Usuario", f"Usuario editado: {username}")
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('gestion_usuarios'))
    return render_template('formulario_usuario.html', is_edit_mode=True, user_data=user)

@app.route('/eliminar-usuario', methods=['POST'])
@admin_required
def eliminar_usuario():
    username = request.form.get('username')
    if username == session.get('username'):
        flash('No puedes eliminar tu propia cuenta mientras estás en sesión.', 'danger')
        return redirect(url_for('gestion_usuarios'))
    success, message = data_manager.delete_user(username)
    if success:
        data_manager.log_action(session.get('username'), "Eliminó Usuario", f"Usuario eliminado: {username}")
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('gestion_usuarios'))

@app.route('/gestion-productos')
@supervisor_required
def gestion_productos():
    search_term = request.args.get('search', '').lower()
    page = request.args.get('page', 1, type=int)
    per_page = 20

    try:
        productos = data_manager.get_all_products_flat()

        if search_term:
            filtered_productos = [
                p for p in productos if
                search_term in p.get('PRODUCTO', '').lower() or
                search_term in p.get('FORMA_FARMACEUTICA', '').lower() or
                search_term in p.get('PRESENTACION', '').lower()
            ]
        else:
            filtered_productos = productos

        total_records = len(filtered_productos)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_records = filtered_productos[start:end]
        total_pages = (total_records + per_page - 1) // per_page

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'table_html': render_template('_productos_table_rows.html', productos=paginated_records),
                'pagination_html': render_template('_pagination.html', current_page=page, total_pages=total_pages, search_term=search_term, endpoint='gestion_productos')
            })

        return render_template('gestion_productos.html', 
                               productos=paginated_records, search_term=search_term, 
                               current_page=page, total_pages=total_pages, endpoint='gestion_productos')
    except Exception as e:
        flash(f"Error al cargar la gestión de productos: {e}", "danger")
        return redirect(url_for('registros'))

@app.route('/nuevo-producto', methods=['GET', 'POST'])
@supervisor_required
def nuevo_producto():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').upper()
        forma = request.form.get('forma', '').upper()
        presentacion = request.form.get('presentacion', '').upper()
        if not all([nombre, forma, presentacion]):
            flash('Todos los campos son obligatorios.', 'warning')
            return redirect(url_for('nuevo_producto'))
        product_data = [nombre, forma, presentacion]
        success, message = data_manager.add_product_presentation(product_data)
        if success:
            data_manager.product_data = data_manager._load_product_data()
            data_manager.log_action(session.get('username'), "Añadió Presentación", f"Producto: {nombre}, Presentación: {presentacion}")
            flash(message, 'success')
            return redirect(url_for('gestion_productos'))
        else:
            flash(message, 'danger')
            return redirect(url_for('nuevo_producto'))
    return render_template('formulario_producto.html')

@app.route('/eliminar-presentacion/<path:product_name>/<path:presentation>', methods=['POST'])
@supervisor_required
def eliminar_presentacion(product_name, presentation):
    try:
        p_name = unquote_plus(product_name)
        p_presentation = unquote_plus(presentation)
        success, message = data_manager.delete_product_presentation(p_name, p_presentation)
        if success:
            data_manager.product_data = data_manager._load_product_data()
            data_manager.log_action(session.get('username'), "Eliminó Presentación", f"Producto: {p_name}, Presentación: {p_presentation}")
            flash(message, 'success')
        else:
            flash(message, 'danger')
    except Exception as e:
        flash(f"Error en el servidor al intentar eliminar: {e}", "danger")
    return redirect(url_for('gestion_productos'))

@app.route('/log-actividad')
@admin_required
def log_actividad():
    logs = data_manager.get_activity_log()
    return render_template('log_actividad.html', logs=logs)

# --- Rutas de Certificados (Registros) y PDF ---
@app.route('/generate-pdf/<string:codigo>/<string:pdf_type>')
def generate_pdf(codigo, pdf_type):
    if 'username' not in session: 
        return redirect(url_for('login'))
    all_records = data_manager.get_all_records()
    record_to_print = next((r for r in all_records if r.get('CODIGO') == codigo), None)
    if record_to_print:
        pdf_bytes = generar_certificado_en_memoria(record_to_print, pdf_class_name=pdf_type)
        if pdf_bytes:
            data_manager.log_action(session.get('username'), f"Generó PDF ({pdf_type})", f"Código: {codigo}")
            response = make_response(pdf_bytes)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename=Certificado-{codigo}.pdf'
            return response
        else:
            flash("Ocurrió un error al generar el archivo PDF.", "danger")
    else:
        flash(f"No se encontró el registro con código {codigo}", "danger")
    return redirect(url_for('registros'))

@app.route('/nuevo-registro', methods=['GET', 'POST'])
def nuevo_registro():
    if 'username' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        campos_principales = ['PRODUCTO', 'LOTE', 'FECHA_PRODUCCION', 'FECHA_VENCIMIENTO', 'FECHA_ANALISIS', 'FECHA_EMISION']
        if not all(request.form.get(campo) for campo in campos_principales):
            flash('Producto, Lote y todas las fechas son campos obligatorios.', 'warning')
            return redirect(url_for('nuevo_registro'))
        try:
            datos_formulario = {key: request.form.get(key, '') for key in get_column_order()}
            for key in ['FECHA_PRODUCCION', 'FECHA_VENCIMIENTO', 'FECHA_ANALISIS', 'FECHA_EMISION']:
                datos_formulario[key] = format_date_for_sheet(request.form.get(key))
            datos_formulario['CODIGO'] = data_manager.get_next_codigo()
            datos_formulario['FECHA_DE_REGISTRO'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            datos_formulario['CREADO_POR'] = session.get('username', 'desconocido')
            datos_formulario['CANTIDAD'] = f"{request.form.get('CANTIDAD', '0')} {request.form.get('UNIDAD_CANTIDAD', 'KG')}"
            lista_ordenada = [datos_formulario.get(col, '') for col in get_column_order()]

            # --- INICIO DE LA CORRECCIÓN ---
            # Añadir un apóstrofo al inicio del LOTE para forzar a Google Sheets a tratarlo como texto.
            lote_index = get_column_order().index('LOTE')
            lista_ordenada[lote_index] = f"'{datos_formulario.get('LOTE', '')}"
            # --- FIN DE LA CORRECCIÓN ---

            data_manager.add_record(lista_ordenada)
            flash('¡Certificado registrado con éxito!', 'success')
            data_manager.log_action(session.get('username'), "Creó Certificado", f"Código: {datos_formulario['CODIGO']}")
            return redirect(url_for('registros'))
        except Exception as e:
            flash(f'Ocurrió un error al guardar el registro: {e}', 'danger')
            return redirect(url_for('nuevo_registro'))
    else: # GET
        return render_template(
            'formulario_registro.html', is_edit_mode=False, record_data={},
            product_list=sorted(list(data_manager.product_data.keys())),
            product_data_json=json.dumps(data_manager.product_data),
            specs_data_json=json.dumps(data_manager.specs_data),
            next_code=data_manager.get_next_codigo()
        )

@app.route('/editar/<string:codigo>', methods=['GET', 'POST'])
def editar_registro(codigo):
    if 'username' not in session: return redirect(url_for('login'))
    
    all_records = data_manager.get_all_records()
    record_to_edit, original_index = None, -1
    for i, record in enumerate(all_records):
        if str(record.get('CODIGO')) == str(codigo):
            record_to_edit, original_index = record, i
            break

    if not record_to_edit:
        flash(f'No se encontró el registro {codigo}.', 'danger')
        return redirect(url_for('registros'))

    if request.method == 'POST':
        try:
            # --- INICIO DE LA MODIFICACIÓN ---
            # 1. Copiamos el registro original para preservar los datos que no se pueden editar.
            datos_actualizados = record_to_edit.copy()

            # 2. Actualizamos el diccionario solo con los datos que vienen del formulario.
            # Los campos deshabilitados en el HTML no se enviarán, por lo que los valores originales se mantienen.
            for key in request.form:
                datos_actualizados[key] = request.form.get(key)

            # 3. Re-formateamos las fechas y la cantidad, como antes.
            for key in ['FECHA_PRODUCCION', 'FECHA_VENCIMIENTO', 'FECHA_ANALISIS', 'FECHA_EMISION']:
                datos_actualizados[key] = format_date_for_sheet(request.form.get(key))
            
            # --- INICIO DE LA CORRECCIÓN ---
            # Solo reconstruir la cantidad si los campos no están deshabilitados (es decir, si vienen en el form)
            if 'CANTIDAD' in request.form and 'UNIDAD_CANTIDAD' in request.form:
                datos_actualizados['CANTIDAD'] = f"{request.form.get('CANTIDAD')} {request.form.get('UNIDAD_CANTIDAD')}"
            # --- FIN DE LA CORRECCIÓN ---
            
            # 4. Creamos la lista final en el orden correcto para la hoja de cálculo.
            lista_ordenada = [datos_actualizados.get(col, '') for col in get_column_order()]
            # --- FIN DE LA MODIFICACIÓN ---
            data_manager.update_record(original_index + 2, lista_ordenada)
            flash('¡Registro actualizado con éxito!', 'success')
            data_manager.log_action(session.get('username'), "Editó Certificado", f"Código: {codigo}")
            return redirect(url_for('registros'))
        except Exception as e:
            flash(f'Ocurrió un error al actualizar: {e}', 'danger')
            return redirect(url_for('editar_registro', codigo=codigo))
    else: # GET
        return render_template(
            'formulario_registro.html', is_edit_mode=True, record_data=record_to_edit,
            product_list=sorted(list(data_manager.product_data.keys())),
            product_data_json=json.dumps(data_manager.product_data),
            specs_data_json=json.dumps(data_manager.specs_data)
        )

@app.cli.command("migrate-passwords")
def migrate_passwords_command():
    """Hashea todas las contraseñas en texto plano en la hoja de Usuarios."""
    print("Iniciando migración de contraseñas...")
    if not data_manager:
        print("Error: No se pudo inicializar el gestor de datos.")
        return

    try:
        users = data_manager.get_all_users()
        migrated_count = 0
        for user in users:
            username = user.get('USERNAME')
            password = str(user.get('PASSWORD', ''))
            
            # Si la contraseña no parece un hash de Werkzeug, la migramos.
            if not password.startswith('pbkdf2:sha256:'):
                print(f"Migrando contraseña para el usuario: {username}...")
                hashed_password = generate_password_hash(password)
                data_manager.update_user(username, {'PASSWORD': hashed_password})
                migrated_count += 1
        print(f"¡Migración completada! Se actualizaron {migrated_count} contraseñas.")
    except Exception as e:
        print(f"Ocurrió un error durante la migración: {e}")

if __name__ == '__main__':
    app.run(debug=True)