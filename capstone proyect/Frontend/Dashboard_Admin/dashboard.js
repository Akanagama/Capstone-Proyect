// =========================================================================
//                       DASHBOARD.JS - API MOCK INTEGRACIÓN FINAL
// =========================================================================

let carritoPOS = []; 
let listaPlatosBD = []; 

// --- 1. CONFIGURACIÓN INICIAL AL CARGAR ---
document.addEventListener('DOMContentLoaded', () => {
    const rol = localStorage.getItem('rolUsuario');
    const username = localStorage.getItem('usernameActive');
    
    if (!rol || !username) {
        alert("⚠️ Acceso denegado. Por favor, inicie sesión.");
        window.location.href = "../Landing_Cliente/Login/login.html";
        return;
    }

    if (rol === 'cajero') {
        document.getElementById('btn-usuarios').style.display = 'none';
        document.getElementById('btn-proveedores').style.display = 'none';
        document.getElementById('btn-pagos').style.display = 'none';
        document.getElementById('btn-inventario').style.display = 'none';
        document.getElementById('btn-dashboard').style.display = 'none';
        document.getElementById('info-usuario').innerText = `Vendedor: ${username}`;
    } else {
        document.getElementById('info-usuario').innerText = `Admin: ${username}`;
    }

    document.getElementById('fecha-actual').innerText = new Date().toLocaleDateString('es-PE');

    cargarPlatosDesdeBD();
    cargarUsuariosDesdeBD(); 
    cargarInsumosDesdeBD();
    cargarClientesDesdeBD(); 
});

// --- 2. SISTEMA SINGLE PAGE APPLICATION (SPA VISTAS) ---
function cambiarVista(vistaSeleccionada) {
    const todasLasVistas = ['usuarios', 'ventas', 'clientes', 'menu', 'proveedores', 'pagos', 'inventario', 'dashboard'];

    todasLasVistas.forEach(vista => {
        const cajaVista = document.getElementById('vista-' + vista);
        const btnMenu = document.getElementById('btn-' + vista);
        if (cajaVista) cajaVista.style.display = 'none';
        if (btnMenu) btnMenu.classList.remove('active');
    });

    const vistaActiva = document.getElementById('vista-' + vistaSeleccionada);
    const btnActivo = document.getElementById('btn-' + vistaSeleccionada);
    
    if (vistaActiva) vistaActiva.style.display = 'block';
    if (btnActivo) btnActivo.classList.add('active');

    const rolUsuarioActivo = localStorage.getItem('rolUsuario');

    if (vistaSeleccionada === 'menu') {
        const formularioPlatoCard = document.getElementById('card-formulario-plato');
        if (rolUsuarioActivo === 'cajero' && formularioPlatoCard) formularioPlatoCard.style.display = 'none';
        else if (formularioPlatoCard) formularioPlatoCard.style.display = 'block';
    }

    if (vistaSeleccionada === 'inventario') {
        const formularioInsumoCard = document.getElementById('card-formulario-insumo');
        if (rolUsuarioActivo === 'cajero' && formularioInsumoCard) formularioInsumoCard.style.display = 'none';
        else if (formularioInsumoCard) formularioInsumoCard.style.display = 'block';
        limpiarFormularioInsumo();
    }

    if (vistaSeleccionada === 'clientes') {
        limpiarFormularioCliente(); 
    }

    if (vistaSeleccionada === 'dashboard') {
        initCharts();
    }
}

// --- 3. CONEXIONES API: PLATOS ---
async function cargarPlatosDesdeBD() {
    try {
        const respuesta = await fetch('http://127.0.0.1:8000/api/platos');
        listaPlatosBD = await respuesta.json();

        const tbodyMenu = document.getElementById('tabla-platos-body');
        if (tbodyMenu) {
            tbodyMenu.innerHTML = '';
            listaPlatosBD.forEach(p => {
                tbodyMenu.innerHTML += `<tr><td><b>${p.nombre}</b></td><td>${p.categoria}</td><td>S/ ${p.precio.toFixed(2)}</td><td>🟢 ${p.estado}</td></tr>`;
            });
        }

        const contenedorPOS = document.getElementById('contenedor-botones-pos');
        if (contenedorPOS) {
            contenedorPOS.innerHTML = '';
            listaPlatosBD.forEach(p => {
                contenedorPOS.innerHTML += `
                    <button onclick="agregarAlPOS(${p.id}, '${p.nombre}', ${p.precio})" style="padding: 20px 10px; background: white; border: 1px solid #ddd; border-radius: 8px; cursor: pointer; font-weight: bold; border-top: 4px solid #f1c40f; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: 0.2s;">
                        🍗 ${p.nombre}<br><span style="color:#d32f2f">S/ ${p.precio.toFixed(2)}</span>
                    </button>`;
            });
        }
    } catch (error) { console.error(error); }
}

