import { guardarNotificacion } from './interfaz.js';

let idParaEliminar = null;
let esEliminacionCarpeta = false;

export function inicializarArchivos() {
    configurarCrearCarpeta();
    configurarAccionesEliminar();
    configurarAccionesMasivas();
    configurarOrdenamiento();
    configurarCambioVista();
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
        const id = tr.getAttribute('data-id') || tr.querySelector('.btn-eliminar-disparador').dataset.id;
        const nombre = tr.querySelector('.nombre').textContent.trim();
        const tipoFila = tr.getAttribute('data-tipo');

        abrirPrevisualizacion(id, nombre, tipoFila);
    });
}

function abrirPrevisualizacion(id, nombre, tipo) {
    const modal = document.getElementById('modal-previsualizacion');
    if (!modal) return;

    const titulo = document.getElementById('titulo-previsualizacion');
    const contenido = document.getElementById('contenido-previsualizacion');
    const btnDescargar = document.getElementById('btn-descargar-prev');

    titulo.textContent = nombre;
    contenido.innerHTML = '<div class="preview-loading"><span class="material-symbols-outlined spin">sync</span> Cargando vista previa...</div>';

    // Generar URL completa para visores externos si es necesario
    const urlActual = window.location.origin;
    const urlArchivo = `${urlActual}/descargar/${id}?inline=true`;

    btnDescargar.href = `/descargar/${id}`;
    modal.style.display = 'flex';

    // Lógica de visualización mejorada
    const extension = nombre.split('.').pop().toLowerCase();

    if (tipo === 'imagen') {
        const img = document.createElement('img');
        img.src = urlArchivo;
        img.className = 'preview-img';
        img.onerror = () => mostrarRespaldo(contenido, tipo);
        contenido.innerHTML = '';
        contenido.appendChild(img);
    }
    else if (tipo === 'pdf') {
        contenido.innerHTML = `<iframe src="${urlArchivo}" class="preview-iframe"></iframe>`;
    }
    else if (tipo === 'video') {
         contenido.innerHTML = `<video src="${urlArchivo}" controls class="preview-video"></video>`;
    }
    else if (tipo === 'audio') {
         contenido.innerHTML = `<div class="preview-audio-container">
            <span class="material-symbols-outlined audio-icon">audiotrack</span>
            <audio src="${urlArchivo}" controls></audio>
         </div>`;
    }
    else if (tipo === 'markdown') {
        fetch(urlArchivo)
            .then(r => r.text())
            .then(texto => {
                contenido.innerHTML = `<div class="preview-markdown markdown-body">${marked.parse(texto)}</div>`;
            })
            .catch(() => mostrarRespaldo(contenido, tipo));
    }
    else if (tipo === 'csv') {
        fetch(urlArchivo)
            .then(r => r.text())
            .then(texto => {
                const filas = texto.split('\n').filter(r => r.trim()).map(r => r.split(','));
                let html = '<div class="preview-table-container"><table class="preview-table"><thead><tr>';
                if (filas.length > 0) {
                    filas[0].forEach(celda => html += `<th>${escaparHtml(celda)}</th>`);
                    html += '</tr></thead><tbody>';
                    for (let i = 1; i < filas.length; i++) {
                        html += '<tr>';
                        filas[i].forEach(celda => html += `<td>${escaparHtml(celda)}</td>`);
                        html += '</tr>';
                    }
                    html += '</tbody></table></div>';
                    contenido.innerHTML = html;
                } else {
                    contenido.innerHTML = '<p>Archivo CSV vacío</p>';
                }
            })
            .catch(() => mostrarRespaldo(contenido, tipo));
    }
    else if (tipo === 'json') {
        fetch(urlArchivo)
            .then(r => r.json())
            .then(json => {
                const formateado = JSON.stringify(json, null, 2);
                contenido.innerHTML = `<pre class="preview-code"><code class="language-json">${escaparHtml(formateado)}</code></pre>`;
                hljs.highlightElement(contenido.querySelector('code'));
            })
            .catch(() => mostrarRespaldo(contenido, tipo));
    }
    else if (tipo === 'word' && extension === 'docx') {
        // Previsualización local para .docx usando mammoth
        fetch(urlArchivo)
            .then(r => r.arrayBuffer())
            .then(arrayBuffer => {
                mammoth.convertToHtml({ arrayBuffer: arrayBuffer })
                    .then(result => {
                        contenido.innerHTML = `<div class="preview-docx-container">${result.value}</div>`;
                    })
                    .catch(() => mostrarRespaldo(contenido, tipo));
            })
            .catch(() => mostrarRespaldo(contenido, tipo));
    }
    else if (tipo === 'word' || tipo === 'excel' || tipo === 'powerpoint') {
        // Usar visor de Google para documentos de Office (solo funciona si es público)
        const urlCodificada = encodeURIComponent(urlArchivo);
        const urlVisorGoogle = `https://docs.google.com/viewer?url=${urlCodificada}&embedded=true`;

        contenido.innerHTML = `
            <div class="preview-office-container">
                <iframe src="${urlVisorGoogle}" class="preview-iframe"></iframe>
                <div class="office-fallback-msg">
                    <small>Este visor requiere que el archivo sea accesible por internet. Si no carga, descárgalo para verlo.</small>
                </div>
            </div>`;
    }
    else if (tipo === 'codigo' || tipo === 'texto') {
        fetch(urlArchivo)
            .then(r => r.text())
            .then(texto => {
                const claseLang = tipo === 'codigo' ? '' : 'language-plaintext';
                contenido.innerHTML = `<pre class="preview-code"><code class="${claseLang}">${escaparHtml(texto)}</code></pre>`;
                if (tipo === 'codigo') {
                    hljs.highlightElement(contenido.querySelector('code'));
                }
            })
            .catch(() => mostrarRespaldo(contenido, tipo));
    }
    else {
        mostrarRespaldo(contenido, tipo);
    }
}

