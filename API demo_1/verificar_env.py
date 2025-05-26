# verificar_env.py

import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

# Obtener las variables
mail_user = os.environ.get("MAIL_USER")
mail_pass = os.environ.get("MAIL_PASS")

print("MAIL_USER:", mail_user)
print("MAIL_PASS:", "(oculto)" if mail_pass else None)

# Verificación básica
if mail_user and mail_pass:
    print("✅ Las variables de entorno se han cargado correctamente.")
else:
    print("❌ Las variables no se están cargando. Revisa el archivo .env o la ubicación.")
