export function inicializarFiltros() {
    configurarBusqueda();
    configurarFiltroTipo();
}

function configurarBusqueda() {
    const entradaBusqueda = document.getElementById('entrada-busqueda');
    if (!entradaBusqueda) return;

    entradaBusqueda.addEventListener('input', (e) => {
        const consulta = e.target.value.toLowerCase();
        filtrarTabla(consulta, null);
    });
}

function configurarFiltroTipo() {
    const selectorTipo = document.getElementById('filtro-tipo');
    if (!selectorTipo) return;

    selectorTipo.addEventListener('change', (e) => {
        const tipo = e.target.value;
        filtrarTabla(null, tipo);
    });
}

function filtrarTabla(consultaBusqueda, tipoFiltro) {
    const filas = document.querySelectorAll('.fila-archivo');
    const entradaBusqueda = document.getElementById('entrada-busqueda');
    const selectorTipo = document.getElementById('filtro-tipo');

    // Obtener valores actuales si no se pasaron
    const consulta = consultaBusqueda !== null ? consultaBusqueda : (entradaBusqueda ? entradaBusqueda.value.toLowerCase() : '');
    const tipo = tipoFiltro !== null ? tipoFiltro : (selectorTipo ? selectorTipo.value : 'todos');

    filas.forEach(filaEnc => {
        const elemNombre = filaEnc.querySelector('.nombre');
        const nombre = elemNombre ? elemNombre.textContent.toLowerCase() : '';
        const tipoArchivo = filaEnc.dataset.tipo || 'carpeta';

        // Filtro de búsqueda
        const coincideBusqueda = nombre.includes(consulta);

        // Filtro de tipo
        const coincideTipo = tipo === 'todos' || tipoArchivo === tipo;

        // Mostrar/ocultar fila
        if (coincideBusqueda && coincideTipo) {
            filaEnc.style.display = '';
        } else {
            filaEnc.style.display = 'none';
        }
    });
}