function mostrarRespaldo(contenedor, tipo) {
    let nombreIcono = 'draft';
    let color = '#64748b';

    const mapeo = {
        'word': { icon: 'description', color: '#2b579a' },
        'excel': { icon: 'table_chart', color: '#217346' },
        'powerpoint': { icon: 'slideshow', color: '#c43e1c' },
        'archivo': { icon: 'folder_zip', color: '#fbbc04' },
        'pdf': { icon: 'picture_as_pdf', color: '#f04438' },
        'imagen': { icon: 'image', color: '#9e77ed' },
        'video': { icon: 'movie', color: '#12b76a' },
        'audio': { icon: 'audiotrack', color: '#d93025' },
        'codigo': { icon: 'code', color: '#5f6368' },
        'texto': { icon: 'article', color: '#667085' },
        'fig': { icon: 'token', color: '#ff7262' }
    };

    if (mapeo[tipo]) {
        nombreIcono = mapeo[tipo].icon;
        color = mapeo[tipo].color;
    }

    contenedor.innerHTML = `<div class="fallback-container">
        <span class="material-symbols-outlined fallback-icon" style="color: ${color};">${nombreIcono}</span>
        <p class="fallback-title">Vista previa no disponible para este formato.</p>
        <p class="fallback-subtitle">Por favor descarga el archivo para verlo.</p>
    </div>`;
}

