import { initUI } from './modules/interfaz.js';
import { initUploads } from './modules/subidas.js';
import { initFiles } from './modules/archivos.js';
import { initAuth } from './modules/autenticacion.js';
import { initFilters } from './modules/filtros.js';

document.addEventListener('DOMContentLoaded', () => {
    initUI();
    initUploads();
    initFiles();
    initAuth();
    initFilters();
});
