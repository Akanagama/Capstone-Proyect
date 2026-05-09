//un js para acortar tiempos

function cambiarVista(vistaSeleccionada) {
    // Lista con todas las pantallas disponibles
    const todasLasVistas = [
        'usuarios', 'ventas', 'clientes', 'menu', 
        'proveedores', 'pagos', 'inventario', 'dashboard'
    ];

    //Ocultar todas las pantallas y quitar el color rojo a los botones
    todasLasVistas.forEach(vista => {
        document.getElementById('vista-' + vista).style.display = 'none';
        document.getElementById('btn-' + vista).classList.remove('active');
    });

    // Mostrar la pantalla seleccionada y pintar su botón de rojo
    document.getElementById('vista-' + vistaSeleccionada).style.display = 'block';
    document.getElementById('btn-' + vistaSeleccionada).classList.add('active');
}
// --- LÓGICA DEL POS (PUNTO DE VENTA) ---
let totalPOS = 0;

function agregarAlPOS() {
    // 1. Obtener valores
    const selectProducto = document.getElementById('pos-producto').value;
    const cantidad = parseInt(document.getElementById('pos-cantidad').value);
    
    // Separamos el valor del select (viene como "Precio|Nombre")
    const partes = selectProducto.split('|');
    const precio = parseFloat(partes[0]);
    const nombre = partes[1];

    // 2. Calcular subtotal de esta fila
    const subtotalFila = precio * cantidad;
    totalPOS += subtotalFila;

    // 3. Crear la fila en la tabla
    const tbody = document.getElementById('tabla-pos-body');
    const nuevaFila = document.createElement('tr');
    
    nuevaFila.innerHTML = `
        <td>${nombre}</td>
        <td>${cantidad}</td>
        <td>S/ ${precio.toFixed(2)}</td>
        <td>S/ ${subtotalFila.toFixed(2)}</td>
        <td><button onclick="eliminarDelPOS(this, ${subtotalFila})" style="background:#e74c3c; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">❌</button></td>
    `;
    
    tbody.appendChild(nuevaFila);
    actualizarTotalesPOS();
}

function eliminarDelPOS(boton, subtotalFila) {
    // Restar del total general y eliminar la fila visualmente
    totalPOS -= subtotalFila;
    boton.closest('tr').remove();
    actualizarTotalesPOS();
}

function actualizarTotalesPOS() {
    // Calcular IGV (18%) y Subtotal base en Perú
    const igv = totalPOS * 0.18;
    const subtotal = totalPOS - igv;

    // Actualizar los textos en pantalla
    document.getElementById('lbl-subtotal').innerText = 'S/ ' + subtotal.toFixed(2);
    document.getElementById('lbl-igv').innerText = 'S/ ' + igv.toFixed(2);
    document.getElementById('lbl-total').innerText = 'S/ ' + totalPOS.toFixed(2);
}