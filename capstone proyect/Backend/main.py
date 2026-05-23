from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pyodbc

app = FastAPI(title="Backend Kial Chicken")

# --- CONFIGURACIÓN DE CORS (EL PERMISO DE SEGURIDAD MÁGICO) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite que tu Live Server (5500) se comunique sin bloqueos
    allow_credentials=True,
    allow_methods=["*"],  # Permite peticiones GET y POST
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DE BASE DE DATOS SQL SERVER ---
SERVER = r'.\SQLEXPRESS'
DATABASE = 'KialChickenDB'
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

def get_db_connection():
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Error conectando a la BD: {e}")
        return None

# --- MODELOS DE DATOS ---
class PlatoNuevo(BaseModel):
    nombre: str
    categoria: str
    precio: float

class ClienteNuevo(BaseModel):
    tipo_documento: str
    numero_documento: str
    nombre_completo: str
    direccion: str

class UsuarioNuevo(BaseModel):
    nombre_completo: str
    username: str
    password: str
    rol: str

# --- RUTAS GET (LEER DATOS) ---
@app.get("/api/platos")
def obtener_platos():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la BD")
    cursor = conn.cursor()
    cursor.execute("SELECT PlatoID, Nombre, Categoria, Precio, Estado FROM Platos WHERE Estado = 'Activo'")
    platos = [{"id": row[0], "nombre": row[1], "categoria": row[2], "precio": float(row[3]), "estado": row[4]} for row in cursor.fetchall()]
    conn.close()
    return platos

# --- RUTAS POST (GUARDAR DATOS) ---
@app.post("/api/platos")
def crear_plato(plato: PlatoNuevo):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Platos (Nombre, Categoria, Precio) VALUES (?, ?, ?)",
        (plato.nombre, plato.categoria, plato.precio)
    )
    conn.commit()
    conn.close()
    return {"mensaje": "Plato guardado con éxito en la BD"}

@app.post("/api/clientes")
def crear_cliente(cliente: ClienteNuevo):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Clientes (TipoDocumento, NumeroDocumento, NombreCompleto, Direccion) VALUES (?, ?, ?, ?)",
        (cliente.tipo_documento, cliente.numero_documento, cliente.nombre_completo, cliente.direccion)
    )
    conn.commit()
    conn.close()
    return {"mensaje": "Cliente guardado con éxito"}

@app.post("/api/usuarios")
def crear_usuario(usuario: UsuarioNuevo):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Usuarios (NombreCompleto, Username, Password, Rol) VALUES (?, ?, ?, ?)",
        (usuario.nombre_completo, usuario.username, usuario.password, usuario.rol)
    )
    conn.commit()
    conn.close()
    return {"mensaje": "Usuario creado con éxito"}