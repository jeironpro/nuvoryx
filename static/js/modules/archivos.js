/**
 * Módulo de Gestión de Archivos y Carpetas.
 * Maneja la interacción con las tarjetas del explorador, la vista previa y las acciones masivas.
 */
import { guardarNotificacion } from './interfaz.js';

let idParaEliminar = null;
let esEliminacionCarpeta = false;

/**
 * Inicializa todos los event listeners relacionados con el explorador.
 */
export function inicializarArchivos() {
    configurarCrearCarpeta();
    configurarAccionesEliminar();
    configurarOrdenamiento();
    configurarVistaPrevia();
    configurarGestionSeleccion();
}

/**
 * Gestión de Selección Avanzada (Impecable).
 * Maneja Shift+Click, Seleccionar Todo y la barra de acciones.
 */
function configurarGestionSeleccion() {
    let ultimoSeleccionadoIndex = -1;
    const cuerpo = document.getElementById('cuerpo-tabla');
    if (!cuerpo) return;

    // --- Lógica de Selección (Clic) ---
    cuerpo.addEventListener('click', (e) => {
        const casilla = e.target.closest('.casilla-archivo');
        if (!casilla) return;

        const tarjetas = Array.from(cuerpo.querySelectorAll('.n-tarjeta:not(.n-cuadricula-vacia)'));
        const tarjetaActual = casilla.closest('.n-tarjeta');
        const indexActual = tarjetas.indexOf(tarjetaActual);

        if (e.shiftKey && ultimoSeleccionadoIndex !== -1) {
            // Selección por RANGO (Shift)
            const inicio = Math.min(indexActual, ultimoSeleccionadoIndex);
            const fin = Math.max(indexActual, ultimoSeleccionadoIndex);

            for (let i = inicio; i <= fin; i++) {
                const cb = tarjetas[i].querySelector('.casilla-archivo');
                cb.checked = true;
                tarjetas[i].classList.add('n-seleccionada');
            }
        } else {
            // Selección simple
            tarjetaActual.classList.toggle('n-seleccionada', casilla.checked);
            ultimoSeleccionadoIndex = casilla.checked ? indexActual : -1;
        }

        actualizarBarraAcciones();
    });

    // --- Seleccionar Todo ---
    const btnTodo = document.getElementById('btn-seleccionar-todo');
    if (btnTodo) {
        btnTodo.addEventListener('click', () => {
            const tarjetas = cuerpo.querySelectorAll('.n-tarjeta:not(.n-cuadricula-vacia)');
            const todosMarcados = Array.from(tarjetas).every(t => t.querySelector('.casilla-archivo').checked);

            tarjetas.forEach(t => {
                const cb = t.querySelector('.casilla-archivo');
                cb.checked = !todosMarcados;
                t.classList.toggle('n-seleccionada', !todosMarcados);
            });

            btnTodo.classList.toggle('activo', !todosMarcados);
            actualizarBarraAcciones();
        });
    }

    // --- Acciones Masivas (Fetch) ---
    const btnDescargar = document.getElementById('btn-descargar-multiples');
    if (btnDescargar) {
        btnDescargar.addEventListener('click', () => {
            const marcados = Array.from(cuerpo.querySelectorAll('.casilla-archivo:checked'));
            if (marcados.length === 0) return;

            const carpetasIds = [];
            const archivosIds = [];

            marcados.forEach(cb => {
                const tarjeta = cb.closest('.n-tarjeta');
                if (tarjeta) {
                    const id = parseInt(tarjeta.getAttribute('data-id'));
                    if (!isNaN(id)) {
                        if (tarjeta.classList.contains('fila-carpeta')) {
                            carpetasIds.push(id);
                        } else {
                            archivosIds.push(id);
                        }
                    }
                }
            });

            btnDescargar.disabled = true;
            guardarNotificacion("Generando paquete ZIP...");

            fetch('/descargar-zip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ids: archivosIds,
                    carpetas_ids: carpetasIds
                })
            })
                .then(async resp => {
                    if (!resp.ok) {
                        const errorData = await resp.json();
                        throw new Error(errorData.error || "Error al descargar");
                    }
                    return resp.blob();
                })
                .then(blob => {
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `nuvoryx_pack_${new Date().getTime()}.zip`;
                    a.click();
                    URL.revokeObjectURL(url);
                })
                .catch(err => {
                    console.error("Download error:", err);
                    alert("Error al descargar: " + err.message);
                })
                .finally(() => btnDescargar.disabled = false);
        });
    }

    const btnEliminarM = document.getElementById('btn-eliminar-multiples');
    if (btnEliminarM) {
        btnEliminarM.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const marcados = Array.from(document.querySelectorAll('.casilla-archivo:checked'));
            if (marcados.length === 0) return;

            const carpetasIds = [];
            const archivosIds = [];

            marcados.forEach(cb => {
                const tarjeta = cb.closest('.n-tarjeta');
                if (tarjeta) {
                    const id = parseInt(tarjeta.getAttribute('data-id'));
                    if (!isNaN(id)) {
                        if (tarjeta.classList.contains('fila-carpeta')) {
                            carpetasIds.push(id);
                        } else {
                            archivosIds.push(id);
                        }
                    }
                }
            });

            console.log("Bulk Delete -> Archivos:", archivosIds, "Carpetas:", carpetasIds);

            const modal = document.getElementById('modal-eliminar');
            if (!modal) return;

            modal.querySelector('h3').textContent = `¿Eliminar ${marcados.length} elementos?`;
            modal.style.display = 'flex';

            const btnConfirmar = document.getElementById('btn-confirmar-modal');
            const nuevoBtn = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(nuevoBtn, btnConfirmar);

            nuevoBtn.addEventListener('click', () => {
                nuevoBtn.disabled = true;
                nuevoBtn.textContent = "Procesando...";

                fetch('/eliminar-multiples', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        ids: archivosIds,
                        carpetas_ids: carpetasIds
                    })
                })
                    .then(async resp => {
                        let data;
                        try {
                            data = await resp.json();
                        } catch (e) {
                            throw new Error("Respuesta del servidor no es JSON.");
                        }
                        if (!resp.ok) throw new Error(data.error || 'Error en servidor');
                        return data;
                    })
                    .then(data => {
                        if (data.success) {
                            guardarNotificacion(`Se eliminaron ${data.count} elementos correctamente.`);
                            window.location.reload();
                        } else {
                            throw new Error(data.error || "No se pudo completar la acción");
                        }
                    })
                    .catch(err => {
                        console.error('Error delete:', err);
                        alert("No se pudo eliminar: " + err.message);
                        nuevoBtn.disabled = false;
                        nuevoBtn.textContent = "Confirmar";
                    });
            });
        });
    }

    // --- Cerrar barra ---
    const btnCerrar = document.getElementById('btn-cerrar-barra');
    if (btnCerrar) {
        btnCerrar.addEventListener('click', () => {
            cuerpo.querySelectorAll('.casilla-archivo').forEach(cb => {
                cb.checked = false;
                cb.closest('.n-tarjeta').classList.remove('n-seleccionada');
            });
            actualizarBarraAcciones();
        });
    }
}

