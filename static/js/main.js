// main.js - Entry point

import { initUI } from './modules/ui.js';
import { initUploads } from './modules/uploads.js';
import { initStats, actualizarEstadisticas } from './modules/stats.js';
import { initFiles } from './modules/files.js';
import { initAuth } from './modules/auth.js';
import { initFilters } from './modules/filters.js';

document.addEventListener('DOMContentLoaded', () => {
    initUI();
    initUploads();
    initStats();
    initFiles();
    initAuth();
    initFilters();
    
    // Calcular estadísticas iniciales
    actualizarEstadisticas();
});
