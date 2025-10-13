import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import sys
import json
from supabase import create_client, Client

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_column_order():
    cols = ['CODIGO','PRODUCTO','PRESENTACION','LOTE',
            'VERSION_ESPECIFICACION',
            'FORMA_FARMACEUTICA','CANTIDAD',
            'FECHA_PRODUCCION','FECHA_VENCIMIENTO','FECHA_ANALISIS','FECHA_EMISION',
            'LABORATORIO','REFERENCIA','FECHA_DE_REGISTRO','CONCLUSION',
            'OBSERVACIONES','CREADO_POR']
    for i in range(1, 21): 
        cols.extend([f'ENSAYO{i}', f'ESPECIFICACION{i}', f'RESULTADO{i}'])
    return cols

class GoogleSheetManager:
    def __init__(self):
        # --- CONEXIÓN A GOOGLE SHEETS ---
        try:
            scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
            google_creds_json = os.getenv('GOOGLE_CREDS_JSON')
            creds = None

            if google_creds_json:
                try:
                    creds_info = json.loads(google_creds_json)
                    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
                except json.JSONDecodeError:
                    print("Advertencia: La variable de entorno GOOGLE_CREDS_JSON está mal formateada. Se intentará usar 'credentials.json'.")

            if not creds:
                creds_path = os.path.join(os.path.abspath("."), 'credentials.json')
                creds = Credentials.from_service_account_file(creds_path, scopes=scopes)

            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open('CertificadosDeAnalisis')
            self.worksheet = self.spreadsheet.sheet1
            print("Conexión con Google Sheets establecida.")
        except Exception as e:
            print(f"ERROR CRÍTICO al inicializar GoogleSheetManager: {e}")
            # --- INICIO DE LA CORRECCIÓN ---
            # No relanzar la excepción para permitir que la app inicie incluso si Sheets falla.
            self.client = None
            self.spreadsheet = None
            # --- FIN DE LA CORRECCIÓN ---

        # --- CONEXIÓN A SUPABASE (SOLO PARA LOGS) ---
        try:
            url: str = os.environ.get("SUPABASE_URL")
            key: str = os.environ.get("SUPABASE_KEY")

            if url and key:
                self.supabase: Client = create_client(url, key)
                print("Conexión con Supabase para logging establecida.")
            else:
                self.supabase = None
                print("Advertencia: No se encontraron credenciales de Supabase. El logging estará desactivado.")
        except Exception as e:
            print(f"ERROR CRÍTICO al inicializar cliente de Supabase: {e}")
            self.supabase = None

        # --- Carga de datos inicial desde Google Sheets ---
        # --- INICIO DE LA CORRECCIÓN ---
        # Solo cargar datos si la conexión con Sheets fue exitosa.
        if self.spreadsheet:
            self.product_data = self._load_product_data()
            self.specs_data = self._load_specs_data()
        else:
            self.product_data, self.specs_data = {}, {}
    
    # --- MÉTODOS QUE USAN SUPABASE ---
    def log_action(self, username, action, details=""):
        if not self.supabase:
            return
        try:
            log_entry = {'usuario': username, 'accion': action, 'detalles': details}
            self.supabase.table('log_actividad').insert(log_entry).execute()
        except Exception as e:
            print(f"Error al registrar en el log de Supabase: {e}")

    def get_activity_log(self):
        if not self.supabase:
            return []
        try:
            response = self.supabase.table('log_actividad').select('*').order('timestamp', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error al obtener el log de actividad de Supabase: {e}")
            return []

    # --- MÉTODOS QUE USAN GOOGLE SHEETS ---
    def _load_product_data(self):
        try:
            print("Cargando datos de productos...")
            product_sheet = self.spreadsheet.worksheet("Productos")
            records = product_sheet.get_all_records()
            processed_data = {}
            for record in records:
                producto = record.get('PRODUCTO')
                if not producto: continue
                if producto not in processed_data:
                    processed_data[producto] = {
                        "presentaciones": [],
                        "forma": record.get('FORMA_FARMACEUTICA', '')
                    }
                presentacion = record.get('PRESENTACION')
                if presentacion:
                    processed_data[producto]["presentaciones"].append(presentacion)
            print("Datos de productos cargados.")
            return processed_data
        except Exception as e:
            print(f"Error Crítico: No se pudieron cargar los datos de los productos: {e}")
            raise
    
    def _load_specs_data(self):
        specs_data = {}
        try:
            print("Cargando datos de especificaciones...")
            specs_sheet = self.spreadsheet.worksheet("Maestro Especificaciones")
            records = specs_sheet.get_all_records()
            for record in records:
                producto = record.get('PRODUCTO')
                version = str(record.get('VER'))
                descripcion = record.get('DESCRIPCIÓN')
                especificacion = record.get('ESPECIFICACIÓN')
                if not all([producto, version, descripcion, especificacion]): continue
                if producto not in specs_data: specs_data[producto] = {}
                if version not in specs_data[producto]: specs_data[producto][version] = []
                specs_data[producto][version].append({"descripcion": descripcion, "especificacion": especificacion})
            print("Datos de especificaciones cargados correctamente.")
            return specs_data
        except Exception as e:
            print(f"Error al cargar especificaciones: {e}")
            raise

    def get_all_products_flat(self):
        # --- INICIO DE LA MODIFICACIÓN: Optimización de carga ---
        # En lugar de hacer una nueva llamada a la API, transformamos los datos cacheados.
        # Esto hace que la carga de la página sea instantánea.
        flat_list = []
        for product_name, data in self.product_data.items():
            for presentation in data.get('presentaciones', []):
                flat_list.append({
                    'PRODUCTO': product_name,
                    'PRESENTACION': presentation,
                    'FORMA_FARMACEUTICA': data.get('forma', '')
                })
        return flat_list

    def add_product_presentation(self, product_data):
        try:
            product_sheet = self.spreadsheet.worksheet("Productos")
            records = product_sheet.get_all_records()
            for rec in records:
                if rec.get('PRODUCTO') == product_data[0] and rec.get('PRESENTACION') == product_data[2]:
                    return False, "Esta presentación para este producto ya existe."
            product_sheet.append_row(product_data, value_input_option='USER_ENTERED')
            return True, "Presentación de producto añadida con éxito."
        except Exception as e:
            return False, f"Error al añadir producto: {e}"

    def delete_product_presentation(self, product_name, presentation):
        try:
            product_sheet = self.spreadsheet.worksheet("Productos")
            records = product_sheet.get_all_records()
            row_to_delete = -1
            for i, rec in enumerate(records):
                if rec.get('PRODUCTO') == product_name and rec.get('PRESENTACION') == presentation:
                    row_to_delete = i + 2
                    break
            if row_to_delete != -1:
                product_sheet.delete_rows(row_to_delete)
                return True, "Presentación eliminada con éxito."
            else:
                return False, "No se encontró la presentación a eliminar."
        except Exception as e:
            return False, f"Error al eliminar la presentación: {e}"

    def get_all_records(self):
        # --- INICIO DE LA CORRECCIÓN ---
        # Se usa get_all_values con value_render_option='FORMATTED_VALUE' para obtener
        # los datos tal como se ven en la hoja (texto), evitando la conversión automática
        # de '0123' a 123. Luego, se construyen los diccionarios manualmente.
        all_values = self.worksheet.get_all_values(value_render_option='FORMATTED_VALUE')
        if not all_values or len(all_values) < 2:
            return []
        headers = all_values[0]
        records = [dict(zip(headers, row)) for row in all_values[1:]]
        return records
    
    def get_next_codigo(self):
        current_year = str(datetime.now().year)
        try:
            all_values = self.worksheet.col_values(1)
            if len(all_values) <= 1: return f"0001-{current_year}"
            last_code = ""
            for value in reversed(all_values):
                if value and isinstance(value, str) and '-' in value:
                    last_code = value
                    break
            if not last_code: return f"0001-{current_year}"
            parts = last_code.split('-')
            if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit(): return f"0001-{current_year}"
            last_num_str, last_year = parts[0], parts[1]
            if last_year != current_year: return f"0001-{current_year}"
            else: return f"{int(last_num_str) + 1:04d}-{current_year}"
        except Exception as e:
            print(f"Error al obtener el último código: {e}.")
            return f"0001-{current_year}"
    
    def add_record(self, data):
        self.worksheet.append_row(data, value_input_option='USER_ENTERED')
    
    def update_record(self, row_index, data):
        self.worksheet.update(f'A{row_index}', [data], value_input_option='USER_ENTERED')

    def get_all_users(self):
        users_sheet = self.spreadsheet.worksheet("Usuarios")
        return users_sheet.get_all_records()

    def find_user(self, username):
        users_sheet = self.spreadsheet.worksheet("Usuarios")
        # --- INICIO DE LA CORRECCIÓN ---
        # Se utiliza find() que es más directo y eficiente para encontrar la celda.
        # Se busca en la columna 1 (USERNAME) según la estructura de la hoja.
        cell = users_sheet.find(username, in_column=1)
        if cell:
            return dict(zip(users_sheet.row_values(1), users_sheet.row_values(cell.row)))
        # --- FIN DE LA CORRECCIÓN ---
        return None

    def add_user(self, user_data):
        username = user_data[0]
        if self.find_user(username):
            return False, "El nombre de usuario ya existe."
        
        try:
            users_sheet = self.spreadsheet.worksheet("Usuarios")
            # Se añade directamente el registro de 3 columnas [USERNAME, PASSWORD, ROL]
            users_sheet.append_row(user_data, value_input_option='USER_ENTERED')
            return True, "Usuario añadido con éxito."
        except Exception as e:
            return False, f"Error al añadir usuario: {e}"
            
    def update_user(self, username, new_data):
        try:
            users_sheet = self.spreadsheet.worksheet("Usuarios")
            cell = users_sheet.find(username, in_column=1)
            if not cell: return False, "Usuario no encontrado."

            if 'ROL' in new_data:
                users_sheet.update_cell(cell.row, 3, new_data['ROL']) # ROL es la columna 3

            if 'PASSWORD' in new_data:
                users_sheet.update_cell(cell.row, 2, new_data['PASSWORD']) # PASSWORD es la columna 2

            return True, "Usuario actualizado con éxito."
        except Exception as e:
            return False, f"Error al actualizar usuario: {e}"

    def delete_user(self, username):
        try:
            users_sheet = self.spreadsheet.worksheet("Usuarios")
            cell_to_delete = users_sheet.find(username, in_column=1)
            if not cell_to_delete: return False, "Usuario no encontrado para eliminar."
            users_sheet.delete_rows(cell_to_delete.row)
            return True, "Usuario eliminado con éxito."
        except Exception as e:
            return False, f"Error al eliminar usuario: {e}"