/**
 * Actualiza la visibilidad de la barra flotante y el contador impecable.
 */
function actualizarBarraAcciones() {
    const marcados = document.querySelectorAll('.casilla-archivo:checked');
    const barra = document.getElementById('barra-acciones-masivas');
    const etiqueta = document.getElementById('contador-seleccionados');

    if (!barra || !etiqueta) return;

    if (marcados.length > 0) {
        etiqueta.textContent = `${marcados.length} elemento${marcados.length !== 1 ? 's' : ''} seleccionado${marcados.length !== 1 ? 's' : ''}`;
        barra.style.display = 'flex';
        // Forzar reflow para animación
        barra.offsetHeight;
        barra.classList.add('activa');
    } else {
        barra.classList.remove('activa');
        setTimeout(() => {
            if (!barra.classList.contains('activa')) {
                barra.style.display = 'none';
            }
        }, 500);
    }

    // Actualizar estado del botón Seleccionar Todo
    const btnTodo = document.getElementById('btn-seleccionar-todo');
    if (btnTodo) {
        const tarjetas = document.querySelectorAll('.n-tarjeta:not(.n-cuadricula-vacia)');
        const todosMarcados = tarjetas.length > 0 && Array.from(tarjetas).every(t => t.querySelector('.casilla-archivo').checked);
        btnTodo.classList.toggle('activo', todosMarcados);
        const span = btnTodo.querySelector('.n-btn-texto-responsive');
        if (span) span.textContent = todosMarcados ? "Deseleccionar todo" : "Seleccionar todo";
    }
}

/**
 * Configura el evento de clic en las tarjetas para abrir la previsualización.
 * Ignora clics en selectores o menús de acciones.
 */
function configurarVistaPrevia() {
    document.addEventListener('click', (e) => {
        if (e.target.closest('.n-tarjeta-seleccion') || e.target.closest('.n-tarjeta-disparador-acciones')) return;

        const tarjeta = e.target.closest('.n-tarjeta');
        if (!tarjeta || tarjeta.classList.contains('fila-carpeta')) return;

        e.preventDefault();
        const id = tarjeta.getAttribute('data-id');
        const nombre = tarjeta.querySelector('.nombre').textContent.trim();
        const tipoFila = tarjeta.getAttribute('data-tipo');

        abrirPrevisualizacion(id, nombre, tipoFila);
    });
}

