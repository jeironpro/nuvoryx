import { formatearTamano, obtenerConfiguracionIcono } from './utilidades.js';
import { guardarNotificacion } from './interfaz.js';

let colaArchivos = [];

export function inicializarSubidas() {
    const zonaArrastre = document.getElementById('zona-arrastre');
    const entradaArchivo = document.getElementById('entrada-archivo');
    const btnSubirTodo = document.getElementById('btn-subir-todo');

    if (zonaArrastre && entradaArchivo) {
        // Click para abrir
        zonaArrastre.addEventListener('click', () => entradaArchivo.click());
        entradaArchivo.addEventListener('click', (e) => e.stopPropagation());

        // Evento de cambio
        entradaArchivo.addEventListener('change', (e) => {
            manejarArchivos(e.target.files);
            entradaArchivo.value = '';
        });

        // Eventos Drago and Drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(nombreEvento => {
            zonaArrastre.addEventListener(nombreEvento, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        ['dragenter', 'dragover'].forEach(nombreEvento => {
            zonaArrastre.addEventListener(nombreEvento, () => {
                zonaArrastre.classList.add('resaltado');
                zonaArrastre.style.borderColor = 'var(--primary-color)';
                zonaArrastre.style.backgroundColor = '#F9F5FF';
            }, false);
        });

        ['dragleave', 'drop'].forEach(nombreEvento => {
            zonaArrastre.addEventListener(nombreEvento, () => {
                zonaArrastre.classList.remove('resaltado');
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

            const copia = [...colaArchivos];
            for (const item of copia) {
                await subirArchivoAlServidor(item);
            }

            colaArchivos = [];
            actualizarVisibilidad();
            btnSubirTodo.textContent = 'Completado';
            setTimeout(() => window.location.reload(), 1000);
        });
    }
}

function manejarArchivos(archivos) {
    // Verificar si el usuario está autenticado
    const estaAutenticado = document.body.getAttribute('data-authenticated') === 'true';

    if (!estaAutenticado) {
        guardarNotificacion('Debes iniciar sesión para subir archivos.', 'error');
        return;
    }

    ([...archivos]).forEach(archivo => agregarACola(archivo));
    actualizarVisibilidad();
}

function agregarACola(archivo) {
    const contenedorProgreso = document.getElementById('contenedor-progreso');
    const plantilla = document.getElementById('plantilla-progreso');
    if (!contenedorProgreso || !plantilla) return;

    const id = Math.random().toString(36).substr(2, 9);
    colaArchivos.push({
        id,
        archivo,
        rutaRelativa: (archivo.webkitRelativePath && archivo.webkitRelativePath.length > 0) ? archivo.webkitRelativePath : archivo.name
    });


    const clon = plantilla.content.cloneNode(true);
    const item = clon.querySelector('.item-progreso-subida');
    item.dataset.colaId = id;

    // Contenido
    clon.querySelector('.nombre-archivo').textContent = archivo.name;
    clon.querySelector('.tamano-archivo').textContent = formatearTamano(archivo.size);

    // Icono
    const contenedorIcono = clon.querySelector('.icono-progreso');
    const conf = obtenerConfiguracionIcono(archivo);
    contenedorIcono.innerHTML = conf.svg;
    contenedorIcono.className = `icono-progreso ${conf.clase}`;

    // Botón eliminar
    item.querySelector('.btn-cerrar').addEventListener('click', () => {
        colaArchivos = colaArchivos.filter(f => f.id !== id);
        item.remove();
        actualizarVisibilidad();
    });

    contenedorProgreso.appendChild(item);
}

function actualizarVisibilidad() {
    const acciones = document.getElementById('acciones-cola');
    if (acciones) {
        acciones.style.display = colaArchivos.length > 0 ? 'block' : 'none';
    }
}

function subirArchivoAlServidor(itemCola) {
    return new Promise((resolve) => {
        const elementoItem = document.querySelector(`.item-progreso-subida[data-cola-id="${itemCola.id}"]`);
        if (!elementoItem) { resolve(); return; }

        const barra = elementoItem.querySelector('.barra-progreso');
        const estado = elementoItem.querySelector('.estado-progreso');
        const btnCerrar = elementoItem.querySelector('.btn-cerrar');
        if (btnCerrar) btnCerrar.style.display = 'none';

        estado.textContent = 'Subiendo...';

        const datosFormulario = new FormData();
        datosFormulario.append('archivos', itemCola.archivo);
        datosFormulario.append('rutas_relativas', itemCola.rutaRelativa);

        const zona = document.getElementById('zona-arrastre');
        const cid = zona ? zona.getAttribute('data-carpeta-actual') : null;
        if (cid) datosFormulario.append('carpeta_id', cid);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/subir', true);

        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const porcentaje = (e.loaded / e.total) * 100;
                barra.style.width = porcentaje + '%';
                estado.textContent = Math.round(porcentaje) + '%';
            }
        };

        xhr.onload = () => {
            if (xhr.status === 200) {
                barra.style.width = '100%';
                estado.textContent = 'Completado';
                guardarNotificacion(`Archivo "${itemCola.archivo.name}" subido.`);
            } else {
                estado.textContent = 'Error';
                elementoItem.style.backgroundColor = '#FEF3F2';
            }
            resolve();
        };
        xhr.onerror = () => {
            estado.textContent = 'Error red';
            elementoItem.style.backgroundColor = '#FEF3F2';
            resolve();
        };

        xhr.send(datosFormulario);
    });
}