function escaparHtml(texto) {
    const mapa = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return texto.replace(/[&<>"']/g, function(m) { return mapa[m]; });
}

function configurarCambioVista() {
    const btnVista = document.getElementById('btn-cambiar-vista');
    const contenedorTabla = document.querySelector('.tabla-archivos').parentNode;
    const icono = btnVista ? btnVista.querySelector('span') : null;

    if (!btnVista || !contenedorTabla) return;

    // Cargar preferencia guardada
    const vistaGuardada = localStorage.getItem('modoVista');
    if (vistaGuardada === 'cuadricula') {
        contenedorTabla.classList.add('vista-cuadricula');
        if(icono) icono.textContent = 'list';
    }

    btnVista.addEventListener('click', () => {
        const esCuadricula = contenedorTabla.classList.toggle('vista-cuadricula');
        localStorage.setItem('modoVista', esCuadricula ? 'cuadricula' : 'lista');
        if(icono) icono.textContent = esCuadricula ? 'list' : 'grid_view';
    });
}

function configurarCrearCarpeta() {
    const btnConfirmar = document.getElementById('btn-confirmar-crear-carpeta');
    if (!btnConfirmar) return;

    // Clonamos para asegurar pureza
    const nuevoBtn = btnConfirmar.cloneNode(true);
    btnConfirmar.parentNode.replaceChild(nuevoBtn, btnConfirmar);

    nuevoBtn.addEventListener('click', () => {
        const entradaNombre = document.getElementById('entrada-nombre-carpeta');
        const nombre = entradaNombre.value.trim();
        if (!nombre) return;

        const zona = document.getElementById('zona-arrastre');
        const cid = zona ? zona.getAttribute('data-carpeta-actual') : null;

        const datosForm = new FormData();
        datosForm.append('nombre', nombre);
        if (cid) datosForm.append('carpeta_padre_id', cid);

        nuevoBtn.textContent = "Creando...";
        nuevoBtn.disabled = true;

        fetch('/crear-carpeta', { method: 'POST', body: datosForm })
            .then(resp => resp.json())
            .then(datos => {
                if (datos.success) {
                    guardarNotificacion(`Carpeta "${datos.nombre}" creada.`);
                    window.location.reload();
                } else {
                    alert('Error: ' + datos.error);
                    nuevoBtn.disabled = false;
                    nuevoBtn.textContent = "Crear";
                }
            })
            .catch(err => {
                console.error(err);
                nuevoBtn.disabled = false;
            });
    });
}

function configurarAccionesEliminar() {
    // Delegación
    document.addEventListener('click', (e) => {
        const btnCarpeta = e.target.closest('.btn-eliminar-carpeta');
        if (btnCarpeta) {
            e.preventDefault();
            confirmarEliminacion(btnCarpeta.dataset.id, true);
            return;
        }

        const btnArchivo = e.target.closest('.btn-eliminar-disparador');
        if (btnArchivo) {
            e.preventDefault();
            confirmarEliminacion(btnArchivo.dataset.id, false);
            return;
        }
    });
}

function confirmarEliminacion(id, esCarpeta) {
    idParaEliminar = id;
    esEliminacionCarpeta = esCarpeta;

    const modal = document.getElementById('modal-eliminar');
    if (!modal) return;

    modal.querySelector('h3').textContent = esCarpeta ? "¿Eliminar carpeta?" : "¿Eliminar archivo?";
    modal.querySelector('p').textContent = esCarpeta
        ? "Se eliminarán todos los archivos contenidos. Irreversible."
        : "Esta acción no se puede deshacer.";

    modal.style.display = 'flex';

    const btnConfirmar = document.getElementById('btn-confirmar-modal');
    if (btnConfirmar) {
        // Reemplazar listener
        const nuevoBtn = btnConfirmar.cloneNode(true);
        btnConfirmar.parentNode.replaceChild(nuevoBtn, btnConfirmar);

        nuevoBtn.textContent = "Eliminar";
        nuevoBtn.disabled = false;
        nuevoBtn.addEventListener('click', () => ejecutarEliminacion(nuevoBtn));
    }
}

function ejecutarEliminacion(btnEjecutar) {
    if (!idParaEliminar) return;

    btnEjecutar.textContent = "Eliminando...";
    btnEjecutar.disabled = true;

    const endpoint = esEliminacionCarpeta
        ? `/eliminar-carpeta/${idParaEliminar}`
        : `/eliminar/${idParaEliminar}`;

    fetch(endpoint, { method: 'DELETE' })
        .then(resp => resp.json())
        .then(datos => {
            guardarNotificacion("Elemento eliminado.");
            window.location.reload();
        })
        .catch(err => {
            alert("Error al eliminar");
            window.location.reload();
        });
}


function configurarAccionesMasivas() {
    const casillaTodo = document.getElementById('casilla-seleccionar-todo');
    const barra = document.getElementById('barra-acciones-masivas');

    if (casillaTodo) {
        casillaTodo.addEventListener('change', () => {
            document.querySelectorAll('.casilla-archivo').forEach(c => c.checked = casillaTodo.checked);
            actualizarBarraAcciones();
        });
    }

    // Delegacion cambio checkboxes
    document.addEventListener('change', (e) => {
        if (e.target.classList.contains('casilla-archivo')) {
            actualizarBarraAcciones();
        }
    });

    const btnCerrarBarra = document.getElementById('btn-cerrar-barra');
    if (btnCerrarBarra) {
        btnCerrarBarra.addEventListener('click', () => {
            if (casillaTodo) casillaTodo.checked = false;
            document.querySelectorAll('.casilla-archivo').forEach(c => c.checked = false);
            actualizarBarraAcciones();
        });
    }

    const btnEliminarMultiples = document.getElementById('btn-eliminar-multiples');
    if (btnEliminarMultiples) {
        btnEliminarMultiples.addEventListener('click', () => {
            const marcados = document.querySelectorAll('.casilla-archivo:checked');
            if (marcados.length === 0) return;

            // Preparar modal para eliminación masiva
            const modal = document.getElementById('modal-eliminar');
            if (!modal) return;

            const idsArchivos = [];
            const idsCarpetas = [];

            marcados.forEach(cb => {
                const tr = cb.closest('tr');
                const id = tr.dataset.id;
                if (tr.classList.contains('fila-carpeta')) idsCarpetas.push(id);
                else idsArchivos.push(id);
            });

            modal.querySelector('h3').textContent = `¿Eliminar ${marcados.length} elementos?`;
            modal.querySelector('p').textContent = "Se eliminará todo permanentemente.";
            modal.style.display = 'flex';

            const btnConfirmar = document.getElementById('btn-confirmar-modal');
            const nuevoBtn = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(nuevoBtn, btnConfirmar);

            nuevoBtn.textContent = "Eliminar Todo";
            nuevoBtn.disabled = false;

            nuevoBtn.addEventListener('click', () => {
                nuevoBtn.textContent = "Procesando...";
                nuevoBtn.disabled = true;

                fetch('/eliminar-multiples', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ids: idsArchivos, carpetas_ids: idsCarpetas })
                })
                    .then(resp => resp.json())
                    .then(d => {
                        guardarNotificacion(`${d.deleted || d.eliminados} elementos eliminados.`);
                        window.location.reload();
                    })
                    .catch(() => window.location.reload());
            });
        });
    }

    const btnDescargar = document.getElementById('btn-descargar-multiples');
    if (btnDescargar) {
        btnDescargar.addEventListener('click', () => {
            const marcados = document.querySelectorAll('.casilla-archivo:checked');
            const ids = [];
            marcados.forEach(cb => {
                const tr = cb.closest('tr');
                if (!tr.classList.contains('fila-carpeta')) ids.push(tr.dataset.id);
            });

            if (ids.length === 0) return alert("Selecciona archivos para descargar (no carpetas).");

            fetch('/descargar-zip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids })
            })
                .then(resp => resp.ok ? resp.blob() : Promise.reject())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url; a.download = 'archivos.zip';
                    document.body.appendChild(a); a.click(); a.remove();
                })
                .catch(() => alert("Error descarga"));
        });
    }
}

