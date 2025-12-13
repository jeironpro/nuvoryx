import { guardarNotificacion } from './interfaz.js';

let idParaEliminar = null;
let esEliminacionCarpeta = false;

export function inicializarArchivos() {
    setupCreateFolder();
    setupDeleteActions();
    setupBulkActions();
    setupSorting();
    setupSorting();
    setupViewToggle();
    configurarVistaPrevia();
}

function configurarVistaPrevia() {
    // Delegación para clicks en filas o nombres
    document.addEventListener('click', (e) => {
        // Ignorar si clic en checkbox o botones
        if (e.target.closest('.casilla-archivo') || e.target.closest('.acciones-tabla')) return;

        const tr = e.target.closest('tr.fila-archivo');
        if (!tr || tr.classList.contains('fila-carpeta')) return;

        // Si es archivo
        e.preventDefault();

        // Obtener datos
        const id = tr.getAttribute('data-id') || tr.querySelector('.btn-eliminar-trigger').dataset.id;
        const nombre = tr.querySelector('.nombre').textContent.trim();
        const tipoRow = tr.getAttribute('data-tipo');

        abrirPrevisualizacion(id, nombre, tipoRow);
    });
}

function abrirPrevisualizacion(id, nombre, tipo) {
    const modal = document.getElementById('modal-previsualizacion');
    if (!modal) return;

    const title = document.getElementById('titulo-previsualizacion');
    const content = document.getElementById('contenido-previsualizacion');
    const btnDown = document.getElementById('btn-descargar-prev');

    title.textContent = nombre;
    content.innerHTML = '<div style="text-align:center;">Cargando...</div>';
    btnDown.href = `/descargar/${id}`;

    modal.style.display = 'flex';

    // Lógica visualización
    if (tipo === 'imagen') {
        const img = document.createElement('img');
        img.src = `/descargar/${id}?inline=true`;
        img.style.maxWidth = '100%';
        img.style.maxHeight = '100%';
        img.style.objectFit = 'contain';
        content.innerHTML = '';
        content.appendChild(img);
    } else if (tipo === 'pdf') {
        const iframe = document.createElement('iframe');
        iframe.src = `/descargar/${id}?inline=true`;
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = 'none';
        content.innerHTML = '';
        content.appendChild(iframe);
    } else if (tipo === 'video') {
         const video = document.createElement('video');
         video.src = `/descargar/${id}?inline=true`;
         video.controls = true;
         video.style.maxWidth = '100%';
         video.style.maxHeight = '100%';
         content.innerHTML = '';
         content.appendChild(video);
    } else if (tipo === 'audio') {
         const audio = document.createElement('audio');
         audio.src = `/descargar/${id}?inline=true`;
         audio.controls = true;
         content.innerHTML = '';
         content.appendChild(audio);
    } else if (tipo === 'codigo' || tipo === 'documento' || tipo === 'otro' || tipo === 'word' || tipo === 'excel' || tipo === 'powerpoint' || tipo === 'archivo') {
        // Texto plano intento leerlo
        if (tipo === 'codigo' || nombre.endsWith('.txt') || nombre.endsWith('.md') || nombre.endsWith('.json') || nombre.endsWith('.py') || nombre.endsWith('.js') || nombre.endsWith('.css') || nombre.endsWith('.html')) {
             fetch(`/descargar/${id}?inline=true`)
                .then(r => r.text())
                .then(text => {
                    content.innerHTML = `<pre class="pre-code-block">${escaparHtml(text)}</pre>`;
                })
                .catch(e => {
                     mostrarFallback(content, tipo);
                });
        } else {
             mostrarFallback(content, tipo);
        }
    } else {
        mostrarFallback(content, tipo);
    }
}

function mostrarFallback(container, tipo) {
    let iconName = 'draft';
    let color = '#ccc';

    if(tipo === 'word') { iconName = 'description'; color = '#2b579a'; }
    else if(tipo === 'excel') { iconName = 'table_chart'; color = '#217346'; }
    else if(tipo === 'powerpoint') { iconName = 'slideshow'; color = '#c43e1c'; }
    else if(tipo === 'archivo') { iconName = 'folder_zip'; color = '#fbbc04'; }

    container.innerHTML = `<div class="fallback-container">
        <span class="material-symbols-outlined fallback-icon" style="color: ${color};">${iconName}</span>
        <p class="fallback-title">Vista previa no disponible para este formato.</p>
        <p class="fallback-subtitle">Por favor descarga el archivo para verlo.</p>
    </div>`;
}

function escaparHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

