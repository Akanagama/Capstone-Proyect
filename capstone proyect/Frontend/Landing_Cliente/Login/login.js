function iniciarSesion() {
    const user = document.getElementById('user').value.trim().toLowerCase();
    const pass = document.getElementById('pass').value.trim();

    if ((user === 'arturo' || user === 'admin') && pass === '123') {
        // 1. Guardamos el acceso en el navegador
        localStorage.setItem('rolUsuario', user);
        
        // 2. Redirigimos al Dashboard
        
        window.location.href = "../../Dashboard_Admin/dashboard.html";
    } else {
        alert(" Credenciales incorrectas. Recuerda usar 'admin' o 'arturo'.");
    }
}