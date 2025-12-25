/**
 * Módulo de Subida de Archivos y Carpetas.
 * Implementa soporte avanzado para subida recursiva vía Drag & Drop y selector tradicional.
 * Sincronizado con el sistema de rutas relativas del backend para recrear estructuras de directorios.
 */
import { formatearTamano } from './utilidades.js';
import { guardarNotificacion } from './interfaz.js';

let colaArchivos = [];
let subiendo = false;

/**
 * Inicializa todos los disparadores y oyentes de eventos para la carga de archivos.
 */
export function inicializarSubidas() {
    const zona = document.getElementById('zona-arrastre');
    const entradaArchivo = document.getElementById('entrada-archivo');
    const entradaCarpeta = document.getElementById('entrada-carpeta');
    const disparadorArchivo = document.getElementById('disparador-archivo');
    const disparadorCarpeta = document.getElementById('disparador-carpeta');

    if (!zona) return;

    // Vinculación de enlaces visuales con inputs ocultos
    disparadorArchivo?.addEventListener('click', () => entradaArchivo.click());
    disparadorCarpeta?.addEventListener('click', () => entradaCarpeta.click());

    // Manejo de selección por explorador de archivos nativo
    entradaArchivo?.addEventListener('change', (e) => {
        manejarArchivos(e.target.files);
        entradaArchivo.value = '';
    });

    entradaCarpeta?.addEventListener('change', (e) => {
        manejarArchivos(e.target.files);
        entradaCarpeta.value = '';
    });

    // Soporte para Arrastrar y Soltar (Drag & Drop) con estados visuales
    zona.addEventListener('dragover', (e) => {
        e.preventDefault();
        zona.classList.add('drag-active');
    });

    zona.addEventListener('dragleave', () => zona.classList.remove('drag-active'));

    zona.addEventListener('drop', async (e) => {
        e.preventDefault();
        zona.classList.remove('drag-active');

        const items = e.dataTransfer.items;
        if (items) {
            // Recorrer elementos arrastrados (pueden ser archivos o carpetas)
            for (let i = 0; i < items.length; i++) {
                const entry = items[i].webkitGetAsEntry();
                if (entry) {
                    await procesarEntrada(entry);
                }
            }
        } else {
            // Respaldo para navegadores antiguos sin webkitGetAsEntry
            manejarArchivos(e.dataTransfer.files);
        }
    });

    // Inicio de subida masiva
    document.getElementById('btn-subir-todo')?.addEventListener('click', procesarCola);
}

/**
 * Escanea recursivamente una entrada del sistema de archivos.
 * Si es carpeta, profundiza en ella; si es archivo, lo añade a la cola.
 * @param {FileSystemEntry} entry - Elemento detectado.
 * @param {string} path - Ruta acumulada para mantener jerarquía.
 */
async function procesarEntrada(entry, path = "") {
    if (entry.isFile) {
        const file = await new Promise((resolve) => entry.file(resolve));
        agregarACola(file, path + file.name);
    } else if (entry.isDirectory) {
        const reader = entry.createReader();
        const entries = await new Promise((resolve) => reader.readEntries(resolve));
        for (const child of entries) {
            await procesarEntrada(child, path + entry.name + "/");
        }
    }
}

/**
 * Procesa una lista de archivos y los incorpora a la cola de subida.
 */
function manejarArchivos(archivos) {
    ([...archivos]).forEach(archivo => agregarACola(archivo));
}

/**
 * Añade un archivo a la cola interna y crea su representación visual en la UI.
 * @param {File} archivo - Objeto File nativo.
 * @param {string} rutaPersonalizada - Ruta relativa forzada (para carpetas D&D).
 */
function agregarACola(archivo, rutaPersonalizada = null) {
    const id = Math.random().toString(36).substr(2, 9);
    const rutaRelativa = rutaPersonalizada || (archivo.webkitRelativePath && archivo.webkitRelativePath.length > 0 ? archivo.webkitRelativePath : archivo.name);

    colaArchivos.push({ id, archivo, rutaRelativa });

    const contenedor = document.querySelector('.cola-archivos');
    const plantilla = document.getElementById('plantilla-progreso');
    if (!contenedor || !plantilla) return;

    const clon = plantilla.content.cloneNode(true);
    const itemElem = clon.querySelector('.item-progreso-subida');
    itemElem.id = `subida-${id}`;
    clon.querySelector('.nombre-archivo').textContent = rutaRelativa;
    clon.querySelector('.tamano-archivo').textContent = formatearTamano(archivo.size);

    // Botón para eliminar un archivo de la cola antes de subir
    clon.querySelector('.btn-cerrar').onclick = () => {
        colaArchivos = colaArchivos.filter(item => item.id !== id);
        itemElem.remove();
        actualizarVisibilidadBotones();
    };

    contenedor.appendChild(clon);
    actualizarVisibilidadBotones();
}

/**
 * Muestra u oculta los controles de subida según el estado de la cola.
 */
function actualizarVisibilidadBotones() {
    const btnEnviar = document.getElementById('acciones-cola');
    if (btnEnviar) {
        btnEnviar.style.display = colaArchivos.length > 0 ? 'block' : 'none';
    }
}

/**
 * Inicia la subida secuencial de la cola de archivos al servidor.
 */
async function procesarCola() {
    if (subiendo || colaArchivos.length === 0) return;
    subiendo = true;

    const btn = document.getElementById('btn-subir-todo');
    if (btn) {
        btn.disabled = true;
        btn.textContent = "Subiendo...";
    }

    // Subida secuencial para evitar saturar el ancho de banda y el servidor
    while (colaArchivos.length > 0) {
        const item = colaArchivos.shift();
        await subirArchivoAlServidor(item);
    }

    guardarNotificacion("Subida finalizada con éxito.");
    window.location.reload();
}

/**
 * Realiza la petición AJAX para subir un archivo individual.
 * Gestiona la barra de progreso en tiempo real.
 */
function subirArchivoAlServidor(itemCola) {
    return new Promise((resolve) => {
        const zona = document.getElementById('zona-arrastre');
        const cid = zona ? zona.getAttribute('data-carpeta-actual') : "";

        const form = new FormData();
        form.append('archivos', itemCola.archivo);
        form.append('rutas_relativas', itemCola.rutaRelativa);
        if (cid) form.append('carpeta_id', cid);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/subir', true);

        const elementoUI = document.getElementById(`subida-${itemCola.id}`);
        const barra = elementoUI?.querySelector('.barra-progreso');
        const textoPorcentaje = elementoUI?.querySelector('.estado-progreso');

        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const pct = Math.round((e.loaded / e.total) * 100);
                if (barra) barra.style.width = pct + '%';
                if (textoPorcentaje) textoPorcentaje.textContent = pct + '%';
            }
        };

        xhr.onload = () => {
            elementoUI?.remove();
            resolve();
        };

        xhr.onerror = () => {
            console.error("Fallo en la subida:", itemCola.rutaRelativa);
            resolve();
        };

        xhr.send(form);
    });
}