function setupViewToggle() {
    const btnToggle = document.getElementById('btn-cambiar-vista');
    const tableContainer = document.querySelector('.tabla-archivos').parentNode;
    const icon = btnToggle ? btnToggle.querySelector('span') : null;

    if (!btnToggle || !tableContainer) return;

    // Load saved pref
    const savedView = localStorage.getItem('modoVista');
    if (savedView === 'cuadricula') {
        tableContainer.classList.add('vista-cuadricula');
        if(icon) icon.textContent = 'list';
    }

    btnToggle.addEventListener('click', () => {
        const isGrid = tableContainer.classList.toggle('vista-cuadricula');
        localStorage.setItem('modoVista', isGrid ? 'cuadricula' : 'lista');
        if(icon) icon.textContent = isGrid ? 'list' : 'grid_view';
    });
}

function setupCreateFolder() {
    const btnCrear = document.getElementById('btn-confirmar-crear-carpeta');
    if (!btnCrear) return;

    // Clonamos para asegurar pureza
    const newBtn = btnCrear.cloneNode(true);
    btnCrear.parentNode.replaceChild(newBtn, btnCrear);

    newBtn.addEventListener('click', () => {
        const inputNombre = document.getElementById('input-nombre-carpeta');
        const nombre = inputNombre.value.trim();
        if (!nombre) return;

        const zona = document.getElementById('zona-arrastre');
        const cid = zona ? zona.getAttribute('data-carpeta-actual') : null;

        const formData = new FormData();
        formData.append('nombre', nombre);
        if (cid) formData.append('carpeta_padre_id', cid);

        newBtn.textContent = "Creando...";
        newBtn.disabled = true;

        fetch('/crear-carpeta', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    guardarNotificacion(`Carpeta "${data.nombre}" creada.`);
                    window.location.reload();
                } else {
                    alert('Error: ' + data.error);
                    newBtn.disabled = false;
                    newBtn.textContent = "Crear";
                }
            })
            .catch(err => {
                console.error(err);
                newBtn.disabled = false;
            });
    });
}

function setupDeleteActions() {
    // Delegación
    document.addEventListener('click', (e) => {
        const btnFolder = e.target.closest('.btn-eliminar-carpeta');
        if (btnFolder) {
            e.preventDefault();
            confirmarEliminacion(btnFolder.dataset.id, true);
            return;
        }

        const btnFile = e.target.closest('.btn-eliminar-trigger');
        if (btnFile) {
            e.preventDefault();
            confirmarEliminacion(btnFile.dataset.id, false);
            return;
        }
    });
}

function confirmarEliminacion(id, isFolder) {
    idParaEliminar = id;
    esEliminacionCarpeta = isFolder;

    const modal = document.getElementById('modal-eliminar');
    if (!modal) return;

    modal.querySelector('h3').textContent = isFolder ? "¿Eliminar carpeta?" : "¿Eliminar archivo?";
    modal.querySelector('p').textContent = isFolder
        ? "Se eliminarán todos los archivos contenidos. Irreversible."
        : "Esta acción no se puede deshacer.";

    modal.style.display = 'flex';

    const btnConfirm = document.getElementById('btn-confirmar-modal');
    if (btnConfirm) {
        // Replace listener
        const newBtn = btnConfirm.cloneNode(true);
        btnConfirm.parentNode.replaceChild(newBtn, btnConfirm);

        newBtn.textContent = "Eliminar";
        newBtn.disabled = false;
        newBtn.addEventListener('click', () => ejecutarEliminacion(newBtn));
    }
}

function ejecutarEliminacion(btnElement) {
    if (!idParaEliminar) return;

    btnElement.textContent = "Eliminando...";
    btnElement.disabled = true;

    const endpoint = esEliminacionCarpeta
        ? `/eliminar-carpeta/${idParaEliminar}`
        : `/eliminar/${idParaEliminar}`;

    fetch(endpoint, { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
            guardarNotificacion("Elemento eliminado.");
            window.location.reload();
        })
        .catch(err => {
            alert("Error al eliminar");
            window.location.reload();
        });
}


