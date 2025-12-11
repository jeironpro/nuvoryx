import { formatearTamano, obtenerConfiguracionIcono } from './utilidades.js';
import { guardarNotificacion } from './interfaz.js';

let filesQueue = [];

export function initUploads() {
    const zonaArrastre = document.getElementById('zona-arrastre');
    const inputArchivo = document.getElementById('input-archivo');
    const btnSubirTodo = document.getElementById('btn-subir-todo');

    if (zonaArrastre && inputArchivo) {
        // Click to open
        zonaArrastre.addEventListener('click', () => inputArchivo.click());
        inputArchivo.addEventListener('click', (e) => e.stopPropagation());

        // Change event
        inputArchivo.addEventListener('change', (e) => {
            manejarArchivos(e.target.files);
            inputArchivo.value = '';
        });

        // DnD Events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            zonaArrastre.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            zonaArrastre.addEventListener(eventName, () => {
                zonaArrastre.classList.add('highlight');
                zonaArrastre.style.borderColor = 'var(--primary-color)';
                zonaArrastre.style.backgroundColor = '#F9F5FF';
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            zonaArrastre.addEventListener(eventName, () => {
                zonaArrastre.classList.remove('highlight');
                zonaArrastre.style.borderColor = 'var(--border-color)';
                zonaArrastre.style.backgroundColor = '#FFFFFF';
            }, false);
        });

        zonaArrastre.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            manejarArchivos(dt.files);
        });
    }

    if (btnSubirTodo) {
        btnSubirTodo.addEventListener('click', async () => {
            btnSubirTodo.disabled = true;
            btnSubirTodo.textContent = 'Subiendo...';

            const copy = [...filesQueue];
            for (const item of copy) {
                await subirArchivoBackend(item);
            }

            filesQueue = [];
            actualizarVisibilidad();
            btnSubirTodo.textContent = 'Completado';
            setTimeout(() => window.location.reload(), 1000);
        });
    }
}

function manejarArchivos(files) {
    // Verificar si el usuario está autenticado
    const isAuthenticated = document.body.getAttribute('data-authenticated') === 'true';

    if (!isAuthenticated) {
        guardarNotificacion('Debes iniciar sesión para subir archivos.', 'error');
        return;
    }

    ([...files]).forEach(file => agregarACola(file));
    actualizarVisibilidad();
}

function agregarACola(file) {
    const contenedorProgreso = document.getElementById('contenedor-progreso');
    const template = document.getElementById('template-progreso');
    if (!contenedorProgreso || !template) return;

    const id = Math.random().toString(36).substr(2, 9);
    filesQueue.push({ id, file });

    const clone = template.content.cloneNode(true);
    const item = clone.querySelector('.item-progreso-subida');
    item.dataset.colaId = id;

    // Content
    clone.querySelector('.nombre-archivo').textContent = file.name;
    clone.querySelector('.tamano-archivo').textContent = formatearTamano(file.size);

    // Icon
    const iconoContainer = clone.querySelector('.icono-progreso');
    const conf = obtenerConfiguracionIcono(file);
    iconoContainer.innerHTML = conf.svg;
    iconoContainer.className = `icono-progreso ${conf.clase}`;

    // Remove btn
    item.querySelector('.btn-cerrar').addEventListener('click', () => {
        filesQueue = filesQueue.filter(f => f.id !== id);
        item.remove();
        actualizarVisibilidad();
    });

    contenedorProgreso.appendChild(item);
}

function actualizarVisibilidad() {
    const acciones = document.getElementById('acciones-cola');
    if (acciones) {
        acciones.style.display = filesQueue.length > 0 ? 'block' : 'none';
    }
}

function subirArchivoBackend(itemCola) {
    return new Promise((resolve) => {
        const itemElement = document.querySelector(`.item-progreso-subida[data-cola-id="${itemCola.id}"]`);
        if (!itemElement) { resolve(); return; }

        const barra = itemElement.querySelector('.barra-progreso');
        const estado = itemElement.querySelector('.estado-progreso');
        const btnCerrar = itemElement.querySelector('.btn-cerrar');
        if (btnCerrar) btnCerrar.style.display = 'none';

        estado.textContent = 'Subiendo...';

        const formData = new FormData();
        formData.append('archivos', itemCola.file);

        const zona = document.getElementById('zona-arrastre');
        const cid = zona ? zona.getAttribute('data-carpeta-actual') : null;
        if (cid) formData.append('carpeta_id', cid);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/subir', true);

        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const pct = (e.loaded / e.total) * 100;
                barra.style.width = pct + '%';
                estado.textContent = Math.round(pct) + '%';
            }
        };

        xhr.onload = () => {
            if (xhr.status === 200) {
                barra.style.width = '100%';
                estado.textContent = 'Completado';
                guardarNotificacion(`Archivo "${itemCola.file.name}" subido.`);
            } else {
                estado.textContent = 'Error';
                itemElement.style.backgroundColor = '#FEF3F2';
            }
            resolve();
        };
        xhr.onerror = () => {
            estado.textContent = 'Error red';
            itemElement.style.backgroundColor = '#FEF3F2';
            resolve();
        };

        xhr.send(formData);
    });
}