/**
 * Abre el modal de previsualización según el tipo de archivo (Imagen, PDF, Video, Audio).
 */
async function abrirPrevisualizacion(id, nombre, tipo) {
    const modal = document.getElementById('modal-previsualizacion');
    if (!modal) return;

    tipo = (tipo || 'otro').toLowerCase().trim();
    console.log(`[Preview] Intentando previsualizar: ${nombre} (ID: ${id}, Tipo: ${tipo})`);

    const titulo = document.getElementById('titulo-previsualizacion');
    const contenido = document.getElementById('contenido-previsualizacion');
    const btnDescargar = document.getElementById('btn-descargar-prev');

    titulo.textContent = nombre;
    contenido.innerHTML = '<div class="preview-loading"><span class="material-symbols-outlined spin">sync</span> Generando vista previa...</div>';

    const urlArchivo = `${window.location.origin}/descargar/${id}?inline=true`;
    btnDescargar.href = `/descargar/${id}`;
    modal.style.display = 'flex';

    try {
        if (tipo === 'imagen') {
            contenido.innerHTML = `<img src="${urlArchivo}" class="preview-img" alt="${nombre}">`;
        } else if (tipo === 'pdf') {
            contenido.innerHTML = `<iframe src="${urlArchivo}" class="preview-iframe"></iframe>`;
        } else if (tipo === 'video') {
            contenido.innerHTML = `<video src="${urlArchivo}" controls class="preview-video"></video>`;
        } else if (tipo === 'audio') {
            contenido.innerHTML = `<div class="preview-audio-container"><audio src="${urlArchivo}" controls></audio></div>`;
        } else if (tipo === 'word' || tipo === 'documento' || nombre.endsWith('.docx')) {
            // Soporte para DOCX vía Mammoth
            const resp = await fetch(urlArchivo);
            const arrayBuffer = await resp.arrayBuffer();
            const result = await mammoth.convertToHtml({ arrayBuffer: arrayBuffer });
            contenido.innerHTML = `<div class="preview-docx-container">${result.value}</div>`;
        } else if (
            ['texto', 'codigo', 'markdown', 'json', 'csv'].includes(tipo) ||
            nombre.endsWith('.txt') ||
            nombre.endsWith('.md') ||
            nombre.startsWith('.') ||
            ['dockerfile', 'procfile', 'readme', 'license', 'makefile'].includes(nombre.toLowerCase())
        ) {
            const resp = await fetch(urlArchivo);
            if (!resp.ok) throw new Error(`Error al descargar el contenido (${resp.status})`);
            const texto = await resp.text();

            if (tipo === 'markdown' || nombre.endsWith('.md')) {
                const htmlMarkdown = (window.marked) ? (marked.parse ? marked.parse(texto) : marked(texto)) : `<pre class="preview-code">${texto}</pre>`;
                contenido.innerHTML = `<div class="preview-markdown github-markdown-body">${htmlMarkdown}</div>`;
            } else {
                const pre = document.createElement('pre');
                pre.className = 'preview-code';
                pre.style.color = '#101828'; // Forzar visibilidad
                const code = document.createElement('code');
                code.textContent = texto;

                if (tipo === 'json') code.className = 'language-json';
                else {
                    const ext = nombre.split('.').pop().toLowerCase();
                    code.className = `language-${ext}`;
                }

                pre.appendChild(code);
                contenido.innerHTML = '';
                contenido.appendChild(pre);
                if (window.hljs && typeof hljs.highlightElement === 'function') {
                    hljs.highlightElement(code);
                }
            }
        } else {
            console.warn(`[Preview] Tipo no reconocido o no soportado: ${tipo}`);
            mostrarRespaldo(contenido, tipo, nombre);
        }
    } catch (error) {
        console.error("[Preview] Error crítico:", error);
        contenido.innerHTML = `<div class="preview-error">
            <span class="material-symbols-outlined" style="font-size: 48px; color: #d92d20">error</span>
            <p style="margin-top: 10px; font-weight: 500">No se pudo cargar la previsualización</p>
            <p style="font-size: 0.9em; color: #667085">${error.message}</p>
        </div>`;
    }
}

/**
 * Muestra un mensaje de descarga para tipos de archivo no previsualizables en navegador.
 */
function mostrarRespaldo(contenedor, tipo, nombre) {
    contenedor.innerHTML = `<div class="fallback-container">
        <span class="material-symbols-outlined fallback-icon">draft</span>
        <p class="fallback-title">${nombre}</p>
        <p class="fallback-subtitle">Previsualización no disponible para este tipo de archivo.</p>
        <p class="fallback-action">Haz clic en descargar para verlo localmente.</p>
    </div>`;
}

