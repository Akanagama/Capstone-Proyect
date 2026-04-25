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