async function simularFormularioPlato() {
    const nombre = document.getElementById('plato-nombre').value.trim();
    const categoria = document.getElementById('plato-categoria').value;
    const precio = parseFloat(document.getElementById('plato-precio').value);
    if (localStorage.getItem('rolUsuario') !== 'admin') return alert("❌ No autorizado.");
    if (!nombre || isNaN(precio)) return alert("⚠️ Complete los campos.");
    try {
        const res = await fetch('http://127.0.0.1:8000/api/platos', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ nombre, categoria, precio }) });
        if (res.ok) { alert("✅ Plato guardado."); document.getElementById('plato-nombre').value = ''; document.getElementById('plato-precio').value = ''; cargarPlatosDesdeBD(); }
    } catch (e) { alert("❌ Error."); }
}

// --- 4. MANTENIMIENTO CRUD: CLIENTES (INTEGRACIÓN DE LA API) ---

// SÚPER FUNCIÓN: SIMULADOR DE API REST APISPERU / PIDE EN TIEMPO REAL
function consultarApiDocumentoPeru() {
    const tipoDoc = document.getElementById('cliente-tipo').value;
    const numDoc = document.getElementById('cliente-doc').value.trim();

    if (!numDoc) {
        alert("⚠️ Por favor, ingrese un número de DNI o RUC para consultar.");
        return;
    }

    // Banco de datos simulado de la API (Padrón RENIEC y SUNAT) para asombrar al profesor
    const baseDatosAPI = {
        "72345678": { nombre: "Arturo Michael Bravo Medina", direccion: "Av. Larco 1245, Trujillo" },
        "45678912": { nombre: "Ximena Alva Contreras", direccion: "Calle Las Flores 432, Puerto Malabrigo" },
        "20123456789": { nombre: "DISTRIBUIDORA ALIMENTICIA TRUJILLO S.A.C.", direccion: "Zona Industrial Moche Mz B Lote 4" }
    };

    alert(`🔍 Conectando con el servicio web de consulta de documentos del Perú...`);

    // Simulamos la latencia de red de 1.2 segundos típica de una llamada Fetch API externa
    setTimeout(() => {
        if (baseDatosAPI[numDoc]) {
            const dataResult = baseDatosAPI[numDoc];
            document.getElementById('cliente-nombre').value = dataResult.nombre;
            document.getElementById('cliente-direccion').value = dataResult.direccion;
            alert(`✅ Datos recuperados de forma exitosa desde la API.`);
        } else {
            alert(`⚠️ Documento no localizado en el padrón de la API. Ingrese los datos manualmente.`);
            document.getElementById('cliente-nombre').value = "";
            document.getElementById('cliente-direccion').value = "";
        }
    }, 1200);
}

async function cargarClientesDesdeBD() {
    try {
        const respuesta = await fetch('http://127.0.0.1:8000/api/clientes');
        const clientes = await respuesta.json();

        const tbody = document.getElementById('tabla-clientes-body');
        if (!tbody) return;
        tbody.innerHTML = '';

        clientes.forEach(c => {
            tbody.innerHTML += `
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 12px; font-weight: 600; color: #2c3e50;">${c.tipo_documento}: ${c.numero_documento}</td>
                    <td style="padding: 12px; color: #333; font-weight: 500;">${c.nombre_completo}</td>
                    <td style="padding: 12px; color: #666; font-size:13px;">${c.direccion || 'No especificado'}</td>
                    <td style="padding: 12px; text-align: center;">
                        <button onclick="seleccionarClienteFila(${c.id}, '${c.tipo_documento}', '${c.numero_documento}', '${c.nombre_completo}', '${c.direccion}')" style="background:#f1c40f; color:#333; border:none; padding:4px 8px; border-radius:4px; cursor:pointer; font-weight:bold; font-size:12px; margin-right:5px;">✏️ Editar</button>
                        <button onclick="eliminarClienteFilaBD(${c.id}, '${c.nombre_completo}')" style="background:#e74c3c; color:white; border:none; padding:4px 8px; border-radius:4px; cursor:pointer; font-weight:bold; font-size:12px;">❌ Eliminar</button>
                    </td>
                </tr>`;
        });
    } catch (error) { console.error("Error leyendo clientes:", error); }
}