function actualizarBarraAcciones() {
    const numSeleccionados = document.querySelectorAll('.casilla-archivo:checked').length;
    const barra = document.getElementById('barra-acciones-masivas');
    const etiqueta = document.getElementById('contador-seleccionados');
    if (etiqueta) etiqueta.textContent = `${numSeleccionados} seleccionados`;
    if (barra) barra.style.display = numSeleccionados > 0 ? 'flex' : 'none';
}

function configurarOrdenamiento() {
    const selectorOrden = document.getElementById('orden-fecha');
    if (!selectorOrden) return;

    selectorOrden.addEventListener('change', () => {
        ordenarTabla(selectorOrden.value);
    });

    // Aplicar orden por defecto (descendente)
    ordenarTabla('desc');
}

function ordenarTabla(orden) {
    const cuerpoTabla = document.getElementById('cuerpo-tabla');
    if (!cuerpoTabla) return;

    // Obtener todas las filas (carpetas y archivos)
    const filas = Array.from(cuerpoTabla.querySelectorAll('tr:not(#fila-sin-archivos)'));

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

    // Limpiar cuerpoTabla
    cuerpoTabla.innerHTML = '';

    // Insertar carpetas primero, luego archivos
    carpetas.forEach(f => cuerpoTabla.appendChild(f));
    archivos.forEach(f => cuerpoTabla.appendChild(f));

    // Si no hay elementos, mostrar mensaje
    if (filas.length === 0) {
        const filaVacia = document.createElement('tr');
        filaVacia.id = 'fila-sin-archivos';
        filaVacia.innerHTML = '<td colspan="6" class="celda-sin-archivos">No hay archivos subidos.</td>';
        cuerpoTabla.appendChild(filaVacia);
    }
}
