from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import mysql.connector
from mysql.connector import Error
from routers import recuperacion 

app = FastAPI()

app.include_router(recuperacion.router)
# ✅ Agrega el middleware CORS aquí
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8100"],  # origen del frontend (Ionic)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Configuración de conexión
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Ajusta si es necesario
    'database': 'demo_1'
}

@app.post("/api/login")
def login(correo: str = Form(...), contrasena: str = Form(...)):
    try:
        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor(dictionary=True) as cursor:
                
                # Buscar usuario por correo
                cursor.execute("SELECT id, correo, p_nombre, rol, contrasena FROM usuarios WHERE correo = %s", (correo,))
                usuario = cursor.fetchone()

                if not usuario:
                    raise HTTPException(status_code=404, detail="Usuario no encontrado")

                # Verificar contraseña
                cursor.execute(
                    "SELECT id, correo, p_nombre, rol FROM usuarios WHERE correo = %s AND contrasena = SHA2(%s, 256)",
                    (correo, contrasena)
                )
                usuario_validado = cursor.fetchone()

                if not usuario_validado:
                    raise HTTPException(status_code=401, detail="Credenciales incorrectas")

                # ✅ Retorno forzado como JSON
                return JSONResponse(content=usuario_validado)

    except Error as e:
        print("Error en la base de datos:", e)
        raise HTTPException(status_code=500, detail="Error del servidor. Intenta más tarde.")