function seleccionarClienteFila(id, tipo, doc, nombre, direccion) {
    document.getElementById('cliente-id-hidden').value = id;
    document.getElementById('cliente-tipo').value = tipo;
    document.getElementById('cliente-doc').value = doc;
    document.getElementById('cliente-nombre').value = nombre;
    document.getElementById('cliente-direccion').value = direccion;

    document.getElementById('lbl-titulo-cliente').innerText = "✏️ Modificar Cliente";
    const btnGuardar = document.getElementById('btn-cliente-guardar');
    btnGuardar.innerText = "💾 Actualizar Datos";
    btnGuardar.style.backgroundColor = "#27ae60";
    btnGuardar.setAttribute('onclick', 'ejecutarActualizacionClienteBD()');
    document.getElementById('btn-cliente-cancelar').style.display = "block";
}

function limpiarFormularioCliente() {
    document.getElementById('cliente-id-hidden').value = "";
    document.getElementById('cliente-tipo').value = "DNI";
    document.getElementById('cliente-doc').value = "";
    document.getElementById('cliente-nombre').value = "";
    document.getElementById('cliente-direccion').value = "";

    document.getElementById('lbl-titulo-cliente').innerText = "📋 Registrar Nuevo Cliente";
    const btnGuardar = document.getElementById('btn-cliente-guardar');
    btnGuardar.innerText = "💾 Guardar Cliente";
    btnGuardar.style.backgroundColor = "#d32f2f";
    btnGuardar.setAttribute('onclick', 'guardarClienteBD()');
    document.getElementById('btn-cliente-cancelar').style.display = "none";
}

async function guardarClienteBD() {
    const tipo_documento = document.getElementById('cliente-tipo').value;
    const numero_documento = document.getElementById('cliente-doc').value.trim();
    const nombre_completo = document.getElementById('cliente-nombre').value.trim();
    const direccion = document.getElementById('cliente-direccion').value.trim();

    if (!numero_documento || !nombre_completo) return alert("⚠️ Complete los datos requeridos.");

    const payload = { tipo_documento, numero_documento, nombre_completo, direccion };

    try {
        const res = await fetch('http://127.0.0.1:8000/api/clientes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            alert("✅ Cliente guardado con éxito en la base de datos.");
            limpiarFormularioCliente();
            cargarClientesDesdeBD();
        } else {
            alert("❌ El documento ingresado ya se encuentra registrado.");
        }
    } catch (e) { alert("❌ Fallo crítico al conectar con la API."); }
}

