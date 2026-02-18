from google_sheets_manager import GoogleSheetManager
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

manager = GoogleSheetManager()
if not manager.spreadsheet:
    print("Error: No conexión a Sheets")
    exit(1)

username = "soporte@agrovetmarket.com"
password = "Soporte2026!"
role = "Administrador"

hashed_pw = generate_password_hash(password)

# Check if exists
user = manager.find_user(username)
if user:
    print(f"El usuario {username} ya existe. Actualizando contraseña...")
    manager.update_user(username, {'PASSWORD': hashed_pw, 'ROL': role})
else:
    print(f"Creando usuario {username}...")
    manager.add_user([username, hashed_pw, role])

print(f"Usuario: {username}")
print(f"Pass: {password}")
print("Listo.")
