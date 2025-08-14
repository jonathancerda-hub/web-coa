from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from datetime import datetime, timedelta
import pandas as pd
import os
import json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from urllib.parse import quote_plus, unquote_plus
from dotenv import load_dotenv

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
        user_found = next((u for u in users if u.get('USERNAME') == username and str(u.get('PASSWORD')) == password), None)

        if user_found:
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

# --- Rutas Principales ---
@app.route('/')
def registros():
    if 'username' not in session:
        return redirect(url_for('login'))
    if not data_manager:
        return "Error: No se pudo conectar con el gestor de datos.", 500
    
    search_term = request.args.get('search', '').lower()
    all_records = data_manager.get_all_records()

    if search_term:
        filtered_records = [rec for rec in all_records if any(search_term in str(val).lower() for val in rec.values())]
    else:
        filtered_records = all_records

    return render_template('registros.html', records=filtered_records, search_term=search_term)

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
    df['FECHA_EMISION_DT'] = pd.to_datetime(df['FECHA_EMISION'], errors='coerce', dayfirst=True)
    target_year = datetime.now().year
    if fecha_inicio_str:
        try:
            target_year = pd.to_datetime(fecha_inicio_str, dayfirst=True).year
        except (ValueError, TypeError):
            pass
    
    df_para_resumen_anual = df[df['FECHA_EMISION_DT'].dt.year == target_year]
    monthly_summary_raw = df_para_resumen_anual.groupby(df_para_resumen_anual['FECHA_EMISION_DT'].dt.month)['CONCLUSION'].value_counts().unstack(fill_value=0)
    
    meses_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    monthly_summary = []
    for i, mes in enumerate(meses_es):
        month_num = i + 1
        if month_num in monthly_summary_raw.index:
            data = monthly_summary_raw.loc[month_num]
            monthly_summary.append({'mes': mes, 'aprobado': data.get('APROBADO', 0), 'rechazado': data.get('RECHAZADO', 0), 'pendiente': data.get('PENDIENTE', 0)})
        else:
            monthly_summary.append({'mes': mes, 'aprobado': 0, 'rechazado': 0, 'pendiente': 0})
    
    product_list = ["Todos los Productos"] + sorted(list(data_manager.product_data.keys()))

    return render_template(
        'dashboard.html',
        stats=dashboard_stats,
        chart_labels=chart_labels,
        chart_data=chart_data,
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
        if not all([username, password, role]):
            flash('Todos los campos son obligatorios.', 'warning')
            return redirect(url_for('nuevo_usuario'))
        user_data = [username, password, role]
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
            data_to_update['PASSWORD'] = new_password
        success, message = data_manager.update_user(username, data_to_update)
        if success:
            data_manager.log_action(session.get('username'), "Editó Usuario", f"Usuario editado: {username}")
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('gestion_usuarios'))
    return render_template('formulario_usuario.html', is_edit_mode=True, user_data=user)

@app.route('/eliminar-usuario/<string:username>', methods=['POST'])
@admin_required
def eliminar_usuario(username):
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
    try:
        productos = data_manager.get_all_products_flat()
        return render_template('gestion_productos.html', productos=productos)
    except Exception as e:
        flash(f"Error al cargar la gestión de productos: {e}", "danger")
        return redirect(url_for('registros'))

@app.route('/nuevo-producto', methods=['GET', 'POST'])
@supervisor_required
def nuevo_producto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        forma = request.form.get('forma')
        presentacion = request.form.get('presentacion')
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
            datos_formulario = {key: request.form.get(key, '') for key in get_column_order()}
            for key in ['FECHA_PRODUCCION', 'FECHA_VENCIMIENTO', 'FECHA_ANALISIS', 'FECHA_EMISION']:
                datos_formulario[key] = format_date_for_sheet(request.form.get(key))
            
            datos_formulario['CODIGO'] = record_to_edit.get('CODIGO')
            datos_formulario['FECHA_DE_REGISTRO'] = record_to_edit.get('FECHA_DE_REGISTRO')
            datos_formulario['CREADO_POR'] = record_to_edit.get('CREADO_POR')
            datos_formulario['CANTIDAD'] = f"{request.form.get('CANTIDAD', '0')} {request.form.get('UNIDAD_CANTIDAD', 'KG')}"
            
            lista_ordenada = [datos_formulario.get(col, '') for col in get_column_order()]
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

if __name__ == '__main__':
    app.run(debug=True)