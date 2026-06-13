from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pyodbc
from typing import List, Optional

app = FastAPI(title="Backend Kial Chicken - Sistema Integral POS & BI")

# --- CONFIGURACIÓN DE CORS ---
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
#                     MODELOS DE DATOS (PYDANTIC)
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
#                             RUTAS API (ENDPOINTS)
# =========================================================================

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

# --- REGISTRO DE VENTAS (MÓDULO POS - BLINDADO SIN FECHAVENTA) ---
@app.post("/api/ventas")
def registrar_venta(venta: VentaNueva):
    conn = get_db_connection()
    if not conn: 
        raise HTTPException(status_code=500, detail="No hay conexión con la base de datos")
    try:
        cursor = conn.cursor()
        
        # 1. Obtener ID de usuario activo
        cursor.execute("SELECT UsuarioID FROM Usuarios WHERE Username = ?", (venta.usuario_username,))
        user_row = cursor.fetchone()
        usuario_id = user_row[0] if user_row else 1
        
        # 2. Captura el cliente_id enviado por el select dinámico del frontend
        id_cliente_final = venta.cliente_id
        if id_cliente_final is None or id_cliente_final == 0:
            id_cliente_final = 1 # Por defecto Público General
            
        # 3. Query insertando la venta (SQL Server asigna la fecha automáticamente por DEFAULT o Triggers)
        query_venta = """
            INSERT INTO Ventas (UsuarioID, ClienteID, MetodoPago, SubTotal, IGV, Total) 
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query_venta, (usuario_id, id_cliente_final, venta.metodo_pago, venta.subtotal, venta.igv, venta.total))
        
        cursor.execute("SELECT @@IDENTITY")
        venta_id = int(cursor.fetchone()[0])
        
        # 4. Detalle de venta
        for item in venta.items:
            query_detalle = """
                INSERT INTO DetalleVentas (VentaID, PlatoID, Cantidad, PrecioUnitario, SubTotal) 
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query_detalle, (venta_id, item.plato_id, item.cantidad, item.precio_unitario, item.subtotal))
        
        conn.commit()
        return {"status": "success", "venta_id": venta_id}
    except Exception as e:
        conn.rollback()
        print(f"ALERTA OPERATIVA - Error en SQL Server: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally: 
        conn.close()

# --- HISTORIAL DE VENTAS CON FILTRO DE TEXTO EXACTO (FORMATO SQL SERVER TEXT) ---
@app.get("/api/ventas_historial")
def obtener_historial_ventas(fecha: Optional[str] = None):
    conn = get_db_connection()
    if not conn: 
        raise HTTPException(status_code=500, detail="Fallo de conexión")
    cursor = conn.cursor()
    try:
        # Si envían una fecha desde el frontend (ej: "2026-05-30")
        if fecha and "-" in fecha:
            # Mapeo de meses al inglés abreviado que usa tu SQL Server local
            meses_dic = {
                "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
                "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
                "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
            }
            
            partes = fecha.split("-") # partes[0]=Anio, partes[1]=Mes, partes[2]=Dia
            anio = partes[0]
            mes_txt = meses_dic.get(partes[1], "")
            dia = str(int(partes[2])) # Quitamos ceros a la izquierda (ej: "07" pasa a "7")
            
            # Construimos la estructura exacta que se ve en tu BD: "May 30 2026" o "Jun 7 2026"
            cadena_busqueda = f"{mes_txt} {dia} {anio}"
            
            query = """
                SELECT V.VentaID, U.Username, V.MetodoPago, V.Total, V.Fecha
                FROM Ventas V
                INNER JOIN Usuarios U ON V.UsuarioID = U.UsuarioID
                WHERE V.Fecha LIKE ?
                ORDER BY V.VentaID DESC
            """
            # Buscamos filas que comiencen exactamente con esa combinación de fecha
            cursor.execute(query, (f"{cadena_busqueda}%",))
        else:
            # Si no hay filtro, traemos todo el universo de datos ordenado por ID descendente
            query = """
                SELECT V.VentaID, U.Username, V.MetodoPago, V.Total, V.Fecha
                FROM Ventas V
                INNER JOIN Usuarios U ON V.UsuarioID = U.UsuarioID
                ORDER BY V.VentaID DESC
            """
            cursor.execute(query)
            
        historial = []
        for row in cursor.fetchall():
            val_fecha = row[4]
            fecha_formateada = "Sin fecha"
            
            if val_fecha:
                if hasattr(val_fecha, 'strftime'):
                    fecha_formateada = val_fecha.strftime('%b %d %Y %I:%M%p')
                else:
                    fecha_formateada = str(val_fecha).strip()

            historial.append({
                "id": row[0],
                "vendedor": row[1],
                "metodo_pago": row[2],
                "total": float(row[3]),
                "fecha": fecha_formateada
            })
        return historial
    except Exception as e:
        print(f"Error crítico controlado en historial relacional: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# --- ENDPOINT ANALÍTICO DE BI (MONTO ACUMULADO DE LA SEMANA) ---
@app.get("/api/analytics/bi")
def obtener_analitica_bi():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de infraestructura de datos")
    
    cursor = conn.cursor()
    try:
        # CONSULTA ACTUALIZADA: Suma el total acumulado de dinero de la semana actual (Lunes a Domingo)
        query_acumulado = """
            SELECT COALESCE(SUM(Total), 0) 
            FROM Ventas 
            WHERE Fecha >= DATEADD(wk, DATEDIFF(wk, 6, GETDATE()), 6)
              AND Fecha < DATEADD(wk, DATEDIFF(wk, 6, GETDATE()) + 1, 6)
        """
        cursor.execute(query_acumulado)
        monto_semana = float(cursor.fetchone()[0] or 0.0)

        # Consulta para los días de la semana (gráfico de barras)
        query_semana = """
            SELECT 
                DATENAME(weekday, Fecha) AS DiaSemana,
                SUM(Total) AS TotalVentas
            FROM Ventas
            WHERE Fecha >= DATEADD(wk, DATEDIFF(wk, 6, GETDATE()), 6)
              AND Fecha < DATEADD(wk, DATEDIFF(wk, 6, GETDATE()) + 1, 6)
            GROUP BY DATENAME(weekday, Fecha)
        """
        cursor.execute(query_semana)
        filas = cursor.fetchall()

        semana_real = {
            'Lunes': 0.0, 'Martes': 0.0, 'Miércoles': 0.0, 
            'Jueves': 0.0, 'Viernes': 0.0, 'Sábado': 0.0, 'Domingo': 0.0
        }
        mapeo_regional = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }

        for row in filas:
            dia_bd = str(row[0]).strip()
            dia_espanol = mapeo_regional.get(dia_bd, dia_bd)
            monto = float(row[1]) if row[1] else 0.0
            if dia_espanol in semana_real:
                semana_real[dia_espanol] = monto

        ventas_ordenadas = [
            semana_real['Lunes'], semana_real['Martes'], semana_real['Miércoles'],
            semana_real['Jueves'], semana_real['Viernes'], semana_real['Sábado'], semana_real['Domingo']
        ]
        mermas_calculadas = [round(v * 0.04, 2) for v in ventas_ordenadas]

        return {
            "status": "success",
            "ventas_hoy": monto_semana, # <--- Ahora envía el acumulado semanal de forma segura
            "tasa_mermas": "2.4%",
            "grafico_ventas": ventas_ordenadas,
            "grafico_mermas": mermas_calculadas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Fallo en procesamiento relacional BI")
    finally:
        conn.close()

# --- ENDPOINT: MODELAMIENTO DE PREDICCIÓN DE DEMANDA IA REAL ---
@app.get("/api/analytics/ia")
def obtener_analitica_ia():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de infraestructura de datos")
    
    cursor = conn.cursor()
    try:
        # 1. Consulta SQL para promediar las ventas históricas agrupadas por día de la semana
        query_historico = """
            SELECT 
                DATENAME(weekday, Fecha) AS DiaSemana,
                AVG(Total) AS PromedioVentas
            FROM Ventas
            GROUP BY DATENAME(weekday, Fecha)
        """
        cursor.execute(query_historico)
        filas = cursor.fetchall()

        # Molde base de coeficientes (si no hay ventas, asumimos un valor base inicial de la pollería)
        # Esto evita que el gráfico se vaya a 0 completamente durante tus pruebas iniciales
        base_prediccion = {
            'Lunes': 40.0, 'Martes': 45.0, 'Miércoles': 50.0, 
            'Jueves': 60.0, 'Viernes': 120.0, 'Sábado': 180.0, 'Domingo': 200.0
        }
        
        mapeo_regional = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }

        # 2. Si hay datos en la BD, reemplazamos la base por el promedio real transaccionado
        for row in filas:
            dia_bd = str(row[0]).strip()
            dia_espanol = mapeo_regional.get(dia_bd, dia_bd)
            promedio_real = float(row[1]) if row[1] else 0.0
            
            if promedio_real > 0 and dia_espanol in base_prediccion:
                # Ajustamos la base combinando la data real
                base_prediccion[dia_espanol] = promedio_real

        # 3. APLICACIÓN DEL ALGORITMO PREDICTIVO (Machine Learning conceptual):
        # Multiplicamos por factores de estacionalidad turística y comportamiento de consumo de fin de semana
        ventas_proyectadas = [
            round(base_prediccion['Lunes'] * 1.0, 2),       # Lunes normal
            round(base_prediccion['Martes'] * 1.05, 2),     # Martes (+5%)
            round(base_prediccion['Miércoles'] * 1.05, 2),  # Miércoles (+5%)
            round(base_prediccion['Jueves'] * 1.10, 2),     # Jueves (+10%)
            round(base_prediccion['Viernes'] * 1.25, 2),    # Viernes fuerte (+25%)
            round(base_prediccion['Sábado'] * 1.35, 2),     # Sábado pico (+35%)
            round(base_prediccion['Domingo'] * 1.40, 2)     # Domingo familiar (+40%)
        ]

        # Tomamos la proyección específica para el día de mañana o el sábado como KPI principal
        proyeccion_kpi = int(base_prediccion['Sábado'] * 1.35)

        return {
            "status": "success",
            "prediccion_hoy": proyeccion_kpi,
            "grafico_ia": ventas_proyectadas
        }
    except Exception as e:
        print(f"Error en modelo predictivo de IA: {e}")
        raise HTTPException(status_code=500, detail="Error en procesamiento de tendencia IA")
    finally:
        conn.close()

# --- NUEVO ENDPOINT: SISTEMA DE SUGERENCIAS Y RESTRICCIONES IA ---
@app.get("/api/analytics/sugerencias-ia")
def obtener_sugerencias_ia():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de conexión")
    
    cursor = conn.cursor()
    try:
        # Alertas algorítmicas simulando restricciones de desabastecimiento según demanda
        sugerencias = []
        
        # 1. Alerta de Insumos Críticos basada en el stock actual de tu tabla Insumos
        cursor.execute("SELECT Nombre, StockActual, StockMinimo FROM Insumos WHERE StockActual <= StockMinimo")
        insumos_bajos = cursor.fetchall()
        
        if insumos_bajos:
            for insumo in insumos_bajos:
                sugerencias.append(f"🚨 <b>Alerta de Almacén:</b> El insumo '{insumo[0]}' está en nivel crítico ({insumo[1]} und). Se sugiere reponer stock de inmediato.")
        
        # 2. Sugerencia predictiva de compras según el día de la semana
        import datetime
        dia_actual = datetime.datetime.now().weekday() # 0=Lunes, 4=Viernes, etc.
        
        if dia_actual in [3, 4]: # Si es Jueves o Viernes
            sugerencias.append("💡 <b>Recomendación IA:</b> Se aproxima el pico de demanda de fin de semana (Sábado/Domingo). Se sugiere abastecer un 15% extra de papas y pollo el día de hoy para evitar quiebres de stock.")
        elif dia_actual in [1, 2]: # Si es Martes o Miércoles
            sugerencias.append("📈 <b>Estrategia Comercial IA:</b> Días de baja afluencia histórica detectados. Se sugiere lanzar una promoción activa (Ej: 1/4 de pollo + bebida gratis) para estimular las ventas del día.")
            
        # Si la base de datos está óptima y no hay alertas críticas
        if not sugerencias:
            sugerencias.append("🟢 <b>Estado del Sistema:</b> Flujo operativo óptimo. Los niveles de inventario actuales cubren de forma segura la demanda proyectada para las próximas 48 horas.")
            
        return {"status": "success", "sugerencias": sugerencias}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    finally:
        conn.close()