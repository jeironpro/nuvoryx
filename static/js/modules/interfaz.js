// Estado interno de notificaciones (se cargará de la DB)
let listaNotificaciones = [];
let indicadorActivo = false;

export function abrirModalEspecifico(idModal) {
    const m = document.getElementById(idModal);
    if (m) {
        m.style.display = 'flex';
        cerrarPaneles();
    }
}

// Exponer globalmente para onclick HTML
window.abrirModalEspecifico = abrirModalEspecifico;


export function inicializarInterfaz() {
    cargarNotificaciones();
    configurarCierreModalesGlobal();
    configurarPaneles();
    configurarInterfazNotificaciones();
}

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

export function guardarNotificacion(msg, tipo = 'info') {
    fetch('/notificaciones', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensaje: msg, tipo: tipo })
    })
    .then(resp => resp.json())
    .then(datos => {
        if (datos.success) {
            cargarNotificaciones(); // Recargar para tener el estado fresco
        }
    })
    .catch(err => console.error("Error guardando notificación:", err));
}

function renderizarIndicador() {
    const indicador = document.getElementById('indicador-notificaciones');
    if (indicador) indicador.style.display = indicadorActivo ? 'block' : 'none';
}

function cerrarPaneles() {
    const p1 = document.getElementById('panel-ajustes');
    if (p1) p1.style.display = 'none';
    const p2 = document.getElementById('panel-usuario');
    if (p2) p2.style.display = 'none';
}

function configurarPaneles() {
    const btnAjustes = document.getElementById('btn-ajustes');
    const panelAjustes = document.getElementById('panel-ajustes');
    const btnUsuario = document.getElementById('btn-usuario');
    const panelUsuario = document.getElementById('panel-usuario');

    if (btnAjustes && panelAjustes) {
        btnAjustes.addEventListener('click', (e) => {
            e.stopPropagation();
            const visible = panelAjustes.style.display === 'block';
            cerrarPaneles(); // cerrar otros
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

    // Cerrar al hacer click fuera
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

function configurarCierreModalesGlobal() {
    // Cierra cualquier modal al hacer click en el overlay
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) {
            e.target.style.display = 'none';
        }
    });

    // Delegación para botones cerrar dentro de modales
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-cerrar-modal') || e.target.closest('.btn-cerrar-modal')) {
            e.preventDefault();
            const modal = e.target.closest('.modal-overlay');
            if (modal) modal.style.display = 'none';
        }
    });

    // Backup especifico ids
    ['btn-cancelar-modal', 'btn-cerrar-notificaciones'].forEach(id => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener('click', () => {
                const modal = btn.closest('.modal-overlay');
                if (modal) modal.style.display = 'none';
            });
        }
    });
}

function configurarInterfazNotificaciones() {
    const btn = document.getElementById('btn-notificaciones');
    const modal = document.getElementById('modal-notificaciones');
    const lista = document.getElementById('lista-notificaciones');

    if (btn && modal) {
        btn.addEventListener('click', async () => {
            lista.innerHTML = '<div style="text-align:center;padding:10px;">Cargando...</div>';

            await cargarNotificaciones(); // Asegurar datos frescos

            lista.innerHTML = '';
            if (listaNotificaciones.length === 0) {
                lista.innerHTML = '<p style="padding:10px;text-align:center;color:#888">Sin notificaciones</p>';
            } else {
                listaNotificaciones.forEach(n => {
                    const div = document.createElement('div');
                    div.innerHTML = `<strong>${n.mensaje}</strong><br><small>${n.fecha}</small>`;
                    div.style.borderBottom = '1px solid #eee';
                    div.style.padding = '8px 0';
                    div.style.opacity = n.leida ? '0.6' : '1';
                    lista.appendChild(div);
                });
            }
            modal.style.display = 'flex';

            // Marcar leídas
            if (indicadorActivo) {
                fetch('/notificaciones/marcar-leidas', { method: 'POST' })
                    .then(() => {
                        indicadorActivo = false;
                        renderizarIndicador();
                    });
            }
        });
    }

    const btnLimpiar = document.getElementById('btn-limpiar-notificaciones');
    if (btnLimpiar) {
        btnLimpiar.addEventListener('click', () => {
            fetch('/notificaciones/limpiar', { method: 'DELETE' })
                .then(resp => resp.json())
                .then(datos => {
                    if (datos.success) {
                        listaNotificaciones = [];
                        if (lista) lista.innerHTML = '<p style="padding:10px;text-align:center;color:#888">Sin notificaciones</p>';
                        indicadorActivo = false;
                        renderizarIndicador();
                    }
                });
        });
    }
}
