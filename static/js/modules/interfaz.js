// Estado interno de notificaciones
let notificaciones = JSON.parse(localStorage.getItem('notificaciones')) || [];
let badgeActive = localStorage.getItem('badgeNotificacion') === 'true';

export function abrirModalEspecifico(idModal) {
    const m = document.getElementById(idModal);
    if (m) {
        m.style.display = 'flex';
        closePanels();
    }
}

// Exponer globalmente para onclick HTML
window.abrirModalEspecifico = abrirModalEspecifico;


export function initUI() {
    renderBadge();
    setupGlobalModalClosers();
    setupPanels();
    setupNotificationUI();
}

export function guardarNotificacion(msg, tipo = 'info') {
    notificaciones.unshift({ mensaje: msg, fecha: new Date().toLocaleTimeString() });
    if (notificaciones.length > 50) notificaciones.pop(); // limit
    localStorage.setItem('notificaciones', JSON.stringify(notificaciones));

    badgeActive = true;
    localStorage.setItem('badgeNotificacion', 'true');
    renderBadge();
}

function renderBadge() {
    const badge = document.getElementById('badge-notificaciones');
    if (badge) badge.style.display = badgeActive ? 'block' : 'none';
}

function closePanels() {
    const p1 = document.getElementById('panel-ajustes');
    if (p1) p1.style.display = 'none';
    const p2 = document.getElementById('panel-usuario');
    if (p2) p2.style.display = 'none';
}

function setupPanels() {
    const btnAjustes = document.getElementById('btn-ajustes');
    const panelAjustes = document.getElementById('panel-ajustes');
    const btnUsuario = document.getElementById('btn-usuario');
    const panelUsuario = document.getElementById('panel-usuario');

    if (btnAjustes && panelAjustes) {
        btnAjustes.addEventListener('click', (e) => {
            e.stopPropagation();
            const visible = panelAjustes.style.display === 'block';
            closePanels(); // close others
            panelAjustes.style.display = visible ? 'none' : 'block';
        });
    }

    if (btnUsuario && panelUsuario) {
        btnUsuario.addEventListener('click', (e) => {
            e.stopPropagation();
            const visible = panelUsuario.style.display === 'block';
            closePanels();
            panelUsuario.style.display = visible ? 'none' : 'block';
        });
    }

    // Close on click outside
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

function setupGlobalModalClosers() {
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

function setupNotificationUI() {
    const btn = document.getElementById('btn-notificaciones');
    const modal = document.getElementById('modal-notificaciones');
    const lista = document.getElementById('lista-notificaciones');

    if (btn && modal) {
        btn.addEventListener('click', () => {
            lista.innerHTML = '';
            if (notificaciones.length === 0) {
                lista.innerHTML = '<p style="padding:10px;text-align:center;color:#888">Sin notificaciones</p>';
            } else {
                notificaciones.forEach(n => {
                    const div = document.createElement('div');
                    div.innerHTML = `<strong>${n.mensaje}</strong><br><small>${n.fecha}</small>`;
                    div.style.borderBottom = '1px solid #eee';
                    div.style.padding = '8px 0';
                    lista.appendChild(div);
                });
            }
            modal.style.display = 'flex';

            // Mark read
            badgeActive = false;
            localStorage.setItem('badgeNotificacion', 'false');
            renderBadge();
        });
    }

    const btnClean = document.getElementById('btn-limpiar-notificaciones');
    if (btnClean) {
        btnClean.addEventListener('click', () => {
            notificaciones = [];
            localStorage.setItem('notificaciones', '[]');
            if (lista) lista.innerHTML = '<p style="padding:10px;text-align:center;color:#888">Sin notificaciones</p>';
        });
    }
}