/**
 * Lógica para la creación de nuevas carpetas desde el modal.
 */
function configurarCrearCarpeta() {
    const btnConfirmar = document.getElementById('btn-confirmar-crear-carpeta');
    const entradaNombre = document.getElementById('entrada-nombre-carpeta');
    if (!btnConfirmar || !entradaNombre) return;

    btnConfirmar.addEventListener('click', () => {
        const nombre = entradaNombre.value.trim();
        if (!nombre) return;

        const zona = document.getElementById('zona-arrastre');
        const cid = zona ? zona.getAttribute('data-carpeta-actual') : null;

        const datosForm = new FormData();
        datosForm.append('nombre', nombre);
        if (cid) datosForm.append('carpeta_padre_id', cid);

        btnConfirmar.disabled = true;
        btnConfirmar.textContent = "Creando...";

        fetch('/crear-carpeta', { method: 'POST', body: datosForm })
            .then(resp => resp.json())
            .then(d => {
                if (d.success) {
                    guardarNotificacion(`Carpeta "${nombre}" creada.`);
                    window.location.reload();
                } else {
                    guardarNotificacion(`Error: ${d.error}`, 'error');
                    btnConfirmar.disabled = false;
                    btnConfirmar.textContent = "Crear";
                }
            });
    });
}

/**
 * Captura clics en botones de eliminación tanto para carpetas como para archivos independientes.
 */
function configurarAccionesEliminar() {
    document.addEventListener('click', (e) => {
        const btnC = e.target.closest('.btn-eliminar-carpeta');
        if (btnC) {
            confirmarEliminacion(btnC.dataset.id, true);
            return;
        }

        const btnA = e.target.closest('.btn-eliminar-disparador');
        if (btnA) {
            confirmarEliminacion(btnA.dataset.id, false);
            return;
        }
    });
}

/**
 * Lanza el modal de confirmación antes de borrar un elemento de la base de datos.
 */
function confirmarEliminacion(id, esCarpeta) {
    idParaEliminar = id;
    esEliminacionCarpeta = esCarpeta;
    const modal = document.getElementById('modal-eliminar');
    if (!modal) return;

    modal.querySelector('h3').textContent = esCarpeta ? "¿Eliminar carpeta?" : "¿Eliminar archivo?";
    modal.style.display = 'flex';

    const btnConfirmar = document.getElementById('btn-confirmar-modal');
    // Clonar para limpiar event listeners previos
    const nuevoBtn = btnConfirmar.cloneNode(true);
    btnConfirmar.parentNode.replaceChild(nuevoBtn, btnConfirmar);

    nuevoBtn.addEventListener('click', () => {
        nuevoBtn.disabled = true;
        nuevoBtn.textContent = "Eliminando...";
        const url = esCarpeta ? `/eliminar-carpeta/${id}` : `/eliminar/${id}`;
        fetch(url, { method: 'DELETE' })
            .then(() => window.location.reload());
    });
}


/**
 * Implementa ordenamiento básico en el DOM (Carpetas siempre primero).
 */
/**
 * Implementa ordenamiento dinámico en el DOM por fecha (usando timestamps).
 * Mantiene la regla estética de carpetas primero, archivos después.
 */
function configurarOrdenamiento() {
    const selector = document.getElementById('orden-fecha');
    if (!selector) return;

    selector.addEventListener('change', () => {
        const cuerpo = document.getElementById('cuerpo-tabla');
        const tarjetas = Array.from(cuerpo.querySelectorAll('.n-tarjeta:not(.n-cuadricula-vacia)'));
        const direccion = selector.value; // 'asc' o 'desc'

        tarjetas.sort((a, b) => {
            // Prioridad 1: Carpetas siempre arriba
            const esCarpetaA = a.classList.contains('fila-carpeta');
            const esCarpetaB = b.classList.contains('fila-carpeta');
            if (esCarpetaA && !esCarpetaB) return -1;
            if (!esCarpetaA && esCarpetaB) return 1;

            // Prioridad 2: Orden cronológico dentro del mismo tipo
            const fechaA = parseFloat(a.getAttribute('data-fecha') || 0);
            const fechaB = parseFloat(b.getAttribute('data-fecha') || 0);

            if (direccion === 'desc') {
                return fechaB - fechaA; // Más recientes arriba
            } else {
                return fechaA - fechaB; // Más antiguos arriba
            }
        });

        // Reinyectar elementos ordenados
        tarjetas.forEach(t => cuerpo.appendChild(t));
    });
}
