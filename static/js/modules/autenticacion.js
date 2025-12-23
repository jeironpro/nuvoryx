import { guardarNotificacion } from './interfaz.js';
import { validaciones } from './validaciones.js';

export function inicializarAutenticacion() {
    configurarInicioSesion();
    configurarRegistro();
    configurarCierreSesion();
    configurarCambioCorreo();
    configurarCambioContrasena();
    configurarOlvidoContrasena();
    configurarRestablecerContrasena();
    verificarTokenRestablecimiento();
}

function configurarInicioSesion() {
    const btnInicioSesion = document.getElementById('btn-confirmar-inicio-sesion');
    if (!btnInicioSesion) return;

    btnInicioSesion.addEventListener('click', async () => {
        const correo = document.getElementById('entrada-inicio-sesion-correo').value.trim();
        const contrasena = document.getElementById('entrada-inicio-sesion-contrasena').value;
        const elError = document.getElementById('error-inicio-sesion');

        if (!correo || !contrasena) {
            elError.textContent = 'Por favor completa todos los campos';
            elError.style.display = 'block';
            return;
        }

        btnInicioSesion.textContent = 'Iniciando...';
        btnInicioSesion.disabled = true;
        elError.style.display = 'none';

        try {
            const respuesta = await fetch('/inicio_sesion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ correo, contrasena })
            });

            const datos = await respuesta.json();

            if (respuesta.ok && datos.success) {
                guardarNotificacion(`¡Bienvenido, ${datos.usuario.nombre}!`);
                window.location.reload();
            } else {
                elError.textContent = datos.error || 'Error al iniciar sesión';
                elError.style.display = 'block';
                btnInicioSesion.textContent = 'Iniciar Sesión';
                btnInicioSesion.disabled = false;
            }
        } catch (error) {
            elError.textContent = 'Error de conexión';
            elError.style.display = 'block';
            btnInicioSesion.textContent = 'Iniciar Sesión';
            btnInicioSesion.disabled = false;
        }
    });
}

function configurarRegistro() {
    const btnRegistro = document.getElementById('btn-confirmar-registro');
    if (!btnRegistro) return;

    const inputPass = document.getElementById('entrada-registro-contrasena');
    const inputEmail = document.getElementById('entrada-registro-correo');
    const errorRegistro = document.getElementById('error-registro');

    inputPass.addEventListener('keyup', (e) => {
        const contrasena = e.target.value;
        const resultado = validaciones.validarContrasena(contrasena);
        actualizarBarraFuerza('barra-fuerza-registro', 'indicador-fuerza-registro', 'reglas-pass-registro', resultado, contrasena);
    });

    inputEmail.addEventListener('blur', (e) => {
        if (e.target.value && !validaciones.validarEmail(e.target.value)) {
            errorRegistro.textContent = "Formato de correo inválido";
            errorRegistro.style.display = 'block';
            errorRegistro.style.color = '#d92d20';
        } else {
            if (errorRegistro.textContent === "Formato de correo inválido") {
                errorRegistro.style.display = 'none';
            }
        }
    });

    btnRegistro.addEventListener('click', async () => {
        const nombre = document.getElementById('entrada-registro-nombre').value.trim();
        const correo = document.getElementById('entrada-registro-correo').value.trim();
        const contrasena = document.getElementById('entrada-registro-contrasena').value;
        const elError = document.getElementById('error-registro');

        if (!nombre || !correo || !contrasena) {
            elError.textContent = 'Por favor completa todos los campos';
            elError.style.display = 'block';
            return;
        }

        if (contrasena.length < 6) {
            elError.textContent = 'La contraseña debe tener al menos 6 caracteres';
            elError.style.display = 'block';
            return;
        }

        const validacionPass = validaciones.validarContrasena(contrasena);
        if (!validacionPass.valido) {
            elError.textContent = 'La contraseña no es segura: ' + validacionPass.mensajes.join(', ');
            elError.style.display = 'block';
            return;
        }

        btnRegistro.textContent = 'Creando cuenta...';
        btnRegistro.disabled = true;
        elError.style.display = 'none';

        try {
            const respuesta = await fetch('/registro', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nombre, correo, contrasena })
            });

            const datos = await respuesta.json();

            if (respuesta.ok && datos.success) {
                guardarNotificacion(`¡Cuenta creada! ¡Bienvenido, ${datos.usuario.nombre}!`);
                window.location.reload();
            } else {
                elError.textContent = datos.error || 'Error al crear cuenta';
                elError.style.display = 'block';
                btnRegistro.textContent = 'Crear Cuenta';
                btnRegistro.disabled = false;
            }
        } catch (error) {
            elError.textContent = 'Error de conexión';
            elError.style.display = 'block';
            btnRegistro.textContent = 'Crear Cuenta';
            btnRegistro.disabled = false;
        }
    });
}