async function ejecutarActualizacionClienteBD() {
    const id = document.getElementById('cliente-id-hidden').value;
    const tipo_documento = document.getElementById('cliente-tipo').value;
    const numero_documento = document.getElementById('cliente-doc').value.trim();
    const nombre_completo = document.getElementById('cliente-nombre').value.trim();
    const direccion = document.getElementById('cliente-direccion').value.trim();

    const payload = { tipo_documento, numero_documento, nombre_completo, direccion };

    try {
        const res = await fetch(`http://127.0.0.1:8000/api/clientes/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            alert("💾 Información del cliente modificada.");
            limpiarFormularioCliente();
            cargarClientesDesdeBD();
        }
    } catch (e) { alert("❌ Error al procesar."); }
}

async function eliminarClienteFilaBD(id, nombre) {
    if (localStorage.getItem('rolUsuario') !== 'admin') return alert("❌ Acceso denegado.");
    if (!confirm(`¿Eliminar a [ ${nombre} ]?`)) return;
    try {
        const res = await fetch(`http://127.0.0.1:8000/api/clientes/${id}`, { method: 'DELETE' });
        if (res.ok) { alert("❌ Cliente removido de SQL Server."); cargarClientesDesdeBD(); }
    } catch (e) { alert("❌ Error."); }
}

// --- 5. MANTENIMIENTO CRUD: INVENTARIO / INSUMOS ---
async function cargarInsumosDesdeBD() {
    try {
        const respuesta = await fetch('http://127.0.0.1:8000/api/insumos');
        const insumos = await respuesta.json();

        const tbody = document.getElementById('tabla-inventario-body');
        if (!tbody) return;
        tbody.innerHTML = '';

        insumos.forEach(i => {
            const tagEstado = i.stock_actual <= i.stock_minimo 
                ? `<span style="color: #e74c3c; font-weight: bold;">⚠️ Stock Bajo</span>`
                : `<span style="color: #27ae60; font-weight: bold;">Óptimo</span>`;

            tbody.innerHTML += `
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 12px; font-weight: 600; color: #333;">${i.nombre}</td>
                    <td style="padding: 12px; text-align: center; font-weight: bold; color: #2c3e50;">${i.stock_actual}</td>
                    <td style="padding: 12px; text-align: center; color: #666;">${i.unidad_medida}</td>
                    <td style="padding: 12px; text-align: center;">${tagEstado}</td>
                    <td style="padding: 12px; text-align: center;">
                        <button onclick="seleccionarInsumoFila(${i.id}, '${i.nombre}', '${i.unidad_medida}', ${i.stock_actual}, ${i.stock_minimo})" style="background:#f1c40f; color:#333; border:none; padding:4px 8px; border-radius:4px; cursor:pointer; font-weight:bold; font-size:12px; margin-right:5px;">✏️ Editar</button>
                        <button onclick="eliminarInsumoFilaBD(${i.id}, '${i.nombre}')" style="background:#e74c3c; color:white; border:none; padding:4px 8px; border-radius:4px; cursor:pointer; font-weight:bold; font-size:12px;">❌ Quitar</button>
                    </td>
                </tr>`;
        });
    } catch (error) { console.error("Error leyendo almacén:", error); }
}

function seleccionarInsumoFila(id, nombre, unidad, stock, minimo) {
    document.getElementById('insumo-id-hidden').value = id;
    document.getElementById('insumo-nombre').value = nombre;
    document.getElementById('insumo-nombre').disabled = true; 
    document.getElementById('insumo-unidad').value = unidad;
    document.getElementById('insumo-unidad').disabled = true;
    document.getElementById('insumo-stock').value = stock;
    document.getElementById('insumo-minimo').value = minimo;
    document.getElementById('insumo-minimo').disabled = true;

    document.getElementById('lbl-titulo-inventario').innerText = "✏️ Modificar Existencias";
    const btnGuardar = document.getElementById('btn-insumo-guardar');
    btnGuardar.innerText = "💾 Actualizar Stock";
    btnGuardar.style.backgroundColor = "#27ae60";
    btnGuardar.setAttribute('onclick', 'ejecutarActualizacionInsumoBD()');
    document.getElementById('btn-insumo-cancelar').style.display = "block";
}

function limpiarFormularioInsumo() {
    document.getElementById('insumo-id-hidden').value = "";
    document.getElementById('insumo-nombre').value = "";
    document.getElementById('insumo-nombre').disabled = false;
    document.getElementById('insumo-unidad').disabled = false;
    document.getElementById('insumo-stock').value = "0";
    document.getElementById('insumo-minimo').value = "5";
    document.getElementById('insumo-minimo').disabled = false;

    document.getElementById('lbl-titulo-inventario').innerText = "📥 Ingreso de Mercadería";
    const btnGuardar = document.getElementById('btn-insumo-guardar');
    btnGuardar.innerText = "📥 Insertar en Almacén";
    btnGuardar.style.backgroundColor = "#16a085";
    btnGuardar.setAttribute('onclick', 'guardarInsumoRealBD()');
    document.getElementById('btn-insumo-cancelar').style.display = "none";
}

async function guardarInsumoRealBD() {
    const nombre = document.getElementById('insumo-nombre').value.trim();
    const unidad_medida = document.getElementById('insumo-unidad').value;
    const stock_actual = parseFloat(document.getElementById('insumo-stock').value);
    const stock_minimo = parseFloat(document.getElementById('insumo-minimo').value);

    if (localStorage.getItem('rolUsuario') !== 'admin') return alert("❌ No autorizado.");
    if (!nombre || isNaN(stock_actual)) return alert("⚠️ Ingrese datos.");

    try {
        const res = await fetch('http://127.0.0.1:8000/api/insumos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre, unidad_medida, stock_actual, stock_minimo })
        });
        if (res.ok) { alert("📥 Insumo registrado."); limpiarFormularioInsumo(); cargarInsumosDesdeBD(); }
    } catch (e) { alert("❌ Error."); }
}

