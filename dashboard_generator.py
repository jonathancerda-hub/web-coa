import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import os
import sys
import json

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_column_order():
    """Función para mantener un único punto de verdad para el orden de columnas."""
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
            
            self.spreadsheet_main = self.client.open('CertificadosDeAnalisis')
            self.worksheet = self.spreadsheet_main.sheet1

            self.spreadsheet_specs = self.client.open('Maestro Especificaciones')

            self.product_data = self._load_product_data()
            self.specs_data = self._load_specs_data()
        except Exception as e:
            print(f"ERROR CRÍTICO al inicializar GoogleSheetManager: {e}")
            raise e
    
    def _load_product_data(self):
        try:
            print("Cargando datos de productos...")
            # Esta es la lógica original que lee una presentación por fila
            product_sheet = self.spreadsheet_main.worksheet("Productos")
            records = product_sheet.get_all_records()
            processed_data = {}
            for record in records:
                producto = record.get('PRODUCTO')
                if not producto: continue
                if producto not in processed_data:
                    # La columna en la hoja original se llamaba 'PRESENTACIONES'
                    processed_data[producto] = {"presentaciones": [record.get('PRESENTACIONES')], "forma": record.get('FORMA_FARMACEUTICA', '')}
                else:
                    processed_data[producto]["presentaciones"].append(record.get('PRESENTACIONES'))
            print("Datos de productos cargados.")
            return processed_data
        except gspread.WorksheetNotFound:
            print("Error Crítico: No se encontró la pestaña 'Productos' dentro de 'CertificadosDeAnalisis'.")
            raise
        except Exception as e:
            print(f"Error Crítico: No se pudieron cargar los datos de los productos: {e}")
            raise
    
    def _load_specs_data(self):
        specs_data = {}
        try:
            records = self.spreadsheet_specs.get_all_records()
            
            for record in records:
                producto = record.get('PRODUCTO')
                version = str(record.get('VER')) 
                descripcion = record.get('DESCRIPCIÓN')
                especificacion = record.get('ESPECIFICACIÓN')
                
                if not all([producto, version, descripcion, especificacion]):
                    continue
                if producto not in specs_data:
                    specs_data[producto] = {}
                if version not in specs_data[producto]:
                    specs_data[producto][version] = []
                specs_data[producto][version].append({
                    "descripcion": descripcion,
                    "especificacion": especificacion
                })
            
            print("Datos de especificaciones cargados correctamente.")
            return specs_data
        except Exception as e:
            print(f"Error al cargar especificaciones: {e}")
            raise

    def get_user_role(self, username):
        users_sheet = self.spreadsheet_main.worksheet("Usuarios")
        users_records = users_sheet.get_all_records()
        for user in users_records:
            if user.get('USERNAME') == username:
                return user.get('ROL', 'Operario')
        return 'Operario'

    def get_all_records(self):
        return self.worksheet.get_all_records()
    
    def get_next_codigo(self):
        current_year = str(datetime.now().year)
        try:
            all_values = self.worksheet.col_values(1)
            if len(all_values) <= 1: return f"0001-{current_year}"
            last_code = all_values[-1]
            if not last_code or '-' not in last_code: return f"0001-{current_year}"
            parts = last_code.split('-')
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
        users_sheet = self.spreadsheet_main.worksheet("Usuarios")
        return users_sheet.get_all_records()