function setupBulkActions() {
    const checkAll = document.getElementById('checkbox-seleccionar-todo');
    const bar = document.getElementById('barra-acciones-masivas');

    if (checkAll) {
        checkAll.addEventListener('change', () => {
            document.querySelectorAll('.casilla-archivo').forEach(c => c.checked = checkAll.checked);
            updateBarra();
        });
    }

    // Delegacion change checkboxes
    document.addEventListener('change', (e) => {
        if (e.target.classList.contains('casilla-archivo')) {
            updateBarra();
        }
    });

    const btnCloseBar = document.getElementById('btn-cerrar-barra');
    if (btnCloseBar) {
        btnCloseBar.addEventListener('click', () => {
            if (checkAll) checkAll.checked = false;
            document.querySelectorAll('.casilla-archivo').forEach(c => c.checked = false);
            updateBarra();
        });
    }

    const btnDeleteMass = document.getElementById('btn-eliminar-multiples');
    if (btnDeleteMass) {
        btnDeleteMass.addEventListener('click', () => {
            const checked = document.querySelectorAll('.casilla-archivo:checked');
            if (checked.length === 0) return;

            // Setup Modal for Mass Delete
            const modal = document.getElementById('modal-eliminar');
            if (!modal) return;

            const fileIds = [];
            const folderIds = [];

            checked.forEach(cb => {
                const tr = cb.closest('tr');
                const id = tr.dataset.id;
                if (tr.classList.contains('fila-carpeta')) folderIds.push(id);
                else fileIds.push(id);
            });

            modal.querySelector('h3').textContent = `¿Eliminar ${checked.length} elementos?`;
            modal.querySelector('p').textContent = "Se eliminará todo permanentemente.";
            modal.style.display = 'flex';

            const btnConfirm = document.getElementById('btn-confirmar-modal');
            const newBtn = btnConfirm.cloneNode(true);
            btnConfirm.parentNode.replaceChild(newBtn, btnConfirm);

            newBtn.textContent = "Eliminar Todo";
            newBtn.disabled = false;

            newBtn.addEventListener('click', () => {
                newBtn.textContent = "Procesando...";
                newBtn.disabled = true;

                fetch('/eliminar-multiples', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ids: fileIds, carpetas_ids: folderIds })
                })
                    .then(res => res.json())
                    .then(d => {
                        guardarNotificacion(`${d.deleted} elementos eliminados.`);
                        window.location.reload();
                    })
                    .catch(() => window.location.reload());
            });
        });
    }

    // Descarga masiva no implementada igual: solo archivos
    const btnDownload = document.getElementById('btn-descargar-multiples');
    if (btnDownload) {
        btnDownload.addEventListener('click', () => {
            const checked = document.querySelectorAll('.casilla-archivo:checked');
            const ids = [];
            checked.forEach(cb => {
                const tr = cb.closest('tr');
                if (!tr.classList.contains('fila-carpeta')) ids.push(tr.dataset.id);
            });

            if (ids.length === 0) return alert("Selecciona archivos para descargar (no carpetas).");

            fetch('/descargar-zip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids })
            })
                .then(res => res.ok ? res.blob() : Promise.reject())
                .then(blob => {
                    const u = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = u; a.download = 'archivos.zip';
                    document.body.appendChild(a); a.click(); a.remove();
                })
                .catch(() => alert("Error descarga"));
        });
    }
}

function updateBarra() {
    const c = document.querySelectorAll('.casilla-archivo:checked').length;
    const bar = document.getElementById('barra-acciones-masivas');
    const lbl = document.getElementById('contador-seleccionados');
    if (lbl) lbl.textContent = `${c} seleccionados`;
    if (bar) bar.style.display = c > 0 ? 'flex' : 'none';
}

function setupSorting() {
    const selectOrden = document.getElementById('orden-fecha');
    if (!selectOrden) return;

    selectOrden.addEventListener('change', () => {
        ordenarTabla(selectOrden.value);
    });

    // Aplicar orden por defecto (descendente)
    ordenarTabla('desc');
}

function ordenarTabla(orden) {
    const tbody = document.getElementById('tabla-body');
    if (!tbody) return;

    // Obtener todas las filas (carpetas y archivos)
    const filas = Array.from(tbody.querySelectorAll('tr:not(#fila-sin-archivos)'));

    // Separar carpetas y archivos
    const carpetas = filas.filter(f => f.classList.contains('fila-carpeta'));
    const archivos = filas.filter(f => !f.classList.contains('fila-carpeta'));

    // Función para extraer fecha de una fila
    const obtenerFecha = (fila) => {
        const celdaFecha = fila.querySelector('td:nth-child(3)'); // Columna de fecha
        if (!celdaFecha) return new Date(0);
        const textoFecha = celdaFecha.textContent.trim();
        if (textoFecha === '-') return new Date(0);
        return new Date(textoFecha);
    };

    // Ordenar carpetas
    carpetas.sort((a, b) => {
        const fechaA = obtenerFecha(a);
        const fechaB = obtenerFecha(b);
        return orden === 'asc' ? fechaA - fechaB : fechaB - fechaA;
    });

    // Ordenar archivos
    archivos.sort((a, b) => {
        const fechaA = obtenerFecha(a);
        const fechaB = obtenerFecha(b);
        return orden === 'asc' ? fechaA - fechaB : fechaB - fechaA;
    });

    // Limpiar tbody
    tbody.innerHTML = '';

    // Insertar carpetas primero, luego archivos
    carpetas.forEach(f => tbody.appendChild(f));
    archivos.forEach(f => tbody.appendChild(f));

    // Si no hay elementos, mostrar mensaje
    if (filas.length === 0) {
        const filaVacia = document.createElement('tr');
        filaVacia.id = 'fila-sin-archivos';
        filaVacia.innerHTML = '<td colspan="6" class="celda-sin-archivos">No hay archivos subidos.</td>';
        tbody.appendChild(filaVacia);
    }
}