function configurarCierreSesion() {
    const btnCierreSesion = document.getElementById('btn-cierre-sesion');
    if (!btnCierreSesion) return;

    btnCierreSesion.addEventListener('click', async () => {
        try {
            const respuesta = await fetch('/cerrar_sesion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (respuesta.ok) {
                guardarNotificacion('Sesión cerrada');
                window.location.reload();
            }
        } catch (error) {
            console.error('Error al cerrar sesión:', error);
        }
    });
}

function configurarCambioCorreo() {
    const modal = document.getElementById('modal-cambiar-correo');
    if (!modal) return;

    const btnConfirmar = modal.querySelector('.btn-primario');
    const entradas = modal.querySelectorAll('input');
    const entradaNuevoCorreo = entradas[0];
    const entradaConfirmarCorreo = entradas[1];

    if (btnConfirmar) {
        btnConfirmar.addEventListener('click', async () => {
            const nuevoCorreo = entradaNuevoCorreo.value.trim();
            const confirmarCorreo = entradaConfirmarCorreo.value.trim();

            if (!nuevoCorreo || !confirmarCorreo) return alert("Completa todos los campos");
            if (nuevoCorreo !== confirmarCorreo) return alert("Los correos no coinciden");

            btnConfirmar.textContent = "Guardando...";
            btnConfirmar.disabled = true;

            try {
                const resp = await fetch('/cambiar_correo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ correo: nuevoCorreo })
                });

                const datos = await resp.json();
                if (datos.success) {
                    guardarNotificacion("Correo actualizado correctamente");
                    window.location.reload();
                } else {
                    alert(datos.error || "Error al actualizar");
                    btnConfirmar.textContent = "Guardar cambios";
                    btnConfirmar.disabled = false;
                }
            } catch (err) {
                alert("Error de red");
                btnConfirmar.textContent = "Guardar cambios";
                btnConfirmar.disabled = false;
            }
        });
    }
}

function configurarCambioContrasena() {
    const modal = document.getElementById('modal-cambiar-contrasena');
    if (!modal) return;

    const inputPass = modal.querySelector('input[type="password"]');

    const btnConfirmar = modal.querySelector('.btn-primario');
    const entradas = modal.querySelectorAll('input');
    const entradaNuevaContrasena = entradas[0];
    const entradaConfirmarContrasena = entradas[1];

    if (btnConfirmar) {
        btnConfirmar.addEventListener('click', async () => {
            const nuevaContrasena = entradaNuevaContrasena.value;
            const confirmarContrasena = entradaConfirmarContrasena.value;

            if (!nuevaContrasena || !confirmarContrasena) return alert("Completa todos los campos");
            if (nuevaContrasena !== confirmarContrasena) return alert("Las contraseñas no coinciden");
            if (nuevaContrasena.length < 6) return alert("La contraseña debe tener al menos 6 caracteres");

            btnConfirmar.textContent = "Actualizando...";
            btnConfirmar.disabled = true;

            try {
                const resp = await fetch('/cambiar_password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ contrasena: nuevaContrasena })
                });

                const datos = await resp.json();
                if (datos.success) {
                    guardarNotificacion("Contraseña actualizada");
                    window.location.reload();
                } else {
                    alert(datos.error || "Error al actualizar");
                    btnConfirmar.textContent = "Actualizar";
                    btnConfirmar.disabled = false;
                }
            } catch (err) {
                alert("Error de red");
                btnConfirmar.textContent = "Actualizar";
                btnConfirmar.disabled = false;
            }
        });
    }
}

