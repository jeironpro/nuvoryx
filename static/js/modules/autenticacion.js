import { guardarNotificacion } from './interfaz.js';

export function inicializarAutenticacion() {
    setupLogin();
    setupRegister();
    setupLogout();
    setupChangeEmail();
    setupChangePassword();
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
                body: JSON.stringify({ correo: email, contrasena: password }) // Note: local vars still email/password
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
                body: JSON.stringify({ nombre, correo: email, contrasena: password })
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

function setupChangeEmail() {
    const modal = document.getElementById('modal-cambiar-correo');
    if (!modal) return;

    const btnConfirm = modal.querySelector('.btn-primario');
    const inputs = modal.querySelectorAll('input');
    const newEmailInput = inputs[0];
    const confirmEmailInput = inputs[1];

    if (btnConfirm) {
        btnConfirm.addEventListener('click', async () => {
            const newEmail = newEmailInput.value.trim();
            const confirmEmail = confirmEmailInput.value.trim();

            if (!newEmail || !confirmEmail) return alert("Completa todos los campos");
            if (newEmail !== confirmEmail) return alert("Los correos no coinciden");

            btnConfirm.textContent = "Guardando...";
            btnConfirm.disabled = true;

            try {
                const res = await fetch('/cambiar_correo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ correo: newEmail })
                });

                const data = await res.json();
                if (data.success) {
                    guardarNotificacion("Correo actualizado correctamente");
                    window.location.reload();
                } else {
                    alert(data.error || "Error al actualizar");
                    btnConfirm.textContent = "Guardar cambios";
                    btnConfirm.disabled = false;
                }
            } catch (err) {
                alert("Error de red");
                btnConfirm.textContent = "Guardar cambios";
                btnConfirm.disabled = false;
            }
        });
    }
}

function setupChangePassword() {
    const modal = document.getElementById('modal-cambiar-pass');
    if (!modal) return;

    const btnConfirm = modal.querySelector('.btn-primario');
    const inputs = modal.querySelectorAll('input');
    const newPassInput = inputs[0];
    const confirmPassInput = inputs[1];

    if (btnConfirm) {
        btnConfirm.addEventListener('click', async () => {
            const newPass = newPassInput.value;
            const confirmPass = confirmPassInput.value;

            if (!newPass || !confirmPass) return alert("Completa todos los campos");
            if (newPass !== confirmPass) return alert("Las contraseñas no coinciden");
            if (newPass.length < 6) return alert("La contraseña debe tener al menos 6 caracteres");

            btnConfirm.textContent = "Actualizando...";
            btnConfirm.disabled = true;

            try {
                const res = await fetch('/cambiar_password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ contrasena: newPass })
                });

                const data = await res.json();
                if (data.success) {
                    guardarNotificacion("Contraseña actualizada");
                    window.location.reload();
                } else {
                    alert(data.error || "Error al actualizar");
                    btnConfirm.textContent = "Actualizar";
                    btnConfirm.disabled = false;
                }
            } catch (err) {
                alert("Error de red");
                btnConfirm.textContent = "Actualizar";
                btnConfirm.disabled = false;
            }
        });
    }
}