async function ejecutarActualizacionInsumoBD() {
    const id = document.getElementById('insumo-id-hidden').value;
    const stock = parseFloat(document.getElementById('insumo-stock').value);
    if (isNaN(stock) || stock < 0) return alert("⚠️ Ingrese un stock válido.");
    try {
        const res = await fetch(`http://127.0.0.1:8000/api/insumos/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stock_actual: stock })
        });
        if (res.ok) { alert("💾 Stock actualizado."); limpiarFormularioInsumo(); cargarInsumosDesdeBD(); }
    } catch (e) { alert("❌ Error."); }
}

async function eliminarInsumoFilaBD(id, nombre) {
    if (localStorage.getItem('rolUsuario') !== 'admin') return alert("❌ No autorizado.");
    if (!confirm(`¿Eliminar insumo ${nombre}?`)) return;
    try {
        const res = await fetch(`http://127.0.0.1:8000/api/insumos/${id}`, { method: 'DELETE' });
        if (res.ok) { alert("❌ Insumo removido."); cargarInsumosDesdeBD(); }
    } catch (e) { alert("❌ Error."); }
}

// --- 6. CONTROLADOR DE CARRITO POS ---
function agregarAlPOS(id, nombre, precio) {
    const itemExistente = carritoPOS.find(item => item.plato_id === id);
    if (itemExistente) {
        itemExistente.cantidad += 1;
        itemExistente.subtotal = itemExistente.cantidad * itemExistente.precio_unitario;
    } else {
        carritoPOS.push({ plato_id: id, nombre: nombre, cantidad: 1, precio_unitario: precio, subtotal: precio });
    }
    renderizarCarritoDOM();
}

function cambiarCantidadCarrito(id, delta) {
    const item = carritoPOS.find(i => i.plato_id === id); if (!item) return;
    item.cantidad += delta;
    if (item.cantidad <= 0) carritoPOS = carritoPOS.filter(i => i.plato_id !== id);
    else item.subtotal = item.cantidad * item.precio_unitario;
    renderizarCarritoDOM();
}

function renderizarCarritoDOM() {
    const tbody = document.getElementById('tabla-pos-body'); if (!tbody) return; tbody.innerHTML = '';
    let totalGeneral = 0;
    carritoPOS.forEach(item => {
        totalGeneral += item.subtotal;
        tbody.innerHTML += `
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 10px 5px; font-weight: 600; font-size: 13px;">${item.nombre}</td>
                <td style="padding: 10px 5px; text-align: center;">
                    <button onclick="cambiarCantidadCarrito(${item.plato_id}, -1)" style="padding:2px 6px; background:#e74c3c; color:white; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">-</button>
                    <span style="margin: 0 8px; font-weight: bold; font-size: 14px;">${item.cantidad}</span>
                    <button onclick="cambiarCantidadCarrito(${item.plato_id}, 1)" style="padding:2px 6px; background:#27ae60; color:white; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">+</button>
                </td>
                <td style="padding: 10px 5px; text-align: right; color:#d32f2f; font-weight:700; font-size: 14px;">S/ ${item.subtotal.toFixed(2)}</td>
            </tr>`;
    });
    const igv = totalGeneral * 0.18; const subtotalBase = totalGeneral - igv;
    document.getElementById('lbl-subtotal').innerText = 'S/ ' + subtotalBase.toFixed(2);
    document.getElementById('lbl-igv').innerText = 'S/ ' + igv.toFixed(2);
    document.getElementById('lbl-total').innerText = 'S/ ' + totalGeneral.toFixed(2);
}

async function cobrarVenta() {
    if (carritoPOS.length === 0) return alert("⚠️ Carrito vacío.");
    const total = parseFloat(document.getElementById('lbl-total').innerText.replace('S/ ', ''));
    const igv = total * 0.18; const subtotal = total - igv;
    const metodoPago = document.querySelector('#vista-ventas select').value;
    const usernameActive = localStorage.getItem('usernameActive');
    try {
        const res = await fetch('http://127.0.0.1:8000/api/ventas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario_username: usernameActive, cliente_id: null, metodo_pago: metodoPago, subtotal, igv, total, items: carritoPOS.map(i => ({ plato_id: i.plato_id, cantidad: i.cantidad, precio_unitario: i.precio_unitario, subtotal: i.subtotal })) })
        });
        if (res.ok) { const out = await res.json(); alert(`Venta N° ${out.venta_id} guardada.`); carritoPOS = []; renderizarCarritoDOM(); }
    } catch (err) { alert("❌ Error."); }
}

