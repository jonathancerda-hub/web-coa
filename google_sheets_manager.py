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
            if google_creds_json:
                creds_info = json.loads(google_creds_json)
                creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
            else:
                creds_path = resource_path('Json/credentials.json')
                creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open('CertificadosDeAnalisis')
            self.worksheet = self.spreadsheet.sheet1
            print("Conexión con Google Sheets establecida.")
        except Exception as e:
            print(f"ERROR CRÍTICO al inicializar GoogleSheetManager: {e}")
            raise e

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
        self.product_data = self._load_product_data()
        self.specs_data = self._load_specs_data()
    
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
        product_sheet = self.spreadsheet.worksheet("Productos")
        return product_sheet.get_all_records()

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
        return self.worksheet.get_all_records()
    
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
        users_records = users_sheet.get_all_records()
        for user in users_records:
            if user.get('USERNAME') == username:
                return user
        return None

    def add_user(self, user_data):
        if self.find_user(user_data[0]):
            return False, "El nombre de usuario ya existe."
        try:
            users_sheet = self.spreadsheet.worksheet("Usuarios")
            users_sheet.append_row(user_data, value_input_option='USER_ENTERED')
            return True, "Usuario añadido con éxito."
        except Exception as e:
            return False, f"Error al añadir usuario: {e}"
            
    def update_user(self, username, new_data):
        try:
            users_sheet = self.spreadsheet.worksheet("Usuarios")
            cell = users_sheet.find(username)
            if not cell: return False, "Usuario no encontrado."
            users_sheet.update_cell(cell.row, 3, new_data['ROL'])
            if 'PASSWORD' in new_data and new_data['PASSWORD']:
                users_sheet.update_cell(cell.row, 2, new_data['PASSWORD'])
            return True, "Usuario actualizado con éxito."
        except Exception as e:
            return False, f"Error al actualizar usuario: {e}"

    def delete_user(self, username):
        try:
            users_sheet = self.spreadsheet.worksheet("Usuarios")
            cell = users_sheet.find(username)
            if not cell: return False, "Usuario no encontrado para eliminar."
            users_sheet.delete_rows(cell.row)
            return True, "Usuario eliminado con éxito."
        except Exception as e:
            return False, f"Error al eliminar usuario: {e}"