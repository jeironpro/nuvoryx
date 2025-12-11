import { guardarNotificacion } from './interfaz.js';

export function initAuth() {
    setupLogin();
    setupRegister();
    setupLogout();
}

function setupLogin() {
    const btnLogin = document.getElementById('btn-confirmar-login');
    if (!btnLogin) return;

    btnLogin.addEventListener('click', async () => {
        const email = document.getElementById('input-login-email').value.trim();
        const password = document.getElementById('input-login-password').value;
        const errorEl = document.getElementById('error-login');

        if (!email || !password) {
            errorEl.textContent = 'Por favor completa todos los campos';
            errorEl.style.display = 'block';
            return;
        }

        btnLogin.textContent = 'Iniciando...';
        btnLogin.disabled = true;
        errorEl.style.display = 'none';

        try {
            const response = await fetch('/inicio_sesion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                guardarNotificacion(`Bienvenido, ${data.usuario.nombre}!`);
                window.location.reload();
            } else {
                errorEl.textContent = data.error || 'Error al iniciar sesión';
                errorEl.style.display = 'block';
                btnLogin.textContent = 'Iniciar Sesión';
                btnLogin.disabled = false;
            }
        } catch (error) {
            errorEl.textContent = 'Error de conexión';
            errorEl.style.display = 'block';
            btnLogin.textContent = 'Iniciar Sesión';
            btnLogin.disabled = false;
        }
    });
}

function setupRegister() {
    const btnRegister = document.getElementById('btn-confirmar-registro');
    if (!btnRegister) return;

    btnRegister.addEventListener('click', async () => {
        const nombre = document.getElementById('input-registro-nombre').value.trim();
        const email = document.getElementById('input-registro-email').value.trim();
        const password = document.getElementById('input-registro-password').value;
        const errorEl = document.getElementById('error-registro');

        if (!nombre || !email || !password) {
            errorEl.textContent = 'Por favor completa todos los campos';
            errorEl.style.display = 'block';
            return;
        }

        if (password.length < 6) {
            errorEl.textContent = 'La contraseña debe tener al menos 6 caracteres';
            errorEl.style.display = 'block';
            return;
        }

        btnRegister.textContent = 'Creando cuenta...';
        btnRegister.disabled = true;
        errorEl.style.display = 'none';

        try {
            const response = await fetch('/registro', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nombre, email, password })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                guardarNotificacion(`Cuenta creada! Bienvenido, ${data.usuario.nombre}!`);
                window.location.reload();
            } else {
                errorEl.textContent = data.error || 'Error al crear cuenta';
                errorEl.style.display = 'block';
                btnRegister.textContent = 'Crear Cuenta';
                btnRegister.disabled = false;
            }
        } catch (error) {
            errorEl.textContent = 'Error de conexión';
            errorEl.style.display = 'block';
            btnRegister.textContent = 'Crear Cuenta';
            btnRegister.disabled = false;
        }
    });
}

function setupLogout() {
    const btnLogout = document.getElementById('btn-logout');
    if (!btnLogout) return;

    btnLogout.addEventListener('click', async () => {
        try {
            const response = await fetch('/cerrar_sesion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                guardarNotificacion('Sesión cerrada');
                window.location.reload();
            }
        } catch (error) {
            console.error('Error al cerrar sesión:', error);
        }
    });
}
