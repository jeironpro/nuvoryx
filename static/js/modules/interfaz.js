/**
 * Módulo de Gestión de Interfaz y Notificaciones.
 * Controla la apertura de modales, paneles desplegables y el sistema de avisos al usuario.
 */
let listaNotificaciones = [];
let indicadorActivo = false;

/**
 * Abre un modal específico por su ID.
 * @param {string} idModal - ID del elemento HTML del modal.
 */
export function abrirModalEspecifico(idModal) {
    const m = document.getElementById(idModal);
    if (m) {
        m.style.display = 'flex';
        cerrarPaneles();
    }
}

// Exponer globalmente para integraciones rápidas en HTML
window.abrirModalEspecifico = abrirModalEspecifico;

/**
 * Registra todos los escuchadores de eventos para la UI global.
 */
export function inicializarInterfaz() {
    cargarNotificaciones();
    configurarCierreModalesGlobal();
    configurarPaneles();
    configurarInterfazNotificaciones();
}

/**
 * Recupera las notificaciones del servidor y actualiza el indicador visual.
 */
async function cargarNotificaciones() {
    try {
        const resp = await fetch('/notificaciones');
        if (resp.ok) {
            listaNotificaciones = await resp.json();
            indicadorActivo = listaNotificaciones.some(n => !n.leida);
            renderizarIndicador();
        }
    } catch (err) {
        console.error("Error cargando notificaciones:", err);
    }
}

/**
 * Envía una nueva notificación al servidor.
 * @param {string} msg - Texto de la notificación.
 * @param {string} tipo - Categoría (info, success, error).
 */
export function guardarNotificacion(msg, tipo = 'info') {
    fetch('/notificaciones', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensaje: msg, tipo: tipo })
    })
        .then(resp => resp.json())
        .then(datos => {
            if (datos.success) {
                cargarNotificaciones();
            }
        })
        .catch(err => console.error("Error guardando notificación:", err));
}

/**
 * Muestra o esconde el punto rojo de notificaciones pendientes.
 */
function renderizarIndicador() {
    const indicador = document.getElementById('indicador-notificaciones');
    if (indicador) indicador.style.display = indicadorActivo ? 'block' : 'none';
}

/**
 * Cierra los paneles de ajustes y usuario.
 */
function cerrarPaneles() {
    const p1 = document.getElementById('panel-ajustes');
    if (p1) p1.style.display = 'none';
    const p2 = document.getElementById('panel-usuario');
    if (p2) p2.style.display = 'none';
}

/**
 * Configura los disparadores de los paneles superiores (Ajustes, Perfil).
 */
function configurarPaneles() {
    const btnAjustes = document.getElementById('btn-ajustes');
    const panelAjustes = document.getElementById('panel-ajustes');
    const btnUsuario = document.getElementById('btn-usuario');
    const panelUsuario = document.getElementById('panel-usuario');

    if (btnAjustes && panelAjustes) {
        btnAjustes.addEventListener('click', (e) => {
            e.stopPropagation();
            const visible = panelAjustes.style.display === 'block';
            cerrarPaneles();
            panelAjustes.style.display = visible ? 'none' : 'block';
        });
    }

    if (btnUsuario && panelUsuario) {
        btnUsuario.addEventListener('click', (e) => {
            e.stopPropagation();
            const visible = panelUsuario.style.display === 'block';
            cerrarPaneles();
            panelUsuario.style.display = visible ? 'none' : 'block';
        });
    }

    // Cerrar al hacer clic fuera del panel
    window.addEventListener('click', (e) => {
        if (panelAjustes && panelAjustes.style.display === 'block') {
            if (!panelAjustes.contains(e.target) && e.target !== btnAjustes) {
                panelAjustes.style.display = 'none';
            }
        }
        if (panelUsuario && panelUsuario.style.display === 'block') {
            if (!panelUsuario.contains(e.target) && e.target !== btnUsuario) {
                panelUsuario.style.display = 'none';
            }
        }
    });
}

