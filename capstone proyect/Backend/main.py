from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pyodbc
from typing import List, Optional

app = FastAPI(title="Backend Kial Chicken - Sistema Integral POS & BI")

# --- CONFIGURACIÓN DE CORS (PERMISOS DE COMUNICACIÓN) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DE CONEXIÓN A BASE DE DATOS SQL SERVER ---
SERVER = r'.\SQLEXPRESS'
DATABASE = 'KialChickenDB'
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

def get_db_connection():
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Error crítico conectando a la BD SQL Server: {e}")
        return None

# =========================================================================
#                     MODELOS DE DATOS (PYDANTIC APPS)
# =========================================================================
class LoginRequest(BaseModel):
    username: str
    password: str

class PlatoNuevo(BaseModel):
    nombre: str
    categoria: str
    precio: float

class InsumoNuevo(BaseModel):  
    nombre: str
    unidad_medida: str
    stock_actual: float
    stock_minimo: float

class InsumoActualizar(BaseModel): 
    stock_actual: float

class ClienteNuevo(BaseModel): # <-- MODELO DE CONTROL EXACTO PARA EL ERROR 422
    tipo_documento: str
    numero_documento: str
    nombre_completo: str
    direccion: str

class UsuarioNuevo(BaseModel):
    nombre_completo: str
    username: str
    password: str
    rol: str

class ItemDetalle(BaseModel):
    plato_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float

class VentaNueva(BaseModel):
    usuario_username: str  
    cliente_id: Optional[int] = None  
    metodo_pago: str
    subtotal: float
    igv: float
    total: float
    items: List[ItemDetalle]

# =========================================================================
#                               RUTAS API (ENDPOINTS)
# =========================================================================

# --- AUTENTICACIÓN ---
@app.post("/api/login")
def login(credenciales: LoginRequest):
    conn = get_db_connection()
    if not conn: raise HTTPException(status_code=500, detail="No hay conexión con la base de datos")
    cursor = conn.cursor()
    cursor.execute("SELECT NombreCompleto, Rol FROM Usuarios WHERE Username = ? AND Password = ?", (credenciales.username, credenciales.password))
    row = cursor.fetchone()
    conn.close()
    if row: return {"status": "success", "nombre": row[0], "rol": row[1]}
    else: raise HTTPException(status_code=401, detail="Credenciales de acceso incorrectas")

# --- RUTAS GET (LECTURA DESDE SQL SERVER) ---
@app.get("/api/platos")
def obtener_platos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT PlatoID, Nombre, Categoria, Precio, Estado FROM Platos WHERE Estado = 'Activo'")
    platos = [{"id": row[0], "nombre": row[1], "categoria": row[2], "precio": float(row[3]), "estado": row[4]} for row in cursor.fetchall()]
    conn.close()
    return platos

@app.get("/api/usuarios")
def obtener_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT UsuarioID, NombreCompleto, Username, Rol FROM Usuarios")
    usuarios = [{"id": row[0], "nombre_completo": row[1], "username": row[2], "rol": row[3]} for row in cursor.fetchall()]
    conn.close()
    return usuarios

@app.get("/api/insumos")  
def obtener_insumos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT InsumoID, Nombre, UnidadMedida, StockActual, StockMinimo FROM Insumos")
    insumos = [{"id": row[0], "nombre": row[1], "unidad_medida": row[2], "stock_actual": float(row[3]), "stock_minimo": float(row[4])} for row in cursor.fetchall()]
    conn.close()
    return insumos

@app.get("/api/clientes")  
def obtener_clientes():
    conn = get_db_connection()
    if not conn: raise HTTPException(status_code=500, detail="Error de infraestructura de datos")
    cursor = conn.cursor()
    cursor.execute("SELECT ClienteID, TipoDocumento, NumeroDocumento, NombreCompleto, Direccion FROM Clientes")
    clientes = [{"id": row[0], "tipo_documento": row[1], "numero_documento": row[2], "nombre_completo": row[3], "direccion": row[4]} for row in cursor.fetchall()]
    conn.close()
    return clientes

