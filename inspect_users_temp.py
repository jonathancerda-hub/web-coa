import os
from google_sheets_manager import GoogleSheetManager
from dotenv import load_dotenv

load_dotenv()

try:
    manager = GoogleSheetManager()
    if not manager.spreadsheet:
        print("No se pudo conectar a Google Sheets.")
    else:
        users = manager.get_all_users()
        print(f"Se encontraron {len(users)} usuarios.")
        for user in users:
            print(f"Usuario: {user.get('USERNAME')}, Rol: {user.get('ROL')}, Password (Hash/Plain): {user.get('PASSWORD')}")
except Exception as e:
    print(f"Error: {e}")
