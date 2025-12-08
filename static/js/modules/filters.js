// filters.js - Filtrado y búsqueda de archivos

import { actualizarEstadisticas } from './stats.js';

export function initFilters() {
    setupSearch();
    setupTypeFilter();
}

function setupSearch() {
    const inputBusqueda = document.getElementById('input-busqueda');
    if (!inputBusqueda) return;
    
    inputBusqueda.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        filtrarTabla(query, null);
    });
}

function setupTypeFilter() {
    const selectTipo = document.getElementById('filtro-tipo');
    if (!selectTipo) return;
    
    selectTipo.addEventListener('change', (e) => {
        const tipo = e.target.value;
        filtrarTabla(null, tipo);
    });
}

function filtrarTabla(searchQuery, tipoFiltro) {
    const filas = document.querySelectorAll('.fila-archivo');
    const inputBusqueda = document.getElementById('input-busqueda');
    const selectTipo = document.getElementById('filtro-tipo');
    
    // Obtener valores actuales si no se pasaron
    const query = searchQuery !== null ? searchQuery : (inputBusqueda ? inputBusqueda.value.toLowerCase() : '');
    const tipo = tipoFiltro !== null ? tipoFiltro : (selectTipo ? selectTipo.value : 'todos');
    
    filas.forEach(fila => {
        const nombreElem = fila.querySelector('.nombre');
        const nombre = nombreElem ? nombreElem.textContent.toLowerCase() : '';
        const tipoArchivo = fila.dataset.tipo || 'carpeta';
        
        // Filtro de búsqueda
        const matchSearch = nombre.includes(query);
        
        // Filtro de tipo
        const matchType = tipo === 'todos' || tipoArchivo === tipo;
        
        // Mostrar/ocultar fila
        if (matchSearch && matchType) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });
    
    // Actualizar estadísticas después de filtrar
    actualizarEstadisticas();
}