# --- RUTAS POST / PUT / DELETE (CONTROL TRANSACCIONAL CRUD) ---
@app.post("/api/platos")
def crear_plato(plato: PlatoNuevo):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Platos (Nombre, Categoria, Precio) VALUES (?, ?, ?)", (plato.nombre, plato.categoria, plato.precio))
    conn.commit()
    conn.close()
    return {"mensaje": "Plato guardado con éxito"}

@app.post("/api/insumos")  
def crear_insumo(insumo: InsumoNuevo):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Insumos (Nombre, UnidadMedida, StockActual, StockMinimo) VALUES (?, ?, ?, ?)", (insumo.nombre, insumo.unidad_medida, insumo.stock_actual, insumo.stock_minimo))
    conn.commit()
    conn.close()
    return {"mensaje": "Insumo registrado"}

@app.put("/api/insumos/{insumo_id}")
def actualizar_insumo(insumo_id: int, insumo: InsumoActualizar):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Insumos SET StockActual = ? WHERE InsumoID = ?", (insumo.stock_actual, insumo_id))
    conn.commit()
    conn.close()
    return {"mensaje": "Stock modificado"}

@app.delete("/api/insumos/{insumo_id}")
def eliminar_insumo(insumo_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Insumos WHERE InsumoID = ?", (insumo_id,))
    conn.commit()
    conn.close()
    return {"mensaje": "Insumo eliminado"}

@app.post("/api/clientes")
def crear_cliente(cliente: ClienteNuevo):
    conn = get_db_connection()
    if not conn: raise HTTPException(status_code=500, detail="Fallo de conexión")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Clientes (TipoDocumento, NumeroDocumento, NombreCompleto, Direccion) VALUES (?, ?, ?, ?)", 
            (cliente.tipo_documento, cliente.numero_documento, cliente.nombre_completo, cliente.direccion)
        )
        conn.commit()
        return {"mensaje": "Cliente registrado de forma persistente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="El número de documento ya existe en la base de datos")
    finally:
        conn.close()

@app.put("/api/clientes/{cliente_id}")
def actualizar_cliente(cliente_id: int, cliente: ClienteNuevo):
    conn = get_db_connection()
    if not conn: raise HTTPException(status_code=500, detail="Fallo de conexión")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Clientes SET TipoDocumento = ?, NumeroDocumento = ?, NombreCompleto = ?, Direccion = ? WHERE ClienteID = ?",
        (cliente.tipo_documento, cliente.numero_documento, cliente.nombre_completo, cliente.direccion, cliente_id)
    )
    conn.commit()
    conn.close()
    return {"mensaje": "Información de cliente actualizada"}

@app.delete("/api/clientes/{cliente_id}")
def eliminar_cliente(cliente_id: int):
    conn = get_db_connection()
    if not conn: raise HTTPException(status_code=500, detail="Fallo de conexión")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Clientes WHERE ClienteID = ?", (cliente_id,))
    conn.commit()
    conn.close()
    return {"mensaje": "Cliente purgado de la base de datos"}

@app.post("/api/usuarios")
def crear_usuario(usuario: UsuarioNuevo):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Usuarios (NombreCompleto, Username, Password, Rol) VALUES (?, ?, ?, ?)", (usuario.nombre_completo, usuario.username, usuario.password, usuario.rol))
    conn.commit()
    conn.close()
    return {"mensaje": "Usuario creado"}

@app.post("/api/ventas")
def registrar_venta(venta: VentaNueva):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT UsuarioID FROM Usuarios WHERE Username = ?", (venta.usuario_username,))
        user_row = cursor.fetchone()
        usuario_id = user_row[0] if user_row else 1
        cursor.execute("INSERT INTO Ventas (UsuarioID, ClienteID, MetodoPago, SubTotal, IGV, Total) VALUES (?, ?, ?, ?, ?, ?)", (usuario_id, venta.cliente_id, venta.metodo_pago, venta.subtotal, venta.igv, venta.total))
        cursor.execute("SELECT @@IDENTITY")
        venta_id = int(cursor.fetchone()[0])
        for item in venta.items:
            cursor.execute("INSERT INTO DetalleVentas (VentaID, PlatoID, Cantidad, PrecioUnitario, SubTotal) VALUES (?, ?, ?, ?, ?)", (venta_id, item.plato_id, item.cantidad, item.precio_unitario, item.subtotal))
        conn.commit()
        return {"status": "success", "venta_id": venta_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally: conn.close()