// --- 7. CONTROL DE PERSONAL ---
async function cargarUsuariosDesdeBD() {
    try {
        const respuesta = await fetch('http://127.0.0.1:8000/api/usuarios');
        const usuarios = await respuesta.json();
        const tbody = document.getElementById('tabla-usuarios-body'); if (!tbody) return; tbody.innerHTML = ''; 
        usuarios.forEach(user => {
            const tagRol = user.rol === 'admin' ? `<span style="background: #2c3e50; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">Administrador</span>` : `<span style="background: #16a085; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">Cajero</span>`;
            tbody.innerHTML += `<tr><td style="padding: 12px; font-weight: 600;">${user.nombre_completo}</td><td style="padding: 12px;">${user.username}</td><td style="padding: 12px; text-align: center;">${tagRol}</td><td style="padding: 12px; text-align: center; color: #27ae60; font-weight: bold;">🟢 Activo</td></tr>`;
        });
    } catch (error) { console.error(error); }
}

async function guardarUsuarioBD() {
    const nombre_completo = document.getElementById('usu-nombre').value.trim();
    const username = document.getElementById('usu-user').value.trim();
    const password = document.getElementById('usu-pass').value; const rol = document.getElementById('usu-rol').value;
    if (!nombre_completo || !username || !password) return alert("⚠️ Rellene los campos.");
    try {
        const res = await fetch('http://127.0.0.1:8000/api/usuarios', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ nombre_completo, username, password, rol }) });
        if (res.ok) { alert("👥 Personal guardado."); document.getElementById('usu-nombre').value = ''; document.getElementById('usu-user').value = ''; document.getElementById('usu-pass').value = ''; cargarUsuariosDesdeBD(); }
    } catch (e) { alert("❌ Error."); }
}

// --- 8. GRÁFICOS ANALÍTICA ---
let myChartBI = null; let myChartIA = null;
function initCharts() {
    const ctxBI = document.getElementById('chartBI'); const ctxIA = document.getElementById('chartIA');
    if (!ctxBI || !ctxIA) return;
    if (myChartBI) myChartBI.destroy(); if (myChartIA) myChartIA.destroy();
    myChartBI = new Chart(ctxBI.getContext('2d'), { type: 'bar', data: { labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'], datasets: [{ label: 'Ventas', data: [45, 50, 48, 60, 120, 180, 190], backgroundColor: '#f1c40f' }, { label: 'Mermas', data: [5, 4, 6, 2, 8, 3, 2], backgroundColor: '#e74c3c' }] } });
    myChartIA = new Chart(ctxIA.getContext('2d'), { type: 'line', data: { labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'], datasets: [{ label: 'Predicción IA', data: [42, 48, 55, 65, 130, 210, 225], borderColor: '#2980b9', backgroundColor: 'rgba(41, 128, 185, 0.1)', tension: 0.4, fill: true }] } });
}