function configurarOlvidoContrasena() {
    const enlace = document.getElementById('enlace-olvido-contrasena');
    const modal = document.getElementById('modal-olvido-contrasena');
    const btnEnviar = document.getElementById('btn-confirmar-olvido');

    if (enlace && modal) {
        enlace.addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('modal-inicio-sesion').style.display = 'none';
            modal.style.display = 'flex';
        });
    }

    if (btnEnviar) {
        btnEnviar.addEventListener('click', async () => {
            const correo = document.getElementById('entrada-olvido-correo').value.trim();
            const elError = document.getElementById('error-olvido');
            const elExito = document.getElementById('exito-olvido');

            if (!correo) return alert("Introduce tu correo electrónico");

            btnEnviar.textContent = "Enviando...";
            btnEnviar.disabled = true;
            elError.style.display = 'none';

            try {
                const resp = await fetch('/olvido_password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ correo })
                });

                const datos = await resp.json();
                if (datos.success) {
                    elExito.textContent = datos.mensaje;
                    elExito.style.display = 'block';
                    btnEnviar.style.display = 'none';
                } else {
                    elError.textContent = datos.error;
                    elError.style.display = 'block';
                    btnEnviar.textContent = "Enviar Enlace";
                    btnEnviar.disabled = false;
                }
            } catch (err) {
                alert("Error de red");
                btnEnviar.disabled = false;
            }
        });
    }
}

function configurarRestablecerContrasena() {
    const btnRestablecer = document.getElementById('btn-confirmar-restablecer');
    if (!btnRestablecer) return;

    btnRestablecer.addEventListener('click', async () => {
        const contrasena = document.getElementById('entrada-restablecer-contrasena').value;
        const confirmar = document.getElementById('entrada-restablecer-confirmar').value;
        const elError = document.getElementById('error-restablecer');

        const parametrosUrl = new URLSearchParams(window.location.search);
        const token = parametrosUrl.get('reset_token');

        if (!contrasena || !confirmar) return alert("Completa todos los campos");
        if (contrasena !== confirmar) return alert("Las contraseñas no coinciden");
        if (contrasena.length < 6) return alert("Mínimo 6 caracteres");

        btnRestablecer.textContent = "Actualizando...";
        btnRestablecer.disabled = true;

        try {
            const resp = await fetch('/restablecer_password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, contrasena })
            });

            const datos = await resp.json();
            if (datos.success) {
                guardarNotificacion(datos.mensaje);
                window.location.href = '/';
            } else {
                elError.textContent = datos.error;
                elError.style.display = 'block';
                btnRestablecer.textContent = "Actualizar Contraseña";
                btnRestablecer.disabled = false;
            }
        } catch (err) {
            alert("Error de red");
            btnRestablecer.disabled = false;
        }
    });
}

function verificarTokenRestablecimiento() {
    const parametrosUrl = new URLSearchParams(window.location.search);
    if (parametrosUrl.has('reset_token')) {
        const modal = document.getElementById('modal-restablecer-contrasena');
        if (modal) modal.style.display = 'flex';

        const inputPass = document.getElementById('entrada-restablecer-contrasena');
        const errorRestablecer = document.getElementById('error-restablecer');
        if (inputPass) {
            inputPass.addEventListener('keyup', (e) => {
                const contrasena = e.target.value;
                const resultado = validaciones.validarContrasena(contrasena);
                actualizarBarraFuerza('barra-fuerza-restablecer', 'indicador-fuerza-restablecer', 'reglas-pass-restablecer', resultado, contrasena);
            });
        }
    }
}

function actualizarBarraFuerza(barraId, indicadorId, reglasId, validacion, texto) {
    const barra = document.getElementById(barraId);
    const indicador = document.getElementById(indicadorId);
    const reglas = document.getElementById(reglasId);

    if (!barra || !indicador) return;

    if (texto.length === 0) {
        barra.style.display = 'none';
        if (reglas) reglas.style.display = 'none';
        return;
    }

    barra.style.display = 'block';
    if (reglas) reglas.style.display = 'block';

    indicador.style.width = `${validacion.fuerza}%`;

    if (validacion.fuerza < 40) {
        indicador.style.backgroundColor = '#d92d20';
    } else if (validacion.fuerza < 80) {
        indicador.style.backgroundColor = '#f59e0b';
    } else {
        indicador.style.backgroundColor = '#027a48';
    }

    if (reglas) {
        if (validacion.valido) {
            reglas.textContent = "Contraseña fuerte";
            reglas.style.color = '#027a48';
        } else {
            reglas.textContent = "Faltan requisitos: " + validacion.mensajes.join(", ");
            reglas.style.color = '#667085';
        }
    }
}