/**
 * Gestión global de modales: cierre por overlay, escape y accesibilidad de foco.
 */
function configurarCierreModalesGlobal() {
    // Cerrar al hacer clic en el fondo oscuro
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) {
            e.target.style.display = 'none';
        }
    });

    // Delegación de eventos para botones de cierre
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-cerrar-modal') || e.target.closest('.btn-cerrar-modal')) {
            e.preventDefault();
            const modal = e.target.closest('.modal-overlay');
            if (modal) modal.style.display = 'none';
        }
    });

    ['btn-cancelar-modal', 'btn-cerrar-notificaciones'].forEach(id => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener('click', () => {
                const modal = btn.closest('.modal-overlay');
                if (modal) modal.style.display = 'none';
            });
        }
    });

    // Foco automático al abrir modales
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'style') {
                const modal = mutation.target;
                if (modal.classList.contains('modal-overlay') && modal.style.display !== 'none') {
                    setTimeout(() => {
                        const primerInput = modal.querySelector('input, textarea, select');
                        if (primerInput) primerInput.focus();
                    }, 50);
                }
            }
        });
    });

    document.querySelectorAll('.modal-overlay').forEach(modal => {
        observer.observe(modal, { attributes: true });
    });

    // Accesibilidad: Confirmar con tecla Enter en modales
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const activeElement = document.activeElement;
            const modal = activeElement.closest('.modal-overlay');

            if (modal && modal.style.display !== 'none') {
                if (activeElement.tagName === 'TEXTAREA') return;
                if (activeElement.tagName === 'BUTTON') return;

                const btnPrimario = modal.querySelector('.btn-primario');
                if (btnPrimario && !btnPrimario.disabled) {
                    e.preventDefault();
                    btnPrimario.click();
                }
            }
        }
    });
}

/**
 * Renderiza la lista de notificaciones en el modal desplegable.
 */
function configurarInterfazNotificaciones() {
    const btn = document.getElementById('btn-notificaciones');
    const modal = document.getElementById('modal-notificaciones');
    const lista = document.getElementById('lista-notificaciones');

    if (btn && modal) {
        btn.addEventListener('click', async () => {
            lista.innerHTML = '';
            await cargarNotificaciones();

            if (listaNotificaciones.length === 0) {
                lista.innerHTML = '<p style="padding:10px;text-align:center;color:#888">Sin notificaciones</p>';
            } else {
                listaNotificaciones.forEach(n => {
                    const div = document.createElement('div');
                    div.style.borderBottom = '1px solid #eee';
                    div.style.padding = '8px 0';
                    div.style.opacity = n.leida ? '0.6' : '1';
                    div.innerHTML = `<strong>${n.mensaje}</strong><br><small>${n.fecha}</small>`;
                    lista.appendChild(div);
                });
            }
            modal.style.display = 'flex';

            if (indicadorActivo) {
                fetch('/notificaciones/marcar-leidas', { method: 'POST' })
                    .then(() => {
                        indicadorActivo = false;
                        renderizarIndicador();
                    });
            }
        });
    }

    // Lógica para vaciar el historial de notificaciones
    const btnLimpiar = document.getElementById('btn-limpiar-notificaciones');
    if (btnLimpiar) {
        btnLimpiar.addEventListener('click', () => {
            fetch('/notificaciones/limpiar', { method: 'DELETE' })
                .then(resp => resp.json())
                .then(datos => {
                    if (datos.success) {
                        listaNotificaciones = [];
                        if (lista) {
                            lista.innerHTML = '';
                            const p = document.createElement('p');
                            p.style.padding = '10px';
                            p.style.textAlign = 'center';
                            p.style.color = '#888';
                            p.textContent = 'Sin notificaciones';
                            lista.appendChild(p);
                        }
                        indicadorActivo = false;
                        renderizarIndicador();
                    }
                });
        });
    }
}
