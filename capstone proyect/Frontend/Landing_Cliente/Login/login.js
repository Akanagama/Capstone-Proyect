// =========================================================================
//                       LOGIN.JS - AUTENTICACIÓN TRANSACCIONAL REAL
// =========================================================================

document.getElementById('form-login').addEventListener('submit', async (event) => {
    // 1. Prevenir que la página se recargue e interrumpa el flujo asíncrono
    event.preventDefault();

    // 2. Capturar los elementos del formulario HTML
    const usernameInput = document.getElementById('input-usuario').value.trim();
    const passwordInput = document.getElementById('input-password').value;

    try {
        // 3. Realizar la petición POST HTTP hacia el backend en Python FastAPI
        const respuesta = await fetch('http://127.0.0.1:8000/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: usernameInput,
                password: passwordInput
            })
        });

        // 4. Si las credenciales coinciden con los registros de SQL Server (Status 200)
        if (respuesta.ok) {
            const data = await respuesta.json();

            // Guardamos las variables de control en el almacenamiento del navegador
            localStorage.setItem('rolUsuario', data.rol);
            localStorage.setItem('usernameActive', usernameInput);

            alert(`¡Bienvenido al sistema, ${data.nombre}!`);

            // Redirección directa hacia el panel administrador según tu árbol de carpetas
            window.location.href = "../../Dashboard_Admin/dashboard.html";
        } else {
            // Si el servidor retorna un error de credenciales (Status 401)
            alert("❌ Credenciales inválidas. Verifique el usuario y contraseña.");
        }

    } catch (error) {
        console.error("Error de conexión:", error);
        alert("❌ No se pudo establecer comunicación con el Backend de FastAPI. Asegúrate de que tu servidor Python esté corriendo en el puerto 8000.");
    }
});