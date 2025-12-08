
// stats.js - Cálculo de estadísticas

import { parseTamano, formatearTamano, detectarTipo } from './utils.js';

export function initStats() {
    // Inicialización de stats si es necesario
    // Por ahora solo actualizamos al cargar
}

export function actualizarEstadisticas() {
    const todasFilas = document.querySelectorAll('.fila-archivo');
    const filasArchivos = document.querySelectorAll('.fila-archivo:not(.fila-carpeta)');
    const filasCarpetas = document.querySelectorAll('.fila-carpeta');

    const statTotal = document.getElementById('stats-total-archivos');
    const statEspacio = document.getElementById('stats-espacio-usado');
    const statTipo = document.getElementById('stats-tipo-comun');

    if (!statTotal) return;

    // Total Count: carpetas + archivos (solo elementos visibles)
    const totalVisible = Array.from(todasFilas).filter(f => f.style.display !== 'none').length;
    statTotal.textContent = totalVisible;

    // Calc Type (solo archivos, no carpetas)
    const tiposConteo = {};

    filasArchivos.forEach(fila => {
        // Solo contar archivos visibles
        if (fila.style.display === 'none') return;

        const nomElem = fila.querySelector('.nombre');
        if (nomElem) {
            const tipo = detectarTipo(nomElem.textContent);
            tiposConteo[tipo] = (tiposConteo[tipo] || 0) + 1;
        }
    });

    if (statTipo) {
        let max = 0;
        let winner = '-';
        Object.entries(tiposConteo).forEach(([k, v]) => {
            if (v > max) { max = v; winner = k; }
        });
        statTipo.textContent = winner.charAt(0).toUpperCase() + winner.slice(1);
    }
}
